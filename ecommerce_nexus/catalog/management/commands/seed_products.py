# ecommerce_nexus/catalog/management/commands/seed_products.py
from django.core.management.base import BaseCommand
from catalog.models import Category, Product
import random
import uuid

class Command(BaseCommand):
    help = "Create sample categories and products"

    def handle(self, *args, **kwargs):
        cat, _ = Category.objects.get_or_create(name="General")
        for i in range(1, 11):
            sku = f"SKU-{i:04d}"
            Product.objects.get_or_create(
                sku=sku,
                defaults={
                    "title": f"Sample Product {i}",
                    "description": f"Description for product {i}",
                    "price": random.randint(1000, 10000) / 100,
                    "category": cat,
                    "stock": random.randint(0, 100),
                    "is_active": True,
                },
            )
        self.stdout.write(self.style.SUCCESS("Seeded categories and products"))
