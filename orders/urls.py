from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('orders/', views.order_list, name='order_list'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('order/<int:order_id>/pdf/', views.download_order_pdf, name='download_order_pdf'),
    path('smart-refills/', views.smart_refills, name='smart_refills'),
    path('quick-reorder/<int:product_id>/', views.quick_reorder, name='quick_reorder'),
    
    # Medicine Reminder URLs
    path('reminders/', views.medicine_reminders, name='medicine_reminders'),
    path('reminders/add/', views.add_reminder, name='add_reminder'),
    path('reminders/<int:reminder_id>/edit/', views.edit_reminder, name='edit_reminder'),
    path('reminders/<int:reminder_id>/delete/', views.delete_reminder, name='delete_reminder'),
    path('reminders/<int:reminder_id>/toggle/', views.toggle_reminder, name='toggle_reminder'),
    
    # Subscription URLs
    path('subscriptions/', views.subscriptions, name='subscriptions'),
    path('subscriptions/add/', views.add_subscription, name='add_subscription'),
    path('subscriptions/<int:subscription_id>/edit/', views.edit_subscription, name='edit_subscription'),
    path('subscriptions/<int:subscription_id>/cancel/', views.cancel_subscription, name='cancel_subscription'),
    path('subscriptions/<int:subscription_id>/pause/', views.pause_subscription, name='pause_subscription'),
    path('subscriptions/<int:subscription_id>/resume/', views.resume_subscription, name='resume_subscription'),
] 