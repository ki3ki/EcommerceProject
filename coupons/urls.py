from django.urls import path
from .views import apply_coupon

urlpatterns = [
    path('apply/', apply_coupon, name='apply_coupon'),
]
