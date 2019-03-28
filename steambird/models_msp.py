from typing import List

from django.db import models
from django.utils.translation import ugettext_lazy as _
from enum import Enum

from steambird.models_user import Teacher, StudyAssociation


class MSPLineType(Enum):
    request_material = 'REQUEST_MATERIAL'
    set_available_materials = 'SET_AVAILABLE_MATERIALS'
    approve_material = 'APPROVE_MATERIAL'


class MSPLine(models.Model):
    type = models.CharField(
        max_length=max([len(t.value) for t in MSPLineType]),
        choices=[(t.name, t.value) for t in MSPLineType],
        verbose_name=_("Mutation type"),
    )
    msp = models.ForeignKey(
        'MSP',
        on_delete=models.CASCADE,
        verbose_name=_("Parent of this line"),
    )
    comment = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("Comment"),
    )
    time = models.DateTimeField(auto_now_add=True)
    materials = models.ManyToManyField(
        'StudyMaterialEdition',
        blank=True,
        verbose_name=_("Related study material(s)")
    )

    class Meta:
        ordering = ['time']


class MSP(models.Model):
    teachers = models.ManyToManyField(
        Teacher,
        blank=True,
        verbose_name=_("Teachers assigned to manage this book process"),
    )

    @property
    def all_teachers(self) -> List[Teacher]:
        return self.teachers + [
            teacher
            for course in self.course_set
            for teacher in course.all_teachers
        ]

    @property
    def associations(self) -> List[StudyAssociation]:
        return [
            association
            for course in self.course_set
            for association in course.associations
        ]

    def teacher_can_edit(self, teacher: Teacher) -> bool:
        return teacher in self.teachers

    def association_can_edit(self, association: StudyAssociation) -> bool:
        return association in self.associations
