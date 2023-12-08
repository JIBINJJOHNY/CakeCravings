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
            'phone_number',
            'country',
            'postcode',
            'town_or_city',
            'street_address1',
            'street_address2',
            'county',
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last name'}),
            'birthday': forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'Birthday', 'type': 'date'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone number'}),
            'country': CountrySelectWidget(attrs={'class': 'form-control'}),
            'postcode': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Postal code'}),
            'own_or_city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Town or city'}),
            'street_address1': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Street address 1'}),
            'street_address2': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Street address 2'}),
            'dcounty': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'County'}),
        }
