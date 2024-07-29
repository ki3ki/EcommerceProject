# admin_panel/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required,  user_passes_test
from django.contrib import messages
from django.forms import formset_factory, modelformset_factory
from store.models import Category, Brand, Product, Variant, ProductImage
from orders.models import Order, OrderItem
from .forms import ProductForm, CategoryForm, VariantForm, BrandForm
from PIL import Image
import os, json





User = get_user_model()

def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_staff:
            login(request, user)
            return redirect('admin_panel:dashboard')
        else:
            messages.error(request, 'Invalid credentials or not an admin')
    return render(request, 'admin_panel/admin_login.html')

def admin_required(view_func):
    decorated_view_func = login_required(user_passes_test(lambda u : u.is_staff, login_url= 'admin_panel : login ')(view_func))
    return decorated_view_func

@admin_required  
@login_required
def admin_dashboard(request):
    return render(request, 'admin_panel/admin_dashboard.html')


def admin_logout(request):
    logout(request)
    return redirect('admin_panel:login')

@login_required
def manage_users(request):
    users = User.objects.all()
    return render(request, 'admin_panel/manage_users.html', {'users': users})

@login_required
def toggle_user_status(request, user_id):
    user = User.objects.get(id=user_id)
    user.is_active = not user.is_active
    user.save()
    return redirect('admin_panel:manage_users')

@login_required
def manage_categories(request):
    categories = Category.objects.filter(is_deleted=False)
    return render(request, 'admin_panel/manage_categories.html', {'categories': categories})

@login_required
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('admin_panel:manage_categories')
    else:
        form = CategoryForm()
    return render(request, 'admin_panel/add_category.html', {'form': form})

@login_required
def edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            return redirect('admin_panel:manage_categories')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'admin_panel/edit_category.html', {'form': form, 'category': category})

@login_required
def delete_category(request, category_id):
    category = Category.objects.get(id=category_id)
    category.is_deleted = True
    category.save()
    return redirect('admin_panel:manage_categories')

@login_required
def manage_products(request):
    products = Product.objects.filter(is_deleted=False)
    return render(request, 'admin_panel/manage_products.html', {'products': products})

@login_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('admin_panel:manage_products')
    else:
        form = ProductForm()
    return render(request, 'admin_panel/add_product.html', {'form': form})

@login_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('admin_panel:manage_products')
    else:
        form = ProductForm(instance=product)
    return render(request, 'admin_panel/edit_product.html', {'form': form})

@login_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        product.is_deleted = True
        product.save()
        return redirect('admin_panel:manage_products')
    
@login_required
def brand_list(request):
    brands = Brand.objects.all()
    return render(request, 'admin_panel/brand_list.html', {'brands': brands})

@login_required
def add_brand(request):
    if request.method == 'POST':
        form = BrandForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_panel:brand_list')
    else:
        form = BrandForm()
    return render(request, 'admin_panel/add_brand.html', {'form': form})

@login_required
def edit_brand(request, brand_id):
    brand = get_object_or_404(Brand, id=brand_id)
    if request.method == 'POST':
        form = BrandForm(request.POST, instance=brand)
        if form.is_valid():
            form.save()
            return redirect('admin_panel:brand_list')
    else:
        form = BrandForm(instance=brand)
    return render(request, 'admin_panel/edit_brand.html', {'form': form, 'brand': brand})

@login_required
def delete_brand(request, brand_id):
    brand = Brand.objects.get(id=brand_id)
    brand.delete()
    return redirect('admin_panel:brand_list')

def manage_variants(request):
    # Fetch all categories with related products and their variants
    categories = Category.objects.prefetch_related(
        'products__variants'
    ).all()
    
    return render(request, 'admin_panel/manage_variants.html', {'categories': categories})

def add_variant(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = VariantForm(request.POST, request.FILES)
        if form.is_valid():
            variant = form.save(commit=False)
            variant.product = product
            variant.save()
            
            # Handle three images
            images = [request.FILES.get('image1'), request.FILES.get('image2'), request.FILES.get('image3')]
            for image in images:
                if image:
                    ProductImage.objects.create(variant=variant, image=image)
            
            messages.success(request, 'Variant added successfully.')
            return redirect('admin_panel:manage_variants')
    else:
        form = VariantForm()
    return render(request, 'admin_panel/add_variant.html', {'form': form, 'product': product})


def edit_variant(request, variant_id):
    variant = get_object_or_404(Variant, id=variant_id)
    if request.method == 'POST':
        form = VariantForm(request.POST, request.FILES, instance=variant)
        if form.is_valid():
            form.save()
            return redirect('admin_panel:manage_variants')
    else:
        form = VariantForm(instance=variant)
    return render(request, 'admin_panel/edit_variant.html', {'form': form, 'variant': variant})

def delete_variant(request, variant_id):
    variant = get_object_or_404(Variant, id=variant_id)
    variant.delete()
    return redirect('admin_panel:manage_variants')


@login_required
def manage_orders(request):
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'admin_panel/manage_orders.html', {'orders': orders})

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'admin_panel/order_detail.html', {'order': order})

@login_required
def change_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.ORDER_STATUS_CHOICES):
            order.status = new_status
            order.save()
            messages.success(request, f'Order status updated to {new_status}')
        else:
            messages.error(request, 'Invalid status')
    return redirect('admin_panel:order_detail', order_id=order.id)

@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        order.status = 'cancelled'
        order.save()
        messages.success(request, 'Order cancelled successfully')
    return redirect('admin_panel:order_detail', order_id=order.id)

@login_required
def manage_inventory(request):
    variants = Variant.objects.all().order_by('product__name', 'color')
    return render(request, 'admin_panel/manage_inventory.html', {'variants': variants})

@login_required
def update_stock(request, variant_id):
    variant = get_object_or_404(Variant, id=variant_id)
    if request.method == 'POST':
        new_stock = request.POST.get('stock')
        try:
            new_stock = int(new_stock)
            variant.stock = new_stock
            variant.save()
            messages.success(request, f'Stock updated for {variant.product.name} - {variant.color}')
        except ValueError:
            messages.error(request, 'Invalid stock value')
    return redirect('admin_panel:manage_inventory')