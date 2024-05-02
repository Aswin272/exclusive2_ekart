from django.forms import ModelForm
from django import forms 
from customers.models import Address

class AddAddressForm(ModelForm):
    class Meta:
        model=Address
        fields=['street','city','district','state','pincode']
        
class EditAddressForm(ModelForm):
    class Meta:
        model=Address
        fields=['street','city','district','state','pincode']
        
