from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from .models import Address, User

# Get the user model dynamically to support custom user models
User = get_user_model()


# ===========================
# Registration Form
# ===========================
class RegisterForm(forms.ModelForm):
    # Confirm password field with custom attributes
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirm Password',
            'id': 'join_confirm_password',
            'required': True
        })
    )

    class Meta:
        model = User
        fields = ['full_name', 'username', 'email', 'phone', 'password']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'placeholder': 'Full Name',
                'id': 'join_full_name',
                'required': True
            }),
            'username': forms.TextInput(attrs={
                'placeholder': 'Username',
                'id': 'join_username',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'Email Address',
                'id': 'join_email_address',
                'required': True
            }),
            'phone': forms.TextInput(attrs={
                'placeholder': '123-456-7890',
                'id': 'phone',
                'required': True
            }),
            'password': forms.PasswordInput(attrs={
                'placeholder': 'Password',
                'id': 'join_password',
                'required': True
            }),
        }

    # Full Name Validation: Ensures no numbers in the name
    def clean_full_name(self):
        full_name = self.cleaned_data['full_name']
        if any(char.isdigit() for char in full_name):
            raise ValidationError('Full name cannot contain numbers.')
        return full_name

    # Username Validation: Prevents numeric-only usernames
    def clean_username(self):
        username = self.cleaned_data['username']
        if username.isdigit():
            raise ValidationError('Username cannot be a number.')
        return username

    # Phone Number Validation: Ensures 10-digit numeric phone number
    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if not phone.isdigit() or len(phone) != 10:
            raise ValidationError('Enter a valid 10-digit phone number.')
        return phone

    # Password and Confirm Password Match Validation
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise ValidationError("Password and Confirm Password do not match")

        return cleaned_data

    # Save method to hash the password before saving
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


# ===========================
# Login Form
# ===========================
class LoginForm(AuthenticationForm):
    # Email field for login instead of username
    username = forms.EmailField(
        max_length=254,
        required=True,
        label="Email",
        widget=forms.EmailInput(attrs={
            'autofocus': True,
            'placeholder': 'Email'
        })
    )

    # Password field with custom attributes
    password = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Password'
        })
    )


# ===========================
# User Profile Form
# ===========================
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['full_name', 'phone', 'username']


# ===========================
# Address Form
# ===========================
class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['address_line1', 'address_line2', 'city', 'state', 'postal_code', 'country']
