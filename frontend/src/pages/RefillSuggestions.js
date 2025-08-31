import React, { useState, useEffect } from 'react';
import axios from 'axios';

const RefillSuggestions = () => {
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchSuggestions = async () => {
      try {
        const response = await axios.get('/api/products/refill-suggestions/');
        setSuggestions(response.data.results || response.data);
      } catch (error) {
        // Silent error handling
      } finally {
        setLoading(false);
      }
    };

    fetchSuggestions();
  }, []);

  const handleReorder = async (productId) => {
    try {
      await axios.post('/api/products/cart/add/', { 
        product_id: productId, 
        quantity: 1 
      });
      alert('Product added to cart!');
    } catch (error) {
      alert('Failed to add to cart');
    }
  };

  if (loading) {
    return <div className="flex justify-center items-center min-h-64"><div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div></div>;
  }

  return (
    <div className="card mt-8">
      <h3 className="text-xl font-semibold mb-4">Smart Refill Suggestions</h3>
      {suggestions.length > 0 ? (
        <div className="space-y-4">
          {suggestions.map((product) => (
            <div key={product.id} className="flex justify-between items-center border-b pb-4">
              <div>
                <h4 className="font-medium">{product.name}</h4>
                <p className="text-sm text-gray-600">{product.brand}</p>
              </div>
              <button onClick={() => handleReorder(product.id)} className="btn-primary">Reorder Now</button>
            </div>
          ))}
        </div>
      ) : (
        <p className="text-gray-500">No refill suggestions at this time.</p>
      )}
    </div>
  );
};

export default RefillSuggestions;
