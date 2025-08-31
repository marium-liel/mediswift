import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { useAuth } from './AuthContext';

const WishlistContext = createContext();

export const useWishlist = () => {
  return useContext(WishlistContext);
};

export const WishlistProvider = ({ children }) => {
  const [wishlist, setWishlist] = useState([]);
  const [loading, setLoading] = useState(true);
  const { isAuthenticated } = useAuth();

  const fetchWishlist = useCallback(async () => {
    if (!isAuthenticated) {
      setWishlist([]);
      setLoading(false);
      return;
    }
    try {
      const response = await axios.get('/api/products/wishlist/');
      
      // Handle paginated response format
      if (response.data && response.data.results && Array.isArray(response.data.results)) {
        // Extract products from paginated wishlist items
        const products = response.data.results.map(item => item.product).filter(product => product);
        setWishlist(products);
      } else if (Array.isArray(response.data)) {
        // Handle direct array response
        const products = response.data.map(item => item.product).filter(product => product);
        setWishlist(products);
      } else {
        setWishlist([]);
      }
    } catch (error) {
      setWishlist([]);
    } finally {
      setLoading(false);
    }
  }, [isAuthenticated]);

  useEffect(() => {
    fetchWishlist();
  }, [fetchWishlist]);

  const addToWishlist = async (productId) => {
    try {
      const response = await axios.post(`/api/products/wishlist/add/${productId}/`);
      await fetchWishlist();
      return true;
    } catch (error) {
      return false;
    }
  };

  const removeFromWishlist = async (productId) => {
    try {
      const response = await axios.post(`/api/products/wishlist/remove/${productId}/`);
      await fetchWishlist();
      return true;
    } catch (error) {
      return false;
    }
  };

  const isInWishlist = (productId) => {
    return wishlist.some(product => product.id === productId);
  };

  const value = {
    wishlist,
    loading,
    addToWishlist,
    removeFromWishlist,
    isInWishlist,
  };

  return (
    <WishlistContext.Provider value={value}>
      {children}
    </WishlistContext.Provider>
  );
};
