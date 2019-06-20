from enum import Enum, auto

from django import forms
from django.urls import reverse_lazy
# noinspection PyUnresolvedReferences
# pylint: disable=no-name-in-module
from django_addanother.contrib.select2 import Select2MultipleAddAnother
from django_addanother.widgets import AddAnotherWidgetWrapper
from django_select2.forms import ModelSelect2MultipleWidget, ModelSelect2Widget

from steambird.models import Course, Teacher, Period


class CourseForm(forms.ModelForm):
    teachers = Course.teachers
    materials = Course.materials

    class Meta:
        model = Course
        fields = [
            'course_code',
            'name',
            'materials',
            'teachers',
            'updated_associations',
            'updated_teacher',
            'calendar_year',
            'coordinator',
            'period'
        ]

        widgets = {
            'materials': Select2MultipleAddAnother(
                reverse_lazy('boecie:teacher.list')),
            # TODO: Make this work on the new MSP selection instead of this old
            #  one (therefore, up until then keep it like this)

            'teachers': AddAnotherWidgetWrapper(ModelSelect2MultipleWidget(
                model=Teacher,
                search_fields=[
                    'titles__icontains',
                    'initials__icontains',
                    'first_name__icontains',
                    'surname_prefix__icontains',
                    'last_name__icontains',
                    'email__icontains'
                ]
            ), reverse_lazy('boecie:teacher.create')),

            'coordinator': ModelSelect2Widget(
                model=Teacher,
                search_fields=[
                    'titles__icontains',
                    'initials__icontains',
                    'first_name__icontains',
                    'surname_prefix__icontains',
                    'last_name__icontains',
                    'email__icontains'
                ]
            )
        }


class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = [
            'titles',
            'initials',
            'first_name',
            'surname_prefix',
            'last_name',
            'email',
            'active',
            'retired',
            'user',
        ]


class LmlExportOptions(Enum):
    YEAR_1 = auto()
    YEAR_2 = auto()
    YEAR_3 = auto()
    MASTER = auto()


class LmlExportForm(forms.Form):
    option = forms.ChoiceField(choices=((i.value, i.name) for i in LmlExportOptions))
    period = forms.ChoiceField(choices=((i, 'Quartile {}'.format(i) ) for i in range(1,5)))

