import uuid
from django.db import models
from django.utils.text import slugify
from django.db.models import CheckConstraint, Q
from django.utils import timezone
from django.conf import settings


class User(models.Model):
    # You will probably extend Django's AbstractUser in real project;
    # this brief model is illustrative if you aren't extending now.
    id = models.BigAutoField(primary_key=True)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.username


class Category(models.Model):
    id = models.BigAutoField(primary_key=True)
    
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=220, unique=True)
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL, related_name="children")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)
    
    def __str__(self): 
        return self.name


class Product(models.Model):
    id = models.BigAutoField(primary_key=True)
    public_id = models.UUIDField(default=uuid.uuid4, unique=True, null=False, editable=False)
    title = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=270, unique=True)
    sku = models.CharField(max_length=64, unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, db_index=True)
    category = models.ForeignKey("Category", related_name="products", on_delete=models.PROTECT)
    stock = models.IntegerField(default=0)  # cached stock
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)[:240]
            unique = f"{base}-{self.sku}"[:270]
            self.slug = unique
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["category"]),  # FK index (optional: Django adds for FK, but explicit is fine)
            models.Index(fields=["price"]),
            models.Index(fields=["-created_at"]),
            # Composite index for common listing: category + is_active + price
            models.Index(fields=["category", "is_active", "price"]),
        ]


class ProductImage(models.Model):
    id = models.BigAutoField(primary_key=True)
    product = models.ForeignKey(Product, related_name="images", on_delete=models.CASCADE)
    image = models.CharField(max_length=1024)  # URL or path - use ImageField if you configure media
    alt_text = models.CharField(max_length=255, blank=True)
    is_main = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self): 
        return f"{self.product.title} image"


class Tag(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=64, unique=True)
    slug = models.SlugField(max_length=80, unique=True)
    
    def __str__(self): 
        return self.name


class ProductTag(models.Model):
    id = models.BigAutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="product_tags")
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, related_name="product_tags")
    
    class Meta:
        unique_together = ("product", "tag")


class Order(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders")    
    status = models.CharField(max_length=32, default="pending", db_index=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["status"]),
            models.Index(fields=["-created_at"]),
        ]


class OrderItem(models.Model):
    id = models.BigAutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="order_items")
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    
    def line_total(self):
        return self.quantity * self.unit_price

    class Meta:
        indexes = [
            models.Index(fields=["order"]),
            models.Index(fields=["product"]),
            # optionally: models.Index(fields=["product", "order"]),
        ]
    constraints = [
        CheckConstraint(check=Q(quantity__gt=0), name="orderitem_quantity_gt_0"),
        CheckConstraint(check=Q(unit_price__gt=0), name="orderitem_unit_price_gt_0"),
    ]
    

class InventoryMovement(models.Model):
    REASONS = [
        ("restock","Restock"),
        ("order","Order"),
        ("return","Return"),
        ("adjustment","Adjustment"),
        ("reservation","Reservation"),
        ("release","Reservation Release"),
    ]
    id = models.BigAutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="movements")
    order_item = models.ForeignKey(OrderItem, null=True, blank=True, on_delete=models.SET_NULL, related_name="movements")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="inventory_movements",
    )    
    change = models.IntegerField()
    reason = models.CharField(max_length=32, choices=REASONS)
    reference = models.CharField(max_length=255, null=True, blank=True)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ["-created_at"]
        
    def __str__(self): 
        return f"{self.product.sku} {self.change} ({self.reason})"
    

class IdempotencyKey(models.Model):
    """
    Store idempotency keys for POST endpoints to avoid duplicate processing.
    Key should be unique per endpoint + user (or per client if unauthenticated).
    """
    id = models.BigAutoField(primary_key=True)
    key = models.CharField(max_length=255, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    response_code = models.IntegerField(null=True, blank=True)
    response_body = models.JSONField(null=True, blank=True)
    user = models.ForeignKey('User', null=True, blank=True, on_delete=models.SET_NULL)

