# forms.py
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
            'county_region_state',
            'country',
            'zip_code',
            'total_paid',
            'billing_status',
            'status',
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address1': forms.TextInput(attrs={'class': 'form-control'}),
            'address2': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'county_region_state': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'zip_code': forms.TextInput(attrs={'class': 'form-control'}),
            'total_paid': forms.TextInput(attrs={'class': 'form-control'}),
            'billing_status': forms.CheckboxInput(),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(OrderForm, self).__init__(*args, **kwargs)
        # Disable the 'country' field for users not in Germany
        if self.instance and self.instance.country != 'Germany':
            self.fields['country'].widget.attrs['readonly'] = True

    def clean_country(self):
        # Ensure that only Germany is allowed as the country
        country = self.cleaned_data.get('country')
        if country != 'Germany':
            raise forms.ValidationError('Delivery is only available for users in Germany.')
        return country


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
