from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from .models import Address, User


User = get_user_model()

class RegisterForm(forms.ModelForm):
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Confirm Password',
        'id': 'join_confirm_password',
        'required': True
    }))

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

    def clean_full_name(self):
        full_name = self.cleaned_data['full_name']
        if any(char.isdigit() for char in full_name):
            raise ValidationError('Full name cannot contain numbers.')
        return full_name

    def clean_username(self):
        username = self.cleaned_data['username']
        if username.isdigit():
            raise ValidationError('Username cannot be a number.')
        return username

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if not phone.isdigit() or len(phone) != 10:
            raise ValidationError('Enter a valid 10-digit phone number.')
        return phone    

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise ValidationError("Password and Confirm Password do not match")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        max_length=254,
        required=True,
        label="Email",
        widget=forms.EmailInput(attrs={'autofocus': True, 'placeholder': 'Email'})
    )

    password = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'})
    )


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['full_name', 'phone', 'username']

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['address_line1', 'address_line2', 'city', 'state', 'postal_code', 'country']