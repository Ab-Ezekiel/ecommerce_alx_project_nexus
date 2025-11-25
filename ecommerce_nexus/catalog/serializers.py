# ecommerce_nexus/catalog/serializers.py
from rest_framework import serializers
from decimal import Decimal
from .models import Category, Product

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug"]
        read_only_fields = ["id", "slug"]


class ProductSerializer(serializers.ModelSerializer):
    # show nested category info when reading
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        source="category", queryset=Category.objects.all(), write_only=True
    )

    class Meta:
        model = Product
        fields = [
            "id",
            "public_id",
            "title",
            "slug",
            "sku",
            "description",
            "price",
            "category",
            "category_id",
            "stock",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "public_id", "slug", "created_at", "updated_at"]
        extra_kwargs = {
            "price": {"help_text": "Price as decimal string (e.g. '19.99')"},
            "stock": {"help_text": "Integer available stock"},
        }

    def validate_price(self, value: Decimal) -> Decimal:
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than zero.")
        return value

    def validate_stock(self, value: int) -> int:
        if value < 0:
            raise serializers.ValidationError("Stock cannot be negative.")
        return value

    def validate_title(self, value: str) -> str:
        if not value or not value.strip():
            raise serializers.ValidationError("Title cannot be empty.")
        return value

    def validate(self, attrs):
        # Ensure SKU is present on create (DB uniqueness is still enforced at DB level)
        if self.instance is None:
            sku = attrs.get("sku")
            if not sku:
                raise serializers.ValidationError({"sku": "SKU is required for a product."})
        return attrs
