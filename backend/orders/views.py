from django.http import HttpResponse
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta

from .models import Order, OrderItem, OrderStatusHistory
from .serializers import (
    OrderSerializer, OrderListSerializer, CreateOrderSerializer,
    UpdateOrderStatusSerializer
)
from products.models import Cart, Product, RefillSuggestion

class OrderListView(generics.ListAPIView):
    serializer_class = OrderListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_admin:
            return Order.objects.all()
        return Order.objects.filter(user=self.request.user)

class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_admin:
            return Order.objects.all()
        return Order.objects.filter(user=self.request.user)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_order(request):
    serializer = CreateOrderSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    # Get user's cart
    cart = Cart.objects.get(user=request.user)
    cart_items = cart.items.select_related('product').all()
    if not cart_items:
        return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)

    # Calculate prices
    subtotal = sum([item.product.price * item.quantity for item in cart_items])
    tax_amount = Decimal('0.00')
    delivery_fee = Decimal('0.00')
    total_amount = subtotal + tax_amount + delivery_fee

    # Create order
    order = Order.objects.create(
        user=request.user,
        delivery_address=serializer.validated_data['delivery_address'],
        phone_number=serializer.validated_data['phone_number'],
        payment_method=serializer.validated_data['payment_method'],
        subtotal=subtotal,
        tax_amount=tax_amount,
        delivery_fee=delivery_fee,
        total_amount=total_amount,
        status='delivered',  # Set status to delivered as per user request
        delivered_at=timezone.now()
    )

    # Add items to order
    for cart_item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=cart_item.product,
            quantity=cart_item.quantity,
            price=cart_item.product.price
        )

    # Optionally create refill suggestion
    for cart_item in cart_items:
        suggested_date = timezone.now().date() + timedelta(days=30)
        RefillSuggestion.objects.get_or_create(
            user=request.user,
            product=cart_item.product,
            defaults={'suggested_date': suggested_date}
        )

    # Clear cart
    cart.items.all().delete()

    return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def update_order_status(request, order_id):
    if not request.user.is_admin:
        return Response(
            {'error': 'Admin access required'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    order = get_object_or_404(Order, id=order_id)
    serializer = UpdateOrderStatusSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    new_status = serializer.validated_data['status']
    notes = serializer.validated_data.get('notes', '')
    
    # Update order status
    order.status = new_status
    if new_status == 'delivered':
        order.delivered_at = timezone.now()
    order.save()
    
    # Create status history
    OrderStatusHistory.objects.create(
        order=order,
        status=new_status,
        notes=notes,
        updated_by=request.user
    )
    
    return Response(OrderSerializer(order).data)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def reorder(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    # Add order items to cart
    for order_item in order.items.all():
        if order_item.product.is_active and not order_item.product.is_expired:
            cart_item, created = cart.items.get_or_create(
                product=order_item.product,
                defaults={'quantity': order_item.quantity}
            )
            if not created:
                cart_item.quantity += order_item.quantity
                cart_item.save()
    
    # ...existing code...
    return Response({'message': 'Items added to cart successfully'})
