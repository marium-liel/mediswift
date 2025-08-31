/*
 * USERS MANAGEMENT COMPONENT - ADMIN USER CONTROL SYSTEM
 * 
 * This component demonstrates:
 * 1. User administration functionality in React
 * 2. Real-time user status updates via Django API
 * 3. Role-based access control (customer vs admin)
 * 4. Interactive table with inline editing capabilities
 * 5. Optimistic UI updates for better user experience
 * 
 * DJANGO INTEGRATION:
 * - Fetches user list from Django User model via REST API
 * - Updates user status (active/inactive) through Django endpoints
 * - Manages user roles (customer/admin) with Django permissions
 * - Uses JWT authentication for admin-only operations
 */

import React, { useState, useEffect } from 'react';

const UsersManagement = () => {
    /*
     * COMPONENT STATE MANAGEMENT
     * 
     * This component manages three key pieces of state:
     * - users: Array of all users fetched from Django backend
     * - loading: Boolean to show loading spinner during API calls
     * - selectedUser: Currently selected user (for future modal/detail view)
     */
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [selectedUser, setSelectedUser] = useState(null);

    /*
     * COMPONENT LIFECYCLE - FETCH USERS ON MOUNT
     * 
     * When component first loads, fetch all users from Django backend.
     * This demonstrates the typical pattern of loading data when component mounts.
     */
    useEffect(() => {
        fetchUsers();
    }, []);

    /*
     * FETCH USERS FROM DJANGO BACKEND
     * 
     * This function demonstrates:
     * 1. Making authenticated API calls to Django
     * 2. Handling async operations with try/catch
     * 3. Updating component state with fetched data
     * 4. Managing loading states for better UX
     */
    const fetchUsers = async () => {
        try {
            // Call Django admin endpoint to get all users
            const response = await fetch('/api/accounts/admin/users/', {
                headers: {
                    // JWT token required for admin operations
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                },
            });
            
            if (response.ok) {
                const data = await response.json();
                // Update component state with user data from Django
                setUsers(data);
            }
        } catch (error) {
            // Silent error handling - could show user notification in production
        } finally {
            // Always stop loading, whether success or error
            setLoading(false);
        }
    };

    /*
     * UPDATE USER STATUS (ACTIVATE/DEACTIVATE)
     * 
     * This function demonstrates:
     * 1. Making PUT requests to update Django User model
     * 2. Sending JSON data to Django REST API
     * 3. Optimistic UI updates (refresh data after successful update)
     * 4. Admin functionality for user account management
     */
    const updateUserStatus = async (userId, isActive) => {
        try {
            // Send PUT request to Django to update user's active status
            const response = await fetch(`/api/accounts/admin/users/${userId}/status/`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                },
                // Send new status as JSON to Django
                body: JSON.stringify({ is_active: isActive }),
            });
            
            if (response.ok) {
                // Refresh user list to show updated status
                fetchUsers();
            }
        } catch (error) {
            // Silent error handling
        }
    };

    /*
     * UPDATE USER TYPE (CUSTOMER/ADMIN ROLE)
     * 
     * This function manages user roles and permissions:
     * 1. Updates user_type field in Django User model
     * 2. Controls access levels (customer vs admin privileges)
     * 3. Demonstrates role-based access control implementation
     * 4. Shows how to update specific fields via REST API
     */
    const updateUserType = async (userId, userType) => {
        try {
            // Send PUT request to update user's role/type
            const response = await fetch(`/api/accounts/admin/users/${userId}/type/`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                },
                // Send new user type to Django
                body: JSON.stringify({ user_type: userType }),
            });
            
            if (response.ok) {
                // Refresh user list to reflect role changes
                fetchUsers();
            }
        } catch (error) {
            // Silent error handling
        }
    };

    // Loading state - show spinner while fetching users
    if (loading) {
        return (
            <div className="flex justify-center items-center min-h-screen">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
        );
    }

    /*
     * MAIN COMPONENT RENDER - INTERACTIVE USER TABLE
     * 
     * This renders a comprehensive user management interface with:
     * 1. Tabular display of all users from Django
     * 2. Inline editing for user roles (dropdown selection)
     * 3. Status indicators with conditional styling
     * 4. Action buttons for user activation/deactivation
     * 5. Responsive design with Tailwind CSS
     */
    return (
        <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-2xl font-semibold text-gray-800 mb-6">Users Management</h2>
            
            {/* RESPONSIVE TABLE - Shows all users with management controls */}
            <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                    {/* TABLE HEADER */}
                    <thead className="bg-gray-50">
                        <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">User</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Email</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                        </tr>
                    </thead>
                    
                    {/* TABLE BODY - Dynamic rows for each user */}
                    <tbody className="bg-white divide-y divide-gray-200">
                        {/* 
                         * ARRAY MAPPING - Render each user from Django data
                         * 
                         * This maps over the users array and creates a table row for each user.
                         * Each row contains user information and interactive controls.
                         */}
                        {users.map((user) => (
                            <tr key={user.id}>
                                {/* USER NAME COLUMN */}
                                <td className="px-6 py-4 whitespace-nowrap">
                                    <div className="flex items-center">
                                        <div className="ml-4">
                                            <div className="text-sm font-medium text-gray-900">{user.username}</div>
                                        </div>
                                    </div>
                                </td>
                                
                                {/* EMAIL COLUMN */}
                                <td className="px-6 py-4 whitespace-nowrap">
                                    <div className="text-sm text-gray-900">{user.email}</div>
                                </td>
                                
                                {/* USER TYPE COLUMN - INLINE EDITING WITH DROPDOWN */}
                                <td className="px-6 py-4 whitespace-nowrap">
                                    {/* 
                                     * CONTROLLED SELECT INPUT
                                     * 
                                     * This dropdown allows admins to change user roles instantly.
                                     * - value: Current user type from Django data
                                     * - onChange: Calls updateUserType function when changed
                                     * - Demonstrates inline editing without separate forms
                                     */}
                                    <select
                                        value={user.user_type}
                                        onChange={(e) => updateUserType(user.id, e.target.value)}
                                        className="rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                                    >
                                        <option value="customer">Customer</option>
                                        <option value="admin">Admin</option>
                                    </select>
                                </td>
                                
                                {/* STATUS COLUMN - VISUAL STATUS INDICATOR */}
                                <td className="px-6 py-4 whitespace-nowrap">
                                    {/* 
                                     * CONDITIONAL STYLING - Status badge with dynamic colors
                                     * 
                                     * Shows green for active users, red for inactive users.
                                     * This provides immediate visual feedback about user status.
                                     */}
                                    <span className={`px-2 py-1 text-xs rounded-full ${
                                        user.is_active
                                            ? 'bg-green-100 text-green-800'  // Active user styling
                                            : 'bg-red-100 text-red-800'      // Inactive user styling
                                    }`}>
                                        {user.is_active ? 'Active' : 'Inactive'}
                                    </span>
                                </td>
                                
                                {/* ACTIONS COLUMN - USER MANAGEMENT BUTTONS */}
                                <td className="px-6 py-4 whitespace-nowrap">
                                    {/* 
                                     * TOGGLE BUTTON - Activate/Deactivate Users
                                     * 
                                     * This button toggles user status and updates Django backend.
                                     * - onClick: Calls updateUserStatus with opposite of current status
                                     * - Dynamic styling: Red for deactivate, green for activate
                                     * - Dynamic text: Changes based on current user status
                                     */}
                                    <button
                                        onClick={() => updateUserStatus(user.id, !user.is_active)}
                                        className={`px-3 py-1 rounded-md ${
                                            user.is_active
                                                ? 'bg-red-100 text-red-600 hover:bg-red-200'    // Deactivate button
                                                : 'bg-green-100 text-green-600 hover:bg-green-200' // Activate button
                                        }`}
                                    >
                                        {user.is_active ? 'Deactivate' : 'Activate'}
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default UsersManagement;
