# MediSwift - Advanced Medicine Ordering Platform

A comprehensive web platform for easy ordering of medicines and supplements built with Django, featuring smart refills, medicine reminders, subscriptions, and advanced user management.

## 🚀 Features

### 1. **Advanced User Authentication & Management**
   - Secure user and admin account creation
   - Profile management with additional fields
   - Role-based access control (user/admin)
   - User dashboard with personalized features

### 2. **Smart Product Search & Discovery**
   - Advanced search by name, category, brand, or description
   - Filter by price range, product type, availability
   - Sort by name, price, newest, or rating
   - Pagination for large product catalogs
   - Category-based browsing

### 3. **Comprehensive Product Management**
   - Detailed product listings with images
   - Product descriptions, dosage, precautions
   - Price and availability information
   - Sale prices with discount calculations
   - Featured products on homepage
   - Admin product management interface

### 4. **Advanced Shopping Cart & Checkout**
   - Add, update, remove items from cart
   - Quantity validation against stock
   - Secure checkout process
   - Order tracking with status updates
   - Real-time cart updates

### 5. **Complete Order Management System**
   - Complete checkout process with shipping information
   - Payment method selection (Cash on Delivery, Credit Card, etc.)


### 6. **Smart Refill System** 🔄
   - **Automated notifications** based on past purchase patterns
   - **One-click reorder** for recurring medications
   - Calculates estimated refill dates using purchase history
   - Tracks refill due dates and notifications
   - Smart refill dashboard for users
   - Intelligent refill date calculation algorithm

### 7. **Medicine Reminders** ⏰
   - **Set daily/weekly/monthly reminders** for medications
   - **Email, SMS, or push notifications**
   - Custom reminder times and frequencies
   - Reminder management (add, edit, delete, toggle)
   - Medicine reminder dashboard
   - Next reminder calculation

### 8. **Subscription & Auto-Reorder System** 📅
   - **Subscribe for recurring orders** (weekly, bi-weekly, monthly, quarterly)
   - **Auto-billing and delivery setup**
   - Subscription management (pause, resume, cancel)
   - Automatic order creation based on schedule
   - Subscription status tracking

### 9. **Product Rating and Reviews** ⭐
   - Users can leave 1-5 star ratings for purchased products
   - Write detailed reviews with comments
   - View average ratings and review counts
   - Only purchasers can review products
   - Edit existing reviews
   - Review management system

### 10. **Wishlist Functionality** ❤️
   - **Add products to wishlist** for future purchase
   - **Move items from wishlist to cart**
   - **Remove items from wishlist**
   - Wishlist management dashboard
   - Wishlist analytics

### 11. **Admin Management Dashboard** 👨‍💼
   - **Add/Edit/Remove products** with comprehensive forms
   - Manage product categories
   - Update stock quantities and availability
   - Set featured products and sale prices
   - Upload product images
   - View product analytics and reviews
   - User and order management
   - Subscription and reminder management

### 12. **Enhanced User Experience** ✨
   - Responsive design with Bootstrap 5
   - Modern UI with hover effects and animations
   - Real-time cart updates
   - User-friendly navigation
   - Professional admin interface
   - Mobile-responsive design

## 🛠️ Technology Stack

- **Backend**: Django 4.2.7
- **Database**: SQLite (configurable to MySQL)
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **Forms**: Django Crispy Forms with Bootstrap 5
- **Authentication**: Django's built-in authentication system


## 📁 Project Structure

```
medicine_platform/
├── manage.py
├── medicine_platform/          # Main project settings
├── accounts/                  # User authentication & profiles
├── products/                  # Product management & reviews
├── cart/                      # Shopping cart functionality
├── orders/                    # Order management & smart refills
├── templates/                 # HTML templates
│   ├── accounts/             # Authentication templates
│   ├── products/             # Product-related templates
│   ├── orders/               # Order management templates
│   └── cart/                 # Shopping cart templates
└── static/                    # Static files (CSS, JS, images)
```




**MediSwift** - Making medicine ordering smart, simple, and secure! 💊✨ 