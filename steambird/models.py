from django.conf import settings
from django.db import models
from django.db.models import SET_NULL
from django.utils.translation import ugettext_lazy as _
from enum import Enum
from polymorphic.models import PolymorphicModel


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


class StudyType(Enum):
    BSc = "Bachelor"
    MSc = "Master"
    PreM = "PreMaster"


class Period(Enum):
    Q1 = "Quartile 1"
    Q2 = "Quartile 2"
    Q3 = "Quartile 3"
    Q4 = "Quartile 4"
    Q5 = "Quartile 5 (sad summer students)"
    Q1_HALF = "Quartile 1, half year course"
    Q3_HALF = "Quartile 3, half year course"
    FULL_YEAR = "Full year course"


class Teacher(models.Model):
    titles = models.CharField(max_length=50)
    initials = models.CharField(max_length=15)
    first_name = models.CharField(max_length=50)
    surname_prefix = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    active = models.BooleanField(verbose_name=_("Is the teacher still active at the UT?"), default=True, )
    retired = models.BooleanField(verbose_name=_("Is the teacher retried?"), default=False)
    last_login = models.DateTimeField(verbose_name=_("Last Login"), null=True, blank=True)


class Module(models.Model):
    name = models.CharField(max_length=80, verbose_name=_("Name of module"))
    course_code = models.IntegerField(verbose_name=_("Course code of module, references Osiris"), unique=True)
    coordinator = models.ForeignKey(Teacher, on_delete=SET_NULL, null=True,
                                    verbose_name=_("Coordinator reference for a module, references the Teacher"))
    module_moment = models.CharField(max_length=5, choices=[(moment, moment.value) for moment in ModuleMoment])


class Course(models.Model):
    class Meta:
        unique_together = (('course_code', 'year'),)

    module = models.ForeignKey(Module, on_delete=SET_NULL, null=True,
                               verbose_name=_("Links course to possible module (maths) if needed"))
    course_code = models.IntegerField(verbose_name=_("Course code of module, references Osiris"), unique=True)
    teacher = models.ManyToManyField(Teacher)
    name = models.CharField(max_length=50, verbose_name=_("Name of Course"))
    year = models.IntegerField()
    materials = models.ManyToManyField('MaterialSelectionProcess')
    updated_teacher = models.BooleanField(default=False, verbose_name=_("Has the course been marked updated by the teacher for this year?"))
    updated_IAPC = models.BooleanField(default=False, verbose_name=_("Have we already checked this course this year?"))


class Study(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Name of the study, e.g. Creative Technology"))
    study_type = models.CharField(max_length=5, choices=[(study_type, study_type.value) for study_type in StudyType])
    courses = models.ManyToManyField(Course, through='StudyCourse', through_fields=('study', 'course'))

    class Meta:
        verbose_name_plural = "studies"


class StudyCourse(models.Model):
    class Meta:
        unique_together = (('course', 'study'),)

    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    study = models.ForeignKey(Study, on_delete=models.CASCADE)
    period = models.CharField(max_length=10, choices=[(period, period.value) for period in Period])


class StudyMaterial(models.Model):
    pass


class StudyMaterialEdition(PolymorphicModel):
    name = models.CharField(null=False, blank=False, max_length=255)
    material_type = models.ForeignKey(StudyMaterial, on_delete=models.DO_NOTHING, null=True)


class OtherMaterial(StudyMaterialEdition):
    """"Use if material is any material other than a scientific article or a book"""
    pass


class Book(StudyMaterialEdition):
    ISBN = models.CharField(null=False, unique=True, verbose_name=_("ISBN 13, used if book is from after 2007"),
                            max_length=13)
    author = models.CharField(null=False, blank=False, verbose_name=_(
        "Author names, these should be added automatically based on the ISBN search"), max_length=1000)
    img = models.URLField()
    year_of_publishing = models.IntegerField(max_length=4)

    def validate_ISBN(self, ISBN):
        if len(ISBN) == 10 or len(ISBN) == 13:
            return
        else:
            raise ValueError("ISBN does not match either known lengths")


class ScientificArticle(StudyMaterialEdition):
    DOI = models.CharField(null=False, blank=True, verbose_name=_(
        "Digital Object Identifier used for most Scientific Articles. Unique per article, if it has one (conference proceedings don't tend to have one)"),
                           max_length=255)
    author = models.CharField(null=False, blank=False, verbose_name=_(
        "Author names, these should be added automatically based on the DOI search"), max_length=1000)
    year_of_publishing = models.IntegerField(max_length=4)


class MaterialSelectionProcess(models.Model):
    osiris_specified_material = models.ForeignKey(StudyMaterialEdition, null=True, on_delete=SET_NULL, related_name='process_in_osiris')
    available_materials = models.ManyToManyField(StudyMaterialEdition, related_name='process_is_available')
    approved_material = models.ForeignKey(StudyMaterialEdition, null=True, on_delete=SET_NULL, related_name='process_is_approved')
    reason = models.CharField(max_length=255, verbose_name=_("Reason why there is a difference between Osiris and availability"), null=True)
