# accounts/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from .forms import RegisterForm, LoginForm, UserProfileForm, AddressForm
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from dateutil.parser import parse
from django.core.exceptions import ObjectDoesNotExist
from .models import User, Address
from orders.models import Wallet, Order
import random
from django.contrib.auth.decorators import login_required


# Function to generate a 6-digit OTP
def generate_otp():
    otp = random.randint(100000, 999999)
    print(f"Generated OTP: {otp}")
    return otp


# User login view
def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')  # Redirect to homepage after successful login
            else:
                form.add_error(None, 'Invalid email or password')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


# User registration view with OTP verification
def user_register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.email = form.cleaned_data['email'].lower()
            otp = generate_otp()
            print(f"OTP to be sent: {otp}")

            # Send OTP to user's email
            send_mail(
                "Your OTP Code",
                f"Your OTP code is {otp}",
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
            )

            # Store OTP and user data in session
            request.session['otp'] = str(otp)
            request.session['user_data'] = form.cleaned_data
            request.session['otp_creation_time'] = timezone.now().isoformat()

            return redirect('accounts:verify_otp')  # Redirect to OTP verification page
        else:
            messages.error(request, 'Registration failed. Please correct the errors below.')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


# OTP verification view
def verify_otp(request):
    if request.method == "POST":
        entered_otp = request.POST.get('entered_otp')
        otp = request.session.get('otp')
        otp_creation_time = request.session.get('otp_creation_time')
        user_data = request.session.get('user_data')

        if not otp or not otp_creation_time:
            messages.error(request, 'OTP not found or expired. Please try registering again.')
            return redirect('accounts:user_register')

        # Parse OTP creation time
        otp_creation_time = parse(otp_creation_time)

        # Check if OTP is expired (valid for 120 seconds)
        if (timezone.now() - otp_creation_time).total_seconds() > 120:
            messages.error(request, 'OTP expired. Please try registering again.')
            return redirect('accounts:user_register')

        # If OTP is valid, create user and activate account
        if entered_otp == otp:
            user = User.objects.create_user(
                full_name=user_data['full_name'],
                username=user_data['username'],
                email=user_data['email'],
                password=user_data['password'],
                phone=user_data['phone'],
            )
            user.is_active = True
            user.save()

            # Log in the user after successful registration
            backend = 'django.contrib.auth.backends.ModelBackend'
            user.backend = backend
            login(request, user, backend=backend)

            # Clear session data after successful registration
            request.session.pop('otp', None)
            request.session.pop('otp_creation_time', None)
            request.session.pop('user_data', None)

            return redirect('home')
        else:
            messages.error(request, 'Invalid OTP')

    else:
        otp_creation_time = request.session.get('otp_creation_time')
        otp_expiration_time = parse(otp_creation_time) + timezone.timedelta(seconds=120)
        print(f"OTP Expiration Time: {otp_expiration_time}")
        print(f"Current Time: {timezone.now()}")

    return render(request, 'accounts/otp_verify.html', {
        'otp_expiration_time': otp_expiration_time
    })


# Resend OTP view
def resend_otp(request):
    user_data = request.session.get('user_data')

    if not user_data:
        messages.error(request, 'User data not found. Please try registering again.')
        return redirect('accounts:user_register')

    otp = generate_otp()

    # Send new OTP to user's email
    send_mail(
        "Your OTP Code",
        f"Your new OTP code is {otp}",
        settings.DEFAULT_FROM_EMAIL,
        [user_data['email']],
    )

    # Update OTP in session
    request.session['otp'] = str(otp)
    request.session['otp_creation_time'] = timezone.now().isoformat()

    messages.success(request, 'A new OTP has been sent to your email.')
    return redirect('accounts:verify_otp')


# User logout view
def user_logout(request):
    logout(request)
    return redirect('home')


# Homepage view
def home(request):
    return render(request, 'index.html')


# View user profile (requires login)
@login_required
def view_profile(request):
    user = request.user
    wallet, created = Wallet.objects.get_or_create(user=user)
    default_address = Address.objects.filter(user=user, is_default=True).first()

    return render(request, 'accounts/view_profile.html', {
        'user': user,
        'wallet': wallet,
        'default_address': default_address
    })


# Edit user profile (requires login)
@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('accounts:view_profile')
    else:
        form = UserProfileForm(instance=request.user)

    return render(request, 'accounts/edit_profile.html', {'form': form})


# Manage addresses (requires login)
@login_required
def manage_addresses(request):
    addresses = Address.objects.filter(user=request.user, is_deleted=False)
    return render(request, 'accounts/manage_addresses.html', {'addresses': addresses})


# Add a new address (requires login)
@login_required
def add_address(request):
    
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            messages.success(request, 'Address added successfully.')
            return redirect('accounts:manage_addresses')
    else:
        form = AddressForm()

    return render(request, 'accounts/address_form.html', {'form': form})


# Edit an existing address (requires login)
@login_required
def edit_address(request, address_id):
    if address_id:
        address = get_object_or_404(Address, id=address_id, user=request.user)
    else:
        address = None
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            messages.success(request, 'Address updated successfully.')
            return redirect('accounts:manage_addresses')
    else:
        form = AddressForm(instance=address)

    return render(request, 'accounts/address_form.html', {'form': form})


# Soft delete an address (requires login)
@login_required
def delete_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    address.is_deleted = True
    address.save()
    messages.success(request, 'Address deleted successfully.')
    return redirect('accounts:manage_addresses')


# Set default address (requires login)
@login_required
def set_default_address(request, address_id):

    # Unset previous default address if exists
    Address.objects.filter(user=request.user, is_default=True).update(is_default=False)
    address = get_object_or_404(Address, id=address_id, user=request.user)
    # Set new default address
    address.is_default = True
    address.save()
    messages.success(request, 'Default address updated successfully.')
    return redirect('accounts:manage_addresses')


