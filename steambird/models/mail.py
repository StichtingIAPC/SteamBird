from typing import List, Optional

from django.db import models
from django.utils.translation import ugettext_lazy as _, ugettext as _t

from email.utils import make_msgid


class MailTopic(models.Model):
    """
    A mail topic describes a chain

    TODO: implement list_post url along with posting through a
      list_archive_manager.
    TODO: implement a list_unsubscribe URL so that we may be GDPR-compliant.
    """

    def last_message(self, exclude=None) -> 'MailMessage':
        if exclude:
            return self.mailmessage_set.exclude(pk=exclude).order_by("-pk").first()
        else:
            return self.mailmessage_set.order_by("-pk").first()

    def mailmessage_set_except(self, exclude) -> List['MailMessage']:
        return self.mailmessage_set.exclude(pk=exclude).order_by("-pk").all()

    @property
    def list_archive_manager(self):
        """
        Returns the object that manages the list archive, so that a List-Archive
        header can be generated.
        """
        return None

    @property
    def list_id(self):
        return "SteamBird_{}".format(self.pk)


def gen_msgid():
    return make_msgid("SteamBird")


class MailMessage(models.Model):
    """
    A mail message describes a single message, that either still needs to be
    sent, or was already sent.
    """

    message_id: str = models.TextField(
        default=gen_msgid,
        unique=True,
        verbose_name=_("The content of the Message-ID header"),
    )
    """
    MessageID is also a header, but has special meaning, and it is therefore
    quite useful to have a separate field for it.
    """

    body: str = models.TextField(
        verbose_name=_("The body of this message"),
    )

    topic: MailTopic = models.ForeignKey(
        MailTopic,
        on_delete=models.DO_NOTHING,
        verbose_name=_("The topic this message belongs to"),
    )

    def _in_reply_to_hdr_body(self) -> Optional[str]:
        msg = self.topic.last_message()
        if msg is None:
            return None

        return msg.message_id

    def _references_hdr_body(self) -> str:
        return " ".join(map(lambda m: m.message_id, self.topic.mailmessage_set))


class MailMessageHeader(models.Model):
    name: str = models.TextField(
        verbose_name=_("The header name"),
    )

    body: str = models.TextField(
        verbose_name=_("The header content"),
    )

    message: MailMessage = models.ForeignKey(
        MailMessage,
        on_delete=models.CASCADE,
        verbose_name=_('The message this header is a part of'),
    )


class BannedEmail(models.Model):
    direction: bool = models.BooleanField(
    )
    email: str = models.CharField(
        max_length=128,
    )
