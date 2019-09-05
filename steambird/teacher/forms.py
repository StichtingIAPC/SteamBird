"""
This module contains all forms used in the teacher Views
"""

from django import forms

from django.forms import HiddenInput, MultipleHiddenInput
from django.urls import reverse_lazy

from django_addanother.widgets import AddAnotherWidgetWrapper
from django_select2.forms import ModelSelect2MultipleWidget

from steambird.models.materials import StudyMaterialEdition
from steambird.models.msp import MSPLine


class PrefilledMSPLineForm(forms.ModelForm):
    class Meta:
        model = MSPLine
        fields = [
            "type",
            "msp",
            "comment",
            "materials",
        ]
        widgets = {
            "msp": HiddenInput(),
            "comment": HiddenInput(),
            "materials": MultipleHiddenInput(),
            "type": HiddenInput(),
        }


class PrefilledSuggestAnotherMSPLineForm(forms.ModelForm):
    class Meta:
        model = MSPLine
        fields = [
            "type",
            "msp",
            "materials",
            "comment",
        ]
        widgets = {
            "msp": HiddenInput(),
            "type": HiddenInput(),
            "materials": AddAnotherWidgetWrapper(ModelSelect2MultipleWidget(
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
            ), reverse_lazy('msp.new')),
            # TODO: Convert this to a teacher:book.create view when it exists.
        }
