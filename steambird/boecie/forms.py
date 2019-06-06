from django import forms
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
# noinspection PyUnresolvedReferences
# pylint: disable=no-name-in-module
from django_addanother.contrib.select2 import Select2MultipleAddAnother, ModelSelect2AddAnother
from django_addanother.widgets import AddAnotherWidgetWrapper
from django_select2.forms import ModelSelect2MultipleWidget, ModelSelect2Widget

from steambird.models import Course, Teacher, Study, CourseStudy


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


class StudyCourseForm(forms.ModelForm):

    class Meta:
        model = CourseStudy
        fields = [
            'course'
        ]

        widgets = {
            'course': AddAnotherWidgetWrapper(ModelSelect2Widget(
                model=Course,
                search_fields=[
                    'name__icontains',
                    'course_code__icontains'
                ]
            ), reverse_lazy('boecie:course.create'))
        }
