/*
 * ADMIN DASHBOARD COMPONENT - REACT ROUTING & COMPONENT COMPOSITION
 * 
 * This component demonstrates advanced React concepts:
 * 1. React Router - Client-side routing for single-page applications
 * 2. Component Composition - Using multiple components together
 * 3. Context API - Sharing authentication state across components
 * 4. Nested Routing - Routes within routes
 * 5. Dynamic Navigation - Active states and programmatic navigation
 * 
 * DJANGO INTEGRATION:
 * - Fetches admin statistics from Django REST API
 * - Uses JWT authentication for protected admin endpoints
 * - Displays real-time data from Django backend
 */

// React Router imports for navigation and routing
import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext'; // Custom hook for authentication
import { Routes, Route, Link, useNavigate, useLocation } from 'react-router-dom';

// Import child components that will be rendered in different routes
import OrdersManagement from './OrdersManagement';
import ProductsManagement from './ProductsManagement';
import UsersManagement from './UsersManagement';

const AdminDashboard = () => {
    /*
     * REACT CONTEXT API USAGE
     * 
     * useAuth is a custom hook that provides access to authentication context.
     * Context allows sharing state between components without prop drilling.
     * This gives us access to current user information across the app.
     */
    const { user } = useAuth();
    
    /*
     * REACT ROUTER HOOKS
     * 
     * useNavigate: Programmatically navigate to different routes
     * useLocation: Get current route information (pathname, search, etc.)
     * These hooks provide access to React Router's navigation system
     */
    const navigate = useNavigate();
    const location = useLocation();
    
    // State for loading indicator and dashboard statistics
    const [loading, setLoading] = useState(true);
    const [stats, setStats] = useState({
        totalOrders: 0,
        totalProducts: 0,
        totalUsers: 0,
        recentOrders: [],
        recentProducts: []
    });

    /*
     * COMPONENT LIFECYCLE - FETCH ADMIN STATISTICS
     * 
     * This useEffect runs when component mounts to fetch dashboard data
     * from Django backend. Shows integration between React frontend and
     * Django REST API for admin functionality.
     */
    useEffect(() => {
        const fetchAdminStats = async () => {
            try {
                // Call Django admin stats endpoint
                const response = await fetch('/api/accounts/admin/stats/', {
                    headers: {
                        // JWT token for admin authentication
                        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                    }
                });
                
                if (response.ok) {
                    const data = await response.json();
                    // Update component state with fetched statistics
                    setStats(data);
                }
            } catch (error) {
                // Silent error handling - could implement user notification
            } finally {
                // Always stop loading, whether success or error
                setLoading(false);
            }
        };

        fetchAdminStats();
    }, []); // Empty dependency array - run once on component mount

    // Loading state - show spinner while fetching data
    if (loading) {
        return (
            <div className="flex justify-center items-center min-h-screen">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
        );
    }

    /*
     * NESTED COMPONENT DEFINITION - OVERVIEW DASHBOARD
     * 
     * This is a component defined inside another component.
     * It's used for the main dashboard overview that shows statistics.
     * This demonstrates component composition and local component definition.
     */
    const Overview = () => (
        <div className="space-y-6">
            {/* STATISTICS CARDS - Display data from Django backend */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* Each card shows different metrics from the stats state */}
                <div className="bg-white rounded-lg shadow p-6">
                    <h3 className="text-lg font-semibold text-gray-700">Total Orders</h3>
                    {/* Dynamic content from state - shows real Django data */}
                    <p className="text-3xl font-bold text-blue-600 mt-2">{stats.totalOrders}</p>
                    <p className="text-sm text-gray-500 mt-2">Last 30 days</p>
                </div>
                <div className="bg-white rounded-lg shadow p-6">
                    <h3 className="text-lg font-semibold text-gray-700">Total Products</h3>
                    <p className="text-3xl font-bold text-green-600 mt-2">{stats.totalProducts}</p>
                    <p className="text-sm text-gray-500 mt-2">In inventory</p>
                </div>
                <div className="bg-white rounded-lg shadow p-6">
                    <h3 className="text-lg font-semibold text-gray-700">Total Users</h3>
                    <p className="text-3xl font-bold text-purple-600 mt-2">{stats.totalUsers}</p>
                    <p className="text-sm text-gray-500 mt-2">Registered users</p>
                </div>
            </div>

            {/* RECENT DATA TABLES - Show recent orders and products */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* RECENT ORDERS TABLE */}
                <div className="bg-white rounded-lg shadow p-6">
                    <div className="flex justify-between items-center mb-4">
                        <h2 className="text-xl font-semibold text-gray-800">Recent Orders</h2>
                        {/* PROGRAMMATIC NAVIGATION - Navigate to orders page */}
                        <button 
                            onClick={() => navigate('/admin/orders')} // useNavigate hook in action
                            className="text-blue-600 hover:text-blue-800"
                        >
                            View All
                        </button>
                    </div>
                    <div className="overflow-x-auto">
                        <table className="min-w-full divide-y divide-gray-200">
                            <thead>
                                <tr>
                                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Order ID</th>
                                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Customer</th>
                                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Amount</th>
                                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-200">
                                {/* ARRAY MAPPING - Render each order from Django data */}
                                {stats.recentOrders.map(order => (
                                    <tr key={order.id} className="hover:bg-gray-50">
                                        <td className="px-4 py-3 text-sm text-gray-900">#{order.id}</td>
                                        <td className="px-4 py-3 text-sm text-gray-900">{order.customer_name}</td>
                                        <td className="px-4 py-3 text-sm text-gray-900">${order.total_amount}</td>
                                        <td className="px-4 py-3">
                                            {/* CONDITIONAL STYLING - Different colors based on order status */}
                                            <span className={`px-2 py-1 text-xs rounded-full ${
                                                order.status === 'completed' ? 'bg-green-100 text-green-800' :
                                                order.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                                                'bg-gray-100 text-gray-800'
                                            }`}>
                                                {order.status}
                                            </span>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>

                {/* RECENT PRODUCTS LIST */}
                <div className="bg-white rounded-lg shadow p-6">
                    <div className="flex justify-between items-center mb-4">
                        <h2 className="text-xl font-semibold text-gray-800">Recent Products</h2>
                        <button 
                            onClick={() => navigate('/admin/products')}
                            className="text-blue-600 hover:text-blue-800"
                        >
                            View All
                        </button>
                    </div>
                    <div className="space-y-4">
                        {/* PRODUCT CARDS - Display recent products from Django */}
                        {stats.recentProducts.map(product => (
                            <div key={product.id} className="flex items-center space-x-4 p-4 hover:bg-gray-50 rounded">
                                <img 
                                    src={product.image} 
                                    alt={product.name}
                                    className="w-12 h-12 object-cover rounded"
                                />
                                <div className="flex-1">
                                    <h3 className="text-sm font-medium text-gray-900">{product.name}</h3>
                                    <p className="text-sm text-gray-500">${product.price}</p>
                                </div>
                                <div className="text-sm text-gray-500">
                                    Stock: {product.stock}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );

    /*
     * MAIN COMPONENT RENDER WITH REACT ROUTER
     * 
     * This demonstrates:
     * 1. Navigation menu with active states
     * 2. Nested routing with Routes and Route components
     * 3. Dynamic styling based on current route
     * 4. Component composition (rendering different components based on route)
     */
    return (
        <div className="min-h-screen bg-gray-100 p-6">
            <div className="max-w-7xl mx-auto">
                {/* DASHBOARD HEADER */}
                <div className="mb-8">
                    <h1 className="text-2xl font-bold text-gray-900">Admin Dashboard</h1>
                    
                    {/* NAVIGATION MENU - React Router Links */}
                    <div className="mt-4 flex space-x-4">
                        {/* 
                         * DYNAMIC NAVIGATION WITH ACTIVE STATES
                         * 
                         * Each Link component uses useLocation to determine if it's active.
                         * Active links get different styling to show current page.
                         * This creates a tab-like navigation experience.
                         */}
                        <Link 
                            to="/admin"
                            className={`px-4 py-2 rounded-lg ${
                                location.pathname === '/admin' 
                                ? 'bg-blue-600 text-white'  // Active state styling
                                : 'bg-white text-gray-600 hover:bg-gray-50' // Inactive state styling
                            }`}
                        >
                            Overview
                        </Link>
                        <Link 
                            to="/admin/orders"
                            className={`px-4 py-2 rounded-lg ${
                                location.pathname === '/admin/orders' 
                                ? 'bg-blue-600 text-white' 
                                : 'bg-white text-gray-600 hover:bg-gray-50'
                            }`}
                        >
                            Orders
                        </Link>
                        <Link 
                            to="/admin/products"
                            className={`px-4 py-2 rounded-lg ${
                                location.pathname === '/admin/products' 
                                ? 'bg-blue-600 text-white' 
                                : 'bg-white text-gray-600 hover:bg-gray-50'
                            }`}
                        >
                            Products
                        </Link>
                        <Link 
                            to="/admin/users"
                            className={`px-4 py-2 rounded-lg ${
                                location.pathname === '/admin/users' 
                                ? 'bg-blue-600 text-white' 
                                : 'bg-white text-gray-600 hover:bg-gray-50'
                            }`}
                        >
                            Users
                        </Link>
                    </div>
                </div>

                {/* 
                 * NESTED ROUTING - ROUTES WITHIN ROUTES
                 * 
                 * This Routes component handles sub-routes within the admin dashboard.
                 * Each Route renders a different component based on the URL path.
                 * This allows for a single-page application with multiple views.
                 * 
                 * Route paths are relative to the parent route (/admin)
                 */}
                <Routes>
                    <Route path="/" element={<Overview />} />                    {/* /admin */}
                    <Route path="/orders" element={<OrdersManagement />} />      {/* /admin/orders */}
                    <Route path="/products" element={<ProductsManagement />} />  {/* /admin/products */}
                    <Route path="/users" element={<UsersManagement />} />        {/* /admin/users */}
                </Routes>
            </div>
        </div>
    );
};

export default AdminDashboard;