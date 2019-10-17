"""
This file is responsible for sending multilingual mails.
When multiple templates are available, RFC8255_ must be commonly adopted.
As this, at the time of writing, RFC8255_ is not yet commonly adopted, so only
one language per email must be specified.

TODO: implement language preferences.

.. _RFC8255: https://tools.ietf.org/html/rfc8255
"""

import os
import re
from collections import defaultdict
from contextlib import contextmanager
from email.encoders import encode_base64
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Tuple

from django.conf import settings
from django.core.mail import EmailMultiAlternatives, SafeMIMEMultipart, \
    SafeMIMEText, EmailMessage, get_connection
from django.template.loader import get_template
from django.template.loaders.app_directories import get_app_template_dirs
from django.utils import translation
from django.utils.translation import ugettext as _


@contextmanager
def language(lang: str):
    translation.activate(lang)
    yield
    translation.deactivate()


class MultiTemplatableEmailMessage(EmailMultiAlternatives):
    """
    A version of EmailMultiAlternative that makes it easy to send
    multipart/alternative messages with a dynamically generated set of
    alternatives.

    This can, as opposed to EmailMultiAlternatives, gracefully handle embedding
    dynamic MIMEBase objects in the alternatives list.
    """
    alternative_subtype = 'alternative'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _create_mime_attachment(self, content, mimetype) -> MIMEBase:
        """
        Ensures content is a valid MIMEBase.

        :param content: the content to be converted.
        :param mimetype: the mimetype of the unconverted content.
        :return: a MIMEBase
        """
        if isinstance(content, MIMEText):
            return content

        if isinstance(content, MIMEBase) and\
                'Content-Transfer-Encoding' in content and\
                content['Content-Transfer-Encoding'] != 'base64':

            encode_base64(content)

        return super()._create_mime_attachment(content, mimetype)


class MultilingualEmailMessage(EmailMultiAlternatives):
    """
    An EmailMessage that can send multilingual (RFC8255_) emails.

    .. _RFC8255: https://tools.ietf.org/html/rfc8255
    """

    def __init__(self, *args, mixed_subtype="multilingual", **kwargs):
        super().__init__(*args, **kwargs)
        self.languages: List[Tuple[str, MIMEBase]] = []
        self.mixed_subtype = mixed_subtype

    def _create_attachments(self, msg) -> SafeMIMEMultipart:
        """
        Construct the list of languages and alternatives.

        :param msg: the message to enhance.
        :return: the enhanced message
        """
        encoding = self.encoding or settings.DEFAULT_CHARSET
        body_msg = msg
        msg = SafeMIMEMultipart(_subtype=self.mixed_subtype, encoding=encoding)

        if self.body or body_msg.is_multipart():
            msg.attach(body_msg)

        # Attach all attachments.
        for attachment in self.attachments:
            if isinstance(attachment, MIMEBase):
                # This may be dysfunctional, but this is unsure.
                msg.attach(attachment)
            else:
                msg.attach(self._create_attachment(*attachment))

        for lang, body in self.languages:
            att = self._create_attachment(filename=None, content=body,
                                          mimetype="message/rfc822")
            att.add_header("Content-Language", lang)
            att.add_header("Content-Translation-Type", "automated")
            att.add_header("Content-Disposition", "inline",
                           filename="translation-{}.eml".format(lang))

            msg.attach(att)

        return msg

    def add_language(self, lang: str, content: MIMEBase):
        self.languages.append((lang, content))


# pylint: disable=invalid-name
templates = None


def ensure_setup() -> None:
    """
    Ensure templates are populated

    :return: None
    """
    # pylint: disable=global-statement
    global templates

    if templates:
        return

    # Collect all mail templates
    templates = defaultdict(lambda: defaultdict(list))
    regex = re.compile(
        r'.*/mail/(?P<name>.*)/(?P<locale>[a-z]+)\.(?P<subtype>[a-z]+)')
    for template_dir in (get_app_template_dirs("templates")):
        for directory, _, filenames in os.walk(template_dir):
            for filename in filenames:
                match = regex.match("{}/{}".format(directory, filename))
                if match:
                    d = match.groupdict()
                    templates[d['name']][d['locale']].append({
                        **d,
                        'file': os.path.join(directory, filename),
                    })

    templates = {k: dict(v) for k, v in templates.items()}


def create_multilingual_mail(template_name: str, subject: str, context: dict,
                             **kwargs) -> EmailMessage:
    ensure_setup()

    languages = templates[template_name]

    if len(languages.items()) == 1:
        languages: dict
        lang, tpls = list(languages.items())[0]

        with language(lang):
            msg = MultiTemplatableEmailMessage(
                subject=subject,
                body=False,
                **kwargs
            )

            for template in tpls:
                msg.attach_alternative(
                    SafeMIMEText(
                        _text=get_template(template['file']).render({
                            'locale': template['locale'],
                            **context,
                        }),
                        _subtype=template['subtype'],
                        _charset=msg.encoding or settings.DEFAULT_CHARSET
                    ), 'unknown/unknown')

        return msg

    msg = MultilingualEmailMessage(subject=subject, **kwargs)

    for lang, tpls in languages.items():
        with language(lang):
            lang_alt = MIMEMultipart(_subtype='alternative')
            lang_alt.add_header("Subject", _(subject))

            for template in tpls:
                lang_alt.attach(
                    SafeMIMEText(get_template(template['file']).render({
                        'locale': template['locale'],
                        **context,
                    }), _subtype=template['subtype']))

            msg.add_language(lang, lang_alt)

    info = MIMEMultipart(_subtype='alternative')
    info.attach(SafeMIMEText(
        get_template("steambird/mail/multilingual_header.html").render({}),
        _subtype="html", _charset="utf-8"))
    info.attach(SafeMIMEText(
        get_template("steambird/mail/multilingual_header.plain").render({}),
        _subtype="plain", _charset="utf-8"))

    info.add_header("Content-Disposition", "inline")

    msg.attach(info)

    return msg


def send_mimemessages(msgs: List[EmailMessage]) -> None:
    """
    Sends a list of EmailMessage.

    :param msgs: list of messages to send
    :return: nothing
    """
    conn = get_connection()
    conn.open()
    for msg in msgs:
        msg.send()
    conn.close()


def _test():
    """
    Example sending of a message.
    """
    context = {}
    subject = "Test"
    template_name = "test"
    from_email = "test@iapc.nl"
    recipients = ["rkleef@iapc.nl"]

    mp = create_multilingual_mail(
        template_name, subject, context, from_email=from_email, to=recipients)
    send_mimemessages([mp])
