from typing import List

from django.db import models
from django.utils.translation import ugettext_lazy as _
from enum import Enum

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
    Q1_HALF = "Quartile 1, half year course"
    Q3_HALF = "Quartile 3, half year course"
    FULL_YEAR = "Full year course"


class Study(models.Model):
    type = models.CharField(
        max_length=max([len(t.value) for t in StudyType]),
        choices=[(t.name, t.value) for t in StudyType],
        verbose_name=_("Type of this study"),
    )
    slug = models.SlugField(
        verbose_name=_("Abbreviation of the study association"),
    )

    class Meta:
        verbose_name = _("Study")
        verbose_name_plural = _("Studies")


class CourseStudy(models.Model):
    study = models.ForeignKey(Study, on_delete=models.CASCADE)
    course = models.ForeignKey('Course', on_delete=models.CASCADE)
    study_year = models.IntegerField()

    class Meta:
        verbose_name = _("Course-Study relation")
        verbose_name_plural = _("Course-Study relations")


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

    def __str__(self):
        return '{} ({}, {})'.format(self.name, self.calendar_year, self.period)
