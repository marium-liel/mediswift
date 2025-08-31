from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('customer', 'Customer'),
        ('admin', 'Admin'),
    )
    
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='customer')
    date_of_birth = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def __str__(self):
        return self.email
    

    @property
    def is_admin(self):
        return self.user_type == 'admin'

    def save(self, *args, **kwargs):
        # Set user_type to 'admin' if user is superuser or staff
        if self.is_superuser or self.is_staff:
            self.user_type = 'admin'
        super().save(*args, **kwargs)
        
        # Ensure superusers are also staff users
        if self.is_superuser and not self.is_staff:
            self.is_staff = True
            super().save(update_fields=['is_staff'])
