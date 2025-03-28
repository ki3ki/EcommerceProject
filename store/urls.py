from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('category/', views.collections, name='category'),  # Updated from 'collections/' to 'category/'
    path('category/<slug:category_slug>/', views.category_detail, name='category_detail'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('update_product_variant/<slug:product_slug>/<int:variant_id>/', views.update_product_variant, name='update_product_variant'),
    path('get-variant-details/<str:product_slug>/<int:variant_id>/', views.get_variant_details, name='get_variant_details'),
    path('advanced-search/', views.advanced_search, name='advanced_search'),
    path('blogs/', views.blog_list, name='blogs'),
    path('blogs/<slug:slug>/', views.blog_detail, name='blog_detail'),
]
