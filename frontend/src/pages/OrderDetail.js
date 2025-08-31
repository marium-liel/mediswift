import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useCart } from '../context/CartContext';
import axios from 'axios';

const OrderDetail = () => {
  const { id } = useParams();
  const [order, setOrder] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const { fetchCart } = useCart();

  useEffect(() => {
    const fetchOrder = async () => {
      try {
        const response = await axios.get(`/api/orders/${id}/`);
        setOrder(response.data);
      } catch (error) {
        // Silent error handling
      } finally {
        setLoading(false);
      }
    };

    fetchOrder();
  }, [id]);

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

  const handleReorder = async () => {
    if (!order) {
      alert('Order details not loaded. Please wait and try again.');
      return;
    }
    try {
      await axios.post(`/api/orders/${id}/reorder/`);
      await fetchCart();
      // Store delivery info in localStorage for fallback
      localStorage.setItem('reorder_delivery_info', JSON.stringify({
        delivery_address: order.delivery_address,
        phone_number: order.phone_number,
        payment_method: order.payment_method
      }));
      navigate('/checkout', {
        state: {
          delivery_address: order.delivery_address,
          phone_number: order.phone_number,
          payment_method: order.payment_method,
          order_id: order.id
        }
      });
    } catch (error) {
      alert(error.response?.data?.error || 'Failed to reorder');
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!order) {
    return (
      <div className="text-center py-12">
        <h2 className="text-2xl font-bold text-gray-600">Order not found</h2>
        <Link to="/orders" className="btn-primary mt-4 inline-block">
          Back to Orders
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold">Order #{order.order_number}</h1>
          <p className="text-gray-600">
            Placed on {new Date(order.created_at).toLocaleDateString()}
          </p>
        </div>
        <div className="flex space-x-2">
          {order.status === 'delivered' && (
            <button
              onClick={handleReorder}
              className="btn-primary"
            >
              Reorder
            </button>
          )}
        </div>
      </div>

      {/* Order Status */}
      <div className="card">
        <h2 className="text-xl font-semibold mb-4">Order Status</h2>
        <div className="flex items-center space-x-4 mb-4">
            <span className={`px-4 py-2 rounded-full font-medium ${getStatusColor('delivered')}`}>
              Delivered
            </span>
          {order.delivered_at && (
            <span className="text-gray-600">
              Delivered on {new Date(order.delivered_at).toLocaleDateString()}
            </span>
          )}
        </div>

        {/* Status Timeline */}
          {/* Status Timeline removed */}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Order Items */}
        <div className="lg:col-span-2 card">
          <h2 className="text-xl font-semibold mb-4">Order Items</h2>
          <div className="space-y-4">
            {order.items.map((item) => (
              <div key={item.id} className="flex items-center space-x-4 pb-4 border-b last:border-b-0">
                <div className="w-16 h-16 bg-gray-200 rounded-lg flex items-center justify-center flex-shrink-0">
                  {item.product.image ? (
                    <img
                      src={item.product.image}
                      alt={item.product.name}
                      className="w-full h-full object-cover rounded-lg"
                    />
                  ) : (
                    <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 8.172V5L8 4z" />
                    </svg>
                  )}
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold">{item.product.name}</h3>
                  <p className="text-gray-600">{item.product.brand}</p>
                  <p className="text-sm text-gray-500">
                    Quantity: {item.quantity} × ${item.price}
                  </p>
                </div>
                <div className="text-right">
                  <p className="font-semibold">${item.total_price}</p>
                  <Link
                    to={`/products/${item.product.id}`}
                    className="text-blue-600 hover:underline text-sm"
                  >
                    View Product
                  </Link>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Order Summary & Delivery Info */}
        <div className="space-y-6">
          {/* Order Summary */}
          <div className="card">
            <h3 className="text-lg font-semibold mb-4">Order Summary</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span>Subtotal</span>
                <span>${order.subtotal}</span>
              </div>
              <div className="flex justify-between">
                <span>Tax</span>
                <span>${order.tax_amount}</span>
              </div>
              <div className="flex justify-between">
                <span>Delivery Fee</span>
                <span>${order.delivery_fee}</span>
              </div>
              <hr />
              <div className="flex justify-between font-semibold text-base">
                <span>Total</span>
                <span>${order.total_amount}</span>
              </div>
            </div>
          </div>

          {/* Delivery Information */}
          <div className="card">
            <h3 className="text-lg font-semibold mb-4">Delivery Information</h3>
            <div className="space-y-2 text-sm">
              <div>
                <span className="font-medium">Address:</span>
                <p className="text-gray-600 mt-1">{order.delivery_address}</p>
              </div>
              <div>
                <span className="font-medium">Phone:</span>
                <p className="text-gray-600">{order.phone_number}</p>
              </div>
              <div>
                <span className="font-medium">Payment Method:</span>
                <p className="text-gray-600 capitalize">
                  {order.payment_method.replace('_', ' ')}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OrderDetail;
