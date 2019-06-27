from enum import Enum, auto

from django import forms
from django.forms import HiddenInput
from django.urls import reverse_lazy
# noinspection PyUnresolvedReferences
# pylint: disable=no-name-in-module
from django_addanother.contrib.select2 import Select2MultipleAddAnother
from django_addanother.widgets import AddAnotherWidgetWrapper
from django_select2.forms import ModelSelect2MultipleWidget, ModelSelect2Widget

from steambird.models import Course, Teacher, CourseStudy, Study, Period, Config


class CourseForm(forms.ModelForm):
    teachers = Course.teachers
    materials = Course.materials

    class Meta:
        model = Course
        fields = [
            'id',
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
            'id': HiddenInput(),

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

            'coordinator': AddAnotherWidgetWrapper(ModelSelect2Widget(
                model=Teacher,
                search_fields=[
                    'titles__icontains',
                    'initials__icontains',
                    'first_name__icontains',
                    'surname_prefix__icontains',
                    'last_name__icontains',
                    'email__icontains'
                ]
            ), reverse_lazy('boecie:teacher.create'))
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


# pylint: disable=invalid-name
def StudyCourseForm(has_course_field: bool = False):
    class _cls(forms.ModelForm):
        class Meta:
            model = CourseStudy
            fields = [
                'study_year',
                ] + (['course'] if has_course_field else ['study'])

            if has_course_field:
                widgets = {
                    'course': AddAnotherWidgetWrapper(ModelSelect2Widget(
                        model=Course,
                        search_fields=[
                            'name__icontains',
                            'course_code__icontains'
                        ]
                    ), reverse_lazy('boecie:index')),

                    'study': HiddenInput(),
                }
            else:
                widgets = {
                    'study': AddAnotherWidgetWrapper(ModelSelect2Widget(
                        model=Study,
                        search_fields=[
                            'name__icontains',
                            'slug__icontains'
                        ]
                    ), reverse_lazy('boecie:index')),

                    'course': HiddenInput(),
                }

    return _cls


class LmlExportOptions(Enum):
    YEAR_1 = auto()
    YEAR_2 = auto()
    YEAR_3 = auto()
    MASTER = auto()
    PREMASTER = auto()


class LmlExportForm(forms.Form):
    option = forms.ChoiceField(choices=((i.value, i.name) for i in LmlExportOptions))
    period = forms.ChoiceField(choices=(('Q{}'.format(i), 'Quartile {}'.format(i) ) for i in range(1,5)))



class ConfigForm(forms.ModelForm):
    class Meta:
        model = Config
        fields = [
            'year',
            'period'
        ]
