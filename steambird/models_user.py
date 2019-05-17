from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _


class Teacher(models.Model):
    titles = models.CharField(max_length=50, verbose_name=_("Academic titles"))
    initials = models.CharField(max_length=15, verbose_name=_("Initials"))
    first_name = models.CharField(max_length=50, verbose_name=_("First name"))
    surname_prefix = models.CharField(
        max_length=50, null=True, blank=True,
        verbose_name=_("Surname prefix"))
    last_name = models.CharField(max_length=50, verbose_name=_("Last name"))
    email = models.EmailField(verbose_name=_("Email"), unique=True)
    active = models.BooleanField(default=True, verbose_name=_("Active"))
    retired = models.BooleanField(default=False, verbose_name=_("Retired"))
    last_login = models.DateTimeField(
        null=True, blank=True, verbose_name=_("Time of last login"))
    user = models.ForeignKey(
        User, on_delete=models.PROTECT,
        verbose_name=_("The user associated to this"),
        blank=True,
        null=True,
    )

    def get_absolute_url(self):
        return reverse('boecie:teacher.detail', kwargs={'pk': self.pk})

    def __str__(self):
        if self.surname_prefix:
            return "{} {} {} {}".format(self.titles, self.initials, self.surname_prefix, self.last_name)
        return "{} {} {}".format(self.titles, self.initials, self.last_name)

    class Meta:
        verbose_name = _('Teacher')
        verbose_name_plural = _('Teachers')


class StudyAssociation(models.Model):
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
            [study for study in self.studies.values_list('slug', flat=True)]))
