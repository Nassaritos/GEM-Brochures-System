from django import forms
from django.core.exceptions import ValidationError
from .models import Product, Order, Delivery, Issue


class DateInput(forms.DateInput):
    input_type = 'date'


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'reorder_level', 'active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'reorder_level': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['product', 'print_house', 'pr_number', 'po_number', 'order_date', 'ordered_quantity', 'unit_price', 'notes']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-select'}),
            'print_house': forms.TextInput(attrs={'class': 'form-control'}),
            'pr_number': forms.TextInput(attrs={'class': 'form-control'}),
            'po_number': forms.TextInput(attrs={'class': 'form-control'}),
            'order_date': DateInput(attrs={'class': 'form-control'}),
            'ordered_quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': '0.01'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class DeliveryForm(forms.ModelForm):
    class Meta:
        model = Delivery
        fields = ['order', 'delivery_date', 'delivered_quantity', 'notes']
        widgets = {
            'order': forms.Select(attrs={'class': 'form-select'}),
            'delivery_date': DateInput(attrs={'class': 'form-control'}),
            'delivered_quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean(self):
        cleaned = super().clean()
        order = cleaned.get('order')
        delivered_quantity = cleaned.get('delivered_quantity') or 0
        if order and delivered_quantity:
            remaining = order.remaining_to_deliver
            if self.instance.pk:
                remaining += self.instance.delivered_quantity
            if delivered_quantity > remaining:
                raise ValidationError(f'Delivered quantity exceeds remaining quantity for this order. Remaining allowed: {remaining}.')
        return cleaned


class IssueForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = ['product', 'issue_date', 'issued_quantity', 'notes']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-select'}),
            'issue_date': DateInput(attrs={'class': 'form-control'}),
            'issued_quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean(self):
        cleaned = super().clean()
        product = cleaned.get('product')
        issued_quantity = cleaned.get('issued_quantity') or 0
        if product and issued_quantity:
            available = product.current_stock
            if self.instance.pk:
                available += self.instance.issued_quantity
            if issued_quantity > available:
                raise ValidationError(f'Issued quantity exceeds available stock. Available stock: {available}.')
        return cleaned
