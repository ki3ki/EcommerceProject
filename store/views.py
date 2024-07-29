#view file
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from .models import Category, Product, ProductImage, Variant, Brand
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q, Min
from django.core.paginator import Paginator
import json


def home(request):
    return render(request, 'index.html')

def collections(request):
    print("collections view is called")
    categories = Category.objects.filter(is_deleted=False).prefetch_related(
        'products__variants__images'
    )
    print(f"Number of categories found: {categories.count()}")

    for category in categories:
        print(f"Processing category: {category.name}")
        category.first_product = category.products.filter(is_deleted=False).first()
        if category.first_product:
            print(f"First product in category: {category.first_product.name}")
            category.first_variant = category.first_product.variants.filter(is_deleted=False).first()
            if category.first_variant:
                print(f"First variant in product: {category.first_variant.color}")
                category.first_image = category.first_variant.images.filter(is_deleted=False).first()
                if category.first_image:
                    print(f'First image URL: {category.first_image.image}')
                else:
                    print('No image found for this variant')
            else:
                category.first_image = None
                print('No variant found for this product')
        else:
            category.first_variant = None
            category.first_image = None
            print('No product found in this category')

    return render(request, 'collections.html', {'categories': categories})

def category_detail(request, category_slug):
    print("category_detail view is called")
    category = get_object_or_404(Category, slug=category_slug, is_deleted=False)
    print(f"Category found: {category.name}")

    products = Product.objects.filter(category=category, is_deleted=False)
    print(f"Number of products found: {products.count()}")

    # Get the first variant and its first image for each product
    for product in products:
        print(f"Processing product: {product.name}")
        product.first_variant = product.variants.filter(is_deleted=False).first()
        if product.first_variant:
            product.first_image = product.first_variant.images.filter(is_deleted=False).first()
            print(f'Product: {product.name}, First Image URL: {product.first_image.image.url if product.first_image else "None"}')
        else:
            product.first_image = None
            print(f'Product: {product.name}, First Image: None')

    return render(request, 'category_detail.html', {'category': category, 'products': products})


def product_detail(request, slug):
    print("product_detail view is called")
    product = get_object_or_404(Product, slug=slug, is_deleted=False)
    print(f"Product found: {product.name}")

    
    variants = product.variants.filter(is_deleted=False)
    images = ProductImage.objects.filter(variant__product=product, is_deleted=False)

    print(f"Number of variants found: {variants.count()}")
    print(f"Number of images found: {images.count()}")

    default_variant = variants.first()
    if default_variant:
        print(f"Default variant: {default_variant.color}")
        product.variant = default_variant
    else:
        product.variant = None
        print("No variant found")

    # Pass all images to the template
    return render(request, 'product_detail.html', {
        'product': product,
        'variants': variants,  
        'images': images,      
        'brand': product.brand
    })

@csrf_exempt
def update_product_variant(request, product_slug, variant_id):
    print("update_product_variant view is called")
    if request.method == 'POST':
        print(f"Product slug: {product_slug}, Variant ID: {variant_id}")
        variant = get_object_or_404(Variant, id=variant_id)
        print(f"Variant found: Color={variant.color}, Price={variant.price}, Stock={variant.stock}")

        response_data = {
            'success': True,
            'price': variant.price,
            'stock': variant.stock,
            'color': variant.color,
        }
        return JsonResponse(response_data)
    
    print("Invalid request method or variant not found")
    return JsonResponse({'success': False}, status=400)

from django.conf import settings

def get_variant_details(request, product_slug, variant_id):
    print("get_variant_details view is called")
    product = get_object_or_404(Product, slug=product_slug, is_deleted=False)
    variant = product.variants.filter(id=variant_id).first()

    if variant:
        print(f"Variant found: Color={variant.color}, Price={variant.price}, Stock={variant.stock}")
        # Aggregate images for the variant
        variant_images = ProductImage.objects.filter(variant=variant, is_deleted=False)
        response_data = {
            'success': True,
            'price': str(variant.price),
            'stock': variant.stock,
            'color': variant.color,
            'images': [{'image': request.build_absolute_uri(image.image.url)} for image in variant_images],
        }
        return JsonResponse(response_data)
    
    print("Variant not found")
    return JsonResponse({'success': False}, status=404)



def advanced_search(request):
    query = request.GET.get('q', '')
    sort_by = request.GET.get('sort_by', 'popularity')
    show_out_of_stock = request.GET.get('show_out_of_stock', 'off') == 'on'

    products = Product.objects.filter(is_deleted=False).annotate(min_price=Min('variants__price'))

    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query) |
            Q(brand__name__icontains=query)
        )

    if not show_out_of_stock:
        products = products.filter(variants__stock__gt=0)

    if sort_by == 'price_low_to_high':
        products = products.order_by('min_price')
    elif sort_by == 'price_high_to_low':
        products = products.order_by('-min_price')
    elif sort_by == 'average_rating':
        products = products.order_by('-average_rating')
    elif sort_by == 'featured':
        products = products.filter(featured=True)
    elif sort_by == 'new_arrivals':
        products = products.order_by('-created_at')
    elif sort_by == 'name_asc':
        products = products.order_by('name')
    elif sort_by == 'name_desc':
        products = products.order_by('-name')
    else:  # Default to popularity
        products = products.order_by('-popularity')

    paginator = Paginator(products, 12)  # Show 12 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'products': page_obj,
        'query': query,
        'sort_by': sort_by,
        'show_out_of_stock': show_out_of_stock,
    }

    return render(request, 'advanced_search.html', context)