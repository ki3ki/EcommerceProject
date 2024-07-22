# accounts/urls.py
from django.urls import path
from . import views

app_name = 'accounts'  # Add this line to register the app namespace

urlpatterns = [
    path('login/', views.user_login, name='user_login'),
    path('register/', views.user_register, name='user_register'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('resend-otp/', views.resend_otp, name='resend_otp'),
    path('logout/', views.user_logout, name='user_logout'),
    path('', views.home, name='home'),
]
