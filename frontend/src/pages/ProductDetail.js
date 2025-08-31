import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import axios from 'axios';
import { useCart } from '../context/CartContext';
import { useAuth } from '../context/AuthContext';
import WishlistButton from '../components/WishlistButton';

// SubscriptionSummary component
const SubscriptionSummary = ({ product, form }) => {
  if (!form.frequency || !form.quantity || !form.duration) return null;
  
  const today = new Date();
  let dates = [];
  let interval = 0;
  
  switch (form.frequency) {
    case 'weekly': interval = 7; break;
    case 'biweekly': interval = 14; break;
    case 'monthly': interval = 30; break;
    case 'yearly': interval = 365; break;
    default: interval = 30;
  }
  
  for (let i = 0; i < form.duration; i++) {
    const d = new Date(today);
    d.setDate(today.getDate() + i * interval);
    dates.push(d.toLocaleDateString());
  }
  
  const totalDeliveries = form.duration;
  const totalCost = product.price * form.quantity * totalDeliveries;
  
  return (
    <div className="bg-blue-50 p-3 rounded mb-2">
      <div><strong>Next Delivery Dates:</strong> {dates.join(', ')}</div>
      <div><strong>Total Deliveries:</strong> {totalDeliveries}</div>
      <div><strong>Total Cost:</strong> ${totalCost.toFixed(2)}</div>
    </div>
  );
};

const ProductDetail = () => {
  const [product, setProduct] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [relatedProducts, setRelatedProducts] = useState([]);
  const [quantity, setQuantity] = useState(1);
  const [loading, setLoading] = useState(true);
  const [reviewLoading, setReviewLoading] = useState(false);
  const [showReviewForm, setShowReviewForm] = useState(false);
  const [editingReviewId, setEditingReviewId] = useState(null);
  const [reviewForm, setReviewForm] = useState({
    rating: 5,
    title: '',
    comment: '',
    image: null,
    video: null
  });
  const [showSubscriptionForm, setShowSubscriptionForm] = useState(false);
  const [subscriptionForm, setSubscriptionForm] = useState({
    frequency: 'monthly',
    quantity: 1,
    duration: 1
  });
  const [submittingSubscription, setSubmittingSubscription] = useState(false);
  
  const { addToCart } = useCart();
  const { user, isAuthenticated } = useAuth();
  const { id } = useParams();

  useEffect(() => {
    fetchProduct();
    fetchReviews();
    fetchRelatedProducts();
  }, [id]);

  const fetchRelatedProducts = async () => {
    try {
      const response = await axios.get(`/api/products/${id}/related/`);
      setRelatedProducts(response.data);
    } catch (error) {
      // Silent error handling
    }
  };

  const fetchProduct = async () => {
    try {
      const response = await axios.get(`/api/products/${id}/`);
      setProduct(response.data);
      
      // Set up auto-refresh for product data if there are active subscriptions
      if (response.data.subscription_count > 0) {
        const intervalId = setInterval(() => {
          refreshProduct();
        }, 5000); // Refresh every 5 seconds if there are subscriptions
        
        // Cleanup interval on unmount
        return () => clearInterval(intervalId);
      }
    } catch (error) {
      // Silent error handling
    } finally {
      setLoading(false);
    }
  };

  const refreshProduct = async () => {
    try {
      const response = await axios.get(`/api/products/${id}/`);
      setProduct(response.data);
    } catch (error) {
      // Silent error handling
    }
  };

  const fetchReviews = async () => {
    try {
      const response = await axios.get(`/api/reviews/product/${id}/`);
      setReviews(response.data.results || response.data);
    } catch (error) {
      // Silent error handling
    }
  };

  const handleAddToCart = async () => {
    const result = await addToCart(product.id, quantity);
    if (result.success) {
      alert('Product added to cart!');
    } else {
      alert(result.error);
    }
  };

  const handleReviewSubmit = async (e) => {
    e.preventDefault();
    setReviewLoading(true);
    
    try {
      const formData = new FormData();
      formData.append('product_id', product.id);
      formData.append('rating', reviewForm.rating);
      formData.append('title', reviewForm.title);
      formData.append('comment', reviewForm.comment);
      if (reviewForm.image) formData.append('image', reviewForm.image);
      if (reviewForm.video) formData.append('video', reviewForm.video);
      
      if (editingReviewId) {
        await axios.put(`/api/reviews/${editingReviewId}/`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
      } else {
        await axios.post('/api/reviews/create/', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
      }
      
      setShowReviewForm(false);
      setEditingReviewId(null);
      setReviewForm({ rating: 5, title: '', comment: '', image: null, video: null });
      fetchReviews();
      fetchProduct();
    } catch (error) {
      // Silent error handling
    } finally {
      setReviewLoading(false);
    }
  };

  const handleSubscriptionSubmit = async (e) => {
    e.preventDefault();
    
    // Check if there's enough stock for the subscription
    const requiredStock = subscriptionForm.quantity * 3; // Need stock for 3 deliveries
    if (product.available_stock < requiredStock) {
      return;
    }
    
    setSubmittingSubscription(true);
    try {
      await axios.post('/api/products/subscriptions/', {
        product: product.id,
        quantity: subscriptionForm.quantity,
        frequency: subscriptionForm.frequency,
        next_delivery: new Date().toISOString().slice(0, 10)
      });
      
      // Reset form
      setShowSubscriptionForm(false);
      setSubscriptionForm({ frequency: 'monthly', quantity: 1, duration: 1 });
      
      // Refresh product data to update stock information
      await fetchProduct();
      
    } catch (error) {
      // Silent error handling
    } finally {
      setSubmittingSubscription(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!product) {
    return (
      <div className="text-center py-12">
        <h2 className="text-2xl font-bold text-gray-600">Product not found</h2>
        <Link to="/products" className="btn-primary mt-4 inline-block">
          Back to Products
        </Link>
      </div>
    );
  }

  return [
    <div key="main" className="space-y-8">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Left Column - Product Image */}
        <div>
          <div className="aspect-square bg-gray-200 rounded-lg flex items-center justify-center">
            {product.image ? (
              <img
                src={product.image}
                alt={product.name}
                className="w-full h-full object-cover rounded-lg"
              />
            ) : (
              <svg className="w-32 h-32 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 8.172V5L8 4z" />
              </svg>
            )}
          </div>
        </div>
        {/* Right Column - Product Details */}
        <div className="space-y-6">
          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-3xl font-bold">{product.name}</h1>
              <p className="text-xl text-gray-600">{product.brand}</p>
              <p className="text-gray-500">{product.category_name}</p>
            </div>
            <WishlistButton productId={product.id} />
          </div>

          {/* Stock Information */}
          <div className="bg-gray-50 p-4 rounded-lg">
            <h3 className="font-semibold mb-2">Stock Information</h3>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-gray-600">Total Stock:</p>
                <p className="font-medium">{product.stock_quantity} units</p>
              </div>
              <div>
                <p className="text-gray-600">Available Stock:</p>
                <p className="font-medium">{product.available_stock} units</p>
              </div>
              <div>
                <p className="text-gray-600">Reserved for Subscriptions:</p>
                <p className="font-medium">{product.reserved_quantity} units</p>
              </div>
              <div>
                <p className="text-gray-600">Active Subscriptions:</p>
                <p className="font-medium">{product.subscription_count || 0}</p>
              </div>
            </div>
          </div>

          {/* Rating */}
          <div className="flex items-center space-x-4">
            <div className="flex items-center">
              {[...Array(5)].map((_, i) => (
                <svg
                  key={i}
                  className={`w-5 h-5 ${
                    i < Math.floor(product.average_rating)
                      ? 'text-yellow-400'
                      : 'text-gray-300'
                  }`}
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                </svg>
              ))}
            </div>
            <span className="text-gray-600">
              {(product.average_rating ? product.average_rating.toFixed(1) : "0.0")} ({product.review_count ?? 0} reviews)
            </span>
          </div>

          {/* Price */}
          <div className="text-4xl font-bold text-blue-600">
            ${product.price}
          </div>

          {/* Stock Status */}
          <div className="space-y-2">
            <div className={`inline-block px-3 py-1 rounded text-sm ${
              product.is_in_stock
                ? 'bg-green-100 text-green-800'
                : 'bg-red-100 text-red-800'
            }`}>
              {product.is_in_stock ? `${product.stock_quantity} in stock` : 'Out of stock'}
            </div>
            
            {product.is_low_stock && product.is_in_stock && (
              <div className="block text-orange-600 text-sm">
                Only {product.stock_quantity} left!
              </div>
            )}
            
            {product.days_to_expiry <= 30 && (
              <div className="block text-red-600 text-sm">
                Expires in {product.days_to_expiry} days
              </div>
            )}
          </div>

          {/* Add to Cart Section */}
          {product.is_in_stock && (
            <div className="flex items-center space-x-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Quantity</label>
                <select
                  value={quantity}
                  onChange={(e) => setQuantity(parseInt(e.target.value))}
                  className="input-field w-20"
                >
                  {[...Array(Math.min(10, product.stock_quantity))].map((_, i) => (
                    <option key={i + 1} value={i + 1}>{i + 1}</option>
                  ))}
                </select>
              </div>
              <button
                onClick={handleAddToCart}
                className="btn-primary"
              >
                Add to Cart
              </button>
              {/* Subscribe Button */}
              {isAuthenticated && (
                <button
                  className="btn-secondary"
                  onClick={() => setShowSubscriptionForm(!showSubscriptionForm)}
                >
                  {showSubscriptionForm ? 'Hide Subscription' : 'Subscribe'}
                </button>
              )}
            </div>
          )}

          {/* Subscription Form */}
          {showSubscriptionForm && (
            <div className="card">
              <h3 className="text-lg font-semibold mb-4">Create Subscription</h3>
              <form onSubmit={handleSubscriptionSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Frequency</label>
                  <select
                    value={subscriptionForm.frequency}
                    onChange={(e) => setSubscriptionForm({...subscriptionForm, frequency: e.target.value})}
                    className="input-field"
                  >
                    <option value="weekly">Weekly</option>
                    <option value="biweekly">Bi-weekly</option>
                    <option value="monthly">Monthly</option>
                    <option value="yearly">Yearly</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Quantity per delivery</label>
                  <select
                    value={subscriptionForm.quantity}
                    onChange={(e) => setSubscriptionForm({...subscriptionForm, quantity: parseInt(e.target.value)})}
                    className="input-field w-24"
                  >
                    {[...Array(Math.min(5, product.available_stock))].map((_, i) => (
                      <option key={i + 1} value={i + 1}>{i + 1}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Duration (deliveries)</label>
                  <select
                    value={subscriptionForm.duration}
                    onChange={(e) => setSubscriptionForm({...subscriptionForm, duration: parseInt(e.target.value)})}
                    className="input-field w-24"
                  >
                    {[...Array(12)].map((_, i) => (
                      <option key={i + 1} value={i + 1}>{i + 1}</option>
                    ))}
                  </select>
                </div>

                <SubscriptionSummary product={product} form={subscriptionForm} />

                <div className="flex space-x-2">
                  <button
                    type="submit"
                    disabled={submittingSubscription}
                    className="btn-primary disabled:opacity-50"
                  >
                    {submittingSubscription ? 'Creating...' : 'Create Subscription'}
                  </button>
                  <button
                    type="button"
                    onClick={() => setShowSubscriptionForm(false)}
                    className="btn-secondary"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          )}
        </div>
      </div>

      {/* Product Description */}
      {product.description && (
        <div className="card">
          <h3 className="text-xl font-semibold mb-4">Description</h3>
          <p className="text-gray-700">{product.description}</p>
        </div>
      )}

      {/* Reviews Section */}
      <div className="card">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-xl font-semibold">Reviews ({reviews.length})</h3>
          {isAuthenticated && (
            <button
              onClick={() => setShowReviewForm(!showReviewForm)}
              className="btn-primary"
            >
              {showReviewForm ? 'Cancel' : 'Write Review'}
            </button>
          )}
        </div>

        {/* Review Form */}
        {showReviewForm && (
          <div className="border-t pt-4 mb-6">
            <form onSubmit={handleReviewSubmit} className="space-y-4">
              <div className="flex justify-between items-center mb-2">
                <h4 className="text-lg font-medium">
                  {editingReviewId ? 'Edit Your Review' : 'Write a Review'}
                </h4>
                <button
                  type="button"
                  onClick={() => {
                    setShowReviewForm(false);
                    setEditingReviewId(null);
                    setReviewForm({ rating: 5, title: '', comment: '', image: null, video: null });
                  }}
                  className="text-gray-600 hover:text-gray-800"
                >
                  Cancel
                </button>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Rating</label>
                <div className="flex items-center space-x-2">
                  <select
                    value={reviewForm.rating}
                    onChange={(e) => setReviewForm({...reviewForm, rating: parseInt(e.target.value)})}
                    className="input-field w-20"
                  >
                    {[5, 4, 3, 2, 1].map(rating => (
                      <option key={rating} value={rating}>{rating} ⭐</option>
                    ))}
                  </select>
                  <span className="text-sm text-gray-500">
                    {reviewForm.rating === 5 ? 'Excellent' :
                     reviewForm.rating === 4 ? 'Very Good' :
                     reviewForm.rating === 3 ? 'Good' :
                     reviewForm.rating === 2 ? 'Fair' : 'Poor'}
                  </span>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Title</label>
                <input
                  type="text"
                  value={reviewForm.title}
                  onChange={(e) => setReviewForm({...reviewForm, title: e.target.value})}
                  className="input-field"
                  placeholder="Summarize your experience"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Review</label>
                <textarea
                  value={reviewForm.comment}
                  onChange={(e) => setReviewForm({...reviewForm, comment: e.target.value})}
                  className="input-field"
                  rows={4}
                  placeholder="Share your experience with this product"
                  required
                />
              </div>

              <div className="flex space-x-3">
                <button
                  type="submit"
                  disabled={reviewLoading}
                  className="btn-primary disabled:opacity-50"
                >
                  {reviewLoading ? 'Submitting...' : editingReviewId ? 'Update Review' : 'Submit Review'}
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setShowReviewForm(false);
                    setEditingReviewId(null);
                    setReviewForm({ rating: 5, title: '', comment: '', image: null, video: null });
                  }}
                  className="btn-secondary"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Reviews List */}
        <div className="space-y-4">
          {reviews.map((review) => {
            const isUserReview = isAuthenticated && user && (
              review.user === user.id || 
              review.user_name === user.username
            );
            
            return (
              <div key={review.id} className="border-b pb-4">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center space-x-3">
                    <span className="font-semibold">{review.user_name || review.user?.username || "Anonymous"}</span>
                    {review.is_verified_purchase && (
                      <span className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded">
                        Verified Purchase
                      </span>
                    )}
                  </div>
                  <div className="flex items-center space-x-3">
                    <div className="flex">
                      {[...Array(5)].map((_, i) => (
                        <svg
                          key={i}
                          className={`w-4 h-4 ${i < review.rating ? 'text-yellow-400' : 'text-gray-300'}`}
                          fill="currentColor"
                          viewBox="0 0 20 20"
                        >
                          <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                        </svg>
                      ))}
                    </div>
                    {isUserReview && (
                      <button
                        className="text-blue-600 hover:underline text-sm"
                        onClick={() => {
                          setEditingReviewId(review.id);
                          setReviewForm({
                            rating: review.rating,
                            title: review.title || '',
                            comment: review.comment || '',
                            image: null,
                            video: null
                          });
                          setShowReviewForm(true);
                        }}
                      >
                        Edit Review
                      </button>
                    )}
                  </div>
                </div>
                {review.title && <h4 className="font-medium text-lg mb-2">{review.title}</h4>}
                <p className="text-gray-700 mb-2">{review.comment}</p>
                <div className="flex items-center justify-between text-sm text-gray-500">
                  <span>{new Date(review.created_at).toLocaleDateString()}</span>
                  <div className="flex items-center space-x-4">
                    <span>Helpful ({review.helpful_count || 0})</span>
                    <span>Not Helpful ({review.not_helpful_count || 0})</span>
                  </div>
                </div>
              </div>
            );
          })}
          
          {reviews.length === 0 && (
            <p className="text-gray-500 text-center py-4">No reviews yet. Be the first to review!</p>
          )}
        </div>
      </div>,

      {/* Related Products Section */}
      {relatedProducts.length > 0 && (
        <div className="card">
          <h3 className="text-xl font-semibold mb-4">Related Products</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {relatedProducts.map((rp) => (
              <Link key={rp.id} to={`/products/${rp.id}`} className="block border rounded-lg p-4 hover:shadow-lg transition-shadow">
                <div className="aspect-square bg-gray-100 rounded flex items-center justify-center mb-2">
                  {rp.image ? (
                    <img src={rp.image} alt={rp.name} className="w-full h-full object-cover rounded" />
                  ) : (
                    <svg className="w-16 h-16 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 8.172V5L8 4z" />
                    </svg>
                  )}
                </div>
                <div className="font-bold text-lg">{rp.name}</div>
                <div className="text-gray-600">{rp.brand}</div>
                <div className="text-blue-600 font-semibold">${rp.price}</div>
              </Link>
            ))}
          </div>
        </div>
      )}
    </div>
  ];
};

export default ProductDetail;
