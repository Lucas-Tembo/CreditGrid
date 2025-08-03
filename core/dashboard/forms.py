from django import forms
from .models import borrower
from .models import user_details

class borrowerForm(forms.ModelForm):
    class Meta:
        model = borrower
        fields = ['name','amount','interest','date']

class user_details_form(forms.ModelForm):
    class Meta:
        model = user_details
        fields = ['first_name','last_name','company','email','phone_number']