from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from .models import Cart, CartItem
from store.models import Variant



@require_POST
@login_required
def add_to_cart(request, variant_id):
    variant = get_object_or_404(Variant, id=variant_id)
    quantity = int(request.POST.get('quantity', 1))
    
    try:
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_item, item_created = CartItem.objects.get_or_create(cart=cart, variant=variant)
        
        if not item_created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity
        
        cart_item.save()
        
        return JsonResponse({
            'status': 'success',
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
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    action = request.POST.get('action')
    
    if action == 'increase':
        if cart_item.quantity >= cart_item.variant.stock:
            return JsonResponse({'status': 'error', 'message': 'Not enough stock'})
        cart_item.quantity += 1
    elif action == 'decrease':
        cart_item.quantity -= 1
    
    if cart_item.quantity < 1:
        cart_item.delete()
    else:
        cart_item.save()
    
    return redirect('cart:view_cart')

@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    return redirect('cart:view_cart')

