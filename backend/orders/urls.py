from django.urls import path
from .views import (
    OrderListView, OrderDetailView, create_order, 
    update_order_status, reorder
)

urlpatterns = [
    path('', OrderListView.as_view(), name='order-list'),
    path('<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('create/', create_order, name='create-order'),
    path('<int:order_id>/update-status/', update_order_status, name='update-order-status'),
    path('<int:order_id>/reorder/', reorder, name='reorder'),
]
