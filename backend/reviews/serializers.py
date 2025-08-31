from rest_framework import serializers
from .models import Review, ReviewHelpful
from products.models import Product
from orders.models import OrderItem

class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    helpful_count = serializers.SerializerMethodField()
    not_helpful_count = serializers.SerializerMethodField()
    user_helpful_vote = serializers.SerializerMethodField()
    
    is_approved = serializers.BooleanField(read_only=True)
    image = serializers.ImageField(required=False, allow_null=True)
    video = serializers.FileField(required=False, allow_null=True)
    class Meta:
        model = Review
        fields = ['id', 'user_name', 'rating', 'title', 'comment', 'is_verified_purchase', 
                 'created_at', 'helpful_count', 'not_helpful_count', 'user_helpful_vote', 'is_approved', 'image', 'video']
        read_only_fields = ['user', 'is_verified_purchase', 'created_at', 'is_approved']
    
    def get_helpful_count(self, obj):
        return obj.helpful_votes.filter(is_helpful=True).count()
    
    def get_not_helpful_count(self, obj):
        return obj.helpful_votes.filter(is_helpful=False).count()
    
    def get_user_helpful_vote(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                vote = obj.helpful_votes.get(user=request.user)
                return vote.is_helpful
            except ReviewHelpful.DoesNotExist:
                return None
        return None

class CreateReviewSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(write_only=True)
    
    image = serializers.ImageField(required=False, allow_null=True)
    video = serializers.FileField(required=False, allow_null=True)
    class Meta:
        model = Review
        fields = ['product_id', 'rating', 'title', 'comment', 'image', 'video']
    
    def validate_product_id(self, value):
        try:
            Product.objects.get(id=value, is_active=True)
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found")
        return value
    
    def validate(self, attrs):
        user = self.context['request'].user
        product_id = attrs['product_id']
        
        # Check if user already reviewed this product
        if Review.objects.filter(user=user, product_id=product_id).exists():
            raise serializers.ValidationError("You have already reviewed this product")
        
        return attrs
    
    def create(self, validated_data):
        user = self.context['request'].user
        product_id = validated_data.pop('product_id')
        product = Product.objects.get(id=product_id)
        # Remove user from validated_data if present
        validated_data.pop('user', None)
        # Check if this is a verified purchase
        is_verified = OrderItem.objects.filter(
            order__user=user,
            product=product,
            order__status='delivered'
        ).exists()
        review = Review.objects.create(
            user=user,
            product=product,
            is_verified_purchase=is_verified,
            **validated_data
        )
        return review

class ReviewHelpfulSerializer(serializers.Serializer):
    is_helpful = serializers.BooleanField()
