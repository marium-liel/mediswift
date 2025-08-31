from django.urls import path
from . import views
from . import admin_views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('profile/', views.UserProfileView.as_view(), name='user-profile'),
    path('orders/', views.UserOrderHistoryView.as_view(), name='user-orders'),
    path('logout/', views.logout_view, name='logout'),
    
    # Admin endpoints
    path('admin/stats/', admin_views.admin_stats, name='admin-stats'),
    path('admin/orders/', admin_views.admin_orders, name='admin-orders'),
    path('admin/orders/<int:order_id>/status/', admin_views.update_order_status, name='update-order-status'),

    path('admin/users/', admin_views.admin_users, name='admin-users'),
    path('admin/users/<int:user_id>/status/', admin_views.update_user_status, name='update-user-status'),
    path('admin/users/<int:user_id>/type/', admin_views.update_user_type, name='update-user-type'),
]
