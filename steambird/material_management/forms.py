from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
import isbnlib as i

from steambird.models import ScientificArticle, Book, OtherMaterial


class ISBNForm(forms.Form):
    """
    Simple form for searching a book. Should be removed in the future
    """
    isbn = forms.CharField(label=_('ISBN number'), max_length=18, min_length=10)

    def clean(self):
        data = self.cleaned_data

        isbn = data.get('isbn')
        if i.get_isbnlike(isbn):
            if i.is_isbn10(isbn) or i.is_isbn13(isbn):
                return True
            raise ValidationError('ISBN does not seem to be a ISBN13 or ISBN10')
        raise ValidationError('ISBN does not seem valid')


class BookForm(forms.ModelForm):
    """
    Form for inputting book information. Makes use of the Book model.
    """
    class Meta:
        model = Book
        fields = [
            "name",
            "ISBN",
            "author",
            "img",
            "edition",
            "year_of_publishing",
        ]


class ScientificPaperForm(forms.ModelForm):
    """
    Form for inputting DOI information. Makes use of the ScientificArticle model.
    """
    class Meta:
        model = ScientificArticle
        fields = [
            "name",
            "DOI",
            "author",
            "year_of_publishing",
            'url'
        ]


class OtherMaterialForm(forms.ModelForm):
    """
    Form for inputting Other Material information. Makes use of the OtherMaterial model.
    """
    class Meta:
        model = OtherMaterial
        fields = [
            "name",
            "description"
        ]
