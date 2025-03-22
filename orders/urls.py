from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_order, name='create_order'),
    path('list/', views.order_list, name='order_list'),
    path('<int:order_id>/', views.order_detail, name='order_detail'),
    path('razorpay-payment/<int:order_id>/', views.razorpay_payment, name='razorpay_payment'),
    path('cancel/<int:order_id>/', views.cancel_order, name='cancel_order'),
    path("validate-coupon/", views.validate_coupon, name="validate_coupon"),
    path("place-order/", views.place_order, name="place_order"),
    path("order-detail/<int:order_id>/", views.order_detail, name="order_detail"),
]
