from django import forms
from django.urls import reverse_lazy
from django_addanother.contrib.select2 import Select2MultipleAddAnother
from django_addanother.widgets import AddAnotherWidgetWrapper
from django_select2.forms import ModelSelect2MultipleWidget, ModelSelect2Widget

from steambird.models import Course, Teacher


# class MaterialsSelect2MultipleWidgetForm(forms.Form):
#     materials = forms.ModelMultipleChoiceField(widget=ModelSelect2MultipleWidget(
#         queryset= Course.ma
#         search_fields=['title__icontains'],
#     ), queryset=models.Genre.objects.all(), required=True)

class CourseForm(forms.ModelForm):
    teachers = Course.teachers
    materials = Course.materials

    class Meta:
        model = Course
        fields = ['course_code', 'name', 'materials', 'teachers', 'updated_associations', 'updated_teacher',
                  'calendar_year', 'coordinator']
        widgets = {
            'materials': Select2MultipleAddAnother(reverse_lazy('boecie:teachers.list')),
            # TODO: Make this work on the new MSP selection instead of this old one (therefore, up until then keep it like this)
            'teachers': AddAnotherWidgetWrapper(ModelSelect2MultipleWidget(
                model=Teacher,
                search_fields=['titles__icontains', 'initials__icontains', 'first_name__icontains',
                               'surname_prefix__icontains', 'last_name__icontains', 'email__icontains']
            ), reverse_lazy('boecie:teacher.create')),
            'coordinator': ModelSelect2Widget(
                model=Teacher,
                search_fields=['titles__icontains', 'initials__icontains', 'first_name__icontains',
                               'surname_prefix__icontains', 'last_name__icontains', 'email__icontains']
            )
        }


class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ['titles', 'initials', 'first_name', 'surname_prefix', 'last_name', 'email', 'active', 'retired',
                  'user']
