from django.db import models
from django.conf import settings
from store.models import Variant
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver




User = get_user_model()


class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('SHIPPED', 'Shipped'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
         ('RETURNED', 'Returned'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('RAZORPAY', 'Razorpay'),
        ('WALLET', 'Wallet'),
        ('COD', 'Cash on Delivery'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    address = models.ForeignKey('accounts.Address', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='PENDING')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='COD')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='PENDING')
    payment_id = models.CharField(max_length=100, blank=True, null=True)
    

    def can_cancel(self):
        return self.status in ['PENDING', 'PROCESSING']

    
    def __str__(self):
        return f"Order {self.id} - {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.variant.product.name} - {self.variant.color}"
    


class Wallet(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.user.username}'s Wallet"

    def add_funds(self, amount):
        self.balance += amount
        self.save()

    def deduct_funds(self, amount):
        if self.balance >= amount:
            self.balance -= amount
            self.save()
            return True
        return False
    
    @receiver(post_save, sender=User)
    def create_user_wallet(sender, instance, created, **kwargs):
        if created:
           Wallet.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_wallet(sender, instance, **kwargs):
        if hasattr(instance, 'wallet'):
            instance.wallet.save()
