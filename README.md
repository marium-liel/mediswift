# Medicine & Supplement Ordering Platform

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

### 🔔 Smart Features
- Automatic refill suggestions based on purchase history
- Stock availability checking
- Expired product prevention
- Email notifications (configurable)

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

## Installation & Setup

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment configuration:**
   ```bash
   copy .env.example .env
   # Edit .env file with your settings
   ```

5. **Database setup:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create superuser:**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run development server:**
   ```bash
   python manage.py runserver
   ```

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start development server:**
   ```bash
   npm start
   ```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Admin Panel: http://localhost:8000/admin

## API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `GET/PUT /api/auth/profile/` - User profile management

### Products
- `GET /api/products/` - List products with filters
- `GET /api/products/{id}/` - Product details
- `GET /api/products/categories/` - List categories
- `GET /api/products/cart/` - Get user cart
- `POST /api/products/cart/add/` - Add to cart

### Orders
- `GET /api/orders/` - List user orders
- `GET /api/orders/{id}/` - Order details
- `POST /api/orders/create/` - Create new order
- `POST /api/orders/{id}/reorder/` - Reorder items

### Reviews
- `GET /api/reviews/product/{id}/` - Product reviews
- `POST /api/reviews/create/` - Create review
- `GET /api/reviews/my-reviews/` - User's reviews

### Admin Endpoints
- `GET /api/products/admin/low-stock/` - Low stock products
- `GET /api/products/admin/expiring/` - Expiring products
- `POST /api/orders/{id}/update-status/` - Update order status

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

## Key Features Implementation

### 1. Authentication System
- JWT tokens with refresh mechanism
- Protected routes and API endpoints
- Role-based permissions

### 2. Product Management
- Advanced filtering and search
- Stock management with alerts
- Expiry date tracking
- Image upload support

### 3. Shopping Cart
- Persistent cart storage
- Real-time stock validation
- Quantity management
- Price calculations

### 4. Order Processing
- Multi-step checkout process
- Order status tracking
- Email notifications
- Receipt generation

### 5. Admin Dashboard
- Real-time statistics
- Inventory alerts
- Order management
- User management

## Security Features

- JWT token authentication
- CORS protection
- Input validation and sanitization
- SQL injection prevention
- XSS protection
- CSRF protection

## Deployment

### Backend Deployment
1. Set `DEBUG=False` in production
2. Configure allowed hosts
3. Set up PostgreSQL database
4. Configure static file serving
5. Set up email backend

### Frontend Deployment
1. Build production bundle: `npm run build`
2. Deploy to static hosting (Netlify, Vercel, etc.)
3. Update API base URL for production

## Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions, please contact the development team or create an issue in the repository.

---

**MediSwift Platform** - Your Health, Our Priority 🏥💊
