from django import forms
from .models import Product,ProductImage,Tag,Discount
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__' 

class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['image', 'alt_text', 'default_image', 'is_active']

class AddTagForm(forms.Form):
    tag_name = forms.CharField(label='Tag Name', max_length=100)
    is_active = forms.BooleanField(label='Is Active', required=False)

    def __init__(self, *args, **kwargs):
        super(AddTagForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Add Tag'))

class AddDiscountForm(forms.ModelForm):
    class Meta:
        model = Discount
        fields = ['percentage', 'start_date', 'end_date', 'is_active']

    def __init__(self, *args, **kwargs):
        super(AddDiscountForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Add Discount'))

        # Add DateInput widget for start_date
        self.fields['start_date'].widget = forms.DateInput(attrs={'type': 'date'})

        # Add DateInput widget for end_date
        self.fields['end_date'].widget = forms.DateInput(attrs={'type': 'date'})