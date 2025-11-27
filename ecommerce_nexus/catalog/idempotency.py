# ecommerce_nexus/catalog/idempotency.py
import json
from functools import wraps
from django.http import JsonResponse
from .models import IdempotencyKey

def idempotent(key_header="Idempotency-Key"):
    """
    Decorator for view functions that ensures idempotent POSTs.
    Usage: decorate your viewset create() method or API view.
    """
    def decorator(func):
        @wraps(func)
        def wrapped(view, request, *args, **kwargs):
            if request.method != "POST":
                return func(view, request, *args, **kwargs)
            key = request.headers.get(key_header)
            user = getattr(request, "user", None)
            if key:
                try:
                    existing = IdempotencyKey.objects.get(key=key)
                    # replay cached response if available
                    if existing.response_body is not None and existing.response_code:
                        return JsonResponse(existing.response_body, status=existing.response_code)
                except IdempotencyKey.DoesNotExist:
                    # reserve the key (so concurrent requests fail early)
                    IdempotencyKey.objects.create(key=key, user=user if user.is_authenticated else None)
            # call original view
            response = func(view, request, *args, **kwargs)
            # store response for future replay (best-effort)
            if key and hasattr(response, "status_code"):
                try:
                    body = response.data if hasattr(response, "data") else None
                    existing = IdempotencyKey.objects.filter(key=key).first()
                    if existing:
                        existing.response_code = response.status_code
                        existing.response_body = body
                        existing.save(update_fields=["response_code", "response_body"])
                except Exception:
                    pass
            return response
        return wrapped
    return decorator
