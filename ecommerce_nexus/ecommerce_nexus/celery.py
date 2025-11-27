import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ecommerce_nexus.settings")
app = Celery("ecommerce_nexus")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    return "debug"
