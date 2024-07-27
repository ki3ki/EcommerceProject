from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Order, OrderItem
from cart.models import Cart
from accounts.models import Address
from .forms import OrderForm
from store.models import Variant
from django.db import transaction

@login_required
def create_order(request):
    user = request.user
    cart = Cart.objects.filter(user=user).first()
    addresses = Address.objects.filter(user=user)

    if not cart or not cart.items.exists():
        return redirect('view_cart')

    if request.method == 'POST':
        address_id = request.POST.get('address')
        if address_id:
            address = get_object_or_404(Address, id=address_id, user=user)
            
            with transaction.atomic():
                # Check stock availability again before creating the order
                for cart_item in cart.items.all():
                    variant = Variant.objects.select_for_update().get(id=cart_item.variant.id)
                    if cart_item.quantity > variant.available_stock():
                        return render(request, 'orders/create_order.html', {
                            'cart': cart,
                            'addresses': addresses,
                            'error': f'Not enough stock for {variant.product.name} - {variant.color}'
                        })
                
                order = Order.objects.create(
                    user=user,
                    address=address,
                    total_price=cart.get_total_price()
                )
                
                for cart_item in cart.items.all():
                    variant = Variant.objects.get(id=cart_item.variant.id)
                    OrderItem.objects.create(
                        order=order,
                        variant=variant,
                        quantity=cart_item.quantity,
                        price=variant.price
                    )
                    # Update actual stock and clear reserved quantity
                    variant.stock -= cart_item.quantity
                    variant.reserved_quantity -= cart_item.quantity
                    variant.save()
                
                cart.items.all().delete()
            
            return redirect('order_detail', order_id=order.id)
        else:
            return render(request, 'orders/create_order.html', {
                'cart': cart,
                'addresses': addresses,
                'error': 'Please select an address.'
            })
    else:
        return render(request, 'orders/create_order.html', {
            'cart': cart,
            'addresses': addresses
        })
    

@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/order_list.html', {'orders': orders})

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})