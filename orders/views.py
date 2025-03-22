from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from .models import Order, OrderItem, Wallet
from cart.models import Cart
from accounts.models import Address
from store.models import Variant
from .forms import OrderForm
from django.db import transaction
import razorpay
from django.utils import timezone
from coupons.models import Coupon, CouponUsage
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt 
from decimal import Decimal

razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

@login_required
def create_order(request):
    user = request.user
    cart = Cart.objects.filter(user=user).first()
    addresses = Address.objects.filter(user=user, is_deleted=False)
    wallet, created = Wallet.objects.get_or_create(user=user)

    if not cart or not cart.items.exists():
        return redirect('view_cart')

    error = None
    discount = 0
    applied_coupon = None

    # ✅ Fetch active coupons
    active_coupons = Coupon.objects.filter(active=True, expiration_date__gte=timezone.now())
    print(active_coupons)

    # ✅ Pass necessary context to template
    return render(request, "orders/create_order.html", {
        "cart": cart,
        "addresses": addresses,
        "wallet": wallet,
        "active_coupons": active_coupons,
        "applied_coupon": applied_coupon,
        "discount": discount,
        "error": error,
    })


@login_required
def razorpay_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if request.method == 'POST':
        payment_id = request.POST.get('razorpay_payment_id')
        order.payment_id = payment_id
        order.payment_status = 'COMPLETED'
        order.save()
        return redirect('order_detail', order_id=order.id)
    
    razorpay_order = razorpay_client.order.create({
        'amount': int(order.total_price * 100),  # Amount in paise
        'currency': 'INR',
        'payment_capture': '1'
    })
    
    return render(request, 'orders/razorpay_payment.html', {
        'order': order,
        'razorpay_order_id': razorpay_order['id'],
        'razorpay_merchant_key': settings.RAZORPAY_KEY_ID,
        'callback_url': request.build_absolute_uri(f"/orders/razorpay-callback/{order.id}/")
    })

@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/order_list.html', {'orders': orders})

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})

@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if not order.can_cancel():
        return render(request, 'orders/cancel_error.html', {'message': 'This order cannot be cancelled.'})
    
    if request.method == 'POST':
        with transaction.atomic():
            # Update order status
            order.status = 'CANCELLED'
            order.save()
            
            # Refund to wallet
            wallet, created = Wallet.objects.get_or_create(user=request.user)
            wallet.add_funds(order.total_price)
            
            # Update stock
            for item in order.items.all():
                variant = item.variant
                variant.stock += item.quantity
                variant.save()
        messages.success(request, f'Order #{order.id} has been successfully cancelled and refunded to your wallet.')
        return redirect('order_detail', order_id=order.id)
    
    return render(request, 'orders/confirm_cancellation.html', {'order': order})


@login_required
@csrf_exempt  # Only needed for testing; remove in production
def validate_coupon(request):
    if request.method == "POST":
        coupon_code = request.POST.get("coupon_code", "").strip()
        user = request.user
        cart = Cart.objects.filter(user=user).first()

        if not cart or not cart.items.exists():
            return JsonResponse({"error": "Your cart is empty."}, status=400)

        try:
            coupon = Coupon.objects.get(code=coupon_code, active=True)

            # ✅ Validate coupon conditions
            if coupon.expiration_date < timezone.now():
                return JsonResponse({"error": "Coupon has expired."}, status=400)
            if CouponUsage.objects.filter(user=user, coupon=coupon).count() >= coupon.usage_limit:
                return JsonResponse({"error": "You have already used this coupon."}, status=400)
            if cart.get_total_price() < coupon.min_order_amount:
                return JsonResponse(
                    {"error": f"Minimum order amount to use this coupon is ₹{coupon.min_order_amount}."},
                    status=400,
                )

            # ✅ Calculate discount
            discount = 0
            if coupon.discount_type == "percentage":
                discount = (Decimal(coupon.discount_value) / Decimal(100)) * cart.get_total_price()
                if coupon.max_discount:
                    discount = min(discount, coupon.max_discount)
            else:
                discount = coupon.discount_value

            # ✅ Store coupon and discount in session
            request.session["applied_coupon"] = coupon.code
            request.session["discount"] = float(discount)
            final_total = cart.get_total_price() - Decimal(str(discount))
            print(final_total)
            final_total = round(float(final_total), 2)
            return JsonResponse(
                {"success": True, "discount": discount, "final_total": final_total}
            )

        except Coupon.DoesNotExist:
            return JsonResponse({"error": "Invalid coupon code."}, status=400)

    return JsonResponse({"error": "Invalid request."}, status=400)



@login_required
@csrf_exempt
def place_order(request):
    if request.method == "POST":
        user = request.user
        address_id = request.POST.get("address_id")
        payment_method = request.POST.get("payment_method")
        final_total = Decimal(request.POST.get("final_total"))
        
        
        # ✅ Validate address and payment method
        if not address_id:
            return JsonResponse({"error": "Please select an address."}, status=400)
        if not payment_method:
            return JsonResponse({"error": "Please select a payment method."}, status=400)

        address = get_object_or_404(Address, id=address_id, user=user)
        cart = Cart.objects.filter(user=user).first()
        

        if not cart or not cart.items.exists():
            return JsonResponse({"error": "Your cart is empty."}, status=400)

        with transaction.atomic():
            # ✅ Check stock before placing order
            for cart_item in cart.items.all():
                variant = Variant.objects.select_for_update().get(id=cart_item.variant.id)
                if variant.available_stock() < cart_item.quantity:
                    return JsonResponse(
                        {"error": f"Not enough stock for {variant.product.name} - {variant.color}."},
                        status=400,
                    )

            # ✅ Create order
            order = Order.objects.create(
                user=user,
                address=address,
                total_price=final_total,
                payment_method=payment_method,
                status="PENDING",
            )

            # ✅ Create order items and update stock
            for cart_item in cart.items.all():
                variant = Variant.objects.get(id=cart_item.variant.id)
                OrderItem.objects.create(
                    order=order,
                    variant=variant,
                    quantity=cart_item.quantity,
                    price=variant.price,
                )
                variant.stock -= cart_item.quantity
                variant.reserved_quantity -= cart_item.quantity
                variant.save()

            # ✅ Clear cart after placing order
            cart.items.all().delete()

            # ✅ Apply coupon usage if coupon applied
            applied_coupon_code = request.session.get("applied_coupon")
            if applied_coupon_code:
                coupon = Coupon.objects.filter(code=applied_coupon_code, active=True).first()
                if coupon:
                    CouponUsage.objects.create(user=user, coupon=coupon)

            # ✅ Handle payment logic
            if payment_method == "RAZORPAY":
                razorpay_payment_url = f"/orders/razorpay-payment/{order.id}/"
                return JsonResponse({"success": True, "order_id": order.id, "redirect_url": razorpay_payment_url})
            elif payment_method == "WALLET":
                wallet = Wallet.objects.get(user=user)
                if wallet.balance >= order.total_price:
                    wallet.deduct_funds(order.total_price)
                    order.payment_status = "COMPLETED"
                    order.save()
                    return JsonResponse({"success": True, "order_id": order.id})
                else:
                    order.delete()
                    return JsonResponse({"error": "Insufficient wallet balance. Please choose another payment method."})
            elif payment_method == "COD":
                order.payment_status = "PENDING"
                order.save()
                return JsonResponse({"success": True, "order_id": order.id})

    return JsonResponse({"error": "Invalid request."}, status=400)
