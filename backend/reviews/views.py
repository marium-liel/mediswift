from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Review, ReviewHelpful
from .serializers import ReviewSerializer, CreateReviewSerializer, ReviewHelpfulSerializer
from products.models import Product

# Admin: Approve review
@api_view(['POST'])
@permission_classes([IsAdminUser])
def approve_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    review.is_approved = True
    review.save()
    return Response({'message': 'Review approved'})

# Admin: Hide review
@api_view(['POST'])
@permission_classes([IsAdminUser])
def hide_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    review.is_approved = False
    review.save()
    return Response({'message': 'Review hidden'})

class ProductReviewListView(generics.ListAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        product_id = self.kwargs['product_id']
        return Review.objects.filter(product_id=product_id, is_approved=True)

class CreateReviewView(generics.CreateAPIView):
    serializer_class = CreateReviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        image = self.request.FILES.get('image')
        video = self.request.FILES.get('video')
        serializer.save(user=self.request.user, image=image, video=video)

class UserReviewListView(generics.ListAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Review.objects.filter(user=self.request.user)

class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Review.objects.filter(user=self.request.user)
    
    def perform_update(self, serializer):
        image = self.request.FILES.get('image')
        video = self.request.FILES.get('video')
        serializer.save(image=image, video=video)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_review_helpful(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    serializer = ReviewHelpfulSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    is_helpful = serializer.validated_data['is_helpful']
    
    # Update or create helpful vote
    helpful_vote, created = ReviewHelpful.objects.update_or_create(
        user=request.user,
        review=review,
        defaults={'is_helpful': is_helpful}
    )
    
    return Response({
        'message': 'Vote recorded successfully',
        'is_helpful': is_helpful
    })

@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def remove_helpful_vote(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    
    try:
        helpful_vote = ReviewHelpful.objects.get(user=request.user, review=review)
        helpful_vote.delete()
        return Response({'message': 'Vote removed successfully'})
    except ReviewHelpful.DoesNotExist:
        return Response(
            {'error': 'No vote found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
