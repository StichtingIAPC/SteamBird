"""
Requires RFC8255_ to be commonly adopted.

.. _RFC8255: https://tools.ietf.org/html/rfc8255
"""

import os
import re
from collections import defaultdict
from contextlib import contextmanager
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from typing import List, Tuple

from django.conf import settings
from django.core.mail import EmailMultiAlternatives, SafeMIMEMultipart, \
    SafeMIMEText
from django.template.loader import get_template
from django.template.loaders.app_directories import get_app_template_dirs
from django.utils import translation
from django.utils.translation import ugettext as _


@contextmanager
def language(l):
    translation.activate(l)
    yield
    translation.deactivate()


class MultilingualEmailMessage(EmailMultiAlternatives):
    def __init__(self, mixed_subtype="multilingual", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.languages: List[Tuple[str, MIMEBase]] = []
        self.mixed_subtype = mixed_subtype

    def _create_attachments(self, msg):
        encoding = self.encoding or settings.DEFAULT_CHARSET
        body_msg = msg
        msg = SafeMIMEMultipart(_subtype=self.mixed_subtype, encoding=encoding)

        if self.body or body_msg.is_multipart():
            msg.attach(body_msg)

        for attachment in self.attachments:
            if isinstance(attachment, MIMEBase):
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


# Collect all mail templates
templates = defaultdict(lambda: defaultdict(list))
rx = re.compile(r'.*/mail/(?P<name>.*)/(?P<locale>[a-z]+)\.(?P<subtype>[a-z]+)')
for template_dir in (get_app_template_dirs("templates")):
    for dir, dirnames, filenames in os.walk(template_dir):
        for filename in filenames:
            match = rx.match("{}/{}".format(dir, filename))
            if match:
                d = match.groupdict()
                templates[d['name']][d['locale']].append({
                    **d,
                    'file': os.path.join(dir, filename),
                })

templates = {k: dict(v) for k, v in templates.items()}


def create_multilingual_mail(template_name: str, subject: str, context: dict,
                             **kwargs):
    msg = MultilingualEmailMessage(subject=subject, **kwargs)

    langs = templates[template_name]
    for lang, ts in langs.items():
        with language(lang):
            lang_alt = MIMEMultipart(_subtype='alternative')
            lang_alt.add_header("Subject", _(subject))

            for template in ts:
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


def test():
    context = {}
    subject = "Test"
    template_name = "teacher_msp"
    from_email = "test@iapc.nl"
    recipients = ["rkleef@iapc.nl"]
    primary_language = "nl"

    mp = create_multilingual_mail(
        template_name, subject, context, from_email=from_email, to=recipients)
    mp.send()
