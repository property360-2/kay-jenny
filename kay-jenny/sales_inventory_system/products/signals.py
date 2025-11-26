"""
Signals for BOM-related events
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib import messages
from sales_inventory_system.orders.models import Payment
from .inventory_service import BOMService, IngredientDeductionError
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Payment)
def deduct_ingredients_on_payment(sender, instance, created, **kwargs):
    """
    Automatically deduct ingredients when payment is confirmed.

    This signal is triggered when a Payment object is saved.
    If the payment status changes to 'SUCCESS', we deduct the required
    ingredients from inventory based on the order's recipe.
    """
    # Only process on update, not on creation
    if created:
        return

    # Only process when payment is confirmed
    if instance.status != 'SUCCESS':
        return

    # Check if ingredients have already been deducted
    # (to prevent double deduction on multiple saves)
    if hasattr(instance, '_ingredients_deducted'):
        return

    try:
        order = instance.order
        user = instance.processed_by

        # Attempt to deduct ingredients
        result = BOMService.deduct_ingredients_for_order(order, user=user)

        # Mark that we've processed this payment
        instance._ingredients_deducted = True

        logger.info(
            f"Ingredients deducted for order {order.order_number}. "
            f"Total cost: ₱{result['total_cost']}"
        )

    except IngredientDeductionError as e:
        # Log the error but don't fail the payment
        logger.error(
            f"Failed to deduct ingredients for order {instance.order.order_number}: {str(e)}"
        )
        # In a production system, you might want to:
        # - Send an alert to kitchen staff
        # - Create a task for manual inventory adjustment
        # - Notify management

    except Exception as e:
        logger.error(
            f"Unexpected error deducting ingredients for order {instance.order.order_number}: {str(e)}"
        )
