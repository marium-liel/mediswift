import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';

const Subscriptions = () => {
  const [subscriptions, setSubscriptions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { isAuthenticated } = useAuth();

  useEffect(() => {
    if (!isAuthenticated) {
      window.location.href = '/login';
      return;
    }
    fetchSubscriptions();
  }, [isAuthenticated]);

  const fetchSubscriptions = async () => {
    try {
      const response = await axios.get('/api/products/subscriptions/');
      // Ensure response.data is an array
      if (Array.isArray(response.data)) {
        setSubscriptions(response.data);
      } else if (response.data.results && Array.isArray(response.data.results)) {
        // Handle DRF pagination format
        setSubscriptions(response.data.results);
      } else {
        setSubscriptions([]);
      }
    } catch (err) {
      setError('Failed to fetch subscriptions');
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = async (id) => {
    try {
      setLoading(true);
      await axios.delete(`/api/products/subscriptions/${id}/`);
      
      // Wait a short moment to allow backend processing
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // Refresh the subscriptions list to get updated stock information
      await fetchSubscriptions();
      
    } catch (err) {
      // Silent error handling
    } finally {
      setLoading(false);
    }
  };

  const getUpcomingDeliveryDates = (subscription) => {
    const dates = subscription.upcoming_deliveries || [];
    return dates.map(date => new Date(date).toLocaleDateString()).join(', ');
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-[400px]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8 text-center">
        <div className="text-red-600 mb-4">{error}</div>
        <button 
          onClick={fetchSubscriptions}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Try Again
        </button>
      </div>
    );
  }

  // Ensure subscriptions is always an array
  const subscriptionsList = Array.isArray(subscriptions) ? subscriptions : [];

  return (
    <div className="container mx-auto px-4 py-6">
      <div className="bg-white rounded-lg shadow-sm p-8 max-w-4xl mx-auto">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold">My Subscriptions</h2>
          <Link to="/products" className="btn-primary">
            Browse Products
          </Link>
        </div>

        {subscriptionsList.length === 0 ? (
          <div className="text-center py-12 bg-gray-50 rounded-lg">
            <p className="text-gray-600 mb-4">You don't have any active subscriptions</p>
            <p className="text-sm text-gray-500 mb-6">Subscribe to products for regular delivery at your convenience</p>
          </div>
        ) : (
          <div className="space-y-6">
            {subscriptionsList.map(sub => (
              <div key={sub.id} className="border rounded-lg p-6 hover:shadow-md transition-shadow">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-4">
                  <div>
                    <div className="font-semibold text-lg">{sub.product_name}</div>
                    <Link 
                      to={`/products/${sub.product_id}`} 
                      className="text-blue-600 hover:text-blue-800 text-sm"
                    >
                      View Product
                    </Link>
                  </div>
                  <div>
                    <div className="text-gray-600">Subscription Details</div>
                    <div className="text-sm">
                      <div>Frequency: {sub.frequency}</div>
                      <div>Quantity: {sub.quantity} units</div>
                    </div>
                  </div>
                  <div>
                    <div className="text-gray-600">Delivery Information</div>
                    <div className="text-sm space-y-2">
                      <div className="font-medium">Next Delivery: {new Date(sub.next_delivery).toLocaleDateString()}</div>
                      <div className="flex items-center gap-2">
                        Status: 
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
                          ${sub.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                          {sub.is_active ? 'Active' : 'Cancelled'}
                        </span>
                      </div>
                      {sub.is_active && sub.upcoming_deliveries && (
                        <div>
                          <div className="text-gray-600 mb-1">Upcoming Deliveries:</div>
                          <div className="grid grid-cols-2 gap-2">
                            {sub.upcoming_deliveries.map((date, index) => (
                              <div 
                                key={index}
                                className="bg-gray-50 px-3 py-1 rounded text-xs"
                              >
                                {new Date(date).toLocaleDateString()}
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                      <div className="text-sm space-y-1">
                        <div className="text-gray-600">
                          Total Stock: {sub.product_stock || 0} units
                        </div>
                        <div className="text-gray-600">
                          Available Stock: {sub.product_available_stock || 0} units
                        </div>
                        <div className="text-gray-600">
                          Reserved for Subscriptions: {sub.product_reserved_quantity || 0} units
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                
                {sub.is_active && (
                  <div className="flex justify-between items-center border-t pt-4 mt-4">
                    <div className="text-sm text-gray-600">
                      Stock will be reserved for upcoming deliveries
                    </div>
                    <button
                      className="inline-flex items-center px-4 py-2 border border-red-300 text-sm font-medium rounded-md text-red-700 hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                      onClick={() => handleCancel(sub.id)}
                    >
                      Cancel Subscription
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Subscription Info Footer */}
      <div className="max-w-4xl mx-auto mt-8 p-6 bg-blue-50 rounded-lg">
        <h3 className="text-lg font-medium text-blue-900 mb-3">About Subscriptions</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-medium text-blue-800 mb-2">Benefits</h4>
            <ul className="text-sm text-blue-700 space-y-2">
              <li>• Never run out of essential medicines</li>
              <li>• Regular delivery at your convenience</li>
              <li>• Cancel anytime with no commitments</li>
              <li>• Priority processing for subscribers</li>
            </ul>
          </div>
          <div>
            <h4 className="font-medium text-blue-800 mb-2">How it Works</h4>
            <ul className="text-sm text-blue-700 space-y-2">
              <li>1. Choose products you want to subscribe to</li>
              <li>2. Select your preferred delivery frequency</li>
              <li>3. We'll automatically process and deliver your orders</li>
              <li>4. Manage or cancel your subscriptions anytime</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Subscriptions;