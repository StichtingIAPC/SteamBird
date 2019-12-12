"""
This module contains the Django Form classes which are used in the Boecie views.
"""

from enum import Enum, auto

from django import forms
from django.forms import HiddenInput, MultipleHiddenInput
from django.urls import reverse_lazy
# noinspection PyUnresolvedReferences
# pylint: disable=no-name-in-module
from django_addanother.widgets import AddAnotherWidgetWrapper
from django_select2.forms import ModelSelect2MultipleWidget, ModelSelect2Widget

from steambird.models import Course, Teacher, CourseStudy, Study, Config, \
    StudyMaterialEdition, MSPLine, MSP, StudyYear


def get_course_form(course_id=None):
    class CourseForm(forms.ModelForm):
        """
        ModelForm for either showing/editing or inputting information related to
        a course. Makes use of the Materials model and Teachers model.
        """

        teachers = Course.teachers
        materials = Course.materials
        if course_id is None:
            study_year = forms.ChoiceField(choices=((i.value, i.name) for i in StudyYear))

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
                'period',
                *(['study_year'] if course_id is None else []),
            ]

            widgets = {
                'id': HiddenInput(),

                "materials": AddAnotherWidgetWrapper(ModelSelect2MultipleWidget(
                    queryset=MSP.objects.all(),
                    search_fields=[
                        "mspline__materials__name__icontains",
                        "mspline__materials__book__ISBN__icontains",
                        "mspline__materials__book__author__icontains",
                        "mspline__materials__book__year_of_publishing__icontains",
                        "mspline__materials__scientificarticle__DOI__icontains",
                        "mspline__materials__scientificarticle__author__icontains",
                        "mspline__materials__scientificarticle__year_of_publishing__icontains",
                    ]
                ), reverse_lazy('boecie:msp.create',
                                kwargs={'course': course_id})) if course_id
                             else MultipleHiddenInput(),

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
                ), reverse_lazy('boecie:teacher.create')),


            }
    return CourseForm


class TeacherForm(forms.ModelForm):
    """
    Modelform for viewing or editing data related to Teacher users.
    """

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
    """
    Function which returns a modelform for usage in a page. The function is used to create a form to
    link information between studies anc courses.

    E.g.
        form_class = StudyCourseForm(True)

        Will return a form with Course field and Study-year visible, study-field is hidden input.

    While:
        form_class = StudyCourseForm(False)

        Will return  a form with Study field and Study-year visible, Course-field is hidden input.

    :param has_course_field: bool
    :return: ModelForm with either Study or Course field
    """

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
    """
    An enum used to define the options for which selections to export. Used as the export options
    are association-linked and can contain Pre-Masters and Masters, which are less 'year' focused
    than Bachelors tend to be.
    """

    YEAR_1 = auto()
    YEAR_2 = auto()
    YEAR_3 = auto()
    MASTER = auto()
    PREMASTER = auto()


class LmlExportForm(forms.Form):
    """
    Form to offer users to download a CSV file containing books for the period
    based on the options selected. Options are presented by LmlExportOptions, combined with Quartile
    """

    # TODO: make sure this will only give the downloads for books within your
    #  association (e.g. we shouldn't get EE)
    option = forms.ChoiceField(choices=((i.value, i.name) for i in LmlExportOptions))
    period = forms.ChoiceField(
        choices=(('Q{}'.format(i), 'Quartile {}'.format(i)) for i in range(1, 5))
    )


class ConfigForm(forms.ModelForm):
    """
    Modelform to offer users the possibility to change the defined periods of the year. Currently
    affects all users due to how the model is set up.
    """

    class Meta:
        model = Config
        fields = [
            'year',
            'period',
        ]


class MSPCreateForm(forms.ModelForm):
    class Meta:
        model = MSPLine
        fields = [
            'comment', 'materials'
        ]
        widgets = {
            'comment': forms.Textarea(),
            'materials': AddAnotherWidgetWrapper(ModelSelect2MultipleWidget(
                queryset=StudyMaterialEdition.objects.all(),
                search_fields=[
                    "name__icontains",
                    "book__ISBN__icontains",
                    "book__author__icontains",
                    "book__year_of_publishing__icontains",
                    "scientificarticle__DOI__icontains",
                    "scientificarticle__author__icontains",
                    "scientificarticle__year_of_publishing__icontains",
                ]
            ), reverse_lazy('material_management:material.create')),
        }

    def clean(self):
        cleaned_data = super().clean()

        if not cleaned_data.get('materials'):
            self.add_error('materials',
                           'At least one material should be specified.')

        return cleaned_data
