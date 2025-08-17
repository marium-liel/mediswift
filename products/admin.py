from django.contrib import admin
from .models import Category, Product, ProductDetail, Review, Wishlist

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    list_filter = ('created_at', 'updated_at')
    ordering = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'brand', 'price', 'current_price', 'availability', 'product_type', 'is_featured', 'average_rating')
    list_filter = ('category', 'product_type', 'availability', 'is_featured', 'requires_prescription', 'created_at')
    search_fields = ('name', 'brand', 'description')
    list_editable = ('price', 'availability', 'is_featured')
    readonly_fields = ('current_price', 'discount_percentage', 'average_rating', 'review_count')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'category', 'brand', 'product_type')
        }),
        ('Pricing', {
            'fields': ('price', 'sale_price', 'current_price', 'discount_percentage')
        }),
        ('Inventory', {
            'fields': ('stock_quantity', 'availability')
        }),
        ('Settings', {
            'fields': ('requires_prescription', 'is_featured', 'image')
        }),
        ('Reviews', {
            'fields': ('average_rating', 'review_count')
        }),
    )

@admin.register(ProductDetail)
class ProductDetailAdmin(admin.ModelAdmin):
    list_display = ('product', 'prescription_required', 'expiry_date')
    list_filter = ('prescription_required', 'expiry_date')
    search_fields = ('product__name',)
    fieldsets = (
        ('Product', {
            'fields': ('product',)
        }),
        ('Medical Information', {
            'fields': ('dosage', 'precautions', 'side_effects', 'prescription_required')
        }),
        ('Product Details', {
            'fields': ('ingredients', 'storage_instructions', 'manufacturer', 'expiry_date')
        }),
    )

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at', 'product__category')
    search_fields = ('product__name', 'user__username', 'comment')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Review Information', {
            'fields': ('product', 'user', 'rating', 'comment')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'added_at')
    list_filter = ('added_at', 'product__category')
    search_fields = ('user__username', 'product__name')
    readonly_fields = ('added_at',)
    ordering = ('-added_at',) 