from django.template.loader import render_to_string
from django.http import HttpResponse
from io import BytesIO
from datetime import datetime, timedelta
from .models import Order, SmartRefill, OrderItem
from products.models import Product

def generate_order_pdf(order):
    """Generate PDF for order invoice"""
    # Try to import WeasyPrint only when needed
    try:
        from weasyprint import HTML
        WEASYPRINT_AVAILABLE = True
    except ImportError:
        WEASYPRINT_AVAILABLE = False
        print("Warning: WeasyPrint not available. Generating HTML instead of PDF.")
    
    html_string = render_to_string('orders/order_pdf.html', {
        'order': order,
        'items': order.items.all(),
    })
    
    if not WEASYPRINT_AVAILABLE:
        # Fallback: Generate HTML instead of PDF
        response = HttpResponse(html_string, content_type='text/html')
        response['Content-Disposition'] = f'attachment; filename="order_{order.order_number}.html"'
        return response
    
    # Original PDF generation
    html = HTML(string=html_string)
    pdf = html.write_pdf()
    
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="order_{order.order_number}.pdf"'
    return response

def calculate_refill_date(user, product, quantity):
    """Calculate estimated refill date based on usage patterns"""
    # Get user's previous orders for this product
    previous_orders = OrderItem.objects.filter(
        order__user=user,
        product=product
    ).order_by('-order__created_at')[:3]
    
    if not previous_orders:
        # Default to 30 days if no previous orders
        return datetime.now() + timedelta(days=30)
    
    # Calculate average days between orders
    total_days = 0
    order_count = len(previous_orders)
    
    for i in range(order_count - 1):
        days_between = (previous_orders[i].order.created_at - previous_orders[i+1].order.created_at).days
        total_days += days_between
    
    if order_count > 1:
        avg_days = total_days / (order_count - 1)
    else:
        avg_days = 30  # Default
    
    # Adjust based on quantity (more quantity = longer time)
    quantity_factor = quantity / 1  # Normalize to 1 unit
    adjusted_days = avg_days * quantity_factor
    
    return datetime.now() + timedelta(days=adjusted_days)

def create_smart_refill(user, product, quantity):
    """Create or update smart refill for a product"""
    refill_date = calculate_refill_date(user, product, quantity)
    
    smart_refill, created = SmartRefill.objects.get_or_create(
        user=user,
        product=product,
        defaults={
            'last_order_date': datetime.now(),
            'estimated_refill_date': refill_date,
        }
    )
    
    if not created:
        smart_refill.last_order_date = datetime.now()
        smart_refill.estimated_refill_date = refill_date
        smart_refill.is_notified = False
        smart_refill.save()
    
    return smart_refill

def get_user_refills(user):
    """Get all smart refills for a user"""
    return SmartRefill.objects.filter(user=user)

def get_due_refills(user):
    """Get refills that are due for notification"""
    return SmartRefill.objects.filter(
        user=user,
        estimated_refill_date__lte=datetime.now(),
        is_notified=False
    )
