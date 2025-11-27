from django.contrib import admin
from .models import Category, Product, ProductImage, Tag, ProductTag, Order, OrderItem, InventoryMovement

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(Tag)
admin.site.register(ProductTag)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(InventoryMovement)
