from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from .models import Cart, CartItem, Wishlist, WishlistItem
from store.models import Variant
from django.db import transaction

@require_POST
@login_required
def add_to_cart(request, variant_id):
    variant = get_object_or_404(Variant, id=variant_id)
    quantity = int(request.POST.get('quantity', 1))
    
    with transaction.atomic():
        variant = Variant.objects.select_for_update().get(id=variant_id)
        
        if quantity > variant.available_stock():
            return JsonResponse({
                'status': 'error',
                'message': f'Only {variant.available_stock()} items available in stock.',
            }, status=400)
        
        try:
            cart, created = Cart.objects.get_or_create(user=request.user)
            cart_item, item_created = CartItem.objects.get_or_create(cart=cart, variant=variant)
            
            if not item_created:
                if cart_item.quantity + quantity > variant.available_stock():
                    return JsonResponse({
                        'status': 'error',
                        'message': f'Cannot add {quantity} more items. Only {variant.available_stock() - cart_item.quantity} more available.',
                    }, status=400)
                cart_item.quantity += quantity
            else:
                cart_item.quantity = quantity
            
            cart_item.save()
            
            variant.reserved_quantity += quantity
            variant.save()
            
            return JsonResponse({
                'status': 'success',
                'message': f'{quantity} item(s) added to cart successfully.',
                'cart_count': cart.items.count(),
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e),
            }, status=400)



@login_required
def view_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    return render(request, 'view_cart.html', {'cart': cart})

@login_required
def update_cart(request, item_id):
    with transaction.atomic():
        cart_item = get_object_or_404(CartItem.objects.select_related('variant'), id=item_id, cart__user=request.user)
        variant = Variant.objects.select_for_update().get(id=cart_item.variant.id)
        action = request.POST.get('action')
        
        if action == 'increase':
            if cart_item.quantity >= variant.available_stock():
                return JsonResponse({'status': 'error', 'message': 'Not enough stock'})
            cart_item.quantity += 1
            variant.reserved_quantity += 1
        elif action == 'decrease':
            cart_item.quantity -= 1
            variant.reserved_quantity -= 1
        
        if cart_item.quantity < 1:
            variant.reserved_quantity -= cart_item.quantity  # Release all reserved quantity
            cart_item.delete()
        else:
            cart_item.save()
        
        variant.save()
    
    return redirect('cart:view_cart')

@login_required
def remove_from_cart(request, item_id):
    with transaction.atomic():
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        variant = Variant.objects.select_for_update().get(id=cart_item.variant.id)
        variant.reserved_quantity -= cart_item.quantity
        variant.save()
        cart_item.delete()
    return redirect('cart:view_cart')

@login_required
@require_POST
def add_to_wishlist(request, variant_id):
    variant = get_object_or_404(Variant, id=variant_id)
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    wishlist_item, created = WishlistItem.objects.get_or_create(wishlist=wishlist, variant=variant)
    
    if created:
        return JsonResponse({'status': 'success', 'message': 'Item added to wishlist.'})
    else:
        return JsonResponse({'status': 'info', 'message': 'Item already in wishlist.'})

@login_required
def view_wishlist(request):
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    return render(request, 'wishlist.html', {'wishlist': wishlist})

@login_required
def remove_from_wishlist(request, item_id):
    wishlist_item = get_object_or_404(WishlistItem, id=item_id, wishlist__user=request.user)
    print(f"Before deletion: {WishlistItem.objects.filter(id=item_id).exists()}")  
    wishlist_item.delete()
    print(f"After deletion: {WishlistItem.objects.filter(id=item_id).exists()}")
    return redirect('cart:view_wishlist')

@login_required
def move_to_cart(request, item_id):
    with transaction.atomic():
        wishlist_item = get_object_or_404(WishlistItem, id=item_id, wishlist__user=request.user)
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, variant=wishlist_item.variant)
        
        if not created:
            cart_item.quantity += 1
            cart_item.save()
        
        wishlist_item.delete()
    
    return redirect('cart:view_cart')