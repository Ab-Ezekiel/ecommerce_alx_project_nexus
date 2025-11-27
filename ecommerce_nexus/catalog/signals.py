# ecommerce_nexus/catalog/signals.py
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.forms.models import model_to_dict
from .audit_models import AuditTrail
from .models import Order, Product, OrderItem, InventoryMovement
from .tasks import send_order_confirmation
from django.db.models.signals import post_save

TRACKED = (Order, Product, OrderItem, InventoryMovement)

@receiver(pre_save)
def capture_changes(sender, instance, **kwargs):
    if sender not in TRACKED:
        return
    if instance.pk:
        try:
            old = sender.objects.get(pk=instance.pk)
            old_data = model_to_dict(old)
            new_data = model_to_dict(instance)
            changes = {}
            for key in new_data.keys():
                if old_data.get(key) != new_data.get(key):
                    changes[key] = [old_data.get(key), new_data.get(key)]
            if changes:
                AuditTrail.objects.create(
                    actor=getattr(instance, "_changed_by", None) or None,
                    action="update",
                    model_name=sender.__name__,
                    object_pk=str(instance.pk),
                    changes=changes
                )
        except sender.DoesNotExist:
            # new object (will be handled in post_save)
            pass

@receiver(post_save)
def book_create(sender, instance, created, **kwargs):
    if sender not in TRACKED:
        return
    if created:
        AuditTrail.objects.create(
            actor=getattr(instance, "_changed_by", None) or None,
            action="create",
            model_name=sender.__name__,
            object_pk=str(instance.pk),
            changes=model_to_dict(instance)
        )

@receiver(post_delete)
def book_delete(sender, instance, **kwargs):
    if sender not in TRACKED:
        return
    AuditTrail.objects.create(
        actor=getattr(instance, "_changed_by", None) or None,
        action="delete",
        model_name=sender.__name__,
        object_pk=str(instance.pk),
        changes=model_to_dict(instance)
    )


@receiver(post_save, sender=Order)
def order_created_handler(sender, instance, created, **kwargs):
    if created:
        # enqueue background job to send email
        send_order_confirmation.delay(instance.id)

