# Medicine Ordering Platform

A web platform for easy ordering of medicines and supplements built with Django and MySQL.

## Features

1. **Admin and User Registration & Login**
   - Secure user and admin account creation
   - Profile management
   - Role-based access control

2. **Search and Browse Medicines/Supplements**
   - Search by name, category, or brand
   - Filter by price, type, availability
   - Advanced search functionality

3. **Product Catalogue**
   - Detailed product listings
   - Product descriptions, dosage, precautions
   - Price and availability information
   - Product images

4. **Shopping Cart & Checkout**
   - Add, update, remove items from cart
   - Secure checkout process
   - Order tracking

## Technology Stack

- **Backend**: Django 4.2.7
- **Database**: MySQL (via phpMyAdmin)
- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **Authentication**: Django's built-in authentication system

## Setup Instructions

1. **Install Python Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Database Setup**
   - Create a MySQL database named `medicine_platform`
   - Configure database settings in `medicine_platform/settings.py`

3. **Run Migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. **Create Superuser**
   ```bash
   python manage.py createsuperuser
   ```

5. **Run Development Server**
   ```bash
   python manage.py runserver
   ```

6. **Access the Application**
   - Main site: http://localhost:8000
   - Admin panel: http://localhost:8000/admin

## Project Structure

```
medicine_platform/
├── manage.py
├── medicine_platform/          # Main project settings
├── accounts/                  # User authentication
├── products/                  # Product management
├── cart/                      # Shopping cart functionality
├── orders/                    # Order management
└── templates/                 # HTML templates
```

## Database Configuration

The project uses MySQL database. Make sure to:
1. Install MySQL server
2. Create a database named `medicine_platform`
3. Update database credentials in settings.py
4. Run migrations to create tables

## Features Implementation

- **User Authentication**: Custom user model with role-based permissions
- **Product Management**: CRUD operations for medicines and supplements
- **Search & Filter**: Advanced search with multiple criteria
- **Shopping Cart**: Session-based cart with persistent storage
- **Order System**: Complete order lifecycle management 