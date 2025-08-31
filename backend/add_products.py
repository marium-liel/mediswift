import os
import django
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medicine_platform.settings')
django.setup()

from products.models import Category, Product

# Ensure at least one category exists
category, _ = Category.objects.get_or_create(name='General', defaults={'description': 'General medicines'})

products_data = [
    {
        'name': f'Medicine {i}',
        'brand': f'Brand {i % 5}',
        'category': category,
        'product_type': 'medicine',
        'description': f'Description for Medicine {i}',
        'dosage': '500mg',
        'precautions': 'None',
        'price': 10.0 + i,
        'stock_quantity': 50 + i,
        'low_stock_threshold': 10,
        'expiry_date': date.today() + timedelta(days=365 + i),
        'is_active': True,
        'requires_prescription': False,
    } for i in range(1, 21)
]

for pdata in products_data:
    Product.objects.get_or_create(name=pdata['name'], defaults=pdata)

print('Added at least 20 products to the database.')
