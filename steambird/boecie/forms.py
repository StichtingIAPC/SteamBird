from django import forms
from django.core.exceptions import ValidationError
from django.forms import widgets
from django_select2.forms import Select2Widget, Select2MultipleWidget, ModelSelect2MultipleWidget

from steambird.models import Course, MSP, Teacher
from django.utils.translation import ugettext_lazy as _


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
        fields = ['course_code', 'name', 'materials', 'teachers', 'updated_associations', 'updated_teacher', 'calendar_year']
        widgets = {
            'materials': Select2MultipleWidget,#     TODO: Make this work on the new MSP selection instead of this old one (therefore, up until then keep it like this)
            'teachers': ModelSelect2MultipleWidget(
                model=Teacher,
                search_fields=['titles__icontains', 'initials__icontains', 'first_name__icontains', 'surname_prefix__icontains', 'last_name__icontains', 'email__icontains']
            )
        }

