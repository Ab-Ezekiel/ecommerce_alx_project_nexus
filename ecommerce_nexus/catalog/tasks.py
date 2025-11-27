# ecommerce_nexus/catalog/tasks.py
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Order


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_order_confirmation(self, order_id):
    try:
        order = Order.objects.get(id=order_id)
        subject = f"Order Confirmation #{order.id}"
        body = f"Thank you for your order. Total: {order.total_amount}\nItems:\n"
        for item in order.items.all():
            body += f"- {item.product.title} x{item.quantity} @ {item.unit_price}\n"
        # use configured EMAIL_BACKEND. For dev you can use console backend.
        send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            [order.user.email] if order.user and order.user.email else [],
            fail_silently=False,
        )
        return {"status": "sent", "order": order_id}
    except Exception as exc:
        raise self.retry(exc=exc)

