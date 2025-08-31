import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useCart } from '../context/CartContext';
import axios from 'axios';

const Orders = () => {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const { fetchCart } = useCart();

  useEffect(() => {
    fetchOrders();
  }, []);

  const fetchOrders = async () => {
    try {
      const response = await axios.get('/api/orders/');
      setOrders(response.data.results || response.data);
    } catch (error) {
      // Silent error handling
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      pending: 'bg-yellow-100 text-yellow-800',
      approved: 'bg-blue-100 text-blue-800',
      shipped: 'bg-purple-100 text-purple-800',
      delivered: 'bg-green-100 text-green-800',
      cancelled: 'bg-red-100 text-red-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  const handleReorder = async (orderId) => {
    try {
      // First get the order details to extract delivery info
      const orderResponse = await axios.get(`/api/orders/${orderId}/`);
      const order = orderResponse.data;
      
      // Add items to cart
      await axios.post(`/api/orders/${orderId}/reorder/`);
      await fetchCart();
      
      // Store delivery info in localStorage for fallback
      localStorage.setItem('reorder_delivery_info', JSON.stringify({
        delivery_address: order.delivery_address,
        phone_number: order.phone_number,
        payment_method: order.payment_method
      }));
      
      // Redirect to checkout with delivery info
      navigate('/checkout', {
        state: {
          delivery_address: order.delivery_address,
          phone_number: order.phone_number,
          payment_method: order.payment_method,
          order_id: order.id
        }
      });
    } catch (error) {
      // Silent error handling
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">My Orders</h1>

      {orders.length > 0 ? (
        <div className="space-y-4">
          {orders.map((order) => (
            <div key={order.id} className="card hover:shadow-lg transition-shadow">
              <div className="flex flex-col md:flex-row md:items-center md:justify-between space-y-4 md:space-y-0">
                <div className="flex-1">
                  <div className="flex items-center space-x-4 mb-2">
                    <h3 className="text-lg font-semibold">
                      Order #{order.order_number}
                    </h3>
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(order.status)}`}>
                      {order.status.charAt(0).toUpperCase() + order.status.slice(1)}
                    </span>
                  </div>
                  
                  <div className="text-gray-600 space-y-1">
                    <p>
                      <span className="font-medium">Items:</span> {order.items_count}
                    </p>
                    <p>
                      <span className="font-medium">Total:</span> ${order.total_amount}
                    </p>
                    <p>
                      <span className="font-medium">Ordered:</span>{' '}
                      {new Date(order.created_at).toLocaleDateString()}
                    </p>
                  </div>
                </div>

                <div className="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-2">
                  <Link
                    to={`/orders/${order.id}`}
                    className="btn-primary text-center"
                  >
                    View Details
                  </Link>
                  
                  {order.status === 'delivered' && (
                    <button
                      onClick={() => handleReorder(order.id)}
                      className="btn-secondary"
                    >
                      Reorder
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <svg className="w-24 h-24 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
          </svg>
          <h2 className="text-2xl font-bold text-gray-600 mb-4">No orders yet</h2>
          <p className="text-gray-500 mb-6">Start shopping to see your orders here!</p>
          <Link to="/products" className="btn-primary">
            Start Shopping
          </Link>
        </div>
      )}
    </div>
  );
};

export default Orders;
