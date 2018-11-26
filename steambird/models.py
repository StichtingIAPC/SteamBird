from django.conf import settings
from django.db import models
from django.db.models import SET_NULL
from django.utils.translation import ugettext_lazy as _
from enum import Enum

class Teacher(models.Model):
    titles = models.CharField(max_length=50)
    initials = models.CharField(max_length=15)
    first_name = models.CharField(max_length=50)
    surname_prefix = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    active = models.BooleanField(verbose_name=_("Is the teacher still active at the UT?"), default=True,)
    retired = models.BooleanField(verbose_name=_("Is the teacher retried?"), default=False)
    last_login = models.DateTimeField(verbose_name=_("Last Login"))


class Module(models.Model):

    class ModuleMoment(Enum):
        y1_1A = "Year one, Quartile 1"
        y1_1B = "Year one, Quartile 2"
        y1_2A = "Year one, Quartile 3"
        y1_2B = "Year one, Quartile 4"

        y2_1A = "Year two, Quartile 1"
        y2_1B = "Year two, Quartile 2"
        y2_2A = "Year two, Quartile 3"
        y2_2B = "Year two, Quartile 4"

        y3_1A = "Year three, Quartile 1"
        y3_1B = "Year three, Quartile 2"
        y3_2A = "Year three, Quartile 3"
        y3_2B = "Year three, Quartile 4"

    name = models.CharField(max_length=80, verbose_name=_("Name of module"))
    course_code = models.IntegerField(verbose_name=_("Course code of module, references Osiris"), unique=True)
    coordinator = models.ForeignKey(Teacher, on_delete=SET_NULL, null=True, verbose_name=_("Coordinator reference for a module, references the Teacher"))
    module_moment = models.CharField(max_length=5, choices=[(moment, moment.value) for moment in ModuleMoment])


class Vak(models.Model):
    module = models.ForeignKey(Module, on_delete=SET_NULL, null=True, verbose_name=_("Links course to possible module (maths) if needed"))
    course_code = models.IntegerField(verbose_name=_("Course code of module, references Osiris"), unique=True)
    teacher_id = models.ForeignKey(Teacher, on_delete=SET_NULL, null=True)
    name = models.CharField(max_length=50, verbose_name=_("Name of Course"))


class Study(models.Model):

    class StudyType(Enum):
        BSc = "Bachelor"
        MSc = "Master"
        PreM = "PreMaster"

    name = models.CharField(max_length=100, verbose_name=_("Name of the study, e.g. Creative Technology"))
    study_type = models.CharField(max_length=5, choices=[(study_type, study_type.value) for study_type in StudyType])


class StudyVak(models.Model):
    class Meta:
        unique_together = (('vak','study'),)

    class Period(Enum):
        Q1 = "Quartile 1"
        Q2 = "Quartile 2"
        Q3 = "Quartile 3"
        Q4 = "Quartile 4"
        Q5 = "Quartile 5 (sad summer students)"
        Q1_HALF = "Quartile 1, half year course"
        Q3_HALF = "Quartile 3, half year course"
        FULL_YEAR = "Full year course"

    vak = models.ForeignKey(Vak, on_delete=models.CASCADE)
    study = models.ForeignKey(Study, on_delete=models.CASCADE)
    period = models.CharField(max_length=10, choices=[(period, period.value) for period in Period])


class Book(models.Model):
    ISBN_13 = models.IntegerField(null=False, unique=True, verbose_name=_("ISBN 13, used if book is from after 2007"))
    ISBN_10 = models.IntegerField(null=False, unique=True, verbose_name=_("ISBN 10, used if book is from before 2007"))
    author = models.CharField(null=False, blank=False, verbose_name=_("Author names, these should be added automatically based on the ISBN search"))
    title = models.CharField(null=False, blank=False, verbose_name=_("Title of the book, should be added automatically based on ISBN search"))


