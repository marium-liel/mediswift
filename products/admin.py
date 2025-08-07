from django.contrib import admin
from .models import Category, Product, ProductDetail

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    list_filter = ('created_at', 'updated_at')
    ordering = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'brand', 'price', 'current_price', 'availability', 'product_type', 'is_featured')
    list_filter = ('category', 'product_type', 'availability', 'is_featured', 'requires_prescription', 'created_at')
    search_fields = ('name', 'brand', 'description')
    list_editable = ('price', 'availability', 'is_featured')
    readonly_fields = ('current_price', 'discount_percentage')
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