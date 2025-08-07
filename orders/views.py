from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from .models import Order, OrderItem
from .forms import CheckoutForm
from cart.views import get_or_create_cart

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
                    order.save()
                    
                    # Create order items
                    for cart_item in cart_items:
                        OrderItem.objects.create(
                            order=order,
                            product=cart_item.product,
                            quantity=cart_item.quantity,
                            price=cart_item.product.current_price
                        )
                        
                        # Update product stock
                        cart_item.product.stock_quantity -= cart_item.quantity
                        if cart_item.product.stock_quantity <= 0:
                            cart_item.product.availability = 'out_of_stock'
                        cart_item.product.save()
                    
                    # Clear cart
                    cart.items.all().delete()
                    
                    messages.success(request, f'Order placed successfully! Order number: {order.order_number}')
                    return redirect('orders:order_detail', order_id=order.id)
                    
            except Exception as e:
                messages.error(request, 'An error occurred while placing your order. Please try again.')
                return redirect('cart:view_cart')
    else:
        form = CheckoutForm()
    
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