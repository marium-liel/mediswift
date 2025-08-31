
from django.urls import path
from .views import (
    CategoryListView, ProductListView, ProductDetailView,
    CartView, add_to_cart, update_cart_item, remove_from_cart, clear_cart,
    RefillSuggestionListView, low_stock_products, expiring_products,
    related_products,
    WishlistView, add_to_wishlist, remove_from_wishlist,
    SaveForLaterListCreateView, SaveForLaterDeleteView,
    InventoryAlertListView,
    AdminAnalyticsView,
    SubscriptionListCreateView,
    SubscriptionDetailView
)
from . import admin_views


urlpatterns = [
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('', ProductListView.as_view(), name='product-list'),
    path('<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    
    # Admin endpoints
    path('admin/products/', admin_views.admin_products, name='admin-products'),
    path('admin/products/<int:product_id>/', admin_views.admin_product_detail, name='admin-product-detail'),
    path('<int:pk>/related/', related_products, name='related-products'),
    path('cart/', CartView.as_view(), name='cart'),
    path('cart/add/', add_to_cart, name='add-to-cart'),
    path('cart/update/<int:item_id>/', update_cart_item, name='update-cart-item'),
    path('cart/remove/<int:item_id>/', remove_from_cart, name='remove-from-cart'),
    path('cart/clear/', clear_cart, name='clear-cart'),
    path('refill-suggestions/', RefillSuggestionListView.as_view(), name='refill-suggestions'),
    path('admin/low-stock/', low_stock_products, name='low-stock-products'),
    path('admin/expiring/', expiring_products, name='expiring-products'),

    # Wishlist
    path('wishlist/', WishlistView.as_view(), name='wishlist'),
    path('wishlist/add/<int:product_id>/', add_to_wishlist, name='add-to-wishlist'),
    path('wishlist/remove/<int:product_id>/', remove_from_wishlist, name='remove-from-wishlist'),

    # Save For Later
    path('save-for-later/', SaveForLaterListCreateView.as_view(), name='saveforlater-list-create'),
    path('save-for-later/<int:pk>/', SaveForLaterDeleteView.as_view(), name='saveforlater-delete'),

    # Inventory Alerts (admin)
    path('admin/inventory-alerts/', InventoryAlertListView.as_view(), name='inventory-alert-list'),
    path('admin/analytics/', AdminAnalyticsView.as_view(), name='admin-analytics'),
    
    # Subscriptions
    path('subscriptions/', SubscriptionListCreateView.as_view(), name='subscription-list-create'),
    path('subscriptions/<int:pk>/', SubscriptionDetailView.as_view(), name='subscription-detail'),
]
