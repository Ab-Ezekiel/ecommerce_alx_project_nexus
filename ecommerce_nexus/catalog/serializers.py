# ecommerce_nexus/catalog/serializers.py
from rest_framework import serializers
from decimal import Decimal
from django.db import transaction
from .models import Category, Order, OrderItem, Product, InventoryMovement

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


class OrderItemInputSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)
 
 
class OrderItemSerializer(serializers.ModelSerializer):
    product_title = serializers.CharField(source="product.title", read_only=True)
    product_sku = serializers.CharField(source="product.sku", read_only=True)
    unit_price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    line_total = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ["id", "product_id", "product_title", "product_sku", "quantity", "unit_price", "line_total"]

    def get_line_total(self, obj):
        return obj.unit_price * obj.quantity    
    
    
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemInputSerializer(many=True, write_only=True)
    order_items = OrderItemSerializer(many=True, read_only=True, source="items")
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Order
        fields = ["id", "user", "status", "total_amount", "items", "order_items", "created_at", "updated_at"]
        read_only_fields = ["id", "user", "total_amount", "created_at", "updated_at"]

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("Order must include at least one item.")
        product_ids = [it["product_id"] for it in value]
        products = Product.objects.filter(id__in=product_ids).in_bulk()
        for it in value:
            prod = products.get(it["product_id"])
            if prod is None:
                raise serializers.ValidationError(f"Product id={it['product_id']} does not exist.")
            if it["quantity"] > prod.stock:
                raise serializers.ValidationError(f"Insufficient stock for product {prod.sku} ({prod.title}). Available: {prod.stock}")
        return value

    def create(self, validated_data):
        items_data = validated_data.pop("items")

        # ensure we have request.user in context and it's an authenticated user
        request = self.context.get("request", None)
        if request is None or not getattr(request, "user", None) or not request.user.is_authenticated:
            raise serializers.ValidationError("Authentication required to create an order.")

        request_user = request.user

        with transaction.atomic():
            # create the order (user must be a proper User instance)
            order = Order.objects.create(user=request_user, status="pending", total_amount=Decimal("0.00"))

            total = Decimal("0.00")
            # lock product rows to avoid race conditions
            product_ids = [it["product_id"] for it in items_data]
            products_qs = Product.objects.select_for_update().filter(id__in=product_ids).in_bulk()

            for it in items_data:
                prod = products_qs.get(it["product_id"])
                qty = int(it["quantity"])
                if prod.stock < qty:
                    # Defensive check (validate_items should catch this)
                    raise serializers.ValidationError(f"Insufficient stock for {prod.sku}")

                unit_price = prod.price  # Decimal
                line_total = (unit_price * qty).quantize(unit_price) if isinstance(unit_price, Decimal) else unit_price * qty

                # create the OrderItem and keep reference
                order_item = OrderItem.objects.create(
                    order=order,
                    product=prod,
                    quantity=qty,
                    unit_price=unit_price
                )

                # create inventory movement linked to the order_item
                InventoryMovement.objects.create(
                    product=prod,
                    order_item=order_item,
                    user=request_user,
                    change=-qty,
                    reason="order",
                    reference=str(order.id),
                    note=f"Order {order.id} created, reserved {qty}"
                )

                # decrement cached stock
                prod.stock = prod.stock - qty
                prod.save(update_fields=["stock"])

                total += (unit_price * qty)

            # finalize order total
            order.total_amount = total
            order.save(update_fields=["total_amount"])
            return order
        
        