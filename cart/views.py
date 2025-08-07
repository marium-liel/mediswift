from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Cart, CartItem
from products.models import Product

def get_or_create_cart(request):
    """Get existing cart or create new one based on user/session"""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_key=session_key)
    return cart

def add_to_cart(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        quantity = int(request.POST.get('quantity', 1))
        
        if product.availability != 'in_stock':
            messages.error(request, f'{product.name} is currently out of stock.')
            return redirect('products:product_detail', product_id=product_id)
        
        if quantity > product.stock_quantity:
            messages.error(request, f'Only {product.stock_quantity} units available for {product.name}.')
            return redirect('products:product_detail', product_id=product_id)
        
        cart = get_or_create_cart(request)
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        
        messages.success(request, f'{product.name} added to cart successfully!')
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'{product.name} added to cart!',
                'cart_count': cart.total_items
            })
        
        return redirect('cart:view_cart')
    
    return redirect('products:product_detail', product_id=product_id)

def view_cart(request):
    cart = get_or_create_cart(request)
    cart_items = cart.items.all()
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
    }
    return render(request, 'cart/view_cart.html', context)

def update_cart_item(request, item_id):
    if request.method == 'POST':
        cart_item = get_object_or_404(CartItem, id=item_id)
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity <= 0:
            cart_item.delete()
            messages.success(request, f'{cart_item.product.name} removed from cart.')
        elif quantity > cart_item.product.stock_quantity:
            messages.error(request, f'Only {cart_item.product.stock_quantity} units available.')
        else:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, f'{cart_item.product.name} quantity updated.')
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'cart_total': cart_item.cart.total_price,
                'item_total': cart_item.total_price,
                'cart_count': cart_item.cart.total_items
            })
    
    return redirect('cart:view_cart')

def remove_cart_item(request, item_id):
    if request.method == 'POST':
        cart_item = get_object_or_404(CartItem, id=item_id)
        product_name = cart_item.product.name
        cart_item.delete()
        messages.success(request, f'{product_name} removed from cart.')
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'{product_name} removed from cart.',
                'cart_count': cart_item.cart.total_items
            })
    
    return redirect('cart:view_cart')

def clear_cart(request):
    if request.method == 'POST':
        cart = get_or_create_cart(request)
        cart.items.all().delete()
        messages.success(request, 'Cart cleared successfully.')
    
    return redirect('cart:view_cart') 