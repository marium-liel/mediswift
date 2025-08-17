from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('category/<int:category_id>/', views.category_detail, name='category_detail'),
    
    # Review URLs
    path('product/<int:product_id>/review/', views.add_review, name='add_review'),
    path('review/<int:review_id>/edit/', views.edit_review, name='edit_review'),
    
    # Wishlist URLs
    path('wishlist/', views.wishlist, name='wishlist'),
    path('product/<int:product_id>/add-to-wishlist/', views.add_to_wishlist, name='add_to_wishlist'),
    path('product/<int:product_id>/remove-from-wishlist/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('product/<int:product_id>/move-to-cart/', views.move_to_cart, name='move_to_cart'),
    
    # Admin URLs
    path('admin/products/', views.admin_product_list, name='admin_product_list'),
    path('admin/products/add/', views.admin_add_product, name='admin_add_product'),
    path('admin/products/<int:product_id>/edit/', views.admin_edit_product, name='admin_edit_product'),
    path('admin/products/<int:product_id>/delete/', views.admin_delete_product, name='admin_delete_product'),
] 