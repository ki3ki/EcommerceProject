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
    path('profile/', views.view_profile, name='view_profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/addresses/', views.manage_addresses, name='manage_addresses'),
    path('profile/addresses/add/', views.add_address, name='add_address'),
    path('profile/addresses/edit/<int:address_id>/', views.edit_address, name='edit_address'),
    path('profile/addresses/delete/<int:address_id>/', views.delete_address, name='delete_address'),
    path('set-default-address/<int:address_id>/', views.set_default_address, name='set_default_address'),
    #path('profile/orders/', views.view_orders, name='view_orders'),
    #path('profile/orders/cancel/<int:order_id>/', views.cancel_order, name='cancel_order'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),


]
