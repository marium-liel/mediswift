# MediSwift

A comprehensive full-stack web application for ordering medicines and supplements online, built with Django REST Framework backend and React frontend.

## Features

### 🔐 User & Admin Authentication
- Secure JWT-based authentication
- Role-based access control (Customer vs Admin)
- User profile management
- Password change functionality

### 🛍️ Product Catalog & Search
- Browse medicines & supplements with advanced filters
- Search by name, brand, category
- Product details with dosage, precautions, and expiry information
- Product ratings and reviews system

### 🛒 Shopping Cart & Checkout
- Add/update/remove items from cart
- Persistent cart storage
- Secure checkout process with multiple payment options
- Order confirmation and receipt generation

### 📦 Order Management
- Real-time order tracking (Pending → Approved → Shipped → Delivered)
- Order history with detailed information
- One-click reorder functionality
- Admin order status management

### 📊 Admin Dashboard
- Inventory management with low-stock alerts
- Expiry date tracking and notifications
- Order management and status updates
- Sales reporting and analytics


## Tech Stack

### Backend
- **Django 4.2** - Web framework
- **Django REST Framework** - API development
- **JWT Authentication** - Secure token-based auth
- **SQLite** - Database (easily configurable to PostgreSQL)
- **Django CORS Headers** - Cross-origin requests
- **Pillow** - Image handling

### Frontend
- **React 18** - UI framework
- **React Router** - Client-side routing
- **Axios** - HTTP client
- **Context API** - State management
- **Tailwind CSS** - Styling framework


## Project Structure

```
Medicine/
├── backend/
│   ├── accounts/          # User authentication & profiles
│   ├── products/          # Product catalog & cart
│   ├── orders/           # Order management
│   ├── reviews/          # Rating & review system
│   ├── medicine_platform/ # Django settings
│   ├── manage.py
│   └── requirements.txt
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/   # Reusable components
│   │   ├── context/      # React context providers
│   │   ├── pages/        # Page components
│   │   ├── App.js
│   │   └── index.js
│   └── package.json
└── README.md
```
