import datetime

from django.db import models
from django.utils.translation import ugettext_lazy as _

from steambird.models_coursetree import Period


class Config(models.Model):
    year = models.IntegerField(
        blank=True,
        null=True,
        default=datetime.date.today().year,
        verbose_name=_("Current year you are working in"))

    period = models.CharField(
        max_length=max([len(t.value) for t in Period]),
        choices=[(t.name, t.value) for t in Period],
        verbose_name=_("The period in the year you are working in"),
    )
