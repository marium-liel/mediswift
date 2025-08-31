from django.contrib import admin
from .models import Category, Product, Cart, CartItem, RefillSuggestion

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'category', 'product_type', 'price', 'stock_quantity', 'expiry_date', 'is_active')
    list_filter = ('category', 'product_type', 'is_active', 'created_at')
    search_fields = ('name', 'brand', 'description')
    list_editable = ('price', 'stock_quantity', 'is_active')
    ordering = ('-created_at',)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if hasattr(request.user, 'is_admin') and request.user.is_admin:
            return qs
        return qs.filter(is_active=True)

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_items', 'total_price', 'created_at')
    readonly_fields = ('total_items', 'total_price')

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity', 'total_price')
    readonly_fields = ('total_price',)

@admin.register(RefillSuggestion)
class RefillSuggestionAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'suggested_date', 'is_active')
    list_filter = ('is_active', 'suggested_date')
    search_fields = ('user__email', 'product__name')
