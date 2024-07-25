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
import random
from django.contrib.auth.decorators import login_required
 


def generate_otp():
    otp = random.randint(100000, 999999)
    print(f"Generated OTP: {otp}")
    return otp

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')  # Corrected redirect to 'home'
            else:
                form.add_error(None, 'Invalid email or password')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})

def user_register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.email = form.cleaned_data['email'].lower()
            otp = generate_otp()
            print(f"OTP to be sent: {otp}")
            send_mail(
                "Your OTP Code",
                f"Your OTP code is {otp}",
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
            )
            request.session['otp'] = str(otp)
            request.session['user_data'] = form.cleaned_data
            request.session['otp_creation_time'] = timezone.now().isoformat()
            return redirect('accounts:verify_otp')  # Corrected redirect to 'accounts:verify_otp'
        else:
            messages.error(request, 'Registration failed. Please correct the errors below.')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

def verify_otp(request):
    if request.method == "POST":
        entered_otp = request.POST.get('entered_otp')
        otp = request.session.get('otp')
        otp_creation_time = request.session.get('otp_creation_time')
        user_data = request.session.get('user_data')

        if not otp or not otp_creation_time:
            messages.error(request, 'OTP not found or expired. Please try registering again.')
            return redirect('accounts:user_register')

        otp_creation_time = parse(otp_creation_time)
        if (timezone.now() - otp_creation_time).total_seconds() > 120:
            messages.error(request, 'OTP expired. Please try registering again.')
            return redirect('accounts:user_register')

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

            backend = 'django.contrib.auth.backends.ModelBackend'
            user.backend = backend
            login(request, user, backend=backend)

            request.session.pop('otp', None)
            request.session.pop('otp_creation_time', None)
            request.session.pop('user_data', None)
            return redirect('home')  # Corrected redirect to 'home'
        else:
            messages.error(request, 'Invalid OTP')
    else:
        otp_creation_time = request.session.get('otp_creation_time')
        otp_expiration_time = parse(otp_creation_time) + timezone.timedelta(seconds=120)
        print(f"OTP Expiration Time: {otp_expiration_time}")  # Print OTP expiration time
        print(f"Current Time: {timezone.now()}") 
    return render(request, 'accounts/otp_verify.html', {
        'otp_expiration_time': otp_expiration_time
    })

def resend_otp(request):
    user_data = request.session.get('user_data')

    if not user_data:
        messages.error(request, 'User data not found. Please try registering again.')
        return redirect('accounts:user_register')

    otp = generate_otp()
    send_mail(
        "Your OTP Code",
        f"Your new OTP code is {otp}",
        settings.DEFAULT_FROM_EMAIL,
        [user_data['email']],
    )

    request.session['otp'] = str(otp)
    request.session['otp_creation_time'] = timezone.now().isoformat()

    messages.success(request, 'A new OTP has been sent to your email.')
    return redirect('accounts:verify_otp')  # Corrected redirect to 'accounts:verify_otp'

def user_logout(request):
    logout(request)
    return redirect('home')

def home(request):
    return render(request, 'index.html')

@login_required
def view_profile(request):
    return render(request, 'accounts/view_profile.html', {'user': request.user})

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

@login_required
def manage_addresses(request):
    addresses = Address.objects.filter(user=request.user)
    return render(request, 'accounts/manage_addresses.html', {'addresses': addresses})

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

@login_required
def edit_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            messages.success(request, 'Address updated successfully.')
            return redirect('accounts:manage_addresses')
    else:
        form = AddressForm(instance=address)
    return render(request, 'accounts/address_form.html', {'form': form})

@login_required
def delete_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    address.delete()
    messages.success(request, 'Address deleted successfully.')
    return redirect('accounts:manage_addresses')

@login_required
def set_default_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    address.is_default = True
    address.save()
    return redirect('accounts:manage_addresses')

@login_required
def view_orders(request):
    # Implement order viewing logic here
    # orders = Order.objects.filter(user=request.user)
    # return render(request, 'accounts/view_orders.html', {'orders': orders})
    pass

@login_required
def cancel_order(request, order_id):
    # Implement order cancellation logic here
    # order = get_object_or_404(Order, id=order_id, user=request.user)
    # order.status = 'Cancelled'
    # order.save()
    # messages.success(request, 'Order cancelled successfully.')
    # return redirect('accounts:view_orders')
    pass

def forgot_password(request):
    # Implement forgot password logic here
    pass
