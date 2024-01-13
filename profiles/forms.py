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
            'state': forms.Select(attrs={'class': 'form-control'}),  
            'country': CountrySelectWidget(attrs={'class': 'form-control'}),  
            'postcode': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Postal code'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone number'}),
            'is_primary_address': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)

        # Set default values for placeholders
        self.fields['first_name'].widget.attrs['placeholder'] = 'First name'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Last name'
        self.fields['birthday'].widget.attrs['placeholder'] = 'Birthday'
        self.fields['street_address1'].widget.attrs['placeholder'] = 'Street address 1'
        self.fields['street_address2'].widget.attrs['placeholder'] = 'Street address 2'
        self.fields['town_or_city'].widget.attrs['placeholder'] = 'Town or city'
        self.fields['postcode'].widget.attrs['placeholder'] = 'Postal code'
        self.fields['phone_number'].widget.attrs['placeholder'] = 'Phone number'

        # Set choices for the 'state' field
        self.fields['state'].choices = Profile.GERMAN_STATES_CHOICES
        # Remove labels and help texts
        for field_name, field in self.fields.items():
            field.widget.attrs['placeholder'] = field_name.capitalize().replace('_', ' ')
            field.help_text = None