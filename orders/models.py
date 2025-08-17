from django.db import models
from django.conf import settings
from products.models import Product
from datetime import datetime, timedelta

class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    order_number = models.CharField(max_length=20, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Shipping information
    shipping_address = models.TextField()
    shipping_city = models.CharField(max_length=100)
    shipping_state = models.CharField(max_length=100)
    shipping_zip_code = models.CharField(max_length=10)
    shipping_phone = models.CharField(max_length=15)
    
    # Payment information
    payment_method = models.CharField(max_length=50, default='Cash on Delivery')
    payment_status = models.CharField(max_length=20, default='pending')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order {self.order_number} - {self.user.username}"
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            # Generate order number
            import datetime
            now = datetime.datetime.now()
            self.order_number = f"ORD{now.strftime('%Y%m%d%H%M%S')}{self.user.id}"
        super().save(*args, **kwargs)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.quantity}x {self.product.name} - {self.order.order_number}"
    
    @property
    def total_price(self):
        return self.price * self.quantity

class SmartRefill(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    last_order_date = models.DateTimeField()
    estimated_refill_date = models.DateTimeField()
    is_notified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'product')
        ordering = ['-estimated_refill_date']
    
    def __str__(self):
        return f"Smart refill for {self.user.username} - {self.product.name}"
    
    @property
    def days_until_refill(self):
        return (self.estimated_refill_date - datetime.now()).days
    
    @property
    def is_due_for_refill(self):
        return self.estimated_refill_date <= datetime.now()

class MedicineReminder(models.Model):
    FREQUENCY_CHOICES = (
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('custom', 'Custom'),
    )
    
    NOTIFICATION_CHOICES = (
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('push', 'Push Notification'),
        ('all', 'All'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    reminder_name = models.CharField(max_length=100)
    dosage = models.CharField(max_length=50, blank=True)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='daily')
    custom_days = models.CharField(max_length=100, blank=True, help_text="Comma-separated days for custom frequency")
    reminder_time = models.TimeField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_CHOICES, default='email')
    is_active = models.BooleanField(default=True)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['reminder_time']
    
    def __str__(self):
        return f"{self.reminder_name} - {self.user.username}"
    
    @property
    def next_reminder(self):
        """Calculate next reminder date and time"""
        now = datetime.now()
        today = now.date()
        reminder_datetime = datetime.combine(today, self.reminder_time)
        
        if reminder_datetime <= now:
            # Reminder time has passed today, move to next occurrence
            if self.frequency == 'daily':
                reminder_datetime += timedelta(days=1)
            elif self.frequency == 'weekly':
                reminder_datetime += timedelta(days=7)
            elif self.frequency == 'monthly':
                reminder_datetime += timedelta(days=30)
            elif self.frequency == 'custom':
                # Handle custom days logic
                reminder_datetime += timedelta(days=1)
        
        return reminder_datetime

class Subscription(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
    )
    
    FREQUENCY_CHOICES = (
        ('weekly', 'Weekly'),
        ('biweekly', 'Bi-weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='monthly')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    start_date = models.DateTimeField(null=True, blank=True)
    next_delivery_date = models.DateTimeField(null=True, blank=True)
    expiry_date = models.DateTimeField(null=True, blank=True)
    auto_billing = models.BooleanField(default=True)
    payment_method = models.CharField(max_length=50, default='Cash on Delivery')
    shipping_address = models.TextField()
    shipping_city = models.CharField(max_length=100)
    shipping_state = models.CharField(max_length=100)
    shipping_zip_code = models.CharField(max_length=10)
    shipping_phone = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Subscription {self.id} - {self.user.username} - {self.product.name}"
    
    def save(self, *args, **kwargs):
        # Set start date if not provided
        if not self.start_date:
            self.start_date = datetime.now()
        
        # Set expiry date if not provided (1 year from start)
        if not self.expiry_date:
            self.expiry_date = self.start_date + timedelta(days=365)
        
        # Set initial next delivery date based on frequency and start date
        if not self.next_delivery_date:
            if self.frequency == 'weekly':
                self.next_delivery_date = self.start_date + timedelta(days=7)
            elif self.frequency == 'biweekly':
                self.next_delivery_date = self.start_date + timedelta(days=14)
            elif self.frequency == 'monthly':
                self.next_delivery_date = self.start_date + timedelta(days=30)
            elif self.frequency == 'quarterly':
                self.next_delivery_date = self.start_date + timedelta(days=90)
        
        # Check if subscription has expired
        if self.expiry_date and self.expiry_date <= datetime.now() and self.status == 'active':
            self.status = 'expired'
        
        super().save(*args, **kwargs)
    
    @property
    def days_until_next_delivery(self):
        return (self.next_delivery_date - datetime.now()).days
    
    @property
    def is_due_for_delivery(self):
        return self.next_delivery_date <= datetime.now() and self.status == 'active'
    
    @property
    def days_until_expiry(self):
        return (self.expiry_date - datetime.now()).days
    
    def process_auto_delivery(self):
        """Process automatic delivery for this subscription"""
        if self.is_due_for_delivery and self.status == 'active':
            # Check if next delivery would exceed expiry date
            next_delivery = None
            if self.frequency == 'weekly':
                next_delivery = self.next_delivery_date + timedelta(days=7)
            elif self.frequency == 'biweekly':
                next_delivery = self.next_delivery_date + timedelta(days=14)
            elif self.frequency == 'monthly':
                next_delivery = self.next_delivery_date + timedelta(days=30)
            elif self.frequency == 'quarterly':
                next_delivery = self.next_delivery_date + timedelta(days=90)
            
            # If next delivery would exceed expiry date, mark as expired
            if self.expiry_date and next_delivery and next_delivery > self.expiry_date:
                self.status = 'expired'
                self.save()
                return None
            
            # Create delivery record (simulated)
            delivery = AutoDelivery.objects.create(
                subscription=self,
                product=self.product,
                quantity=self.quantity,
                delivery_date=datetime.now(),
                status='delivered'
            )
            
            # Update next delivery date
            if self.frequency == 'weekly':
                self.next_delivery_date = self.next_delivery_date + timedelta(days=7)
            elif self.frequency == 'biweekly':
                self.next_delivery_date = self.next_delivery_date + timedelta(days=14)
            elif self.frequency == 'monthly':
                self.next_delivery_date = self.next_delivery_date + timedelta(days=30)
            elif self.frequency == 'quarterly':
                self.next_delivery_date = self.next_delivery_date + timedelta(days=90)
            
            self.save()
            return delivery
        return None

class AutoDelivery(models.Model):
    STATUS_CHOICES = (
        ('scheduled', 'Scheduled'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
    )
    
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name='deliveries')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    scheduled_date = models.DateTimeField()
    delivery_date = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    tracking_number = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-scheduled_date']
    
    def __str__(self):
        return f"Auto Delivery {self.id} - {self.subscription.user.username} - {self.product.name}" 