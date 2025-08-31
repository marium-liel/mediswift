from django.core.management.base import BaseCommand
from products.models import Product

class Command(BaseCommand):
    help = 'Assign Unsplash image URLs to products missing images.'

    def handle(self, *args, **options):
        updated_count = 0
        products = Product.objects.filter(image__isnull=True) | Product.objects.filter(image='')
        for product in products:
            # Assign Unsplash image based on product name
            product.image = f"https://source.unsplash.com/400x400/?{product.name.replace(' ', '+')}"
            product.save()
            updated_count += 1
        self.stdout.write(self.style.SUCCESS(f'Updated {updated_count} products with Unsplash images.'))
