from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count, Sum
from orders.models import Order
from products.models import Product
from .models import User
from orders.serializers import OrderSerializer
from products.serializers import ProductSerializer
from accounts.serializers import UserSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_stats(request):
    # Check if user is admin
    if not request.user.user_type == 'admin':
        return Response(
            {'error': 'You do not have permission to access this resource'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Get statistics
    total_orders = Order.objects.count()
    total_products = Product.objects.count()
    total_users = User.objects.count()
    
    # Get recent orders
    recent_orders = Order.objects.order_by('-created_at')[:5].values(
        'id', 
        'user__username', 
        'total_amount',
        'status',
        'created_at'
    )
    
    # Convert the orders to a list and format the data
    recent_orders_list = [
        {
            'id': order['id'],
            'customer_name': order['user__username'],
            'total_amount': order['total_amount'],
            'status': order['status'],
            'date': order['created_at'].strftime('%Y-%m-%d %H:%M:%S')
        }
        for order in recent_orders
    ]
    
    # Get recent products
    recent_products = Product.objects.order_by('-created_at')[:5]
    
    return Response({
        'totalOrders': total_orders,
        'totalProducts': total_products,
        'totalUsers': total_users,
        'recentOrders': recent_orders_list,
        'recentProducts': ProductSerializer(recent_products, many=True).data
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_orders(request):
    if not request.user.user_type == 'admin':
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    orders = Order.objects.all().order_by('-created_at')
    return Response(OrderSerializer(orders, many=True).data)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_order_status(request, order_id):
    if not request.user.user_type == 'admin':
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        order = Order.objects.get(id=order_id)
        order.status = request.data.get('status', order.status)
        order.save()
        return Response(OrderSerializer(order).data)
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_users(request):
    if not request.user.user_type == 'admin':
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    users = User.objects.all()
    return Response(UserSerializer(users, many=True).data)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_user_status(request, user_id):
    if not request.user.user_type == 'admin':
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        user = User.objects.get(id=user_id)
        user.is_active = request.data.get('is_active', user.is_active)
        user.save()
        return Response(UserSerializer(user).data)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_user_type(request, user_id):
    if not request.user.user_type == 'admin':
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        user = User.objects.get(id=user_id)
        user.user_type = request.data.get('user_type', user.user_type)
        user.save()
        return Response(UserSerializer(user).data)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
