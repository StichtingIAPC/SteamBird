"""
This package contains everything related to Users and possible Groups the might belong to
"""
import uuid
from datetime import datetime
from typing import Union
from urllib.parse import quote

from django.contrib.auth.models import User
from django.db import models
from django.db.models.query import EmptyQuerySet, QuerySet
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _


class Teacher(models.Model):
    """
    Teacher definition. The information here is things one could find on e.g. people.utwente.nl
    """
    titles = models.CharField(max_length=50,
                              verbose_name=_("Academic titles"),
                              blank=True,
                              null=True)
    initials = models.CharField(max_length=15, verbose_name=_("Initials"))
    first_name = models.CharField(max_length=50, verbose_name=_("First name"))
    surname_prefix = models.CharField(
        max_length=50, null=True, blank=True,
        verbose_name=_("Surname prefix"))
    last_name = models.CharField(max_length=50, verbose_name=_("Last name"))
    email = models.EmailField(verbose_name=_("Email"), unique=True)
    active = models.BooleanField(default=True, verbose_name=_("Active"))
    retired = models.BooleanField(default=False, verbose_name=_("Retired"))
    user = models.ForeignKey(
        User, on_delete=models.PROTECT,
        verbose_name=_("The user associated to this teacher"),
        blank=True,
        null=True,
    )

    def last_login(self) -> datetime:
        """
        Method which returns the last login of a user

        :return: DateTime field
        """
        return self.user.last_login

    def get_absolute_url(self) -> str:
        """
        Absolute URL resolver for to teachers personal edit page. Used in Boecie views

        :return: Teacher url
        """
        return reverse('boecie:teacher.detail', kwargs={'pk': self.pk})

    def all_courses(self) -> Union[EmptyQuerySet, QuerySet]:
        """
        Method which returns all courses a teacher has ever given or is giving

        :return: Queryset, which can be an empty queryset
        """
        return self.coordinated_courses.all().union(self.teaches_courses.all())

    def all_courses_period(self, year: int, period) -> Union[EmptyQuerySet, QuerySet]:
        """
        Returns all courses the Teacher from which it is called gives within a given period and Year
        combination. Return can be empty.

        :param year: Integer Year (start of year)
        :param period: Period, as given by Period Enum
        :return: Queryset containing all courses teacher gives in that period of the year
        """
        return self.coordinated_courses.filter(calendar_year=year, period=period)\
            .union(self.teaches_courses.filter(calendar_year=year, period=period))

    def all_courses_year(self, year: int) -> Union[EmptyQuerySet, QuerySet]:
        """
        Returns all courses the Teacher from which it is called gives within a given Year. Return
        can be empty.

        :param year: int
        :return: Queryset containing
        """

        return self.coordinated_courses.filter(calendar_year=year) \
            .union(self.teaches_courses.filter(calendar_year=year))

    def __str__(self) -> str:
        """
        Returns stringified formal name

        :return: string consisting of all non-None names
        """
        return ' '.join(filter(lambda x: x,
                               [self.titles,
                                self.initials,
                                self.surname_prefix,
                                self.last_name]))

    class Meta:
        verbose_name = _('Teacher')
        verbose_name_plural = _('Teachers')


class StudyAssociation(models.Model):
    """
    Model which makes it possible to limit users capabilities to their own association

    String representation:
        <association name> (<studies association is responsible/associated with>)
    """

    name = models.CharField(
        max_length=128, verbose_name=_("Name of this association"))
    users = models.ManyToManyField(
        User, verbose_name=_('All the users that can manage books on behalf of '
                             'this organization'))
    studies = models.ManyToManyField(
        'Study', verbose_name=('The studies this association is affiliated '
                               'with'))

    class Meta:
        verbose_name = _('Association')
        verbose_name_plural = _('Associations')

    def __str__(self):
        return '{} ({})'.format(self.name, ', '.join(
            self.studies.values_list('slug', flat=True)))


class AuthToken(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name=_('User that will log in with given token'),
        on_delete=models.CASCADE,
        db_index=True,
    )

    token = models.UUIDField(
        max_length=64,
        verbose_name=_('Token that will be placed in the auth endpoint'),
        primary_key=True,
        default=uuid.uuid4,
    )

    last_host = models.GenericIPAddressField(
        verbose_name=_('Last location that this token was used.'),
        null=True,
        blank=True,
        default=None,
    )

    def login_url(self, next_url="/"):
        return "{}?token={}&next={}".format(
            reverse('token_login'), self.token, quote(next_url, safe=''))
