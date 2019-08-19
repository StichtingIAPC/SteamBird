"""
This package contains all the setup and definitions used to define anything related to Studies and
Courses within SteamBird.
"""
from enum import Enum, IntEnum
from typing import List, Optional

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.translation import ugettext_lazy as _

from steambird.models.user import Teacher, StudyAssociation


class StudyType(Enum):
    """
    Simple Enum containing the StudyType options: Bachelor, Master, Premaster
    """
    bachelor = 'BACHELOR'
    master = 'MASTER'
    premaster = 'PREMASTER'


class Period(Enum):
    """
    An enum containing all period options so that it only needs to be defined only once
    """
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
        """
        Method which returns the pre-defined sorting order. Makes Periods comparable and is used by
        the Period.__gt__ and Period.__lt__ operators

        :return:
        """
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

    def __gt__(self, other: 'Period') -> bool:
        """
        Greater than operator definition for Period comparison

        :param other: The other Period to compare with
        :return: A bool which is true if self is bigger than the other Period object
        """
        return self.sorting_index() > other.sorting_index()

    def __lt__(self, other: 'Period') -> bool:
        """
        Less than operator definition for Period comparison

        :param other: The other Period to compare with
        :return: A bool which is true if self is smaller (less) than the other Period object
        """
        return self.sorting_index() < other.sorting_index()

    def is_quartile(self) -> bool:
        """
        Simple method which returns true if a Period is a quartile

        :return: bool
        """
        return self in [Period.Q1, Period.Q2, Period.Q3, Period.Q4, Period.Q5]

    def parent(self) -> Optional['Period']:
        """
        Method which returns the parents of a Period

        :return: Usually a Period, or None
        """

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
        """
        Method which returns the children of a Period

        :return: List of Periods, List can be empty
        """

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

    def all_children(self) -> List['Period']:
        """
        Method which returns all children of a Period. Recursively adds until there is no further
        child object to be found

        :return: List of Periods that are children of requested period
        """
        result = []
        for child in self.children():
            result += child.all_children()
            result.append(child)

        return sorted(result)

    def all_parents(self) -> List['Period']:
        """
        Method which returns all parents of a Period. Recursively adds until there is no further
         child object to be found

        :return: List of Periods that are parents of requested period
        """
        result = []
        parent = self.parent()
        if parent:
            result.append(parent)
            result += parent.all_parents()
        return result


class StudyYear(IntEnum):
    """
    Integer Enum which contains possible Years of a study. This represents the year of nominal study
    in which a student would do a course. It's usage is to figure out when a course is followed in
    e.g. course-study. Combined with Period you can create an overview such that you have a Yx-Qy or
    Period 12 for Y3-Q4
    """

    Y1 = 1
    Y2 = 2
    Y3 = 3
    Y4 = 4

    def __str__(self) -> str:
        """
        Returns string representation as Year {year-value}

        :return: String representation
        """
        return _("Year {}").format(self.value)


class Study(models.Model):
    """
    All data related to a Study is stored in this model.

    Example Row:
        type= BACHELOR, name="Creative Technology", slug="CreaTe"

    String Representation:
        <Study name> (<Study Type>)
    """

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
    """
    CourseStudy defines the linking between a study and a course. Instead of a M2M interface, we use
    a self-defined M2M model as the same course might be given to different studies in different
    study-years.

    Example Row:
        study = Study object id, course = Course object id, study_year = :any:`StudyYear` option

    String Representation:
        <Study Name> (Year: <Study Year>) <-> <Course name> (<Course code>)
    """
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
    """
    Model in which course-objects are stored. This model mirrors most of Osiris, where some entries
    are taken to a different model for less data redundancy. Stores related teachers outside the
    Coordinator by a M2M relation. Study Materials (MSP's) also uses an M2M relation to be stored.

    Example Row:
        name = 'Human Factors and Engineering', period = :any:`Period` option, \
        calendar_year = 2018, coordinator = Teacher object id, course-code = 115545882, \
        updated_association = True, updated_teacher = False

    String Representation:
        <Course Name> (<Calendar Year>, <Period>)
    """
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
        """
        Method which returns both the coordinator and teachers of a study in a list. Filled in with
        the information according to osiris

        :return: List of all teachers helping out with a course.
        """
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
        """
        Method which returns the study directors (OLD/OLC)

        :return: List of directors, should generally not be empty
        """
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
        """
        Method which returns all the associations related to a course. Basically retrieve who can
        edit the course from the backend

        :return: List of StudyAssociations
        """
        return [
            *[
                association
                for course in self.parent_courses
                for association in course.associations
            ],
            *map(lambda study: study.association, self.studies.all())
        ]

    def teacher_can_edit(self, teacher: Teacher) -> bool:
        """
        Can a teacher suggest changes to a course, e.g. on MSP's? Returns true if teacher is either
        coordinator of course or study directors

        :param teacher: Teacher object of which we want to know if they can make suggestions
        :return: Boolean
        """
        return teacher in (self.coordinators + self.directors)

    def association_can_edit(self, association: StudyAssociation) -> bool:
        """
        Returns if an association can edit a specific course.

        :param association: A studyassociation object
        :return: Boolean
        """
        return association in self.associations

    def teacher_can_manage_msp(self, teacher: Teacher) -> bool:
        """
        Can a teacher in some way or form manage a course? Returns true for coordinators, directors
        and teachers.

        :param teacher: Teachers object for which you want to check if they can manage
        :return: boolean
        """
        return teacher in (self.coordinators + self.directors + self.teachers)

    def association_can_manage_msp(self, association: StudyAssociation) -> bool:
        """


        :param association: Study association you want to check this for
        :return:
        """
        return association in self.associations

    def falls_in(self, period: Period) -> bool:
        """
        Which periods does a period fall in? Returns true if self falls in given period

        :param period: Period you want to check against
        :return: Boolean
        """
        return period.name in self.period_all

    def __str__(self):
        return '{} ({}, {})'.format(self.name, self.calendar_year, self.period)
