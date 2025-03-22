#view file
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from .models import Category, Product, ProductImage, Variant, Brand
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q, Min
from django.core.paginator import Paginator
from cart.models import Cart, Wishlist, WishlistItem, CartItem
from orders.models import OrderItem
import json
from django.db.models import Sum
from admin_panel.models import Blog

# Create your views here.


def home(request):
    wishlist_count = 0
    cart_count = 0
    if request.user.is_authenticated:
        wishlist = Wishlist.objects.filter(user = request.user)
        print(wishlist)
        wishlist_count = WishlistItem.objects.filter(wishlist__user=request.user).count()
        
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            cart_count = CartItem.objects.filter(cart__user=request.user).count()

    
    featured_products = Product.objects.filter(is_featured=True)[:6] 
    context = {
        'featured_products': featured_products,
        'wishlist_count': wishlist_count,
        'cart_count': cart_count,
    }
    return render(request, 'index.html',  context)

def collections(request):
    print("collections view is called")
    categories = Category.objects.filter(is_deleted=False).prefetch_related(
        'products__variants__images'
    )
    print(f"Number of categories found: {categories.count()}")

    brands = Brand.objects.filter(is_deleted=False)
    print(f"Number of brands found: {brands.count()}")

    featured_products = Product.objects.filter(is_featured=True, is_deleted=False)
    print(f"Number of featured products found: {featured_products.count()}")


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

    for product in featured_products:
        product.first_variant = product.variants.filter(is_deleted=False).first()
           
        if product.first_variant:
           print(f"First variant in featured product: {product.first_variant.color}")  
           product.first_image = product.first_variant.images.filter(is_deleted=False).first()
           if product.first_image:
              print(f'First image URL: {product.first_image.image}')
           else:
              print('No image found for this variant')
        else:
           product.first_image = None

    best_sellers = (
      OrderItem.objects.values('variant')  # Group by variant
      .annotate(total_sold=Sum('quantity'))  # Sum the quantity sold
      .order_by('-total_sold')[:4]  # Get the top 4 best-sellers
    )
    best_seller_variant_ids = [item['variant'] for item in best_sellers]
    best_seller_variants = (
       Variant.objects
       .select_related('product')  # Fetch product details
       .prefetch_related('images')  # Fetch related images
       .filter(id__in=best_seller_variant_ids)  # Filter only best-selling variants
    )
    best_seller_data = []
    for variant in best_seller_variants:
        first_image = variant.images.filter(is_deleted=False).first()
        print(f"Product Name: {variant.product.name}")
        if first_image:
            print(f"Image URL: {first_image.image.url}")
        else:
             print("No image available for this variant.")
        best_seller_data.append({
            'product_name': variant.product.name,
            'variant_id': variant.id,
            'image_url': first_image.image.url if first_image else None,
        })


   


    context = {
        'categories': categories,
        'brands': brands,  # Passing brand data with name and image
        'featured_products': featured_products,
        'best_seller_data': best_seller_data
    }


    return render(request, 'collections.html', context)

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


def blog_list(request):
    blogs = Blog.objects.all().order_by('-created_at')
    return render(request, 'blog.html', {'blogs': blogs})

def blog_detail(request, slug):
    blog = get_object_or_404(Blog, slug=slug)
    return render(request, 'blog_detail.html', {'blog': blog})