
from django import forms
from django.forms import ModelForm, Textarea

from dal import autocomplete

from models import *

class CompareMathletesForm(forms.Form):
    first = forms.ModelChoiceField(
        queryset=Mathlete.objects.all(),
        widget=autocomplete.ModelSelect2(url='mathlete-autocomplete',
            attrs={'data-placeholder': "First mathlete's name...",
            'data-minimum-input-length': 3,
            'style': 'width: 50%'})
    )

    second = forms.ModelChoiceField(
        queryset=Mathlete.objects.all(),
        widget=autocomplete.ModelSelect2(url='mathlete-autocomplete',
            attrs={'data-placeholder': "Second mathlete's name...",
                'data-minimum-input-length': 3,
                'style': 'width: 50%'})
    )

class UserRequestForm(ModelForm):
    class Meta:
        model = UserRequest
        fields = ['text']
        widgets = {
            'text' : Textarea(attrs={'class': 'materialize-textarea'})
        }

        labels = {
            'text': 'Suggestion text.'
        }
