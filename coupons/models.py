from django.db import models
from accounts.models import User
from store.models import Category
from django.conf import settings 

class Coupon(models.Model):
    DISCOUNT_TYPES = [
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    ]

    code = models.CharField(max_length=20, unique=True)  # Coupon code (e.g., "SAVE10")
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPES)  # % or ₹
    discount_value = models.FloatField()  # Amount or percentage
    min_order_amount = models.FloatField(default=0)  # Minimum order value
    max_discount = models.FloatField(null=True, blank=True)  # Cap for % discounts
    expiration_date = models.DateTimeField(null=True)  # Expiry date
    usage_limit = models.IntegerField(default=1)  # Max times a user can use
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)  # Optional category-based
    active = models.BooleanField(default=True)  # Enable/Disable

    def __str__(self):
        return self.code


class CouponUsage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    used_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} used {self.coupon.code}"
