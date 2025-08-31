
from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import timedelta, date

User = get_user_model()

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Categories"
    
    def __str__(self):
        return self.name

class Product(models.Model):
    PRODUCT_TYPE_CHOICES = (
        ('medicine', 'Medicine'),
        ('supplement', 'Supplement'),
    )
    
    name = models.CharField(max_length=200)
    brand = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    product_type = models.CharField(max_length=20, choices=PRODUCT_TYPE_CHOICES)
    description = models.TextField()
    dosage = models.CharField(max_length=100, blank=True)
    precautions = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.PositiveIntegerField(default=0)
    reserved_quantity = models.PositiveIntegerField(default=0)
    low_stock_threshold = models.PositiveIntegerField(default=10)
    expiry_date = models.DateField()
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    requires_prescription = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.brand}"
    
    def calculate_reserved_stock(self):
        """Calculate total stock reserved for active subscriptions"""
        total = self.subscription_set.filter(is_active=True).aggregate(
            total=models.Sum('reserved_stock'))['total']
        return total if total is not None else 0
    
    def update_stock_quantity(self):
        """Update available stock considering reserved quantities for subscriptions"""
        # Calculate total reserved stock from active subscriptions
        total_reserved = self.calculate_reserved_stock()
        
        # Update the reserved quantity
        self.reserved_quantity = total_reserved
        
        # Ensure we don't over-reserve
        if self.reserved_quantity > self.stock_quantity:
            self.reserved_quantity = self.stock_quantity
        
        self.save(update_fields=['reserved_quantity'])
        
        # Return actual available stock
        return self.available_stock
    
    @property
    def available_stock(self):
        """Get available stock after considering subscriptions"""
        reserved = self.calculate_reserved_stock()
        return max(0, self.stock_quantity - reserved)
    
    @property
    def is_in_stock(self):
        """Check if product is in stock considering reservations"""
        return self.available_stock > 0
    
    @property
    def is_in_stock(self):
        return self.stock_quantity > 0
    
    @property
    def is_low_stock(self):
        return self.stock_quantity <= self.low_stock_threshold
    
    @property
    def is_expired(self):
        return self.expiry_date < timezone.now().date()
    
    @property
    def days_to_expiry(self):
        return (self.expiry_date - timezone.now().date()).days

# Wishlist model
class WishlistItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'product']

    def __str__(self):
        return f"{self.user.username}'s wishlist item: {self.product.name}"

# SaveForLater model
class SaveForLater(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'product')

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Cart for {self.user.email}"
    
    @property
    def total_items(self):
        return sum([item.quantity for item in self.items.all()])
    
    @property
    def total_price(self):
        return sum([item.total_price for item in self.items.all()])

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('cart', 'product')
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
    
    @property
    def total_price(self):
        return self.quantity * self.product.price

class RefillSuggestion(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='refill_suggestions')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    suggested_date = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'product')

class InventoryAlert(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    alert_type = models.CharField(max_length=20, choices=[('low_stock', 'Low Stock'), ('expiry', 'Expiry')])
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.alert_type} alert for {self.product.name}"

class Subscription(models.Model):
    FREQUENCY_CHOICES = [
        ('weekly', 'Weekly'),
        ('biweekly', 'Biweekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES)
    next_delivery = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    reserved_stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.user} - {self.product} ({self.frequency})"

    def save(self, *args, **kwargs):
        # Store old active state if this is an existing subscription
        old_active = None
        if self.pk:
            old_instance = Subscription.objects.get(pk=self.pk)
            old_active = old_instance.is_active

        # Calculate reserved stock for new subscriptions or status changes
        if not self.pk or (old_active is not None and old_active != self.is_active):
            if self.is_active:
                # Reserve stock for next 3 deliveries
                self.reserved_stock = self.quantity * 3
            else:
                # Release reserved stock when cancelled
                self.reserved_stock = 0

        # Save the subscription
        super().save(*args, **kwargs)

        # Always update product stock after saving
        if hasattr(self, 'product'):
            self.product.update_stock_quantity()
    
    def calculate_next_deliveries(self, num_dates=5):
        """Calculate the next delivery dates based on frequency."""
        dates = []
        current_date = self.next_delivery
        
        for _ in range(num_dates):
            dates.append(current_date)
            if self.frequency == 'weekly':
                current_date = current_date + timedelta(days=7)
            elif self.frequency == 'biweekly':
                current_date = current_date + timedelta(days=14)
            elif self.frequency == 'monthly':
                # Add one month (approximately)
                current_date = current_date + timedelta(days=30)
            elif self.frequency == 'yearly':
                # Add one year
                current_date = current_date + timedelta(days=365)
        
        return dates

    def update_stock_reservation(self):
        """Update the product's reserved stock."""
        if self.is_active:
            # Reserve stock for the next 3 deliveries
            self.reserved_stock = self.quantity * 3
            self.save()
            # Update product's available stock
            self.product.update_stock_quantity()
        else:
            # Release reserved stock when subscription is cancelled
            old_reserved = self.reserved_stock
            self.reserved_stock = 0
            self.save()
            # Update product's available stock
            self.product.update_stock_quantity()

    def save(self, *args, **kwargs):
        # Update stock reservation when subscription status changes
        if self.pk:
            old_instance = Subscription.objects.get(pk=self.pk)
            status_changed = old_instance.is_active != self.is_active
        else:
            status_changed = True
        
        super().save(*args, **kwargs)
        
        if status_changed:
            self.update_stock_reservation()
