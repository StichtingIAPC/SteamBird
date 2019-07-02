from enum import Enum
from typing import List

from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _, ugettext as _t

from steambird.models.user import Teacher, StudyAssociation


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

    @property
    def bootstrap_type(self):
        if str.upper(self.type) == MSPLineType.request_material.value:
            return "warning"

        if str.upper(self.type) == MSPLineType.set_available_materials.value:
            return "warning"

        return "success"

    @property
    def fa_icon_type(self):
        if str.upper(self.type) == MSPLineType.request_material.value:
            return "question"

        if str.upper(self.type) == MSPLineType.set_available_materials.value:
            return "book"

        return "check-square"

    class Meta:
        ordering = ['time']
        verbose_name = _("Material Selection Process line")
        verbose_name_plural = _("Material Selection Process lines")

    def __str__(self):
        if self.type == MSPLineType.request_material.name:
            return "Material request: {}".format(
                ', '.join(self.materials.values_list('name', flat=True)))

        if self.type == MSPLineType.approve_material.name:
            return "Material approval: {}".format(
                ', '.join(self.materials.values_list('name', flat=True)))

        if self.type == MSPLineType.set_available_materials.name:
            return "Material(s) available: {}".format(
                ', '.join(self.materials.values_list('name', flat=True)))

        return False


class MSP(models.Model):
    teachers = models.ManyToManyField(
        Teacher,
        blank=True,
        verbose_name=_("Teachers assigned to manage this book process"),
    )
    mandatory = models.BooleanField(
        default=True,
        verbose_name=_('Is the material mandatory?')
    )

    def resolved(self):
        return self.mspline_set.last().type == MSPLineType.approve_material.name

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
            for course in self.course_set.all()
            for association in course.associations
        ]

    def teacher_can_edit(self, teacher: Teacher) -> bool:
        return self.teachers.filter(pk=teacher.pk).exists()

    def association_can_edit(self, association: StudyAssociation) -> bool:
        return association in self.associations

    def teacher_str(self):
        last_line = self.mspline_set.filter(
            Q(type=MSPLineType.request_material) |
            Q(type=MSPLineType.approve_material)).last()

        if not last_line:
            last_line = self.mspline_set.last()

        if not last_line:
            return _t("Empty MSP")

        return '{}: {}'.format(
            last_line.type, ', '.join(map(str, last_line.materials.all())))

    def __str__(self):
        last_line: MSPLine = self.mspline_set.last()
        if not last_line:
            return _t("Empty MSP")

        return ', '.join(map(lambda l: l.name, last_line.materials.all()))

    class Meta:
        verbose_name = _("Material Selection Process")
        verbose_name_plural = _("Material Selection Processes")
