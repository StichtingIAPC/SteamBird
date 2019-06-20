from enum import Enum
from typing import List

from django.db import models
from django.utils.translation import ugettext_lazy as _

from steambird.models_user import Teacher, StudyAssociation


class StudyType(Enum):
    bachelor = 'BACHELOR'
    master = 'MASTER'
    premaster = 'PREMASTER'


class Period(Enum):
    Q1 = "Quartile 1"
    Q2 = "Quartile 2"
    Q3 = "Quartile 3"
    Q4 = "Quartile 4"
    Q5 = "Quartile 5 (sad summer students)"
    S1 = "Semester 1, half year course"
    S2 = "Semester 2, half year course"
    S3 = "Semester 3, half year course"
    FULL_YEAR = "Full year course"


class Study(models.Model):
    type = models.CharField(
        max_length=max([len(t.value) for t in StudyType]),
        choices=[(t.name, t.value) for t in StudyType],
        verbose_name=_("Type of this study"),
    )
    name = models.CharField(
        max_length=255,
        verbose_name=_('Name of study')
    )
    slug = models.SlugField(
        verbose_name=_("Abbreviation of the study"),
    )

    def __str__(self):
        return '{} ({})'.format(self.name, self.type.capitalize())

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = _("Study")
        verbose_name_plural = _("Studies")


class CourseStudy(models.Model):
    study = models.ForeignKey(Study, on_delete=models.CASCADE)
    course = models.ForeignKey('Course', on_delete=models.CASCADE)
    study_year = models.IntegerField(
        verbose_name=_('N-th year'),
        help_text=_('In which year the course is given for this study'))

    class Meta:
        verbose_name = _("Course-Study relation")
        verbose_name_plural = _("Course-Study relations")

    def __str__(self):
        return '{} (Year {}) <-> {} ({})'.format(
            self.study.name,
            self.study_year,
            self.course.name,
            self.course.course_code
        )

class Course(models.Model):
    studies = models.ManyToManyField(
        Study,
        through=CourseStudy,
        blank=True,
        verbose_name=_("Studies this course belong to"),
    )
    name = models.CharField(
        max_length=64,
        verbose_name=_("Name of this course"),
    )
    materials = models.ManyToManyField(
        'MSP',
        blank=True,
        verbose_name=_("Materials that are required by this study"),
    )
    sub_courses = models.ManyToManyField(
        'Course',
        related_name='parent_courses',
        blank=True,
        verbose_name=_("Sub-courses for this course."),
    )
    coordinator = models.ForeignKey(
        'Teacher',
        on_delete=models.PROTECT,
        related_name='coordinated_courses',
        null=True,
        blank=True,
        verbose_name=_("Coordinator of this course"),
    )
    teachers = models.ManyToManyField(
        'Teacher',
        related_name='teaches_courses',
        blank=True,
        verbose_name=_("Teachers of this course"),
    )
    period = models.CharField(
        max_length=max([len(t.value) for t in Period]),
        choices=[(t.name, t.value) for t in Period],
        verbose_name=_("The period in the year for this course"),
    )
    calendar_year = models.IntegerField(
        verbose_name=_("The year in which this course takes place"),
    )
    course_code = models.CharField(
        max_length=64,
        verbose_name=_('Course Code'),
    )
    updated_associations = models.BooleanField(
        default=False,
        verbose_name=_('Updated by association?')
    )
    updated_teacher = models.BooleanField(
        default=False,
        verbose_name=_('Updated by teacher?')
    )

    @property
    def all_teachers(self) -> List[Teacher]:
        return [
            self.coordinator,
            *self.teachers,
            *[
                teacher
                for course in self.parent_courses
                for teacher in course.all_teachers
            ],
            *[
                study.director
                for study in self.studies.all()
            ]
        ]

    @property
    def coordinators(self) -> List[Teacher]:
        """
        These coordinators are also to be autonotified in case of delayed MSP's.

        :return: A list of teachers that have the end-control over this course.
        """
        return [
            self.coordinator,
            *[
                teacher
                for course in self.parent_courses
                for teacher in course.coordinators
            ]
        ]

    @property
    def directors(self) -> List[Teacher]:
        return [
            *[
                director
                for course in self.parent_courses
                for director in course.directors
            ],
            *map(lambda study: study.director, self.studies.all())
        ]

    @property
    def associations(self) -> List[StudyAssociation]:
        return [
            *[
                association
                for course in self.parent_courses
                for association in course.associations
            ],
            *map(lambda study: study.association, self.studies.all())
        ]

    def teacher_can_edit(self, teacher: Teacher) -> bool:
        return teacher in (self.coordinators + self.directors)

    def association_can_edit(self, association: StudyAssociation) -> bool:
        return association in self.associations

    def teacher_can_manage_msp(self, teacher: Teacher) -> bool:
        return teacher in (self.coordinators + self.directors + self.teachers)

    def association_can_manage_msp(self, association: StudyAssociation) -> bool:
        return association in self.associations

    def falls_in(self, period: Period):
        if self.period == Period.FULL_YEAR:
            return True

        if period == self.period:
            return True

        if period == Period.Q1 or period == Period.Q2:
            return self.period == Period.S1

        if period == Period.Q3 or period == Period.Q4:
            return self.period == Period.S2

        if period == Period.Q5:
            return self.period == Period.S3


    def __str__(self):
        return '{} ({}, {})'.format(self.name, self.calendar_year, self.period)
