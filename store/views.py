from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from .models import Category, Product, ProductImage, Variant, Brand
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import json
# Create your views here.
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
                    print(f'First image URL: {category.first_image.image.url}')
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
        print("No default variant found")

    return render(request, 'product_detail.html', {'product': product, 'variants': variants, 'images': images, 'brand': product.brand})

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