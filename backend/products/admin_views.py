from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Product
from .serializers import ProductSerializer

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def admin_products(request):
    if not request.user.user_type == 'admin':
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    if request.method == 'GET':
        products = Product.objects.all()
        return Response(ProductSerializer(products, many=True).data)
    
    elif request.method == 'POST':
        data = request.data.copy()
        image_file = request.FILES.get('image')
        if image_file:
            data['image'] = image_file
        # If no image is provided, set a default image URL based on product name
        if not data.get('image'):
            name = data.get('name', 'medicine')
            data['image'] = f'https://source.unsplash.com/400x400/?{name}'
        serializer = ProductSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def admin_product_detail(request, product_id):
    if not request.user.user_type == 'admin':
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'PUT':
        data = request.data.copy()
        
        # Handle image file upload properly
        image_file = request.FILES.get('image')
        if image_file:
            data['image'] = image_file
        elif 'image' in data and isinstance(data['image'], str) and data['image']:
            # Keep the string URL as is (for Unsplash URLs)
            pass
        elif not data.get('image') and not product.image:
            # Set default Unsplash image if no image provided
            name = data.get('name', product.name if hasattr(product, 'name') else 'medicine')
            data['image'] = f'https://source.unsplash.com/400x400/?{name}'
        
        # Remove empty image field to avoid serialization issues
        if 'image' in data and not data['image']:
            del data['image']
            
        serializer = ProductSerializer(product, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        # Improved error reporting: show missing/invalid fields
        error_details = serializer.errors
        missing_fields = [field for field in serializer.fields if field not in data and serializer.fields[field].required]
        if missing_fields:
            error_details['missing_fields'] = missing_fields
        return Response(error_details, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
