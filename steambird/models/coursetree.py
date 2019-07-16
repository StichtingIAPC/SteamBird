from enum import Enum, IntEnum
from typing import List, Optional

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.translation import ugettext_lazy as _

from steambird.models.user import Teacher, StudyAssociation


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
    YEAR = "Course that is in both S1 and S2"
    FULL_YEAR = "Full year course"

    def sorting_index(self):
        return {
            Period.Q1: 0x01,
            Period.Q2: 0x02,
            Period.Q3: 0x03,
            Period.Q4: 0x04,
            Period.Q5: 0x05,
            Period.S1: 0x10,
            Period.S2: 0x11,
            Period.S3: 0x12,
            Period.YEAR: 0x20,
            Period.FULL_YEAR: 0x30
        }[self]

    def __gt__(self, other: 'Period'):
        return self.sorting_index() > other.sorting_index()

    def __lt__(self, other: 'Period'):
        return self.sorting_index() < other.sorting_index()

    def is_quartile(self):
        return self in [Period.Q1, Period.Q2, Period.Q3, Period.Q4, Period.Q5]

    def parent(self) -> Optional['Period']:
        if self in [Period.Q1, Period.Q2]:
            return Period.S1
        if self in [Period.Q3, Period.Q4]:
            return Period.S2
        if self == Period.Q5:
            return Period.S3
        if self in [Period.S1, Period.S2]:
            return Period.YEAR
        if self in [Period.S3, Period.YEAR]:
            return Period.FULL_YEAR
        return None

    def children(self) -> List['Period']:
        if self == Period.S1:
            return [Period.Q1, Period.Q2]
        if self == Period.S2:
            return [Period.Q3, Period.Q4]
        if self == Period.S3:
            return [Period.Q5]
        if self == Period.YEAR:
            return [Period.S1, Period.S2]
        if self == Period.FULL_YEAR:
            return [Period.YEAR, Period.S3]
        return []

    def all_children(self):
        result = []
        for child in self.children():
            result += child.all_children()
            result.append(child)

        return sorted(result)

    def all_parents(self) -> List['Period']:
        result = []
        parent = self.parent()
        if parent:
            result.append(parent)
            result += parent.all_parents()
        return result


class StudyYear(IntEnum):
    Y1 = 1
    Y2 = 2
    Y3 = 3
    Y4 = 4

    def __str__(self):
        return _("Year {}").format(self.value)


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
        choices=[(t.value, str(t)) for t in StudyYear],
        verbose_name=_("The year of (nominal) study this course is given"),
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = _("Course-Study relation")
        verbose_name_plural = _("Course-Study relations")
        unique_together = ['study', 'course', 'study_year']

    def __str__(self):
        return '{} (Year {}) <-> {} ({})'.format(
            self.study.name,
            self.study_year,
            self.course.name,
            self.course.course_code
        )


class CourseQuerySet(models.QuerySet):
    def with_all_periods(self):
        """
        This function populates the :py:attr:`Course.period_all` field.

        :return: a QuerySet
        """
        cases = [
            models.When(
                models.Q(period=period.name),
                then=models.Value(
                    list(map(
                        lambda e: e.name,
                        [*period.all_children(), period, *period.all_parents()]
                    )),
                    output_field=ArrayField(models.CharField())
                )
            )
            for period in Period
        ]

        return self.annotate(period_all=models.Case(
            *cases,
            default=models.Value([], ArrayField(models.CharField()))))

    def with_self_and_parents(self):
        """
        This function populates the :py:attr:`Course.period_self_and_parents`
        field.

        :return: a QuerySet
        """
        cases = [
            models.When(
                models.Q(period=period.name),
                then=models.Value(list(map(lambda e: e.name,
                                           [period, *period.all_parents()])),
                                  output_field=ArrayField(models.CharField()))
            )
            for period in Period
        ]

        return self.annotate(period_parents_and_self=models.Case(
            *cases,
            default=models.Value([], ArrayField(models.CharField()))))

    def with_is_quartile(self):
        """
        This function populates the :py:attr:`Course.is_quartile` field.

        :return: a QuerySet
        """
        cases = [
            models.When(
                models.Q(period=period.name),
                then=models.Value(period.is_quartile(),
                                  output_field=models.BooleanField())
            )
            for period in Period
        ]

        return self.annotate(period_is_quartile=models.Case(
            *cases,
            default=models.Value(False, models.BooleanField())))


class Course(models.Model):
    objects = CourseQuerySet.as_manager()

    period_parents_and_self: Optional[List[str]]
    """
    This field will be populated by the
    :func:`CourseQuerySet.with_self_and_parents` function. It contains a list
    of all direct parents and the period itself.
    """

    period_all: Optional[List[str]]
    """
    This field will be populated by the
    :func:`CourseQuerySet.with_all_periods` function. It contains a list
    of all direct parents and all children, and the period itself.
    """

    period_is_quartile: Optional[bool]
    """
    This field will be populated by the
    :func:`CourseQuerySet.with_is_quartile` function. It is true when the
    period of this course is exactly a quartile.
    """

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
        verbose_name=_("Materials that are required by this course"),
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
        return period.name in self.period_all

    def __str__(self):
        return '{} ({}, {})'.format(self.name, self.calendar_year, self.period)
