from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponse
from .models import Order, OrderItem, SmartRefill, MedicineReminder, Subscription
from .forms import CheckoutForm, MedicineReminderForm, SubscriptionForm
from .utils import generate_order_pdf, create_smart_refill, get_user_refills, get_due_refills
from cart.views import get_or_create_cart
from cart.models import CartItem
from products.models import Product

@login_required
def checkout(request):
    cart = get_or_create_cart(request)
    cart_items = cart.items.all()
    
    if not cart_items:
        messages.error(request, 'Your cart is empty.')
        return redirect('cart:view_cart')
    
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Create order
                    order = form.save(commit=False)
                    order.user = request.user
                    order.total_amount = cart.total_price
                    # Automatically mark as delivered and simulate payment
                    order.status = 'delivered'
                    order.payment_status = 'paid'
                    order.save()
                    
                    # Create order items and smart refills
                    for cart_item in cart_items:
                        OrderItem.objects.create(
                            order=order,
                            product=cart_item.product,
                            quantity=cart_item.quantity,
                            price=cart_item.product.current_price
                        )
                        
                        # Create smart refill for recurring products
                        create_smart_refill(request.user, cart_item.product, cart_item.quantity)
                        
                        # Update product stock
                        cart_item.product.stock_quantity -= cart_item.quantity
                        if cart_item.product.stock_quantity <= 0:
                            cart_item.product.availability = 'out_of_stock'
                        cart_item.product.save()
                    
                    # Clear cart
                    cart.items.all().delete()
                    
                    messages.success(request, f'Order placed and delivered successfully! Order number: {order.order_number}')
                    return redirect('orders:order_detail', order_id=order.id)
                    
            except Exception as e:
                messages.error(request, 'An error occurred while placing your order. Please try again.')
                return redirect('cart:view_cart')
    else:
        form = CheckoutForm()
        
        # Pre-fill form with quick reorder shipping info if available
        if 'quick_reorder_shipping' in request.session:
            shipping_info = request.session['quick_reorder_shipping']
            form.fields['shipping_address'].initial = shipping_info.get('shipping_address')
            form.fields['shipping_city'].initial = shipping_info.get('shipping_city')
            form.fields['shipping_state'].initial = shipping_info.get('shipping_state')
            form.fields['shipping_zip_code'].initial = shipping_info.get('shipping_zip_code')
            form.fields['shipping_phone'].initial = shipping_info.get('shipping_phone')
            form.fields['payment_method'].initial = shipping_info.get('payment_method')
            # Clear the session data after using it
            del request.session['quick_reorder_shipping']
    
    context = {
        'form': form,
        'cart': cart,
        'cart_items': cart_items,
    }
    return render(request, 'orders/checkout.html', context)

@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user)
    context = {
        'orders': orders,
    }
    return render(request, 'orders/order_list.html', context)

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    context = {
        'order': order,
    }
    return render(request, 'orders/order_detail.html', context)

@login_required
def download_order_pdf(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return generate_order_pdf(order)

@login_required
def smart_refills(request):
    # Get all previous orders for the user
    previous_orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    # Get unique products from all orders for quick reorder
    ordered_products = {}
    for order in previous_orders:
        for item in order.items.all():
            if item.product.id not in ordered_products:
                ordered_products[item.product.id] = {
                    'product': item.product,
                    'last_ordered': order.created_at,
                    'last_quantity': item.quantity,
                    'total_orders': 1,
                    'total_quantity': item.quantity
                }
            else:
                ordered_products[item.product.id]['total_orders'] += 1
                ordered_products[item.product.id]['total_quantity'] += item.quantity
                if order.created_at > ordered_products[item.product.id]['last_ordered']:
                    ordered_products[item.product.id]['last_ordered'] = order.created_at
                    ordered_products[item.product.id]['last_quantity'] = item.quantity
    
    # Convert to list and sort by last ordered date
    reorder_items = list(ordered_products.values())
    reorder_items.sort(key=lambda x: x['last_ordered'], reverse=True)
    
    context = {
        'reorder_items': reorder_items,
        'previous_orders': previous_orders,
    }
    return render(request, 'orders/smart_refills.html', context)

@login_required
def quick_reorder(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        # Get the last order for this product to pre-fill shipping info
        last_order = Order.objects.filter(
            user=request.user,
            items__product=product
        ).order_by('-created_at').first()
        
        if last_order:
            # Store shipping info in session for checkout
            request.session['quick_reorder_shipping'] = {
                'shipping_address': last_order.shipping_address,
                'shipping_city': last_order.shipping_city,
                'shipping_state': last_order.shipping_state,
                'shipping_zip_code': last_order.shipping_zip_code,
                'shipping_phone': last_order.shipping_phone,
                'payment_method': last_order.payment_method,
            }
        
        # Add product to cart using cart app functionality
        from cart.views import get_or_create_cart
        cart = get_or_create_cart(request)
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': 1}
        )
        
        if not created:
            cart_item.quantity += 1
            cart_item.save()
        
        messages.success(request, f'{product.name} added to cart for quick reorder!')
        return redirect('orders:checkout')
    
    return redirect('orders:smart_refills')

# Medicine Reminder views
@login_required
def medicine_reminders(request):
    reminders = MedicineReminder.objects.filter(user=request.user)
    context = {
        'reminders': reminders,
    }
    return render(request, 'orders/medicine_reminders.html', context)

@login_required
def add_reminder(request):
    if request.method == 'POST':
        form = MedicineReminderForm(request.POST)
        if form.is_valid():
            reminder = form.save(commit=False)
            reminder.user = request.user
            reminder.save()
            messages.success(request, 'Medicine reminder created successfully!')
            return redirect('orders:medicine_reminders')
    else:
        form = MedicineReminderForm()
    
    context = {
        'form': form,
        'title': 'Add Medicine Reminder',
    }
    return render(request, 'orders/add_reminder.html', context)

@login_required
def edit_reminder(request, reminder_id):
    reminder = get_object_or_404(MedicineReminder, id=reminder_id, user=request.user)
    
    if request.method == 'POST':
        form = MedicineReminderForm(request.POST, instance=reminder)
        if form.is_valid():
            form.save()
            messages.success(request, 'Medicine reminder updated successfully!')
            return redirect('orders:medicine_reminders')
    else:
        form = MedicineReminderForm(instance=reminder)
    
    context = {
        'form': form,
        'reminder': reminder,
        'title': 'Edit Medicine Reminder',
    }
    return render(request, 'orders/edit_reminder.html', context)

@login_required
def delete_reminder(request, reminder_id):
    reminder = get_object_or_404(MedicineReminder, id=reminder_id, user=request.user)
    
    if request.method == 'POST':
        reminder.delete()
        messages.success(request, 'Medicine reminder deleted successfully!')
        return redirect('orders:medicine_reminders')
    
    context = {
        'reminder': reminder,
    }
    return render(request, 'orders/delete_reminder.html', context)

@login_required
def toggle_reminder(request, reminder_id):
    reminder = get_object_or_404(MedicineReminder, id=reminder_id, user=request.user)
    
    if request.method == 'POST':
        reminder.is_active = not reminder.is_active
        reminder.save()
        
        status = 'activated' if reminder.is_active else 'deactivated'
        messages.success(request, f'Reminder {status} successfully!')
    
    return redirect('orders:medicine_reminders')

# Subscription views
@login_required
def subscriptions(request):
    subscriptions = Subscription.objects.filter(user=request.user)
    context = {
        'subscriptions': subscriptions,
    }
    return render(request, 'orders/subscriptions.html', context)

@login_required
def add_subscription(request):
    if request.method == 'POST':
        form = SubscriptionForm(request.POST, user=request.user)
        if form.is_valid():
            subscription = form.save(commit=False)
            subscription.user = request.user
            subscription.save()
            messages.success(request, 'Subscription created successfully!')
            return redirect('orders:subscriptions')
    else:
        form = SubscriptionForm(user=request.user)
    
    context = {
        'form': form,
        'title': 'Add Subscription',
    }
    return render(request, 'orders/add_subscription.html', context)

@login_required
def edit_subscription(request, subscription_id):
    subscription = get_object_or_404(Subscription, id=subscription_id, user=request.user)
    
    if request.method == 'POST':
        form = SubscriptionForm(request.POST, instance=subscription, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Subscription updated successfully!')
            return redirect('orders:subscriptions')
    else:
        form = SubscriptionForm(instance=subscription, user=request.user)
    
    context = {
        'form': form,
        'subscription': subscription,
        'title': 'Edit Subscription',
    }
    return render(request, 'orders/edit_subscription.html', context)

@login_required
def cancel_subscription(request, subscription_id):
    subscription = get_object_or_404(Subscription, id=subscription_id, user=request.user)
    
    if request.method == 'POST':
        subscription.status = 'cancelled'
        subscription.save()
        messages.success(request, 'Subscription cancelled successfully!')
        return redirect('orders:subscriptions')
    
    context = {
        'subscription': subscription,
    }
    return render(request, 'orders/cancel_subscription.html', context)

@login_required
def pause_subscription(request, subscription_id):
    subscription = get_object_or_404(Subscription, id=subscription_id, user=request.user)
    
    if request.method == 'POST':
        subscription.status = 'paused'
        subscription.save()
        messages.success(request, 'Subscription paused successfully!')
    
    return redirect('orders:subscriptions')

@login_required
def resume_subscription(request, subscription_id):
    subscription = get_object_or_404(Subscription, id=subscription_id, user=request.user)
    
    if request.method == 'POST':
        subscription.status = 'active'
        subscription.save()
        messages.success(request, 'Subscription resumed successfully!')
    
    return redirect('orders:subscriptions') 