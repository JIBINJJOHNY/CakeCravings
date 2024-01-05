# profiles/forms.py
from django import forms
from .models import Profile


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'first_name',
            'last_name',
            'birthday',
            'street_address1',
            'street_address2',
            'town_or_city',
            'state',
            'country',
            'postcode',
            'phone_number',
            'is_primary_address',
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last name'}),
            'birthday': forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'Birthday', 'type': 'date'}),
            'street_address1': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Street address 1'}),
            'street_address2': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Street address 2'}),
            'town_or_city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Town or city'}),
            'state': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'State'}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Country'}),
            'postcode': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Postal code'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone number'}),
            'is_primary_address': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
