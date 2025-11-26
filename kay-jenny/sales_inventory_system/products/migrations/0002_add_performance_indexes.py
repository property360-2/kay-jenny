# Generated migration to add performance indexes

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        # Add indexes for frequently filtered fields
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['is_archived'], name='products_product_is_archived_idx'),
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['created_at'], name='products_product_created_at_idx'),
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['category', 'is_archived'], name='products_product_category_archived_idx'),
        ),
    ]
