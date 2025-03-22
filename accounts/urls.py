# accounts/urls.py
from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

# Namespace for the accounts app
app_name = 'accounts'

urlpatterns = [
    # ========================
    # Authentication URLs
    # ========================
    path('login/', views.user_login, name='user_login'),  # User login
    path('register/', views.user_register, name='user_register'),  # User registration
    path('verify-otp/', views.verify_otp, name='verify_otp'),  # OTP verification
    path('resend-otp/', views.resend_otp, name='resend_otp'),  # Resend OTP
    path('logout/', views.user_logout, name='user_logout'),  # User logout

    # ========================
    # Password Reset URLs
    # ========================
    path(
        'password_reset/',
        auth_views.PasswordResetView.as_view(template_name='accounts/password_reset.html'),
        name='password_reset'
    ),
    path(
        'password_reset/done/',
        auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'),
        name='password_reset_done'
    ),
    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html'),
        name='password_reset_confirm'
    ),
    path(
        'reset/done/',
        auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'),
        name='password_reset_complete'
    ),

    # ========================
    # Home and Profile URLs
    # ========================
    path('', views.home, name='home'),  # Home page
    path('profile/', views.view_profile, name='view_profile'),  # View profile
    path('profile/edit/', views.edit_profile, name='edit_profile'),  # Edit profile

    # ========================
    # Address Management URLs
    # ========================
    path('profile/addresses/', views.manage_addresses, name='manage_addresses'),  # Manage addresses
    path('profile/addresses/add/', views.add_address, name='add_address'),  # Add address
    path('profile/addresses/edit/<int:address_id>/', views.edit_address, name='edit_address'),  # Edit address
    path('profile/addresses/delete/<int:address_id>/', views.delete_address, name='delete_address'),  # Delete address
    path('set-default-address/<int:address_id>/', views.set_default_address, name='set_default_address'),  # Set default address
]
