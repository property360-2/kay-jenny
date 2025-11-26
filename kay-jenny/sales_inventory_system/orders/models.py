from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta
import uuid

class Order(models.Model):
    """Order model for tracking customer orders"""

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('FINISHED', 'Finished'),
        ('CANCELLED', 'Cancelled'),
        ('EXPIRED', 'Expired'),
    ]

    order_number = models.CharField(max_length=20, unique=True, editable=False)
    customer_name = models.CharField(max_length=200, blank=True)
    table_number = models.CharField(max_length=20, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    notes = models.TextField(blank=True)
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processed_orders'
    )
    is_archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order {self.order_number} - {self.get_status_display()}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            # Generate unique order number
            self.order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def calculate_total(self):
        """Calculate total amount from order items"""
        total = sum(item.subtotal for item in self.items.all())
        self.total_amount = total
        self.save()
        return total

    def is_expired(self):
        """Check if order is pending and older than 1 hour"""
        if self.status != 'PENDING':
            return False

        time_elapsed = timezone.now() - self.created_at
        return time_elapsed >= timedelta(hours=1)

    def expire(self):
        """Mark order as expired"""
        if self.status == 'PENDING' and self.is_expired():
            self.status = 'EXPIRED'
            self.save()
            return True
        return False

    @staticmethod
    def expire_old_pending_orders():
        """Expire all pending orders older than 1 hour"""
        one_hour_ago = timezone.now() - timedelta(hours=1)
        expired_count = Order.objects.filter(
            status='PENDING',
            created_at__lt=one_hour_ago
        ).update(status='EXPIRED')
        return expired_count


class OrderItem(models.Model):
    """Order item model for individual products in an order"""

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('products.Product', on_delete=models.PROTECT)
    product_name = models.CharField(max_length=200)  # Snapshot of product name
    product_price = models.DecimalField(max_digits=10, decimal_places=2)  # Snapshot of price
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.quantity}x {self.product_name}"

    def save(self, *args, **kwargs):
        # Auto-calculate subtotal and snapshot product details
        if not self.product_name:
            self.product_name = self.product.name
        if not self.product_price:
            self.product_price = self.product.price
        self.subtotal = self.product_price * self.quantity
        super().save(*args, **kwargs)


class Payment(models.Model):
    """Payment model for tracking order payments"""

    METHOD_CHOICES = [
        ('CASH', 'Cash'),
        ('ONLINE', 'Online Demo'),
    ]

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    method = models.CharField(max_length=20, choices=METHOD_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reference_number = models.CharField(max_length=100, blank=True)
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processed_payments'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Payment for {self.order.order_number} - {self.get_status_display()}"
