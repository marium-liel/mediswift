import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from './AuthContext';

const CartContext = createContext();

export const useCart = () => {
  const context = useContext(CartContext);
  if (!context) {
    throw new Error('useCart must be used within a CartProvider');
  }
  return context;
};

export const CartProvider = ({ children }) => {
  const [cart, setCart] = useState(null);
  const [loading, setLoading] = useState(false);
  const { isAuthenticated } = useAuth();

  useEffect(() => {
    if (isAuthenticated) {
      fetchCart();
    } else {
      setCart(null);
    }
  }, [isAuthenticated]);

  const fetchCart = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/api/products/cart/');
      setCart(response.data);
    } catch (error) {
      // Removed console message
    } finally {
      setLoading(false);
    }
  };

  const addToCart = async (productId, quantity = 1) => {
    try {
      const response = await axios.post('/api/products/cart/add/', {
        product_id: productId,
        quantity,
      });
      await fetchCart();
      return { success: true, data: response.data };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.error || 'Failed to add to cart',
      };
    }
  };

  const updateCartItem = async (itemId, quantity) => {
    try {
      if (quantity <= 0) {
        return await removeFromCart(itemId);
      }
      
      await axios.put(`/api/products/cart/update/${itemId}/`, {
        quantity,
      });
      await fetchCart();
      return { success: true };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.error || 'Failed to update cart item',
      };
    }
  };

  const removeFromCart = async (itemId) => {
    try {
      await axios.delete(`/api/products/cart/remove/${itemId}/`);
      await fetchCart();
      return { success: true };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.error || 'Failed to remove from cart',
      };
    }
  };

  const clearCart = async () => {
    try {
      await axios.delete('/api/products/cart/clear/');
      await fetchCart();
      return { success: true };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.error || 'Failed to clear cart',
      };
    }
  };

  const value = {
    cart,
    loading,
    addToCart,
    updateCartItem,
    removeFromCart,
    clearCart,
    fetchCart,
    itemCount: cart?.total_items || 0,
    totalPrice: cart?.total_price || 0,
  };

  return <CartContext.Provider value={value}>{children}</CartContext.Provider>;
};
