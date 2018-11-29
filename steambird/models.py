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
    titles = models.CharField(max_length=50, verbose_name=_("Academic titles"))
    initials = models.CharField(max_length=15, verbose_name=_("Initials"))
    first_name = models.CharField(max_length=50, verbose_name=_("First name"))
    surname_prefix = models.CharField(
        max_length=50, null=True, blank=True,
        verbose_name=_("Surname prefix"))
    last_name = models.CharField(max_length=50, verbose_name=_("Last name"))
    email = models.EmailField(verbose_name=_("Email"))
    active = models.BooleanField(default=True, verbose_name=_("Active"))
    retired = models.BooleanField(default=False, verbose_name=_("Retired"))
    last_login = models.DateTimeField(
        null=True, blank=True, verbose_name=_("Time of last login"))

    def __str__(self):
        return "{} {} {}".format(self.titles, self.initials, self.last_name)


class Module(models.Model):
    name = models.CharField(max_length=80, verbose_name=_("Name of module"))
    course_code = models.IntegerField(
        unique=True,
        verbose_name=_("Course code of module, references Osiris"))
    coordinator = models.ForeignKey(
        Teacher, on_delete=SET_NULL, null=True,
        verbose_name=_(
            "Coordinator reference for a module, references the Teacher"))
    module_moment = models.CharField(
        max_length=5,
        choices=[(moment.name, moment.value) for moment in ModuleMoment],
        verbose_name=_("Module quartile"))

    def __str__(self):
        return "{}: {}".format(self.course_code, self.name)


class Course(models.Model):
    class Meta:
        unique_together = (('course_code', 'year'),)

    module = models.ForeignKey(
        Module, on_delete=SET_NULL, null=True, blank=True,
        verbose_name=_("Links course to possible module (maths) if needed"))
    course_code = models.IntegerField(
        verbose_name=_("Course code of module, references Osiris"), unique=True)
    teachers = models.ManyToManyField(
        Teacher, verbose_name=_("List of teachers that teach this course"))
    name = models.CharField(max_length=50, verbose_name=_("Name of Course"))
    year = models.IntegerField(
        verbose_name=_("The year this course takes place in"))
    materials = models.ManyToManyField(
        'MaterialSelectionProcess',
        verbose_name=_("The list of materials relevant for this course"), blank=True, null=True)
    updated_teacher = models.BooleanField(
        default=False,
        verbose_name=_(
            "Has the course been marked updated by the teacher for this year?"))
    updated_IAPC = models.BooleanField(
        default=False,
        verbose_name=_("Have we already checked this course this year?"))

    def __str__(self):
        return "{}, {}".format(self.name, self.year)


class Study(models.Model):
    class Meta:
        verbose_name_plural = "studies"

    name = models.CharField(
        max_length=100,
        verbose_name=_("Name of the study, e.g. Creative Technology"))
    study_type = models.CharField(
        max_length=5,
        choices=[(study_type.name, study_type.value) for study_type in StudyType],
        verbose_name=_("Type of study"))

    courses = models.ManyToManyField(
        Course, through='StudyCourse', through_fields=('study', 'course'),
        verbose_name=_("List of courses"))

    def __str__(self):
        return "{}".format(self.name)


class StudyCourse(models.Model):
    class Meta:
        unique_together = (('course', 'study'),)

    course = models.ForeignKey(
        Course, on_delete=models.CASCADE,
        verbose_name=_("Course"))
    study = models.ForeignKey(
        Study, on_delete=models.CASCADE,
        verbose_name=_("Study"))
    period = models.CharField(
        max_length=10, choices=[(period.name, period.value) for period in Period],
        verbose_name=_("Period this relationship is relevant in"))

    def __str__(self):
        return "{} -> {}".format(self.course, self.study)


class StudyMaterial(models.Model):
    name = models.CharField(
        null=False, blank=False, max_length=255,
        verbose_name=_('Category name of this article'))

    def __str__(self):
        return self.name


class StudyMaterialEdition(PolymorphicModel):
    # Could be derived from either OID or ISBN
    name = models.CharField(
        null=False, blank=False, max_length=255,
        verbose_name=_("Name of the material"))

    # The type if material, e.g. the list of different revisions of the book
    material_type = models.ForeignKey(
        StudyMaterial,
        on_delete=models.DO_NOTHING, null=True, blank=True,
        verbose_name=_("Material collection"))

    def __str__(self):
        return self.name


class OtherMaterial(StudyMaterialEdition):
    """"
    Use if material is any material other than a scientific article or a book
    """
    pass

    def __str__(self):
        return self.name


class Book(StudyMaterialEdition):
    ISBN = models.CharField(null=False, unique=True,
                            verbose_name=_("ISBN 10 or ISBN 13"),
                            max_length=13)
    # Authors should be derived from the ISBN
    author = models.CharField(null=False, blank=False, verbose_name=_(
        "Author names, comma separated"), max_length=1000)
    # Cover image of the book, should be derived from ISBN
    img = models.URLField(verbose_name=_("Link to cover image of book"), blank=True, null=True)

    # Year of publishing, should be derived from ISBN
    year_of_publishing = models.IntegerField(
        max_length=4,
        verbose_name="Year this revision of the book was published.")

    # noinspection PyPep8Naming,PyMethodMayBeStatic
    def validate_ISBN(self, ISBN):
        if len(ISBN) == 10 or len(ISBN) == 13:
            return
        else:
            raise ValueError("ISBN does not match either known lengths")

    def __str__(self):
        return "{}: {}".format(self.ISBN, self.name)


class ScientificArticle(StudyMaterialEdition):
    DOI = models.CharField(null=False, blank=True, verbose_name=_(
        "Digital Object Identifier"),
                           max_length=255)

    # List of authors, comma separated, should be derived from DOI
    author = models.CharField(null=False, blank=False, verbose_name=_(
        "Author names, comma separated"), max_length=1000)

    # Year of publishing, should be derived from OID
    year_of_publishing = models.IntegerField(
        max_length=4,
        verbose_name="Year this revision of the book was published.")

    def __str__(self):
        return "{}: {}".format(self.DOI, self.name)


class MaterialSelectionProcess(models.Model):
    osiris_specified_material = models.ForeignKey(
        StudyMaterialEdition, null=True, on_delete=SET_NULL,
        related_name='process_in_osiris')
    available_materials = models.ManyToManyField(
        StudyMaterialEdition, related_name='process_is_available')
    approved_material = models.ForeignKey(
        StudyMaterialEdition, null=True, on_delete=SET_NULL,
        related_name='process_is_approved')
    reason = models.CharField(
        max_length=255, null=True,
        verbose_name=_(
            "Reason why there is a difference between Osiris and availability"))

    def __str__(self):
        return "{}: {}".format(self.current_active_book.name, self.stage)

    @property
    def current_active_book(self) -> StudyMaterialEdition:
        if self.approved_material:
            return self.approved_material
        else:
            return self.osiris_specified_material

    @property
    def stage(self):
        if not self.available_materials \
                or self.available_materials.count() == 0 \
                and not self.approved_material:
            return _("Awaiting upstream check")
        elif self.approved_material:
            return _("Approved")
        elif self.available_materials and self.available_materials.count() != 0:
            return _("Awaiting approval")
        else:
            return _("Unspecified")
