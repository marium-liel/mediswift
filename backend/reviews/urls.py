from django.urls import path
from .views import (
    ProductReviewListView, CreateReviewView, UserReviewListView,
    ReviewDetailView, mark_review_helpful, remove_helpful_vote,
    approve_review, hide_review
)

urlpatterns = [
    path('product/<int:product_id>/', ProductReviewListView.as_view(), name='product-reviews'),
    path('create/', CreateReviewView.as_view(), name='create-review'),
    path('my-reviews/', UserReviewListView.as_view(), name='user-reviews'),
    path('<int:pk>/', ReviewDetailView.as_view(), name='review-detail'),
    path('<int:review_id>/helpful/', mark_review_helpful, name='mark-helpful'),
    path('<int:review_id>/helpful/remove/', remove_helpful_vote, name='remove-helpful-vote'),
    path('admin/<int:review_id>/approve/', approve_review, name='approve-review'),
    path('admin/<int:review_id>/hide/', hide_review, name='hide-review'),
]
