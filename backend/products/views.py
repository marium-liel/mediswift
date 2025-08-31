from rest_framework import generics, status, permissions, serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.shortcuts import get_object_or_404
from django.db import models
from django.utils import timezone
from datetime import timedelta
from .models import (
    Category, Product, Cart, CartItem, RefillSuggestion, 
    WishlistItem, SaveForLater, InventoryAlert, Subscription
)
from .serializers import (
    CategorySerializer, ProductSerializer, ProductListSerializer,
    CartSerializer, CartItemSerializer, AddToCartSerializer,
    RefillSuggestionSerializer, WishlistSerializer, SaveForLaterSerializer, InventoryAlertSerializer, SubscriptionSerializer
)
from orders.models import Order, OrderItem
from accounts.models import User
from django.db.models import Sum, Count

class CategoryListView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class ProductListView(generics.ListCreateAPIView):
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductListSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'product_type', 'brand']
    search_fields = ['name', 'brand', 'description']
    ordering_fields = ['price', 'created_at', 'name']
    ordering = ['-created_at']
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        queryset = super().get_queryset()
        in_stock = self.request.query_params.get('in_stock')
        if in_stock == 'true':
            queryset = queryset.filter(stock_quantity__gt=0)
        return queryset

class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]



@api_view(['GET'])
def related_products(request, pk):
    # permissions.AllowAny is set via @api_view by default for GET
    product = get_object_or_404(Product, pk=pk, is_active=True)
    related = Product.objects.filter(
        is_active=True,
        category=product.category
    ).exclude(pk=product.pk)[:8]
    serializer = ProductListSerializer(related, many=True)
    return Response(serializer.data)
class CartView(generics.RetrieveAPIView):
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return cart

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def add_to_cart(request):
    import logging
    logger = logging.getLogger("django")
    try:
        serializer = AddToCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product_id = serializer.validated_data['product_id']
        quantity = serializer.validated_data['quantity']
        product = get_object_or_404(Product, id=product_id, is_active=True)
        cart, created = Cart.objects.get_or_create(user=request.user)
        if quantity > product.stock_quantity:
            logger.error(f"Add to cart failed: Only {product.stock_quantity} items available for product {product_id}")
            return Response(
                {'error': f'Only {product.stock_quantity} items available in stock'},
                status=status.HTTP_400_BAD_REQUEST
            )
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        if not created:
            new_quantity = cart_item.quantity + quantity
            if new_quantity > product.stock_quantity:
                logger.error(f"Add to cart failed: Cannot add more items. Only {product.stock_quantity} available for product {product_id}")
                return Response(
                    {'error': f'Cannot add more items. Only {product.stock_quantity} available'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            cart_item.quantity = new_quantity
            cart_item.save()
        logger.info(f"Add to cart success: Product {product_id}, Quantity {quantity}, User {request.user}")
        return Response(CartItemSerializer(cart_item).data, status=status.HTTP_201_CREATED)
    except Exception as e:
        logger.error(f"Add to cart exception: {str(e)}", exc_info=True)
        return Response({'error': f'Internal Server Error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT'])
@permission_classes([permissions.IsAuthenticated])
def update_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    quantity = request.data.get('quantity', 1)
    
    if quantity <= 0:
        cart_item.delete()
        return Response({'message': 'Item removed from cart'})
    
    if quantity > cart_item.product.stock_quantity:
        return Response(
            {'error': f'Only {cart_item.product.stock_quantity} items available'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    cart_item.quantity = quantity
    cart_item.save()
    
    return Response(CartItemSerializer(cart_item).data)

@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    return Response({'message': 'Item removed from cart'})

@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def clear_cart(request):
    cart = get_object_or_404(Cart, user=request.user)
    cart.items.all().delete()
    return Response({'message': 'Cart cleared'})

class RefillSuggestionListView(generics.ListAPIView):
    serializer_class = RefillSuggestionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Smart refill suggestion based on user order history
        from orders.models import Order, OrderItem
        user = self.request.user
        delivered_orders = Order.objects.filter(user=user, status='delivered').order_by('-created_at')
        product_freq = {}
        last_order_date = {}
        for order in delivered_orders:
            for item in order.items.all():
                pid = item.product_id
                product_freq[pid] = product_freq.get(pid, 0) + 1
                if pid not in last_order_date or order.created_at > last_order_date[pid]:
                    last_order_date[pid] = order.created_at
        suggestions = []
        today = timezone.now().date()
        for pid, freq in product_freq.items():
            # Suggest if last order was > 20 days ago and ordered at least twice
            if freq >= 2 and (today - last_order_date[pid].date()).days > 20:
                try:
                    product = Product.objects.get(pk=pid, is_active=True)
                    suggestions.append(product)
                except Product.DoesNotExist:
                    continue
        return suggestions

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def low_stock_products(request):
    if not request.user.is_admin:
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    
    products = Product.objects.filter(
        is_active=True,
        stock_quantity__lte=models.F('low_stock_threshold')
    )
    serializer = ProductListSerializer(products, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def expiring_products(request):
    if not request.user.is_admin:
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    
    expiry_threshold = timezone.now().date() + timedelta(days=30)
    products = Product.objects.filter(
        is_active=True,
        expiry_date__lte=expiry_threshold
    ).order_by('expiry_date')
    
    serializer = ProductListSerializer(products, many=True)
    return Response(serializer.data)

# Wishlist API
class WishlistView(generics.ListAPIView):
    serializer_class = WishlistSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return WishlistItem.objects.filter(user=self.request.user)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    wishlist_item, created = WishlistItem.objects.get_or_create(
        user=request.user,
        product=product
    )
    return Response({
        'status': 'added to wishlist',
        'product_id': product_id,
        'created': created
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def remove_from_wishlist(request, product_id):
    WishlistItem.objects.filter(
        user=request.user,
        product_id=product_id
    ).delete()
    return Response({
        'status': 'removed from wishlist',
        'product_id': product_id
    }, status=status.HTTP_200_OK)

# SaveForLater API
class SaveForLaterListCreateView(generics.ListCreateAPIView):
    serializer_class = SaveForLaterSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return SaveForLater.objects.filter(user=self.request.user)
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class SaveForLaterDeleteView(generics.DestroyAPIView):
    serializer_class = SaveForLaterSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return SaveForLater.objects.filter(user=self.request.user)

# Inventory Alerts API (admin only)
class InventoryAlertListView(generics.ListAPIView):
    serializer_class = InventoryAlertSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = InventoryAlert.objects.filter(is_resolved=False)
    
    def get_queryset(self):
        if not self.request.user.is_admin:
            return InventoryAlert.objects.none()
        return super().get_queryset()

# Admin Analytics API
from rest_framework.views import APIView

class AdminAnalyticsView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        if not request.user.is_admin:
            return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
        # Sales stats
        total_sales = Order.objects.filter(status='delivered').aggregate(total=Sum('total_amount'))['total'] or 0
        total_orders = Order.objects.filter(status='delivered').count()
        # Inventory stats
        total_products = Product.objects.count()
        low_stock = Product.objects.filter(stock_quantity__lte=10).count()
        expiring_soon = Product.objects.filter(expiry_date__lte=timezone.now()+timedelta(days=30)).count()
        # User stats
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        return Response({
            'total_sales': total_sales,
            'total_orders': total_orders,
            'total_products': total_products,
            'low_stock': low_stock,
            'expiring_soon': expiring_soon,
            'total_users': total_users,
            'active_users': active_users
        })

# Subscription API
class SubscriptionListCreateView(generics.ListCreateAPIView):
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        # Get product and validate stock availability
        product = serializer.validated_data.get('product')
        quantity = serializer.validated_data.get('quantity', 1)
        
        # Check if enough stock is available
        if product.available_stock < quantity * 3:  # Need stock for 3 deliveries
            raise serializers.ValidationError(
                f"Not enough stock available. Need {quantity * 3} units but only {product.available_stock} available."
            )
        
        # Create the subscription
        subscription = serializer.save(user=self.request.user)
        
        # Update the reserved stock for this subscription
        subscription.reserved_stock = quantity * 3
        subscription.save()
        
        # Update product's stock information
        product.update_stock_quantity()
        
        return subscription

class SubscriptionDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user)
    
    def perform_destroy(self, instance):
        try:
            product = instance.product
            # Mark subscription as inactive to trigger stock update
            instance.is_active = False
            instance.save()
            # Now delete the instance
            instance.delete()
            # Final stock update
            product.update_stock_quantity()
            product.save()
        except Exception as e:
            print(f"Error in perform_destroy: {str(e)}")
            raise
        
    def perform_update(self, serializer):
        try:
            old_instance = self.get_object()
            instance = serializer.save()
            # If subscription status changed, update product stock
            if old_instance.is_active != instance.is_active:
                instance.product.update_stock_quantity()
                instance.product.save()
        except Exception as e:
            print(f"Error in perform_update: {str(e)}")
            raise
