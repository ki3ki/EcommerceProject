from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from .models import Category, Product, ProductImage, Variant, Brand
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q, Min, Sum
from django.core.paginator import Paginator
from cart.models import Cart, Wishlist, WishlistItem, CartItem
from orders.models import OrderItem
from admin_panel.models import Blog
from django.conf import settings
import json


def home(request):
    wishlist_count = 0
    cart_count = 0
    if request.user.is_authenticated:
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
    return render(request, 'index.html', context)


def collections(request):
    categories = Category.objects.filter(is_deleted=False).prefetch_related(
        'products__variants__images'
    )
    brands = Brand.objects.filter(is_deleted=False)
    featured_products = Product.objects.filter(is_featured=True, is_deleted=False)

    for category in categories:
        category.first_product = category.products.filter(is_deleted=False).first()
        if category.first_product:
            category.first_variant = category.first_product.variants.filter(is_deleted=False).first()
            category.first_image = category.first_variant.images.filter(is_deleted=False).first() if category.first_variant else None

    for product in featured_products:
        product.first_variant = product.variants.filter(is_deleted=False).first()
        product.first_image = product.first_variant.images.filter(is_deleted=False).first() if product.first_variant else None

    best_sellers = (
        OrderItem.objects.values('variant')
        .annotate(total_sold=Sum('quantity'))
        .order_by('-total_sold')[:4]
    )
    best_seller_variant_ids = [item['variant'] for item in best_sellers]
    best_seller_variants = Variant.objects.select_related('product').prefetch_related('images').filter(id__in=best_seller_variant_ids)

    best_seller_data = [
        {
            'product_name': variant.product.name,
            'variant_id': variant.id,
            'image_url': variant.images.filter(is_deleted=False).first().image.url if variant.images.filter(is_deleted=False).first() else None,
        }
        for variant in best_seller_variants
    ]

    context = {
        'categories': categories,
        'brands': brands,
        'featured_products': featured_products,
        'best_seller_data': best_seller_data,
    }
    return render(request, 'collections.html', context)


def category_detail(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug, is_deleted=False)
    products = Product.objects.filter(category=category, is_deleted=False)

    for product in products:
        product.first_variant = product.variants.filter(is_deleted=False).first()
        product.first_image = product.first_variant.images.filter(is_deleted=False).first() if product.first_variant else None

    return render(request, 'category_detail.html', {'category': category, 'products': products})


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_deleted=False)
    variants = product.variants.filter(is_deleted=False)
    images = ProductImage.objects.filter(variant__product=product, is_deleted=False)

    default_variant = variants.first()
    product.variant = default_variant if default_variant else None

    return render(request, 'product_detail.html', {
        'product': product,
        'variants': variants,
        'images': images,
        'brand': product.brand
    })


@csrf_exempt
def update_product_variant(request, product_slug, variant_id):
    if request.method == 'POST':
        variant = get_object_or_404(Variant, id=variant_id)
        response_data = {
            'success': True,
            'price': variant.price,
            'stock': variant.stock,
            'color': variant.color,
        }
        return JsonResponse(response_data)

    return JsonResponse({'success': False}, status=400)


def get_variant_details(request, product_slug, variant_id):
    product = get_object_or_404(Product, slug=product_slug, is_deleted=False)
    variant = product.variants.filter(id=variant_id).first()

    if variant:
        variant_images = ProductImage.objects.filter(variant=variant, is_deleted=False)
        response_data = {
            'success': True,
            'price': str(variant.price),
            'stock': variant.stock,
            'color': variant.color,
            'images': [{'image': request.build_absolute_uri(image.image.url)} for image in variant_images],
        }
        return JsonResponse(response_data)

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

    sort_options = {
        'price_low_to_high': 'min_price',
        'price_high_to_low': '-min_price',
        'average_rating': '-average_rating',
        'featured': 'featured',
        'new_arrivals': '-created_at',
        'name_asc': 'name',
        'name_desc': '-name',
    }
    products = products.order_by(sort_options.get(sort_by, '-popularity'))

    paginator = Paginator(products, 10)
    page_number = request.GET.get('page')
    paginated_products = paginator.get_page(page_number)

    return render(request, 'search_results.html', {'products': paginated_products})

def blog_list(request):
    blogs = Blog.objects.all().order_by('-created_at')
    return render(request, 'blog.html', {'blogs': blogs})

def blog_detail(request, slug):
    blog = get_object_or_404(Blog, slug=slug)
    return render(request, 'blog_detail.html', {'blog': blog})