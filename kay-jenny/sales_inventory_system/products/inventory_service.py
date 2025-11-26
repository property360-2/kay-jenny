"""
Bill of Materials (BOM) Service Module

Handles:
- Ingredient deduction from orders
- Variance allowance calculations
- Stock transaction logging
- Physical count variance analysis
- Waste and spoilage tracking
"""

from decimal import Decimal
from django.db import transaction
from django.db.models import Q, F
from django.utils import timezone
from .models import (
    RecipeItem, StockTransaction, Ingredient,
    VarianceRecord, WasteLog, PhysicalCount
)


class IngredientDeductionError(Exception):
    """Raised when ingredient deduction fails"""
    pass


class BOMService:
    """Service for Bill of Materials operations"""

    @staticmethod
    def deduct_ingredients_for_order(order, user=None):
        """
        Deduct ingredients from stock when an order is completed.
        STRICT: All products must have recipes and sufficient ingredients must exist.

        Args:
            order: Order instance
            user: User who authorized the deduction

        Raises:
            IngredientDeductionError: If product lacks recipe or insufficient ingredients

        Returns:
            dict: Transaction details
        """
        deductions = []

        try:
            with transaction.atomic():
                # FIRST PASS: Validate all products have recipes and ingredients are sufficient
                for order_item in order.items.all():
                    product = order_item.product
                    quantity = order_item.quantity

                    # STRICT: Product MUST have a recipe
                    try:
                        recipe = product.recipe
                    except RecipeItem.DoesNotExist:
                        raise IngredientDeductionError(
                            f"Product '{product.name}' does not have a recipe defined. "
                            "All products must have recipes before orders can be placed."
                        )

                    # STRICT: Check all ingredients are sufficient BEFORE any deductions
                    for recipe_ingredient in recipe.ingredients.all():
                        ingredient = recipe_ingredient.ingredient
                        total_needed = recipe_ingredient.quantity * quantity

                        if ingredient.current_stock < total_needed:
                            raise IngredientDeductionError(
                                f"Insufficient '{ingredient.name}' for {product.name}. "
                                f"Need {total_needed} {ingredient.unit}, but only {ingredient.current_stock} available."
                            )

                # SECOND PASS: Perform actual deductions (only if all validations passed)
                for order_item in order.items.all():
                    product = order_item.product
                    quantity = order_item.quantity
                    recipe = product.recipe  # Already validated to exist

                    for recipe_ingredient in recipe.ingredients.all():
                        ingredient = recipe_ingredient.ingredient
                        total_needed = recipe_ingredient.quantity * quantity

                        # Deduct from ingredient stock
                        ingredient.current_stock -= total_needed
                        ingredient.save()

                        # Create stock transaction
                        StockTransaction.objects.create(
                            ingredient=ingredient,
                            transaction_type='DEDUCTION',
                            quantity=total_needed,
                            unit_cost=0,
                            reference_type='order',
                            reference_id=order.id,
                            notes=f"Deduction for {product.name} (Order: {order.order_number})",
                            recorded_by=user
                        )

                        deductions.append({
                            'ingredient': ingredient.name,
                            'quantity_deducted': total_needed,
                            'unit': ingredient.unit,
                            'cost': 0,
                            'remaining_stock': ingredient.current_stock
                        })

                return {
                    'success': True,
                    'deductions': deductions,
                    'total_cost': sum(d['cost'] for d in deductions),
                    'order_id': order.id
                }

        except Exception as e:
            if isinstance(e, IngredientDeductionError):
                raise
            raise IngredientDeductionError(f"Error deducting ingredients: {str(e)}")

    @staticmethod
    def check_ingredient_availability(product_id, quantity=1):
        """
        Check if a product has sufficient ingredients available.
        STRICT: Products MUST have recipes defined.

        Args:
            product_id: Product ID
            quantity: Quantity to produce

        Returns:
            dict: Availability status with shortage details
        """
        try:
            recipe = RecipeItem.objects.prefetch_related(
                'ingredients__ingredient'
            ).get(product_id=product_id)
        except RecipeItem.DoesNotExist:
            # STRICT: Product MUST have a recipe
            from .models import Product
            try:
                product = Product.objects.get(id=product_id)
                product_name = product.name
            except Product.DoesNotExist:
                product_name = f"Product #{product_id}"

            return {
                'available': False,
                'has_recipe': False,
                'error': f"Product '{product_name}' does not have a recipe defined. All products must have recipes.",
                'shortages': []
            }

        shortages = []

        for recipe_ingredient in recipe.ingredients.all():
            ingredient = recipe_ingredient.ingredient
            total_needed = recipe_ingredient.quantity * quantity

            # Check if ingredient is marked as unavailable by cashier
            if not ingredient.is_available:
                shortages.append({
                    'ingredient': ingredient.name,
                    'needed': total_needed,
                    'available': 0,
                    'shortage': total_needed,
                    'unit': ingredient.unit,
                    'reason': 'Marked as unavailable'
                })
            # Check if there's sufficient quantity
            elif ingredient.current_stock < total_needed:
                shortage = total_needed - ingredient.current_stock
                shortages.append({
                    'ingredient': ingredient.name,
                    'needed': total_needed,
                    'available': ingredient.current_stock,
                    'shortage': shortage,
                    'unit': ingredient.unit
                })

        return {
            'available': len(shortages) == 0,
            'has_recipe': True,
            'shortages': shortages,
            'total_shortages': len(shortages)
        }

    @staticmethod
    def log_waste(ingredient_id, quantity, waste_type='WASTE', reason='', user=None):
        """
        Log waste, spoilage, or freebie.

        Args:
            ingredient_id: Ingredient ID
            quantity: Quantity wasted
            waste_type: Type of waste (SPOILAGE, WASTE, FREEBIE, SAMPLE, OTHER)
            reason: Reason for waste
            user: User reporting the waste

        Returns:
            WasteLog instance
        """
        ingredient = Ingredient.objects.get(id=ingredient_id)

        with transaction.atomic():
            # Reduce ingredient stock
            ingredient.current_stock -= quantity
            ingredient.save()

            # Create waste log
            waste_log = WasteLog.objects.create(
                ingredient=ingredient,
                waste_type=waste_type,
                quantity=quantity,
                reason=reason,
                reported_by=user
            )

            # Create stock transaction for tracking
            StockTransaction.objects.create(
                ingredient=ingredient,
                transaction_type=waste_type,
                quantity=quantity,
                reference_type='waste_log',
                reference_id=waste_log.id,
                notes=f"{waste_type}: {reason}",
                recorded_by=user
            )

            return waste_log

    @staticmethod
    def calculate_variance(ingredient_id, period_start=None, period_end=None):
        """
        Calculate variance between theoretical and actual usage.

        Args:
            ingredient_id: Ingredient ID
            period_start: Start of period (default: beginning of month)
            period_end: End of period (default: now)

        Returns:
            dict: Variance analysis
        """
        if not period_end:
            period_end = timezone.now()

        if not period_start:
            # Default to beginning of current month
            period_start = period_end.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        ingredient = Ingredient.objects.get(id=ingredient_id)

        # Get all transactions in period
        transactions = StockTransaction.objects.filter(
            ingredient=ingredient,
            created_at__gte=period_start,
            created_at__lte=period_end
        )

        # Calculate theoretical usage
        deductions = transactions.filter(transaction_type='DEDUCTION')
        theoretical_used = sum(t.quantity for t in deductions) or Decimal('0')

        # Get actual usage from waste logs and physical counts
        waste_logs = WasteLog.objects.filter(
            ingredient=ingredient,
            waste_date__gte=period_start,
            waste_date__lte=period_end
        )
        actual_waste = sum(w.quantity for w in waste_logs) or Decimal('0')

        # Variance
        variance_qty = theoretical_used - actual_waste
        variance_pct = (variance_qty / theoretical_used * 100) if theoretical_used > 0 else Decimal('0')

        # Check if within tolerance
        within_tolerance = abs(variance_pct) <= ingredient.variance_allowance

        return {
            'ingredient': ingredient.name,
            'period_start': period_start,
            'period_end': period_end,
            'theoretical_used': theoretical_used,
            'actual_waste': actual_waste,
            'variance_quantity': variance_qty,
            'variance_percentage': float(variance_pct),
            'tolerance': ingredient.variance_allowance,
            'within_tolerance': within_tolerance
        }

    @staticmethod
    def record_physical_count(ingredient_id, physical_qty, notes='', user=None):
        """
        Record a physical count for variance analysis.

        Args:
            ingredient_id: Ingredient ID
            physical_qty: Physically counted quantity
            notes: Count notes
            user: User performing count

        Returns:
            PhysicalCount instance with variance data
        """
        ingredient = Ingredient.objects.get(id=ingredient_id)
        theoretical_qty = ingredient.current_stock

        physical_count = PhysicalCount.objects.create(
            ingredient=ingredient,
            physical_quantity=physical_qty,
            theoretical_quantity=theoretical_qty,
            notes=notes,
            counted_by=user
        )

        # Auto-update ingredient stock to physical count
        if physical_qty != theoretical_qty:
            ingredient.current_stock = physical_qty
            ingredient.save()

            # Log the adjustment as a transaction
            variance_qty = physical_qty - theoretical_qty
            StockTransaction.objects.create(
                ingredient=ingredient,
                transaction_type='ADJUSTMENT',
                quantity=abs(variance_qty),
                reference_type='physical_count',
                reference_id=physical_count.id,
                notes=f"Stock adjustment from physical count: {notes}",
                recorded_by=user
            )

        return physical_count

    @staticmethod
    def get_low_stock_ingredients():
        """
        Get all ingredients below minimum stock level.

        Returns:
            queryset: Ingredients with low stock
        """
        return Ingredient.objects.filter(
            Q(current_stock__lt=F('min_stock')) & Q(is_active=True)
        ).order_by('current_stock')

    @staticmethod
    def get_ingredient_usage_report(ingredient_id, days=30):
        """
        Generate ingredient usage report.

        Args:
            ingredient_id: Ingredient ID
            days: Number of days to include

        Returns:
            dict: Usage statistics
        """
        from django.utils import timezone
        from datetime import timedelta

        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)

        ingredient = Ingredient.objects.get(id=ingredient_id)

        # Get transactions
        transactions = StockTransaction.objects.filter(
            ingredient=ingredient,
            created_at__gte=start_date,
            created_at__lte=end_date
        )

        # Group by type
        by_type = {}
        for t in transactions:
            trans_type = t.get_transaction_type_display()
            if trans_type not in by_type:
                by_type[trans_type] = {
                    'quantity': Decimal('0'),
                    'cost': Decimal('0'),
                    'count': 0
                }
            by_type[trans_type]['quantity'] += t.quantity
            by_type[trans_type]['cost'] += (t.quantity * (t.unit_cost or 0))
            by_type[trans_type]['count'] += 1

        # Waste logs
        waste = WasteLog.objects.filter(
            ingredient=ingredient,
            waste_date__gte=start_date,
            waste_date__lte=end_date
        )

        by_waste_type = {}
        for w in waste:
            waste_type = w.get_waste_type_display()
            if waste_type not in by_waste_type:
                by_waste_type[waste_type] = {
                    'quantity': Decimal('0'),
                    'cost': Decimal('0'),
                    'count': 0
                }
            by_waste_type[waste_type]['quantity'] += w.quantity
            by_waste_type[waste_type]['cost'] += w.cost_impact
            by_waste_type[waste_type]['count'] += 1

        return {
            'ingredient': ingredient.name,
            'unit': ingredient.unit,
            'period_days': days,
            'period_start': start_date,
            'period_end': end_date,
            'transactions_by_type': by_type,
            'waste_by_type': by_waste_type,
            'total_transactions': transactions.count(),
            'current_stock': ingredient.current_stock,
            'cost_per_unit': 0
        }

    @staticmethod
    def check_order_availability(order_items_data):
        """
        Check if ingredients are available for all items in an order.

        Args:
            order_items_data: List of dicts with 'product_id' and 'quantity'
                Example: [{'product_id': 1, 'quantity': 2}, {'product_id': 2, 'quantity': 1}]

        Returns:
            dict: {
                'available': bool,  # True if all items can be made
                'shortages': [      # List of shortage details
                    {
                        'product': 'Product Name',
                        'ingredient': 'Ingredient Name',
                        'needed': 10,
                        'available': 5,
                        'shortage': 5,
                        'unit': 'kg'
                    }
                ]
            }
        """
        shortages = []

        for item_data in order_items_data:
            product_id = item_data.get('product_id')
            quantity = item_data.get('quantity', 1)

            availability = BOMService.check_ingredient_availability(product_id, quantity)

            if not availability['available']:
                # Add product info to shortage list
                try:
                    from .models import Product
                    product = Product.objects.get(id=product_id)
                    for shortage in availability['shortages']:
                        shortage['product'] = product.name
                        shortages.append(shortage)
                except:
                    for shortage in availability['shortages']:
                        shortage['product'] = f"Product #{product_id}"
                        shortages.append(shortage)

        return {
            'available': len(shortages) == 0,
            'shortages': shortages
        }

    @staticmethod
    def get_critical_low_stock(threshold_percentage=25):
        """
        Get ingredients that are critically low (below 25% of min stock).

        Args:
            threshold_percentage: Percentage threshold (default 25%)

        Returns:
            queryset: Ingredients below threshold
        """
        from django.db.models import F, ExpressionWrapper, FloatField
        from decimal import Decimal

        return Ingredient.objects.filter(
            is_active=True
        ).annotate(
            stock_ratio=ExpressionWrapper(
                F('current_stock') / F('min_stock'),
                output_field=FloatField()
            )
        ).filter(
            stock_ratio__lt=(Decimal(threshold_percentage) / 100)
        ).order_by('stock_ratio')
