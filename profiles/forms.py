from django import forms
from django_countries.widgets import CountrySelectWidget
from .models import Profile

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'first_name',
            'last_name',
            'birthday',
            'avatar',
            'subscription',
            'default_phone_number',
            'default_country',
            'default_postcode',
            'default_town_or_city',
            'default_street_address1',
            'default_street_address2',
            'default_county',
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last name'}),
            'birthday': forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'Birthday', 'type': 'date'}),
            'subscription': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'default_phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone number'}),
            'default_country': CountrySelectWidget(attrs={'class': 'form-control'}),
            'default_postcode': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Postal code'}),
            'default_town_or_city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Town or city'}),
            'default_street_address1': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Street address 1'}),
            'default_street_address2': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Street address 2'}),
            'default_county': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'County'}),
        }
