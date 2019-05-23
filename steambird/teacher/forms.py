import isbnlib as i
from django import forms
from django.core.exceptions import ValidationError
from django.forms import HiddenInput, MultipleHiddenInput
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django_addanother.widgets import AddAnotherWidgetWrapper
from django_select2.forms import ModelSelect2MultipleWidget

from steambird.models_materials import StudyMaterialEdition
from steambird.models_msp import MSPLine


class ISBNForm(forms.Form):
    isbn = forms.CharField(label=_('ISBN number'), max_length=18, min_length=10)

    def clean(self):
        data = self.cleaned_data

        isbn = data.get('isbn')
        if i.get_isbnlike(isbn):
            if i.is_isbn10(isbn) or i.is_isbn13(isbn):
                return True
            raise ValidationError('ISBN does not seem to be a ISBN13 or ISBN10')
        raise ValidationError('ISBN does not seem valid')


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
            ), reverse_lazy('teacher:isbn')),
            # TODO: Convert this to a teacher:book.create view when it exists.
        }
