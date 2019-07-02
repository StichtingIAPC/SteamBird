import datetime

from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _

from steambird.models.coursetree import Period


class Config(models.Model):
    year = models.IntegerField(
        blank=True,
        null=True,
        default=datetime.date.today().year,
        verbose_name=_("Current year you are working in"))

    period = models.CharField(
        max_length=max([len(t.value) for t in Period]),
        choices=[(t.name, t.value) for t in Period],
        default="Q1",
        verbose_name=_("The period in the year you are working in"),
    )
    # default on period is so that migrations don't break a number of views
    # due to invalid config setup

    @staticmethod
    def get_system_value(name: str):
        """
        Get the property 'name' from the first DB config entry

        :param name: the database name you want the value for
        :return: value of param
        """
        return Config.objects.first().__dict__[name]

    # pylint: disable=unused-argument
    @staticmethod
    def get_user_value(name: str, user: User):
        return Config.get_system_value(name)
