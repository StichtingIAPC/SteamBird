"""
This package contains the definitions used for any config options that don't relate to any other of
the packages
"""

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

    @staticmethod
    def get_system_value(name: str):
        """
        Get the property 'name' from the first DB config entry

        :param name: The database name you want the value for
        :return: Value of param
        """
        return Config.objects.first().__dict__[name]

    # pylint: disable=unused-argument
    @staticmethod
    def get_user_value(name: str, user: User):
        """
        Get the property 'name' from the DB entry config matching the User param

        :param name: The database name you want to retrieve the value for
        :param user: The user you want said named config value for
        :return: Value of 'name' parameter for 'User'
        """
        return Config.get_system_value(name)
