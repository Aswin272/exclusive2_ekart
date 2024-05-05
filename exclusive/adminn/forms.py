from django.forms import ModelForm
from django import forms
from products.models import Category,Product,ProductImage
from .models import Coupon

class AddCategoryForm(ModelForm):
    class Meta:
        model=Category
        fields='__all__'

class UpdateCategoryForm(ModelForm):
    class Meta:
        model=Category
        fields='__all__'
        
class ProductForm(ModelForm):
    class Meta:
        model=Product
        fields='__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'Category': forms.Select(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'priority': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        
        
class ProductImageForm(ModelForm):
    class Meta:
        model=ProductImage
        fields=['image']
        
        
class ProductUpdateForm(forms.ModelForm):
    class Meta:
        model=Product
        fields='__all__'
        
        
class AddCouponForm(ModelForm):
    class Meta:
        model=Coupon
        fields=['coupon_code','coupon_name','discount','min_purchase_amount','is_active']
        
        