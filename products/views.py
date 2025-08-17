from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.db import IntegrityError
from .models import Product, Category, Review, Wishlist
from .forms import ProductForm, CategoryForm, ReviewForm
from orders.utils import create_smart_refill
from orders.models import OrderItem

def is_admin(user):
    return user.is_authenticated and user.user_type == 'admin'

def home(request):
    featured_products = Product.objects.filter(is_featured=True, availability='in_stock')[:6]
    categories = Category.objects.all()[:8]
    
    # Get user's wishlist products for wishlist icons
    user_wishlist_products = []
    if request.user.is_authenticated:
        user_wishlist_products = list(Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True))
    
    context = {
        'featured_products': featured_products,
        'categories': categories,
        'user_wishlist_products': user_wishlist_products,
    }
    return render(request, 'products/home.html', context)

def product_list(request):
    products = Product.objects.filter(availability='in_stock')
    
    # Search functionality
    query = request.GET.get('q', '')
    if query and query != 'None':
        products = products.filter(
            Q(name__icontains=query) |
            Q(brand__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        )
    
    # Filter by category
    category_id = request.GET.get('category', '')
    if category_id and category_id != 'None':
        products = products.filter(category_id=category_id)
    
    # Filter by product type
    product_type = request.GET.get('type', '')
    if product_type and product_type != 'None':
        products = products.filter(product_type=product_type)
    
    # Filter by price range
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    if min_price and min_price != 'None':
        try:
            products = products.filter(price__gte=float(min_price))
        except (ValueError, TypeError):
            pass
    if max_price and max_price != 'None':
        try:
            products = products.filter(price__lte=float(max_price))
        except (ValueError, TypeError):
            pass
    
    # Sort products
    sort_by = request.GET.get('sort', 'name')
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'newest':
        products = products.order_by('-created_at')
    elif sort_by == 'rating':
        products = sorted(products, key=lambda x: x.average_rating, reverse=True)
    else:
        products = products.order_by('name')
    
    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = Category.objects.all()
    
    # Get user's wishlist products for wishlist icons
    user_wishlist_products = []
    if request.user.is_authenticated:
        user_wishlist_products = list(Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True))
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'query': query if query != 'None' else '',
        'selected_category': category_id if category_id != 'None' else '',
        'selected_type': product_type if product_type != 'None' else '',
        'min_price': min_price if min_price != 'None' else '',
        'max_price': max_price if max_price != 'None' else '',
        'sort_by': sort_by,
        'user_wishlist_products': user_wishlist_products,
    }
    return render(request, 'products/product_list.html', context)

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    related_products = Product.objects.filter(
        category=product.category,
        availability='in_stock'
    ).exclude(id=product.id)[:4]
    
    # Get user's review if exists
    user_review = None
    if request.user.is_authenticated:
        user_review = Review.objects.filter(product=product, user=request.user).first()
    
    # Get all reviews for this product
    reviews = Review.objects.filter(product=product)
    
    # Check if product is in user's wishlist
    in_wishlist = False
    if request.user.is_authenticated:
        in_wishlist = Wishlist.objects.filter(user=request.user, product=product).exists()
    
    context = {
        'product': product,
        'related_products': related_products,
        'reviews': reviews,
        'user_review': user_review,
        'in_wishlist': in_wishlist,
    }
    return render(request, 'products/product_detail.html', context)

def category_detail(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    products = Product.objects.filter(category=category, availability='in_stock')
    
    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'page_obj': page_obj,
    }
    return render(request, 'products/category_detail.html', context)

@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # Check if user has already reviewed this product
    existing_review = Review.objects.filter(user=request.user, product=product).first()
    if existing_review:
        messages.info(request, 'You have already reviewed this product. You can edit your existing review.')
        return redirect('products:edit_review', review_id=existing_review.id)
    
    # Check if user has purchased this product
    has_purchased = OrderItem.objects.filter(
        order__user=request.user,
        product=product
    ).exists()
    
    if not has_purchased:
        messages.error(request, 'To review this product, please purchase it first. You can only review products you have bought.')
        return redirect('products:product_detail', product_id=product_id)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            try:
                review = form.save(commit=False)
                review.product = product
                review.user = request.user
                review.save()
                messages.success(request, 'Review submitted successfully!')
                return redirect('products:product_detail', product_id=product_id)
            except IntegrityError:
                messages.error(request, 'You have already reviewed this product.')
                return redirect('products:product_detail', product_id=product_id)
    else:
        form = ReviewForm()
    
    context = {
        'form': form,
        'product': product,
    }
    return render(request, 'products/add_review.html', context)

@login_required
def edit_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, 'Review updated successfully!')
            return redirect('products:product_detail', product_id=review.product.id)
    else:
        form = ReviewForm(instance=review)
    
    context = {
        'form': form,
        'review': review,
    }
    return render(request, 'products/edit_review.html', context)

# Wishlist views
@login_required
def wishlist(request):
    wishlist_items = Wishlist.objects.filter(user=request.user)
    context = {
        'wishlist_items': wishlist_items,
    }
    return render(request, 'products/wishlist.html', context)

@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        wishlist_item, created = Wishlist.objects.get_or_create(
            user=request.user,
            product=product
        )
        
        if created:
            messages.success(request, f'{product.name} added to wishlist!')
        else:
            messages.info(request, f'{product.name} is already in your wishlist.')
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'{product.name} added to wishlist!',
                'in_wishlist': True
            })
    
    return redirect('products:product_detail', product_id=product_id)

@login_required
def remove_from_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        try:
            wishlist_item = Wishlist.objects.get(user=request.user, product=product)
            wishlist_item.delete()
            messages.success(request, f'{product.name} removed from wishlist.')
        except Wishlist.DoesNotExist:
            messages.error(request, 'Item not found in wishlist.')
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'{product.name} removed from wishlist.',
                'in_wishlist': False
            })
    
    return redirect('products:wishlist')

@login_required
def move_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        # Remove from wishlist
        try:
            wishlist_item = Wishlist.objects.get(user=request.user, product=product)
            wishlist_item.delete()
        except Wishlist.DoesNotExist:
            pass
        
        # Add to cart
        from cart.views import get_or_create_cart
        cart = get_or_create_cart(request)
        cart_item, created = cart.items.get_or_create(
            product=product,
            defaults={'quantity': 1}
        )
        
        if not created:
            cart_item.quantity += 1
            cart_item.save()
        
        messages.success(request, f'{product.name} moved to cart!')
    
    return redirect('products:wishlist')

# Admin views for product management
@login_required
@user_passes_test(is_admin)
def admin_product_list(request):
    products = Product.objects.all().order_by('-created_at')
    context = {
        'products': products,
    }
    return render(request, 'products/admin_product_list.html', context)

@login_required
@user_passes_test(is_admin)
def admin_add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product added successfully!')
            return redirect('products:admin_product_list')
    else:
        form = ProductForm()
    
    context = {
        'form': form,
        'title': 'Add New Product',
    }
    return render(request, 'products/admin_product_form.html', context)

@login_required
@user_passes_test(is_admin)
def admin_edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully!')
            return redirect('products:admin_product_list')
    else:
        form = ProductForm(instance=product)
    
    context = {
        'form': form,
        'product': product,
        'title': 'Edit Product',
    }
    return render(request, 'products/admin_product_form.html', context)

@login_required
@user_passes_test(is_admin)
def admin_delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully!')
        return redirect('products:admin_product_list')
    
    context = {
        'product': product,
    }
    return render(request, 'products/admin_delete_product.html', context) 