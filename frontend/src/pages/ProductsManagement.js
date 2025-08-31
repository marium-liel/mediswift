/*
 * PRODUCTS MANAGEMENT COMPONENT - REACT + DJANGO INTEGRATION
 * 
 * This is a React functional component that manages products in the MediSwift platform.
 * It demonstrates key React concepts and Django REST API integration.
 * 
 * KEY REACT CONCEPTS USED:
 * 1. useState Hook - Manages component state (local data that can change)
 * 2. useEffect Hook - Handles side effects (API calls when component loads)
 * 3. Event Handlers - Functions that respond to user interactions
 * 4. Conditional Rendering - Shows different UI based on state
 * 5. Form Handling - Manages user input and form submission
 * 6. Component Lifecycle - How component mounts, updates, and unmounts
 * 
 * DJANGO API INTEGRATION:
 * - Uses Django REST Framework endpoints for CRUD operations
 * - Handles authentication with JWT tokens
 * - Manages file uploads (images) with FormData
 * - Error handling for API responses
 */

// React imports - these are essential React features we need
import React, { useState, useEffect } from 'react';

const ProductsManagement = () => {
    /*
     * REACT STATE MANAGEMENT WITH useState HOOK
     * 
     * useState is a React Hook that lets you add state to functional components.
     * State is data that can change over time and affects what the component displays.
     * 
     * Syntax: const [stateVariable, setterFunction] = useState(initialValue);
     * - stateVariable: current value of the state
     * - setterFunction: function to update the state
     * - initialValue: what the state starts as
     */
    
    // Array to store all products fetched from Django backend
    const [products, setProducts] = useState([]);
    
    // Boolean to track if data is still loading from the server
    const [loading, setLoading] = useState(true);
    
    // Object to store product being edited (null when not editing)
    const [editProduct, setEditProduct] = useState(null);
    
    // Object to store new product form data with default empty values
    const [newProduct, setNewProduct] = useState({
        name: '',
        brand: '',
        category: '',
        product_type: '',
        description: '',
        price: '',
        stock_quantity: '',
        expiry_date: '',
        image: '',
        is_active: true
    });
    
    // String to store and display error messages to users
    const [errorMsg, setErrorMsg] = useState('');

    /*
     * REACT useEffect HOOK - COMPONENT LIFECYCLE MANAGEMENT
     * 
     * useEffect runs side effects in functional components.
     * Side effects are operations that affect something outside the component:
     * - API calls, timers, DOM manipulation, subscriptions
     * 
     * Syntax: useEffect(effectFunction, dependencyArray)
     * - effectFunction: code to run
     * - dependencyArray: when to run the effect
     *   - [] (empty): run once when component mounts
     *   - [variable]: run when variable changes
     *   - no array: run after every render
     */
    useEffect(() => {
        // This runs once when component first loads (mounts)
        fetchProducts();
    }, []); // Empty dependency array means "run once on mount"

    /*
     * API FUNCTION - FETCH PRODUCTS FROM DJANGO BACKEND
     * 
     * This function demonstrates:
     * 1. Async/await for handling asynchronous operations
     * 2. Fetch API for making HTTP requests to Django
     * 3. JWT authentication with Bearer token
     * 4. Error handling with try/catch
     * 5. State updates with setter functions
     */
    const fetchProducts = async () => {
        try {
            // Make GET request to Django REST API endpoint
            const response = await fetch('/api/products/admin/products/', {
                headers: {
                    // Send JWT token for authentication (stored in browser's localStorage)
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                }
            });
            
            // Check if request was successful (status 200-299)
            if (response.ok) {
                // Convert response to JSON format
                const data = await response.json();
                // Update products state with fetched data
                setProducts(data);
            }
        } catch (error) {
            // Silent error handling - could log to console or show user message
        } finally {
            // This runs whether success or error - stop loading indicator
            setLoading(false);
        }
    };

    /*
     * FORM SUBMISSION HANDLER - CREATE/UPDATE PRODUCTS
     * 
     * This function handles both creating new products and updating existing ones.
     * It demonstrates:
     * 1. Event handling (e.preventDefault() stops form's default behavior)
     * 2. Form validation (checking required fields)
     * 3. File upload handling with FormData vs JSON
     * 4. HTTP POST (create) vs PUT (update) requests
     * 5. Error handling and user feedback
     */
    const handleSubmit = async (e) => {
        // Prevent form's default submit behavior (page refresh)
        e.preventDefault();
        
        // Determine if we're editing existing product or creating new one
        let productData = editProduct ? editProduct : newProduct;
        
        // CLIENT-SIDE VALIDATION - Check required fields before sending to server
        const requiredFields = ['name', 'brand', 'category', 'product_type', 'description', 'price', 'stock_quantity', 'expiry_date'];
        const missingFields = requiredFields.filter(field => !productData[field]);
        
        if (missingFields.length > 0) {
            // Show error message to user if required fields are missing
            setErrorMsg(`Missing required fields: ${missingFields.join(', ')}`);
            return; // Exit function early
        }

        // AUTO-GENERATE IMAGE URL if no image provided (using Unsplash API)
        if (!productData.image) {
            const query = encodeURIComponent(productData.name || 'medicine');
            productData = {
                ...productData, // Spread operator - copies all existing properties
                image: `https://source.unsplash.com/400x400/?${query}` // Add/override image property
            };
        }

        // DETERMINE REQUEST FORMAT - FormData for files, JSON for text-only
        const hasFileUpload = productData.image instanceof File;
        
        let requestBody;
        let headers = {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        };

        if (hasFileUpload) {
            // Use FormData for file uploads (multipart/form-data)
            const formData = new FormData();
            Object.keys(productData).forEach(key => {
                if (productData[key] !== null && productData[key] !== undefined) {
                    formData.append(key, productData[key]);
                }
            });
            requestBody = formData;
            // Don't set Content-Type header - browser sets it automatically for FormData
        } else {
            // Use JSON for text-only updates (application/json)
            headers['Content-Type'] = 'application/json';
            requestBody = JSON.stringify(productData);
        }

        try {
            // Make HTTP request to Django API
            const response = await fetch(
                // Dynamic URL - different endpoints for create vs update
                editProduct ? `/api/products/admin/products/${editProduct.id}/` : '/api/products/admin/products/',
                {
                    method: editProduct ? 'PUT' : 'POST', // PUT for update, POST for create
                    headers: headers,
                    body: requestBody
                }
            );
            
            if (response.ok) {
                // SUCCESS - Refresh product list and reset form
                fetchProducts(); // Re-fetch all products from server
                
                if (editProduct) {
                    // Close edit modal
                    setEditProduct(null);
                } else {
                    // Reset new product form to empty state
                    setNewProduct({
                        name: '',
                        brand: '',
                        category: '',
                        product_type: '',
                        description: '',
                        price: '',
                        stock_quantity: '',
                        expiry_date: '',
                        image: '',
                        is_active: true
                    });
                }
                setErrorMsg(''); // Clear any previous error messages
            } else {
                // ERROR HANDLING - Parse and display server error messages
                const errorText = await response.text();
                try {
                    const errorData = JSON.parse(errorText);
                    if (typeof errorData === 'string') {
                        setErrorMsg(errorData);
                    } else if (errorData.error) {
                        setErrorMsg(errorData.error);
                    } else if (typeof errorData === 'object') {
                        // Handle Django form validation errors (field-specific errors)
                        setErrorMsg(Object.values(errorData).flat().join(' '));
                    } else {
                        setErrorMsg('Failed to save product.');
                    }
                } catch (parseError) {
                    // If response isn't valid JSON, show HTTP status
                    setErrorMsg(`Server error: ${response.status} ${response.statusText}`);
                }
            }
        } catch (error) {
            // Network error (server unreachable, internet down, etc.)
            setErrorMsg('Network error or server unavailable.');
        }
    };

    /*
     * DELETE PRODUCT HANDLER
     * 
     * This function demonstrates:
     * 1. HTTP DELETE request to Django API
     * 2. Optimistic UI updates (refresh list after successful delete)
     * 3. Silent error handling
     */
    const handleDelete = async (productId) => {
        try {
            // Send DELETE request to Django API with product ID in URL
            const response = await fetch(`/api/products/admin/products/${productId}/`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                }
            });
            
            if (response.ok) {
                // SUCCESS - Refresh product list to remove deleted item
                fetchProducts();
            }
        } catch (error) {
            // Silent error handling - in production, might want to show user feedback
        }
    };

    /*
     * CONDITIONAL RENDERING - LOADING STATE
     * 
     * React allows you to return different JSX based on component state.
     * This shows a loading spinner while data is being fetched from Django.
     */
    if (loading) {
        return (
            <div className="flex justify-center items-center min-h-screen">
                {/* Tailwind CSS classes for styling - creates animated spinner */}
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
        );
    }

    /*
     * MAIN COMPONENT RENDER - JSX (JavaScript XML)
     * 
     * JSX allows you to write HTML-like syntax in JavaScript.
     * Key differences from HTML:
     * - className instead of class
     * - camelCase for attributes (onClick, onChange)
     * - JavaScript expressions in curly braces {}
     * - Self-closing tags must have />
     */
    return (
        <div className="bg-white rounded-lg shadow p-6">
            {/* CONDITIONAL RENDERING - Show error message if exists */}
            {errorMsg && (
                <div className="mb-4 p-2 bg-red-100 text-red-700 rounded">{errorMsg}</div>
            )}
            
            <div className="mb-8">
                <h2 className="text-2xl font-semibold text-gray-800 mb-6">Products Management</h2>
                
                {/* 
                 * FORM HANDLING IN REACT
                 * 
                 * React uses "controlled components" where form inputs are controlled by state.
                 * - value prop connects input to state
                 * - onChange prop updates state when user types
                 * - onSubmit prop handles form submission
                 */}
                <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-4 p-4 bg-gray-50 rounded-lg mb-6">
                    <div>
                        <label className="block text-sm font-medium text-gray-700">Name</label>
                        <input
                            type="text"
                            // Controlled input - value from state
                            value={newProduct.name || ''}
                            // Update state on change
                            onChange={(e) => setNewProduct({...newProduct, name: e.target.value})}
                            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                            required
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700">Brand</label>
                        <input
                            type="text"
                            value={newProduct.brand || ''}
                            onChange={(e) => setNewProduct({...newProduct, brand: e.target.value})}
                            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                            required
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700">Category ID</label>
                        <input
                            type="number"
                            value={newProduct.category || ''}
                            onChange={(e) => setNewProduct({...newProduct, category: e.target.value})}
                            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                            required
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700">Product Type</label>
                        <select
                            value={newProduct.product_type || ''}
                            onChange={(e) => setNewProduct({...newProduct, product_type: e.target.value})}
                            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                            required
                        >
                            <option value="">Select type</option>
                            <option value="medicine">Medicine</option>
                            <option value="supplement">Supplement</option>
                        </select>
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700">Price</label>
                        <input
                            type="number"
                            step="0.01"
                            value={newProduct.price || ''}
                            onChange={(e) => setNewProduct({...newProduct, price: e.target.value})}
                            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                            required
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700">Stock Quantity</label>
                        <input
                            type="number"
                            value={newProduct.stock_quantity || ''}
                            onChange={(e) => setNewProduct({...newProduct, stock_quantity: e.target.value})}
                            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                            required
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700">Expiry Date</label>
                        <input
                            type="date"
                            value={newProduct.expiry_date || ''}
                            onChange={(e) => setNewProduct({...newProduct, expiry_date: e.target.value})}
                            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                            required
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700">Product Image</label>
                        <input
                            type="file"
                            accept="image/*"
                            onChange={(e) => setNewProduct({...newProduct, image: e.target.files[0]})}
                            className="mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                        />
                    </div>
                    <div className="md:col-span-2">
                        <label className="block text-sm font-medium text-gray-700">Description</label>
                        <textarea
                            value={newProduct.description || ''}
                            onChange={(e) => setNewProduct({...newProduct, description: e.target.value})}
                            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                            rows="3"
                            required
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700">Active</label>
                        <input
                            type="checkbox"
                            checked={newProduct.is_active || false}
                            onChange={(e) => setNewProduct({...newProduct, is_active: e.target.checked})}
                            className="mt-1"
                        />
                    </div>
                    <div className="md:col-span-2">
                        <button
                            type="submit"
                            className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                        >
                            Add New Product
                        </button>
                    </div>
                </form>
            </div>

            {/* Products List */}
            <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                        <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Image</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Price</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Stock</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                        </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                        {products.map((product) => (
                            <tr key={product.id}>
                                <td className="px-6 py-4 whitespace-nowrap">
                                    <img
                                        src={product.image}
                                        alt={product.name}
                                        className="h-16 w-16 object-cover rounded"
                                    />
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap">{product.name}</td>
                                <td className="px-6 py-4 whitespace-nowrap">${product.price}</td>
                                <td className="px-6 py-4 whitespace-nowrap">{product.stock_quantity}</td>
                                <td className="px-6 py-4 whitespace-nowrap">
                                    <button
                                        onClick={() => setEditProduct({
                                            ...product,
                                            category: product.category?.toString() || '',
                                            price: product.price?.toString() || '',
                                            stock_quantity: product.stock_quantity?.toString() || ''
                                        })}
                                        className="text-blue-600 hover:text-blue-900 mr-4"
                                    >
                                        Edit
                                    </button>
                                    <button
                                        onClick={() => handleDelete(product.id)}
                                        className="text-red-600 hover:text-red-900"
                                    >
                                        Delete
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {/* Edit Product Modal */}
            {editProduct && (
                <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full">
                    <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
                        <div className="flex justify-between items-center mb-4">
                            <h3 className="text-lg font-medium">Edit Product</h3>
                            <button
                                onClick={() => setEditProduct(null)}
                                className="text-gray-500 hover:text-gray-700"
                            >
                                ×
                            </button>
                        </div>
                        <form onSubmit={handleSubmit}>
                            <div className="space-y-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700">Name</label>
                                    <input
                                        type="text"
                                        value={editProduct.name || ''}
                                        onChange={(e) => setEditProduct({
                                            ...editProduct,
                                            name: e.target.value
                                        })}
                                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                                        required
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700">Brand</label>
                                    <input
                                        type="text"
                                        value={editProduct.brand || ''}
                                        onChange={(e) => setEditProduct({
                                            ...editProduct,
                                            brand: e.target.value
                                        })}
                                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                                        required
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700">Category ID</label>
                                    <input
                                        type="number"
                                        value={editProduct.category || ''}
                                        onChange={(e) => setEditProduct({
                                            ...editProduct,
                                            category: e.target.value
                                        })}
                                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                                        required
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700">Product Type</label>
                                    <select
                                        value={editProduct.product_type || ''}
                                        onChange={(e) => setEditProduct({
                                            ...editProduct,
                                            product_type: e.target.value
                                        })}
                                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                                        required
                                    >
                                        <option value="">Select type</option>
                                        <option value="medicine">Medicine</option>
                                        <option value="supplement">Supplement</option>
                                    </select>
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700">Price</label>
                                    <input
                                        type="number"
                                        step="0.01"
                                        value={editProduct.price || ''}
                                        onChange={(e) => setEditProduct({
                                            ...editProduct,
                                            price: e.target.value
                                        })}
                                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                                        required
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700">Stock Quantity</label>
                                    <input
                                        type="number"
                                        value={editProduct.stock_quantity || ''}
                                        onChange={(e) => setEditProduct({
                                            ...editProduct,
                                            stock_quantity: e.target.value
                                        })}
                                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                                        required
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700">Expiry Date</label>
                                    <input
                                        type="date"
                                        value={editProduct.expiry_date || ''}
                                        onChange={(e) => setEditProduct({
                                            ...editProduct,
                                            expiry_date: e.target.value
                                        })}
                                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                                        required
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700">Product Image</label>
                                    <div className="mt-1 flex items-center">
                                        {editProduct.image && typeof editProduct.image === 'string' && (
                                            <div className="mb-2">
                                                <img
                                                    src={editProduct.image}
                                                    alt="Current"
                                                    className="h-20 w-20 object-cover rounded"
                                                />
                                            </div>
                                        )}
                                    </div>
                                    <input
                                        type="file"
                                        accept="image/*"
                                        onChange={(e) => setEditProduct({
                                            ...editProduct,
                                            image: e.target.files[0]
                                        })}
                                        className="mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700">Description</label>
                                    <textarea
                                        value={editProduct.description || ''}
                                        onChange={(e) => setEditProduct({
                                            ...editProduct,
                                            description: e.target.value
                                        })}
                                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                                        rows="3"
                                        required
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700">Active</label>
                                    <input
                                        type="checkbox"
                                        checked={editProduct.is_active || false}
                                        onChange={(e) => setEditProduct({
                                            ...editProduct,
                                            is_active: e.target.checked
                                        })}
                                        className="mt-1"
                                    />
                                </div>
                            </div>
                            <div className="mt-4 flex justify-end">
                                <button
                                    type="button"
                                    onClick={() => setEditProduct(null)}
                                    className="mr-2 px-4 py-2 text-gray-500 hover:text-gray-700"
                                >
                                    Cancel
                                </button>
                                <button
                                    type="submit"
                                    className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                                >
                                    Save Changes
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
};

export default ProductsManagement;
