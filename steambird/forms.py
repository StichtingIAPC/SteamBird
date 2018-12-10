from django import forms
from django.utils.translation import ugettext_lazy as _

class ISBNForm(forms.Form):
    isbn = forms.CharField(label=_('ISBN number'), max_length=13)
    