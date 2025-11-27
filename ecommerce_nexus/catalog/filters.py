# ecommerce_nexus/catalog/filters.py
import django_filters
from .models import Product

class ProductFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr="lte")
    # Accept either numeric PK via `category` or friendly slug via `category_slug`
    category = django_filters.NumberFilter(field_name="category", lookup_expr="exact")
    category_slug = django_filters.CharFilter(field_name="category__slug", lookup_expr="iexact")

    class Meta:
        model = Product
        fields = ["category", "category_slug", "min_price", "max_price", "is_active"]
