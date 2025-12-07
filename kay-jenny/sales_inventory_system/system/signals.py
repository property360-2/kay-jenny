"""
Signal handlers for automatic audit trail tracking
"""
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from django.forms.models import model_to_dict
import threading

from sales_inventory_system.accounts.models import User
from sales_inventory_system.products.models import Product, Ingredient, StockTransaction
from sales_inventory_system.orders.models import Order, Payment
from .models import AuditLog

# Thread-local storage for request context
_thread_locals = threading.local()


def get_current_user():
    """Get current user from thread-local storage"""
    return getattr(_thread_locals, 'user', None)


def set_current_user(user):
    """Set current user in thread-local storage"""
    _thread_locals.user = user


def serialize_model_instance(instance, exclude_fields=None):
    """
    Serialize a model instance to a JSON-safe dictionary

    Args:
        instance: Model instance to serialize
        exclude_fields: List of fields to exclude

    Returns:
        dict: JSON-safe dictionary representation
    """
    if exclude_fields is None:
        exclude_fields = []

    # Add common exclusions
    exclude_fields.extend(['created_at', 'updated_at'])

    try:
        data = model_to_dict(instance, exclude=exclude_fields)
    except Exception:
        return {}

    # Convert special types to JSON-serializable formats
    for key, value in data.items():
        if hasattr(value, '__class__'):
            class_name = value.__class__.__name__
            if class_name == 'Decimal':
                data[key] = float(value)
            elif hasattr(value, 'isoformat'):  # DateTime
                data[key] = value.isoformat()
            elif value is None:
                data[key] = None
            else:
                data[key] = str(value)

    return data


# ==================== USER TRACKING ====================

@receiver(post_save, sender=User)
def log_user_changes(sender, instance, created, **kwargs):
    """Track user creation and updates"""
    user = get_current_user()
    content_type = ContentType.objects.get_for_model(instance)

    # Exclude password field from snapshots
    data_after = serialize_model_instance(instance, exclude_fields=['password'])

    if created:
        AuditLog.objects.create(
            user=user,
            action='CREATE',
            content_type=content_type,
            object_id=instance.id,
            model_name='User',
            record_id=instance.id,
            description=f'Created user: {instance.username} ({instance.get_role_display()})',
            data_after=data_after
        )
    else:
        # Check if it's an archive/restore operation
        action = getattr(instance, '_audit_action', 'UPDATE')

        if action == 'ARCHIVE':
            description = f'Archived user: {instance.username}'
        elif action == 'RESTORE':
            description = f'Restored user: {instance.username}'
        else:
            description = f'Updated user: {instance.username}'

        # Get before state if available
        data_before = getattr(instance, '_audit_before_state', None)

        AuditLog.objects.create(
            user=user,
            action=action,
            content_type=content_type,
            object_id=instance.id,
            model_name='User',
            record_id=instance.id,
            description=description,
            data_before=data_before,
            data_after=data_after
        )


@receiver(post_delete, sender=User)
def log_user_deletion(sender, instance, **kwargs):
    """Track user deletion"""
    user = get_current_user()
    content_type = ContentType.objects.get_for_model(instance)

    AuditLog.objects.create(
        user=user,
        action='DELETE',
        content_type=content_type,
        object_id=instance.id,
        model_name='User',
        record_id=instance.id,
        description=f'Deleted user: {instance.username}',
        data_before=serialize_model_instance(instance, exclude_fields=['password'])
    )


# ==================== PRODUCT TRACKING ====================

@receiver(post_save, sender=Product)
def log_product_changes(sender, instance, created, **kwargs):
    """Track product creation and updates"""
    user = get_current_user()
    content_type = ContentType.objects.get_for_model(instance)

    data_after = serialize_model_instance(instance)

    if created:
        AuditLog.objects.create(
            user=user,
            action='CREATE',
            content_type=content_type,
            object_id=instance.id,
            model_name='Product',
            record_id=instance.id,
            description=f'Created product: {instance.name} (₱{instance.price})',
            data_after=data_after
        )
    else:
        # Check for archive/restore
        action = getattr(instance, '_audit_action', 'UPDATE')

        if action == 'ARCHIVE':
            description = f'Archived product: {instance.name}'
        elif action == 'RESTORE':
            description = f'Restored product: {instance.name}'
        else:
            description = f'Updated product: {instance.name}'

        # Get before state if available
        data_before = getattr(instance, '_audit_before_state', None)

        AuditLog.objects.create(
            user=user,
            action=action,
            content_type=content_type,
            object_id=instance.id,
            model_name='Product',
            record_id=instance.id,
            description=description,
            data_before=data_before,
            data_after=data_after
        )


@receiver(post_delete, sender=Product)
def log_product_deletion(sender, instance, **kwargs):
    """Track product deletion"""
    user = get_current_user()
    content_type = ContentType.objects.get_for_model(instance)

    AuditLog.objects.create(
        user=user,
        action='DELETE',
        content_type=content_type,
        object_id=instance.id,
        model_name='Product',
        record_id=instance.id,
        description=f'Deleted product: {instance.name}',
        data_before=serialize_model_instance(instance)
    )


# ==================== ORDER TRACKING ====================

@receiver(post_save, sender=Order)
def log_order_changes(sender, instance, created, **kwargs):
    """Track order creation and updates"""
    user = get_current_user() or instance.processed_by
    content_type = ContentType.objects.get_for_model(instance)

    data_after = serialize_model_instance(instance)

    if created:
        AuditLog.objects.create(
            user=user,
            action='CREATE',
            content_type=content_type,
            object_id=instance.id,
            model_name='Order',
            record_id=instance.id,
            description=f'Created order {instance.order_number} - {instance.get_status_display()}',
            data_after=data_after
        )
    else:
        data_before = getattr(instance, '_audit_before_state', None)

        AuditLog.objects.create(
            user=user,
            action='UPDATE',
            content_type=content_type,
            object_id=instance.id,
            model_name='Order',
            record_id=instance.id,
            description=f'Updated order {instance.order_number} to {instance.get_status_display()}',
            data_before=data_before,
            data_after=data_after
        )


# ==================== PAYMENT TRACKING ====================

@receiver(post_save, sender=Payment)
def log_payment_changes(sender, instance, created, **kwargs):
    """Track payment creation and updates"""
    user = get_current_user() or instance.processed_by
    content_type = ContentType.objects.get_for_model(instance)

    data_after = serialize_model_instance(instance)

    if created:
        AuditLog.objects.create(
            user=user,
            action='CREATE',
            content_type=content_type,
            object_id=instance.id,
            model_name='Payment',
            record_id=instance.id,
            description=f'Payment created: {instance.get_method_display()} ₱{instance.amount} for {instance.order.order_number}',
            data_after=data_after
        )
    else:
        data_before = getattr(instance, '_audit_before_state', None)

        AuditLog.objects.create(
            user=user,
            action='UPDATE',
            content_type=content_type,
            object_id=instance.id,
            model_name='Payment',
            record_id=instance.id,
            description=f'Payment updated: {instance.get_status_display()} - {instance.get_method_display()} ₱{instance.amount}',
            data_before=data_before,
            data_after=data_after
        )


# ==================== STOCK TRANSACTION TRACKING ====================

@receiver(post_save, sender=StockTransaction)
def log_stock_transaction(sender, instance, created, **kwargs):
    """Track stock transactions"""
    if not created:
        return  # Only log creation of stock transactions

    user = get_current_user() or instance.recorded_by
    content_type = ContentType.objects.get_for_model(instance)

    AuditLog.objects.create(
        user=user,
        action='CREATE',
        content_type=content_type,
        object_id=instance.id,
        model_name='StockTransaction',
        record_id=instance.id,
        description=f'Stock {instance.get_transaction_type_display()}: {instance.quantity} {instance.ingredient.unit} of {instance.ingredient.name}',
        data_after=serialize_model_instance(instance)
    )


# ==================== PRE-SAVE HOOKS FOR BEFORE STATE ====================

@receiver(pre_save, sender=User)
def capture_user_before_state(sender, instance, **kwargs):
    """Capture user state before update"""
    if instance.pk:  # Only for updates
        try:
            old_instance = User.objects.get(pk=instance.pk)
            instance._audit_before_state = serialize_model_instance(old_instance, exclude_fields=['password'])
        except User.DoesNotExist:
            pass


@receiver(pre_save, sender=Product)
def capture_product_before_state(sender, instance, **kwargs):
    """Capture product state before update"""
    if instance.pk:  # Only for updates
        try:
            old_instance = Product.objects.get(pk=instance.pk)
            instance._audit_before_state = serialize_model_instance(old_instance)
        except Product.DoesNotExist:
            pass


@receiver(pre_save, sender=Order)
def capture_order_before_state(sender, instance, **kwargs):
    """Capture order state before update"""
    if instance.pk:
        try:
            old_instance = Order.objects.get(pk=instance.pk)
            instance._audit_before_state = serialize_model_instance(old_instance)
        except Order.DoesNotExist:
            pass


@receiver(pre_save, sender=Payment)
def capture_payment_before_state(sender, instance, **kwargs):
    """Capture payment state before update"""
    if instance.pk:
        try:
            old_instance = Payment.objects.get(pk=instance.pk)
            instance._audit_before_state = serialize_model_instance(old_instance)
        except Payment.DoesNotExist:
            pass
