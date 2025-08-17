from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('user', 'User'),
        ('admin', 'Admin'),
    )
    
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='user')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    
    def is_admin(self):
        return self.user_type == 'admin'
    
    def __str__(self):
        return self.username 