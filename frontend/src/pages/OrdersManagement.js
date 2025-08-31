/*
 * ORDERS MANAGEMENT COMPONENT - E-COMMERCE ORDER PROCESSING SYSTEM
 * 
 * This component demonstrates:
 * 1. Order lifecycle management in React
 * 2. Real-time order status updates via Django API
 * 3. Client-side filtering and data manipulation
 * 4. Order fulfillment workflow (pending → processing → shipped → delivered)
 * 5. Admin interface for order tracking and management
 * 
 * DJANGO INTEGRATION:
 * - Fetches orders from Django Order model via REST API
 * - Updates order status through Django backend
 * - Displays customer information from Django User model
 * - Handles order workflow states and transitions
 */

import React, { useState, useEffect } from 'react';

const OrdersManagement = () => {
    /*
     * COMPONENT STATE MANAGEMENT
     * 
     * This component manages order data and filtering:
     * - orders: Array of all orders from Django backend
     * - loading: Loading state for API operations
     * - selectedStatus: Current filter for order status (client-side filtering)
     */
    const [orders, setOrders] = useState([]);
    const [loading, setLoading] = useState(true);
    const [selectedStatus, setSelectedStatus] = useState('all');

    /*
     * COMPONENT LIFECYCLE - FETCH ORDERS ON MOUNT
     * 
     * Load all orders when component first renders.
     * This is the typical pattern for data-driven components.
     */
    useEffect(() => {
        fetchOrders();
    }, []);

    /*
     * FETCH ORDERS FROM DJANGO BACKEND
     * 
     * This function demonstrates:
     * 1. Authenticated API calls to Django Order endpoints
     * 2. Fetching relational data (orders with customer info)
     * 3. Error handling for network requests
     * 4. Loading state management for better UX
     */
    const fetchOrders = async () => {
        try {
            // Call Django admin endpoint to get all orders with customer details
            const response = await fetch('/api/accounts/admin/orders/', {
                headers: {
                    // JWT authentication required for admin access
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                // Update component state with order data from Django
                setOrders(data);
            }
        } catch (error) {
            // Silent error handling - could implement user notifications
        } finally {
            // Always stop loading, whether success or error
            setLoading(false);
        }
    };

    /*
     * UPDATE ORDER STATUS - ORDER WORKFLOW MANAGEMENT
     * 
     * This function manages the order fulfillment lifecycle:
     * 1. Sends PUT request to Django to update order status
     * 2. Handles order state transitions (pending → processing → shipped → delivered)
     * 3. Provides real-time updates to order tracking
     * 4. Demonstrates admin control over order workflow
     */
    const updateOrderStatus = async (orderId, newStatus) => {
        try {
            // Send PUT request to Django to update specific order's status
            const response = await fetch(`/api/accounts/admin/orders/${orderId}/status/`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                },
                // Send new status to Django Order model
                body: JSON.stringify({ status: newStatus })
            });
            
            if (response.ok) {
                // Refresh orders list to show updated status
                fetchOrders();
            }
        } catch (error) {
            // Silent error handling
        }
    };

    /*
     * CLIENT-SIDE FILTERING - FILTER ORDERS BY STATUS
     * 
     * This demonstrates client-side data filtering in React:
     * - Uses JavaScript array filter method
     * - Filters based on selectedStatus state
     * - Provides instant filtering without server requests
     * - Shows conditional logic with ternary operator
     */
    const filteredOrders = selectedStatus === 'all'
        ? orders                                                    // Show all orders
        : orders.filter(order => order.status === selectedStatus);  // Filter by status

    // Loading state - show spinner while fetching orders
    if (loading) {
        return (
            <div className="flex justify-center items-center min-h-screen">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
        );
    }

    /*
     * MAIN COMPONENT RENDER - ORDER MANAGEMENT INTERFACE
     * 
     * This renders a comprehensive order management system with:
     * 1. Status filtering dropdown for quick order searches
     * 2. Tabular display of order information from Django
     * 3. Visual status indicators with color coding
     * 4. Inline status editing for order workflow management
     * 5. Responsive design for different screen sizes
     */
    return (
        <div className="bg-white rounded-lg shadow p-6">
            {/* HEADER WITH FILTERING */}
            <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-semibold text-gray-800">Orders Management</h2>
                
                {/* 
                 * STATUS FILTER DROPDOWN
                 * 
                 * This dropdown provides client-side filtering:
                 * - Controlled component (value from state)
                 * - onChange updates selectedStatus state
                 * - Filters are applied via filteredOrders computed property
                 * - No server requests needed for filtering
                 */}
                <select
                    value={selectedStatus}
                    onChange={(e) => setSelectedStatus(e.target.value)}
                    className="rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                >
                    <option value="all">All Orders</option>
                    <option value="pending">Pending</option>
                    <option value="processing">Processing</option>
                    <option value="shipped">Shipped</option>
                    <option value="delivered">Delivered</option>
                    <option value="cancelled">Cancelled</option>
                </select>
            </div>

            {/* ORDERS TABLE - RESPONSIVE DATA DISPLAY */}
            <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                    {/* TABLE HEADER */}
                    <thead className="bg-gray-50">
                        <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Order ID</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Customer</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Total</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                        </tr>
                    </thead>
                    
                    {/* TABLE BODY - DYNAMIC ORDER ROWS */}
                    <tbody className="bg-white divide-y divide-gray-200">
                        {/* 
                         * ARRAY MAPPING - RENDER FILTERED ORDERS
                         * 
                         * Maps over filteredOrders (not raw orders) to show filtered results.
                         * Each row displays order information from Django models.
                         */}
                        {filteredOrders.map((order) => (
                            <tr key={order.id}>
                                {/* ORDER ID COLUMN */}
                                <td className="px-6 py-4 whitespace-nowrap">#{order.id}</td>
                                
                                {/* CUSTOMER NAME COLUMN - From Django User model */}
                                <td className="px-6 py-4 whitespace-nowrap">{order.user_name}</td>
                                
                                {/* ORDER DATE COLUMN - JavaScript Date formatting */}
                                <td className="px-6 py-4 whitespace-nowrap">
                                    {/* Convert Django datetime to readable format */}
                                    {new Date(order.created_at).toLocaleDateString()}
                                </td>
                                
                                {/* ORDER TOTAL COLUMN - From Django Order model */}
                                <td className="px-6 py-4 whitespace-nowrap">${order.total_amount}</td>
                                
                                {/* STATUS COLUMN - VISUAL STATUS INDICATORS */}
                                <td className="px-6 py-4 whitespace-nowrap">
                                    {/* 
                                     * CONDITIONAL STYLING - Status badges with color coding
                                     * 
                                     * Each order status gets different colors for quick visual identification:
                                     * - Green: Delivered (completed)
                                     * - Yellow: Pending (needs attention)
                                     * - Blue: Processing (in progress)
                                     * - Purple: Shipped (in transit)
                                     * - Red: Cancelled (failed/cancelled)
                                     */}
                                    <span className={`px-2 py-1 text-xs rounded-full ${
                                        order.status === 'delivered' ? 'bg-green-100 text-green-800' :
                                        order.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                                        order.status === 'processing' ? 'bg-blue-100 text-blue-800' :
                                        order.status === 'shipped' ? 'bg-purple-100 text-purple-800' :
                                        'bg-red-100 text-red-800'  // Cancelled or other status
                                    }`}>
                                        {order.status}
                                    </span>
                                </td>
                                
                                {/* ACTIONS COLUMN - ORDER STATUS MANAGEMENT */}
                                <td className="px-6 py-4 whitespace-nowrap">
                                    {/* 
                                     * STATUS UPDATE DROPDOWN
                                     * 
                                     * This dropdown allows admins to change order status:
                                     * - Controlled component with current order status
                                     * - onChange triggers updateOrderStatus function
                                     * - Immediately updates Django backend
                                     * - Demonstrates inline editing for workflow management
                                     */}
                                    <select
                                        value={order.status}
                                        onChange={(e) => updateOrderStatus(order.id, e.target.value)}
                                        className="rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                                    >
                                        <option value="pending">Pending</option>
                                        <option value="processing">Processing</option>
                                        <option value="shipped">Shipped</option>
                                        <option value="delivered">Delivered</option>
                                        <option value="cancelled">Cancelled</option>
                                    </select>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default OrdersManagement;
