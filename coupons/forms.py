# forms.py
from django import forms
from .models import Coupon

class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = [
            'code', 'discount_type', 'discount_value', 'min_order_amount', 
            'max_discount', 'expiration_date', 'usage_limit', 'category', 'active'
        ]
        widgets = {
            'expiration_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        discount_type = cleaned_data.get('discount_type')
        discount_value = cleaned_data.get('discount_value')
        max_discount = cleaned_data.get('max_discount')

        # Ensure discount value is positive
        if discount_value is not None and discount_value <= 0:
            self.add_error('discount_value', "Discount value must be greater than zero.")

        # Ensure max discount is set for percentage-based discounts
        if discount_type == 'percentage' and (max_discount is None or max_discount <= 0):
            self.add_error('max_discount', "Max discount must be set for percentage discounts.")

        return cleaned_data
