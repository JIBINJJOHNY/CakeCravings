from django import forms
from .models import Order, OrderItem

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            'full_name',
            'email',
            'phone',
            'address1',
            'address2',
            'city',
            'state',
            'country',
            'zip_code',
            'total_paid',
            'billing_status',
            'status',
            'delivery_option', 
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address1': forms.TextInput(attrs={'class': 'form-control'}),
            'address2': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.Select(attrs={'class': 'form-control'}),
            'country': forms.HiddenInput(),  # Hide the 'country' field
            'zip_code': forms.TextInput(attrs={'class': 'form-control'}),
            'total_paid': forms.TextInput(attrs={'class': 'form-control'}),
            'billing_status': forms.CheckboxInput(),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'delivery_option': forms.HiddenInput(),  # Hide the 'delivery_option' field
        }

    def __init__(self, *args, **kwargs):
        super(OrderForm, self).__init__(*args, **kwargs)

        # Set choices for state
        self.fields['state'].choices = Order.GERMAN_STATES_CHOICES

        # Set a default value for 'country' to 'Germany' and hide it
        self.fields['country'].initial = 'Germany'
        self.fields['country'].widget = forms.HiddenInput()

        # Disable the 'country' field for users not in Germany
        if self.instance and self.instance.country != 'Germany':
            self.fields['country'].widget.attrs['readonly'] = True

        # Set a default value for 'delivery_option' to 'online' and hide it
        self.fields['delivery_option'].initial = 'online'
        self.fields['delivery_option'].widget = forms.HiddenInput()

    def clean_country(self):
        # Ensure that only Germany is allowed as the country
        country = self.cleaned_data.get('country')
        if country != 'Germany':
            # Set the country to Germany if it's not already
            self.cleaned_data['country'] = 'Germany'
            # Log or notify about the attempt to change the country
        return self.cleaned_data['country']

    def clean_delivery_option(self):
        # Ensure that only 'online' or 'pickup' are allowed as delivery options
        delivery_option = self.cleaned_data.get('delivery_option')
        valid_options = ['online', 'pickup']
        if delivery_option not in valid_options:
            # Set the delivery option to 'online' if it's not a valid option
            self.cleaned_data['delivery_option'] = 'online'
            # Log or notify about the attempt to change the delivery option
        return self.cleaned_data['delivery_option']

class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = [
            'order',
            'product',
            'quantity',
            'size',
        ]
        widgets = {
            'order': forms.HiddenInput(),
            'product': forms.HiddenInput(),
            'quantity': forms.TextInput(attrs={'class': 'form-control'}),
            'size': forms.Select(attrs={'class': 'form-control'}),
        }