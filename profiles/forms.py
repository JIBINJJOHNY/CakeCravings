from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User  
from .models import Profile
from django_countries.widgets import CountrySelectWidget


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
            'email_verified', 
            'role',
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last name'}),
            'birthday': forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'Birthday', 'type': 'date'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone number'}),
            'country': CountrySelectWidget(attrs={'class': 'form-control'}),
            'postcode': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Postal code'}),
            'town_or_city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Town or city'}),
            'street_address1': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Street address 1'}),
            'street_address2': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Street address 2'}),
            'county': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'County'}),  # Fix the typo in the field name
            'email_verified': forms.CheckboxInput(attrs={'class': 'form-check-input'}),  # Adjust widget for email_verified
            'role': forms.Select(attrs={'class': 'form-control'}),  # Use a dropdown for the role field
        }

