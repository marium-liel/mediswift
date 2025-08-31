import React from 'react';
import { Link } from 'react-router-dom';
import { useCart } from '../context/CartContext';
import WishlistButton from './WishlistButton';

const ProductCard = ({ product }) => {
  const { addToCart } = useCart();

  const handleAddToCart = async () => {
    await addToCart(product.id, 1);
  };

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden">
      {product.image && (
        <img
          src={product.image}
          alt={product.name}
          className="w-full h-48 object-cover"
        />
      )}
      <div className="p-4">
        <div className="flex justify-between items-start">
          <Link 
            to={`/products/${product.id}`}
            className="text-xl font-semibold hover:text-blue-600"
          >
            {product.name}
          </Link>
          <WishlistButton productId={product.id} />
        </div>
        
        <p className="text-gray-600 mt-1">{product.brand}</p>
        <p className="text-gray-700 mt-2 text-sm line-clamp-2">{product.description}</p>
        
        <div className="mt-4 flex justify-between items-center">
          <span className="text-xl font-bold text-blue-600">${product.price}</span>
          <button
            onClick={handleAddToCart}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition"
            disabled={!product.is_in_stock}
          >
            {product.is_in_stock ? 'Add to Cart' : 'Out of Stock'}
          </button>
        </div>
        
        {product.requires_prescription && (
          <p className="mt-2 text-sm text-yellow-600">
            * Prescription required
          </p>
        )}
      </div>
    </div>
  );
};

export default ProductCard;
