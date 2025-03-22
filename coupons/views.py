from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib import messages
from django.utils import timezone
from .models import Coupon, CouponUsage

def apply_coupon(request):
    if request.method == "POST":
        code = request.POST.get("coupon_code")
        cart_total = request.session.get("cart_total", 0)

        try:
            coupon = Coupon.objects.get(code=code, active=True)

            # Check if expired
            if coupon.expiration_date < timezone.now():
                messages.error(request, "Coupon has expired.")
                return redirect("cart")

            # Check usage limit
            if CouponUsage.objects.filter(user=request.user, coupon=coupon).count() >= coupon.usage_limit:
                messages.error(request, "You have already used this coupon.")
                return redirect("cart")

            # Check min order amount
            if cart_total < coupon.min_order_amount:
                messages.error(request, f"Minimum order amount to use this coupon is ₹{coupon.min_order_amount}")
                return redirect("cart")

            # Apply discount
            if coupon.discount_type == "percentage":
                discount = (coupon.discount_value / 100) * cart_total
                if coupon.max_discount:
                    discount = min(discount, coupon.max_discount)
            else:
                discount = coupon.discount_value

            # Store discount in session
            request.session["discount"] = discount
            request.session["applied_coupon"] = code

            messages.success(request, f"Coupon applied! You saved ₹{discount}")
            return redirect("cart")

        except Coupon.DoesNotExist:
            messages.error(request, "Invalid coupon code.")
            return redirect("cart")
