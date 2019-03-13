from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
import isbnlib as i

class ISBNForm(forms.Form):
    isbn = forms.CharField(label=_('ISBN number'), max_length=18, min_length=10)

    def clean(self):
        cd = self.cleaned_data

        isbn = cd.get('isbn')
        if i.get_isbnlike(isbn):
            if i.is_isbn10(isbn) or i.is_isbn13(isbn):
                return True
            else:
                raise ValidationError('ISBN does not seem to be a ISBN13 or ISBN10')
        else:
            raise ValidationError('ISBN does not seem valid')
