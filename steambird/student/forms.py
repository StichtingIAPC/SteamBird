from django import forms

from steambird.models import Study


class StudyCoursesFilterForm(forms.Form):
    period = forms.ChoiceField(
        choices=(('Q{}'.format(i), 'Quartile {}'.format(i)) for i in range(1, 5)))
    study = forms.ModelChoiceField(queryset=Study.objects.all())
    calendar_year = forms.IntegerField(min_value=2016)
