# catalog/migrations/0003_populate_product_public_ids.py
from django.db import migrations
import uuid

def generate_public_ids(apps, schema_editor):
    Product = apps.get_model("catalog", "Product")
    # Use a queryset and bulk update for efficiency
    objs = []
    for p in Product.objects.all():
        if not p.public_id:
            p.public_id = uuid.uuid4()
            objs.append(p)
    if objs:
        Product.objects.bulk_update(objs, ["public_id"])

class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0002_alter_order_options_alter_product_options_and_more'),  # adjust if different
    ]

    operations = [
        migrations.RunPython(generate_public_ids, reverse_code=migrations.RunPython.noop),
    ]
