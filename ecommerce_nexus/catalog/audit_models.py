# ecommerce_nexus/catalog/audit_models.py
from django.db import models
from django.utils import timezone

class AuditTrail(models.Model):
    id = models.BigAutoField(primary_key=True)
    actor = models.CharField(max_length=255, null=True, blank=True)  # username or service
    action = models.CharField(max_length=100)  # e.g., 'create', 'update', 'delete'
    model_name = models.CharField(max_length=100)
    object_pk = models.CharField(max_length=255, null=True, blank=True)
    changes = models.JSONField(null=True, blank=True)  # {"field": ["old", "new"], ...}
    created_at = models.DateTimeField(default=timezone.now)
