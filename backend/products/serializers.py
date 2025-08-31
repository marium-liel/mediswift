from rest_framework import serializers
from .models import (
    Category, Product, Cart, CartItem, RefillSuggestion,
    WishlistItem, SaveForLater, InventoryAlert, Subscription
)

class SubscriptionSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_brand = serializers.CharField(source='product.brand', read_only=True)
    product_stock = serializers.IntegerField(source='product.stock_quantity', read_only=True)
    product_available_stock = serializers.IntegerField(source='product.available_stock', read_only=True)
    product_reserved_quantity = serializers.IntegerField(source='product.reserved_quantity', read_only=True)
    upcoming_deliveries = serializers.SerializerMethodField()
    product_id = serializers.IntegerField(source='product.id', read_only=True)
    
    def get_upcoming_deliveries(self, obj):
        return obj.calculate_next_deliveries(num_dates=5) if obj.is_active else []
    
    class Meta:
        model = Subscription
        fields = [
            'id', 'user', 'product', 'product_id', 'product_name', 'product_brand', 
            'product_stock', 'product_available_stock', 'product_reserved_quantity',
            'quantity', 'frequency', 'next_delivery', 'is_active', 'created_at',
            'updated_at', 'upcoming_deliveries', 'reserved_stock'
        ]
        read_only_fields = ['user', 'reserved_stock']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ProductListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    is_in_stock = serializers.ReadOnlyField()
    average_rating = serializers.ReadOnlyField()
    review_count = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'brand', 'category_name', 'price',
            'stock_quantity', 'is_in_stock', 'image',
            'average_rating', 'review_count'
        ]

class WishlistSerializer(serializers.ModelSerializer):
    product = ProductListSerializer()

    class Meta:
        model = WishlistItem
        fields = ['id', 'product', 'created_at']

class ProductSerializer(serializers.ModelSerializer):
    average_rating = serializers.ReadOnlyField()
    review_count = serializers.ReadOnlyField()
    is_in_stock = serializers.ReadOnlyField()
    is_low_stock = serializers.ReadOnlyField()
    is_expired = serializers.ReadOnlyField()
    days_to_expiry = serializers.ReadOnlyField()
    category_name = serializers.CharField(source='category.name', read_only=True)
    available_stock = serializers.ReadOnlyField()
    reserved_quantity = serializers.ReadOnlyField()
    subscription_count = serializers.SerializerMethodField()
    
    def get_subscription_count(self, obj):
        return obj.subscription_set.filter(is_active=True).count()
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'brand', 'category', 'category_name', 'product_type',
                 'description', 'dosage', 'precautions', 'price', 'stock_quantity',
                 'reserved_quantity', 'available_stock', 'low_stock_threshold',
                 'expiry_date', 'image', 'is_active', 'requires_prescription',
                 'created_at', 'updated_at', 'average_rating', 'review_count',
                 'is_in_stock', 'is_low_stock', 'is_expired', 'days_to_expiry',
                 'subscription_count']

class ProductListSerializer(serializers.ModelSerializer):
    average_rating = serializers.ReadOnlyField()
    review_count = serializers.ReadOnlyField()
    is_in_stock = serializers.ReadOnlyField()
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'brand', 'category_name', 'product_type', 'description', 'price', 
                 'stock_quantity', 'image', 'average_rating', 'review_count', 'is_in_stock']

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    total_price = serializers.ReadOnlyField()
    
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_id', 'quantity', 'total_price', 'created_at']

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.ReadOnlyField()
    total_price = serializers.ReadOnlyField()
    
    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_items', 'total_price', 'created_at', 'updated_at']

class AddToCartSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, default=1)
    
    def validate_product_id(self, value):
        try:
            product = Product.objects.get(id=value, is_active=True)
            if product.is_expired:
                raise serializers.ValidationError("This product has expired")
            if not product.is_in_stock:
                raise serializers.ValidationError("This product is out of stock")
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found")
        return value

class RefillSuggestionSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    
    class Meta:
        model = RefillSuggestion
        fields = ['id', 'product', 'suggested_date', 'is_active', 'created_at']



class SaveForLaterSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaveForLater
        fields = ['id', 'user', 'product', 'added_at']
        read_only_fields = ['user']

class InventoryAlertSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    class Meta:
        model = InventoryAlert
        fields = ['id', 'product', 'product_name', 'alert_type', 'message', 'created_at', 'is_resolved']
