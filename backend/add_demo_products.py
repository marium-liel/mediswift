"""
DJANGO DEMO PRODUCTS SCRIPT - DATABASE POPULATION UTILITY

This Python script demonstrates Django database operations and model management.
It's used to populate the MediSwift platform with sample product data for testing and development.

KEY DJANGO CONCEPTS DEMONSTRATED:
1. Django Setup - Configuring Django environment outside of web server
2. Model Operations - Creating and querying Django ORM models
3. Database Relationships - Foreign key relationships between models
4. Bulk Data Creation - Efficiently populating database with sample data
5. get_or_create() Pattern - Avoiding duplicate records during data import

DJANGO ORM (Object-Relational Mapping):
- Translates Python objects to database records
- Handles SQL queries automatically
- Manages relationships between database tables
- Provides data validation and constraints

This script is typically run via: python add_demo_products.py
"""

# Standard Python imports for environment and date handling
import os
import django
from datetime import date, timedelta

# DJANGO ENVIRONMENT SETUP
# This is required when running Django code outside of the web server context
# It tells Django which settings file to use and initializes the Django application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medicine_platform.settings')
django.setup()

# Note: The duplicate lines below are likely from copy-paste error, but harmless
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medicine_platform.settings')
django.setup()

# DJANGO MODEL IMPORTS
# Import the Django models we'll be working with
# These represent database tables in the PostgreSQL/SQLite database
from products.models import Category, Product

"""
CATEGORY CREATION - ESTABLISHING PRODUCT CATEGORIES

Categories in Django represent a one-to-many relationship:
- One category can have many products
- Each product belongs to one category
- This is implemented as a ForeignKey in the Product model
"""

# Define categories as tuples: (name, description)
categories = [
    ('Pain Relief', 'Pain relief medicines'),
    ('Supplements', 'Vitamins and supplements'),
    ('Allergy', 'Allergy relief medicines'),
    ('Digestive', 'Digestive health'),
]

# Dictionary to store created category objects for later reference
cat_objs = {}

# CREATE CATEGORIES USING get_or_create() PATTERN
for name, desc in categories:
    """
    get_or_create() is a Django ORM method that:
    1. Tries to find an existing record with the given criteria
    2. If found, returns the existing object
    3. If not found, creates a new object with the provided defaults
    4. Returns tuple: (object, created_boolean)
    
    This prevents duplicate records when running the script multiple times.
    """
    cat, created = Category.objects.get_or_create(
        name=name,                    # Search criteria
        defaults={'description': desc} # Values to use if creating new record
    )
    cat_objs[name] = cat  # Store reference for use in product creation

"""
PRODUCT CREATION - POPULATING MEDICINE INVENTORY

Each product dictionary contains all the fields defined in the Product model:
- Basic info: name, brand, description
- Pricing: price
- Inventory: stock_quantity, reserved_quantity, low_stock_threshold
- Medical info: dosage, precautions, requires_prescription
- Categorization: category (foreign key), product_type
- Status: is_active, expiry_date

This demonstrates Django model field types:
- CharField: name, brand, description
- DecimalField: price
- IntegerField: stock quantities
- DateField: expiry_date
- BooleanField: is_active, requires_prescription
- ForeignKey: category (relationship to Category model)
"""

products = [
    # PAIN RELIEF CATEGORY - Demonstrates medical product data structure
    {
        'name': 'Paracetamol 500mg',
        'brand': 'MediCure',  # Note: This was updated from 'MediCare' to 'MediSwift' in previous changes
        'category': cat_objs['Pain Relief'],  # Foreign key relationship
        'product_type': 'medicine',
        'description': 'Used for pain and fever.',
        'dosage': '500mg',
        'precautions': 'Do not exceed recommended dose.',
        'price': 2.99,  # DecimalField for precise currency handling
        'stock_quantity': 100,
        'reserved_quantity': 0,  # For subscription/order reservations
        'low_stock_threshold': 10,  # Inventory management
        'expiry_date': date.today() + timedelta(days=365),  # Dynamic date calculation
        'is_active': True,
        'requires_prescription': False
    },
    {
        'name': 'Ibuprofen 200mg',
        'brand': 'HealFast',
        'category': cat_objs['Pain Relief'],
        'product_type': 'medicine',
        'description': 'Anti-inflammatory painkiller.',
        'dosage': '200mg',
        'precautions': 'Take with food.',
        'price': 3.49,
        'stock_quantity': 80,
        'reserved_quantity': 0,
        'low_stock_threshold': 10,
        'expiry_date': date.today() + timedelta(days=400),
        'is_active': True,
        'requires_prescription': False
    },
    {
        'name': 'Aspirin 100mg',
        'brand': 'PainAway',
        'category': cat_objs['Pain Relief'],
        'product_type': 'medicine',
        'description': 'Pain and inflammation relief.',
        'dosage': '100mg',
        'precautions': 'Not for children.',
        'price': 2.49,
        'stock_quantity': 60,
        'reserved_quantity': 0,
        'low_stock_threshold': 8,
        'expiry_date': date.today() + timedelta(days=300),
        'is_active': True,
        'requires_prescription': False
    },
    {
        'name': 'Diclofenac Gel',
        'brand': 'FlexiGel',
        'category': cat_objs['Pain Relief'],
        'product_type': 'medicine',
        'description': 'Topical pain relief gel.',
        'dosage': '1%',
        'precautions': 'External use only.',
        'price': 4.99,
        'stock_quantity': 40,
        'reserved_quantity': 0,
        'low_stock_threshold': 5,
        'expiry_date': date.today() + timedelta(days=200),
        'is_active': True,
        'requires_prescription': False
    },
    {
        'name': 'Naproxen 250mg',
        'brand': 'ReliefX',
        'category': cat_objs['Pain Relief'],
        'product_type': 'medicine',
        'description': 'Long-lasting pain relief.',
        'dosage': '250mg',
        'precautions': 'Take with water.',
        'price': 3.99,
        'stock_quantity': 70,
        'reserved_quantity': 0,
        'low_stock_threshold': 7,
        'expiry_date': date.today() + timedelta(days=350),
        'is_active': True,
        'requires_prescription': False
    },
    
    # SUPPLEMENTS CATEGORY - Demonstrates different product type
    {
        'name': 'Vitamin C Tablets',
        'brand': 'NutriPlus',
        'category': cat_objs['Supplements'],
        'product_type': 'supplement',  # Different product type
        'description': 'Boosts immunity.',
        'dosage': '1000mg',
        'precautions': 'Store in a cool place.',
        'price': 5.99,
        'stock_quantity': 50,
        'reserved_quantity': 0,
        'low_stock_threshold': 5,
        'expiry_date': date.today() + timedelta(days=500),
        'is_active': True,
        'requires_prescription': False
    },
    {
        'name': 'Calcium + D3',
        'brand': 'BoneCare',
        'category': cat_objs['Supplements'],
        'product_type': 'supplement',
        'description': 'For bone health.',
        'dosage': '500mg',
        'precautions': 'Take after meals.',
        'price': 6.49,
        'stock_quantity': 45,
        'reserved_quantity': 0,
        'low_stock_threshold': 5,
        'expiry_date': date.today() + timedelta(days=600),
        'is_active': True,
        'requires_prescription': False
    },
    {
        'name': 'Multivitamin',
        'brand': 'VitaMax',
        'category': cat_objs['Supplements'],
        'product_type': 'supplement',
        'description': 'Daily multivitamin.',
        'dosage': '1 tablet',
        'precautions': 'Do not exceed daily dose.',
        'price': 7.99,
        'stock_quantity': 80,
        'reserved_quantity': 0,
        'low_stock_threshold': 8,
        'expiry_date': date.today() + timedelta(days=700),
        'is_active': True,
        'requires_prescription': False
    },
    {
        'name': 'Zinc Tablets',
        'brand': 'ImmunoZ',
        'category': cat_objs['Supplements'],
        'product_type': 'supplement',
        'description': 'Supports immune system.',
        'dosage': '50mg',
        'precautions': 'Take with food.',
        'price': 4.49,
        'stock_quantity': 60,
        'reserved_quantity': 0,
        'low_stock_threshold': 6,
        'expiry_date': date.today() + timedelta(days=400),
        'is_active': True,
        'requires_prescription': False
    },
    {
        'name': 'Omega-3 Fish Oil',
        'brand': 'HeartPlus',
        'category': cat_objs['Supplements'],
        'product_type': 'supplement',
        'description': 'Supports heart health.',
        'dosage': '1000mg',
        'precautions': 'Store in a cool place.',
        'price': 8.99,
        'stock_quantity': 30,
        'reserved_quantity': 0,
        'low_stock_threshold': 3,
        'expiry_date': date.today() + timedelta(days=800),
        'is_active': True,
        'requires_prescription': False
    },
    
    # ALLERGY CATEGORY - More medicine examples
    {
        'name': 'Cetirizine 10mg',
        'brand': 'AllerFree',
        'category': cat_objs['Allergy'],
        'product_type': 'medicine',
        'description': 'Allergy relief.',
        'dosage': '10mg',
        'precautions': 'May cause drowsiness.',
        'price': 2.99,
        'stock_quantity': 90,
        'reserved_quantity': 0,
        'low_stock_threshold': 9,
        'expiry_date': date.today() + timedelta(days=365),
        'is_active': True,
        'requires_prescription': False
    },
    {
        'name': 'Loratadine 10mg',
        'brand': 'ClearAll',
        'category': cat_objs['Allergy'],
        'product_type': 'medicine',
        'description': 'Non-drowsy allergy relief.',
        'dosage': '10mg',
        'precautions': 'Do not exceed daily dose.',
        'price': 3.29,
        'stock_quantity': 85,
        'reserved_quantity': 0,
        'low_stock_threshold': 8,
        'expiry_date': date.today() + timedelta(days=400),
        'is_active': True,
        'requires_prescription': False
    },
    {
        'name': 'Fexofenadine 120mg',
        'brand': 'AllergyX',
        'category': cat_objs['Allergy'],
        'product_type': 'medicine',
        'description': 'Seasonal allergy relief.',
        'dosage': '120mg',
        'precautions': 'Take with water.',
        'price': 4.99,
        'stock_quantity': 70,
        'reserved_quantity': 0,
        'low_stock_threshold': 7,
        'expiry_date': date.today() + timedelta(days=450),
        'is_active': True,
        'requires_prescription': False
    },
    {
        'name': 'Montelukast 10mg',
        'brand': 'MontiCare',
        'category': cat_objs['Allergy'],
        'product_type': 'medicine',
        'description': 'Asthma and allergy relief.',
        'dosage': '10mg',
        'precautions': 'Take in the evening.',
        'price': 5.49,
        'stock_quantity': 60,
        'reserved_quantity': 0,
        'low_stock_threshold': 6,
        'expiry_date': date.today() + timedelta(days=500),
        'is_active': True,
        'requires_prescription': False
    },
    {
        'name': 'Chlorpheniramine 4mg',
        'brand': 'ChloroTab',
        'category': cat_objs['Allergy'],
        'product_type': 'medicine',
        'description': 'Relief from sneezing and runny nose.',
        'dosage': '4mg',
        'precautions': 'May cause drowsiness.',
        'price': 2.49,
        'stock_quantity': 50,
        'reserved_quantity': 0,
        'low_stock_threshold': 5,
        'expiry_date': date.today() + timedelta(days=300),
        'is_active': True,
        'requires_prescription': False
    },
    
    # DIGESTIVE CATEGORY - Final category examples
    {
        'name': 'Omeprazole 20mg',
        'brand': 'AcidEase',
        'category': cat_objs['Digestive'],
        'product_type': 'medicine',
        'description': 'Reduces stomach acid.',
        'dosage': '20mg',
        'precautions': 'Take before meals.',
        'price': 3.99,
        'stock_quantity': 75,
        'reserved_quantity': 0,
        'low_stock_threshold': 7,
        'expiry_date': date.today() + timedelta(days=365),
        'is_active': True,
        'requires_prescription': False
    },
    {
        'name': 'Loperamide 2mg',
        'brand': 'StopDia',
        'category': cat_objs['Digestive'],
        'product_type': 'medicine',
        'description': 'Relieves diarrhea.',
        'dosage': '2mg',
        'precautions': 'Do not exceed recommended dose.',
        'price': 2.99,
        'stock_quantity': 60,
        'reserved_quantity': 0,
        'low_stock_threshold': 6,
        'expiry_date': date.today() + timedelta(days=400),
        'is_active': True,
        'requires_prescription': False
    },
    {
        'name': 'Domperidone 10mg',
        'brand': 'MotilEase',
        'category': cat_objs['Digestive'],
        'product_type': 'medicine',
        'description': 'Relieves nausea and vomiting.',
        'dosage': '10mg',
        'precautions': 'Take before meals.',
        'price': 3.49,
        'stock_quantity': 55,
        'reserved_quantity': 0,
        'low_stock_threshold': 5,
        'expiry_date': date.today() + timedelta(days=350),
        'is_active': True,
        'requires_prescription': False
    },
    {
        'name': 'ORS Sachets',
        'brand': 'HydraPlus',
        'category': cat_objs['Digestive'],
        'product_type': 'supplement',  # Mixed category - supplement in digestive
        'description': 'Oral rehydration salts.',
        'dosage': '1 sachet',
        'precautions': 'Dissolve in water.',
        'price': 1.99,
        'stock_quantity': 100,
        'reserved_quantity': 0,
        'low_stock_threshold': 10,
        'expiry_date': date.today() + timedelta(days=500),
        'is_active': True,
        'requires_prescription': False
    },
    {
        'name': 'Probiotic Capsules',
        'brand': 'GutHealth',
        'category': cat_objs['Digestive'],
        'product_type': 'supplement',
        'description': 'Supports digestive health.',
        'dosage': '1 capsule',
        'precautions': 'Store in a cool place.',
        'price': 6.99,
        'stock_quantity': 40,
        'reserved_quantity': 0,
        'low_stock_threshold': 4,
        'expiry_date': date.today() + timedelta(days=600),
        'is_active': True,
        'requires_prescription': False
    },
]

"""
BULK PRODUCT CREATION - POPULATING DATABASE

This loop creates all products using the get_or_create() pattern:
1. Iterates through the products list
2. For each product dictionary, tries to find existing product by name
3. If not found, creates new product with all the provided data
4. If found, skips creation (prevents duplicates)

This demonstrates Django ORM bulk operations and database efficiency.
"""

for prod in products:
    """
    get_or_create() for Product model:
    - name: Used as the unique identifier (search criteria)
    - defaults=prod: All product data used if creating new record
    
    The ** operator unpacks the dictionary, so prod becomes individual keyword arguments.
    This is equivalent to: Product.objects.get_or_create(name=prod['name'], defaults=prod)
    """
    Product.objects.get_or_create(name=prod['name'], defaults=prod)

# SUCCESS MESSAGE - Confirmation of script completion
print('20+ demo products added!')

"""
SCRIPT EXECUTION SUMMARY:

This script demonstrates several Django concepts:

1. ENVIRONMENT SETUP: Configuring Django outside web context
2. MODEL RELATIONSHIPS: Foreign keys between Category and Product
3. ORM OPERATIONS: Using get_or_create() for safe data insertion
4. DATA MODELING: Comprehensive product data structure
5. BULK OPERATIONS: Efficiently creating multiple database records
6. DATE HANDLING: Dynamic expiry date calculation
7. DATA INTEGRITY: Preventing duplicate records

When you run this script, it:
- Creates 4 product categories
- Creates 20+ products across different categories
- Establishes relationships between products and categories
- Populates all required fields for the medicine platform
- Can be run multiple times without creating duplicates

This is typical for Django data migration or seeding scripts used in development and testing.
"""
