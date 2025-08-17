from django.contrib import admin
from .models import Order, OrderItem, SmartRefill, MedicineReminder, Subscription, AutoDelivery

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('total_price',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'status', 'total_amount', 'created_at')
    list_filter = ('status', 'payment_status', 'created_at')
    search_fields = ('order_number', 'user__username', 'shipping_address')
    readonly_fields = ('order_number', 'created_at', 'updated_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Order Information', {
            'fields': ('user', 'order_number', 'status', 'total_amount')
        }),
        ('Shipping Information', {
            'fields': ('shipping_address', 'shipping_city', 'shipping_state', 'shipping_zip_code', 'shipping_phone')
        }),
        ('Payment Information', {
            'fields': ('payment_method', 'payment_status')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price', 'total_price')
    list_filter = ('order__status', 'product__category')
    search_fields = ('order__order_number', 'product__name')
    readonly_fields = ('total_price',)

@admin.register(SmartRefill)
class SmartRefillAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'last_order_date', 'estimated_refill_date', 'is_notified', 'days_until_refill')
    list_filter = ('is_notified', 'estimated_refill_date', 'product__category')
    search_fields = ('user__username', 'product__name')
    readonly_fields = ('days_until_refill', 'is_due_for_refill')
    ordering = ('-estimated_refill_date',)
    
    fieldsets = (
        ('Refill Information', {
            'fields': ('user', 'product', 'last_order_date', 'estimated_refill_date', 'is_notified')
        }),
        ('Calculated Fields', {
            'fields': ('days_until_refill', 'is_due_for_refill'),
            'classes': ('collapse',)
        }),
    )

@admin.register(MedicineReminder)
class MedicineReminderAdmin(admin.ModelAdmin):
    list_display = ('user', 'reminder_name', 'product', 'frequency', 'reminder_time', 'is_active', 'next_reminder')
    list_filter = ('frequency', 'notification_type', 'is_active', 'start_date')
    search_fields = ('user__username', 'reminder_name', 'product__name')
    readonly_fields = ('next_reminder',)
    ordering = ('reminder_time',)
    
    fieldsets = (
        ('Reminder Information', {
            'fields': ('user', 'reminder_name', 'product', 'dosage')
        }),
        ('Schedule', {
            'fields': ('frequency', 'custom_days', 'reminder_time', 'start_date', 'end_date')
        }),
        ('Notifications', {
            'fields': ('notification_type', 'is_active')
        }),
        ('Calculated Fields', {
            'fields': ('next_reminder',),
            'classes': ('collapse',)
        }),
    )

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity', 'frequency', 'status', 'next_delivery_date', 'days_until_next_delivery')
    list_filter = ('status', 'frequency', 'auto_billing', 'created_at')
    search_fields = ('user__username', 'product__name')
    readonly_fields = ('days_until_next_delivery', 'is_due_for_delivery', 'days_until_expiry')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Subscription Information', {
            'fields': ('user', 'product', 'quantity', 'frequency', 'status')
        }),
        ('Billing & Shipping', {
            'fields': ('auto_billing', 'payment_method', 'shipping_address', 'shipping_city', 'shipping_state', 'shipping_zip_code', 'shipping_phone')
        }),
        ('Schedule', {
            'fields': ('next_delivery_date', 'expiry_date')
        }),
        ('Calculated Fields', {
            'fields': ('days_until_next_delivery', 'is_due_for_delivery', 'days_until_expiry'),
            'classes': ('collapse',)
        }),
    )

@admin.register(AutoDelivery)
class AutoDeliveryAdmin(admin.ModelAdmin):
    list_display = ('subscription', 'product', 'quantity', 'scheduled_date', 'delivery_date', 'status')
    list_filter = ('status', 'scheduled_date', 'delivery_date')
    search_fields = ('subscription__user__username', 'product__name', 'tracking_number')
    readonly_fields = ('subscription', 'product', 'quantity', 'scheduled_date')
    ordering = ('-scheduled_date',)
    
    fieldsets = (
        ('Delivery Information', {
            'fields': ('subscription', 'product', 'quantity', 'status')
        }),
        ('Schedule', {
            'fields': ('scheduled_date', 'delivery_date')
        }),
        ('Tracking', {
            'fields': ('tracking_number', 'notes')
        }),
    ) 