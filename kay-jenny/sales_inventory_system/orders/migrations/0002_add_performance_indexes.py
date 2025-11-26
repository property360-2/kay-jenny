# Generated migration to add performance indexes

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        # Add indexes for frequently filtered fields
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['status'], name='orders_order_status_idx'),
        ),
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['created_at'], name='orders_order_created_at_idx'),
        ),
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['-created_at'], name='orders_order_created_at_desc_idx'),
        ),
        migrations.AddIndex(
            model_name='payment',
            index=models.Index(fields=['status'], name='orders_payment_status_idx'),
        ),
        migrations.AddIndex(
            model_name='payment',
            index=models.Index(fields=['created_at'], name='orders_payment_created_at_idx'),
        ),
    ]
