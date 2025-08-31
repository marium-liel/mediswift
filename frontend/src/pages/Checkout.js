import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
// ...existing code...
import { useCart } from '../context/CartContext';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';

const Checkout = () => {
  const { cart, clearCart } = useCart();
  const { user } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  // Subscription info from localStorage if present
  const subscriptionInfo = (() => {
    try {
      return JSON.parse(localStorage.getItem('subscription_checkout_info')) || null;
    } catch {
      return null;
    }
  })();

  // Use navigation state for quick reorder info if present, else fallback to last order
  // Try to get delivery info from navigation state, then localStorage, then user profile
  const localStorageInfo = (() => {
    try {
      return JSON.parse(localStorage.getItem('reorder_delivery_info')) || {};
    } catch {
      return {};
    }
  })();
  const [formData, setFormData] = useState({
    delivery_address: location.state?.delivery_address || localStorageInfo.delivery_address || user?.address || '',
    phone_number: location.state?.phone_number || localStorageInfo.phone_number || user?.phone || '',
    payment_method: location.state?.payment_method || localStorageInfo.payment_method || 'cod'
  });

  React.useEffect(() => {
    async function fetchLastOrderInfo() {
      if (!location.state?.delivery_address && !location.state?.phone_number && !location.state?.payment_method && !localStorageInfo.delivery_address && !localStorageInfo.phone_number && !localStorageInfo.payment_method) {
        try {
          const response = await axios.get('/api/orders/?ordering=-created_at&limit=1');
          const lastOrder = response.data?.results?.[0];
          if (lastOrder) {
            setFormData({
              delivery_address: lastOrder.delivery_address || user?.address || '',
              phone_number: lastOrder.phone_number || user?.phone || '',
              payment_method: lastOrder.payment_method || 'cod'
            });
          }
        } catch (err) {
          // ignore, fallback to user info
        }
      }
    }
    fetchLastOrderInfo();
  }, [location.state, user]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await axios.post('/api/orders/create/', formData);
      await clearCart();
      navigate(`/orders/${response.data.id}`);
    } catch (error) {
      setError(error.response?.data?.error || 'Failed to place order');
    } finally {
      setLoading(false);
    }
  };

  // If subscription, show subscription summary instead of cart
  if (subscriptionInfo) {
    return (
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Subscription Checkout</h1>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div className="card">
            <h2 className="text-xl font-semibold mb-6">Delivery Information</h2>
            <form className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Delivery Address *</label>
                <textarea
                  id="delivery_address"
                  name="delivery_address"
                  value={formData.delivery_address}
                  onChange={handleChange}
                  className="input-field"
                  rows="3"
                  required
                  placeholder="Enter your complete delivery address"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Phone Number *</label>
                <input
                  type="tel"
                  id="phone_number"
                  name="phone_number"
                  value={formData.phone_number}
                  onChange={handleChange}
                  className="input-field"
                  required
                  placeholder="Enter your phone number"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Payment Method *</label>
                <select
                  id="payment_method"
                  name="payment_method"
                  value={formData.payment_method}
                  onChange={handleChange}
                  className="input-field"
                  required
                >
                  <option value="cod">Cash on Delivery</option>
                  <option value="card">Credit/Debit Card</option>
                  <option value="online">Online Payment</option>
                </select>
              </div>
              <button
                type="button"
                className="w-full btn-primary"
                onClick={() => {
                  alert('Subscription order placed! (Demo only)');
                  localStorage.removeItem('subscription_checkout_info');
                  navigate('/subscriptions');
                }}
              >
                Place Subscription Order
              </button>
            </form>
          </div>
          <div className="card">
            <h2 className="text-xl font-semibold mb-6">Subscription Summary</h2>
            <div className="space-y-2">
              <div><strong>Product:</strong> {subscriptionInfo.product_name}</div>
              <div><strong>Frequency:</strong> {subscriptionInfo.frequency}</div>
              <div><strong>Quantity:</strong> {subscriptionInfo.quantity}</div>
              <div><strong>Duration:</strong> {subscriptionInfo.duration} month(s)</div>
              <div><strong>Next Deliveries:</strong> {subscriptionInfo.next_deliveries.join(', ')}</div>
              <div className="font-bold text-lg"><strong>Total Cost:</strong> ${subscriptionInfo.total_cost.toFixed(2)}</div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!cart || cart.items.length === 0) {
    return (
      <div className="text-center py-12">
        <h2 className="text-2xl font-bold text-gray-600">Your cart is empty</h2>
        <p className="text-gray-500 mt-2">Add some products before checkout</p>
      </div>
    );
  }

  const subtotal = parseFloat(cart.total_price);
  const tax = subtotal * 0.05;
  const deliveryFee = subtotal >= 500 ? 0 : 50;
  const total = subtotal + tax + deliveryFee;

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold mb-8">Checkout</h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Checkout Form */}
        <div className="card">
          <h2 className="text-xl font-semibold mb-6">Delivery Information</h2>
          
          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="delivery_address" className="block text-sm font-medium text-gray-700 mb-1">
                Delivery Address *
              </label>
              <textarea
                id="delivery_address"
                name="delivery_address"
                value={formData.delivery_address}
                onChange={handleChange}
                className="input-field"
                rows="3"
                required
                placeholder="Enter your complete delivery address"
              />
            </div>

            <div>
              <label htmlFor="phone_number" className="block text-sm font-medium text-gray-700 mb-1">
                Phone Number *
              </label>
              <input
                type="tel"
                id="phone_number"
                name="phone_number"
                value={formData.phone_number}
                onChange={handleChange}
                className="input-field"
                required
                placeholder="Enter your phone number"
              />
            </div>

            <div>
              <label htmlFor="payment_method" className="block text-sm font-medium text-gray-700 mb-1">
                Payment Method *
              </label>
              <select
                id="payment_method"
                name="payment_method"
                value={formData.payment_method}
                onChange={handleChange}
                className="input-field"
                required
              >
                <option value="cod">Cash on Delivery</option>
                <option value="card">Credit/Debit Card</option>
                <option value="online">Online Payment</option>
              </select>
            </div>

            {formData.payment_method === 'cod' && (
              <div className="bg-blue-100 text-blue-800 p-3 rounded text-sm">
                <strong>Cash on Delivery:</strong> Pay when your order is delivered to your doorstep.
              </div>
            )}

            {formData.payment_method !== 'cod' && (
              <div className="bg-yellow-100 text-yellow-800 p-3 rounded text-sm">
                <strong>Note:</strong> This is a demo. Payment processing is simulated.
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full btn-primary disabled:opacity-50"
            >
              {loading ? 'Placing Order...' : 'Place Order'}
            </button>
          </form>
        </div>

        {/* Order Summary */}
        <div className="card">
          <h2 className="text-xl font-semibold mb-6">Order Summary</h2>
          
          <div className="space-y-4 mb-6">
            {cart.items.map((item) => (
              <div key={item.id} className="flex items-center space-x-3">
                <div className="w-12 h-12 bg-gray-200 rounded flex items-center justify-center flex-shrink-0">
                  {item.product.image ? (
                    <img
                      src={item.product.image}
                      alt={item.product.name}
                      className="w-full h-full object-cover rounded"
                    />
                  ) : (
                    <svg className="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 8.172V5L8 4z" />
                    </svg>
                  )}
                </div>
                <div className="flex-1">
                  <h4 className="font-medium">{item.product.name}</h4>
                  <p className="text-sm text-gray-600">
                    {item.quantity} x ${item.product.price}
                  </p>
                </div>
                <div className="font-semibold">
                  ${item.total_price}
                </div>
              </div>
            ))}
          </div>

          <div className="border-t pt-4 space-y-2">
            <div className="flex justify-between">
              <span>Subtotal ({cart.total_items} items)</span>
              <span>${subtotal.toFixed(2)}</span>
            </div>
            <div className="flex justify-between">
              <span>Tax (5%)</span>
              <span>${tax.toFixed(2)}</span>
            </div>
            <div className="flex justify-between">
              <span>Delivery Fee</span>
              <span>{deliveryFee === 0 ? 'FREE' : `$${deliveryFee.toFixed(2)}`}</span>
            </div>
            <hr />
            <div className="flex justify-between font-semibold text-lg">
              <span>Total</span>
              <span>${total.toFixed(2)}</span>
            </div>
          </div>

          {subtotal < 500 && (
            <div className="bg-blue-100 text-blue-800 p-3 rounded mt-4 text-sm">
              Add ${(500 - subtotal).toFixed(2)} more for free delivery!
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Checkout;
