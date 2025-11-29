# ecommerce_nexus/catalog/views.py
from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import LimitOffsetPagination
from drf_yasg.utils import swagger_auto_schema

from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer
from .filters import ProductFilter
from drf_yasg import openapi

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import OrderSerializer
from .models import Order
from rest_framework.permissions import IsAuthenticated
from idempotency_key.decorators import idempotency_key

class StandardResultsSetPagination(LimitOffsetPagination):
    default_limit = 20
    max_limit = 100

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = None  # do not paginate categories by default
    # use default lookup (pk) for categories unless you add public_id to model

# Example payload for docs
product_create_example = {
    "title": "Example Shirt",
    "sku": "SKU-1234",
    "description": "A comfortable shirt.",
    "price": "29.99",
    "category_id": 1,
    "stock": 10,
    "is_active": True
}

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.filter(is_active=True).select_related("category")
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ["title", "sku", "description"]
    ordering_fields = ["price", "created_at"]
    ordering = ["-created_at"]
    lookup_field = "public_id"

    def get_queryset(self):
        # allow admin/staff to see inactive products when requested
        qs = super().get_queryset()
        if self.request.user and self.request.user.is_staff:
            return Product.objects.all().select_related("category")
        return qs

    @swagger_auto_schema(
        request_body=ProductSerializer,
        operation_description="Create a product",
        # If drf-yasg version supports examples you can provide them; serializer will be shown either way.
        request_body_examples={"application/json": product_create_example},
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().select_related("user").prefetch_related("items__product")
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    
    @idempotency_key()
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return super().get_queryset()
        
        # Fix for Swagger/Redoc schema generation
        if getattr(self, 'swagger_fake_view', False):
            return self.queryset.none()

        if user.is_anonymous:
            return self.queryset.none()
        
        return self.queryset.filter(user=user)
        
    def perform_create(self, serializer):
        order = serializer.save(user=self.request.user)
        order._changed_by = self.request.user.username
        order.save()

    def perform_update(self, serializer):
        order = serializer.save()
        order._changed_by = self.request.user.username
        order.save()

