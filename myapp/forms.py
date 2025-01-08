from django import forms
from .models import Product, Customer, Order

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'available']
