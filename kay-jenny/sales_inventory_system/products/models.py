from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.utils import timezone

class Product(models.Model):
    """Product model for inventory management"""

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    stock = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    threshold = models.IntegerField(
        default=10,
        validators=[MinValueValidator(0)],
        help_text="Minimum stock level before low-stock alert"
    )
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    category = models.CharField(max_length=100, blank=True)
    requires_bom = models.BooleanField(
        default=False,
        help_text="If True, this product requires a Bill of Materials (BOM). If False, it's a simple stock item."
    )
    is_archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def is_low_stock(self):
        """Check if product stock is below threshold"""
        return self.stock < self.threshold

    @property
    def is_available(self):
        """Check if product is available for ordering"""
        return not self.is_archived and self.stock > 0

    @property
    def calculated_stock(self):
        """
        Calculate available product stock based on recipe ingredients.
        Returns the minimum number of units that can be produced with current ingredient stock.
        If product has no recipe, returns the hardcoded stock value.

        Formula: For each ingredient in recipe, calculate:
            available_units = ingredient_stock / required_quantity_per_product
        Return: min(available_units) for all ingredients (bottleneck ingredient)
        """
        # If product doesn't require a BOM or has no recipe, return hardcoded stock
        if not self.requires_bom:
            return self.stock

        try:
            recipe = self.recipe
        except RecipeItem.DoesNotExist:
            return self.stock

        # Get all ingredients in the recipe
        recipe_ingredients = recipe.ingredients.all()

        if not recipe_ingredients.exists():
            # Recipe exists but has no ingredients
            return 0

        # Calculate available units for each ingredient
        available_units = []
        for recipe_ingredient in recipe_ingredients:
            ingredient = recipe_ingredient.ingredient
            required_qty = recipe_ingredient.quantity

            # Avoid division by zero
            if required_qty == 0:
                continue

            # How many product units can we make with this ingredient?
            units_possible = int(ingredient.current_stock / required_qty)
            available_units.append(units_possible)

        # Return the minimum (bottleneck ingredient determines max producible units)
        return min(available_units) if available_units else 0


class Ingredient(models.Model):
    """Raw material/ingredient used in recipes"""

    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    unit = models.CharField(
        max_length=50,
        choices=[
            ('g', 'Grams'),
            ('ml', 'Milliliters'),
            ('pcs', 'Pieces'),
        ],
        default='g',
        help_text="Unit of measurement"
    )
    current_stock = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0'))]
    )
    min_stock = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Minimum stock level before alert"
    )
    variance_allowance = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=10,
        help_text="Variance allowance percentage (e.g., 10% for portioning tolerance)"
    )
    is_active = models.BooleanField(default=True)
    is_available = models.BooleanField(
        default=True,
        help_text="Temporarily toggleable by cashier (false = out of stock/unavailable)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.unit})"

    @property
    def is_low_stock(self):
        return self.current_stock < self.min_stock


class RecipeItem(models.Model):
    """Bill of Materials - ingredients needed for a product"""

    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        related_name='recipe',
        db_index=True,
        help_text="Product that this recipe creates"
    )
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Recipe"
        verbose_name_plural = "Recipes"

    def __str__(self):
        return f"Recipe for {self.product.name}"

    @property
    def total_cost(self):
        """Calculate total cost of all ingredients in recipe"""
        return 0  # Cost calculation not applicable with simplified ingredient system


class RecipeIngredient(models.Model):
    """Individual ingredient in a recipe"""

    recipe = models.ForeignKey(
        RecipeItem,
        on_delete=models.CASCADE,
        related_name='ingredients'
    )
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.001'))]
    )

    class Meta:
        unique_together = ('recipe', 'ingredient')

    def __str__(self):
        return f"{self.ingredient.name} ({self.quantity}{self.ingredient.unit}) for {self.recipe.product.name}"


class StockTransaction(models.Model):
    """Log all ingredient stock movements"""

    TRANSACTION_TYPES = [
        ('PURCHASE', 'Purchase'),
        ('DEDUCTION', 'Deduction (Sale)'),
        ('ADJUSTMENT', 'Adjustment'),
        ('WASTE', 'Waste/Spoilage'),
        ('FREEBIE', 'Freebie/Giveaway'),
        ('PREP', 'Prep Batch Conversion'),
    ]

    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    quantity = models.DecimalField(max_digits=10, decimal_places=3)
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    reference_type = models.CharField(
        max_length=50,
        blank=True,
        help_text="e.g., 'order', 'physical_count', 'waste_log', 'prep_batch'"
    )
    reference_id = models.IntegerField(null=True, blank=True)
    notes = models.TextField(blank=True)
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['ingredient', 'created_at']),
        ]

    def __str__(self):
        return f"{self.transaction_type}: {self.quantity} {self.ingredient.unit} of {self.ingredient.name}"


class PhysicalCount(models.Model):
    """Record physical stock counts for variance analysis"""

    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name='physical_counts')
    counted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    physical_quantity = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        help_text="Actual quantity counted"
    )
    theoretical_quantity = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        help_text="Quantity according to system records"
    )
    count_date = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-count_date']

    def __str__(self):
        return f"Count of {self.ingredient.name} on {self.count_date.date()}"

    @property
    def variance_quantity(self):
        """Difference between physical and theoretical"""
        return self.physical_quantity - self.theoretical_quantity

    @property
    def variance_percentage(self):
        """Variance as percentage"""
        if self.theoretical_quantity == 0:
            return 0
        return ((self.variance_quantity / self.theoretical_quantity) * 100)

    @property
    def within_tolerance(self):
        """Check if variance is within ingredient's tolerance"""
        return abs(self.variance_percentage) <= self.ingredient.variance_allowance


class VarianceRecord(models.Model):
    """Track variance between theoretical and actual inventory"""

    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name='variance_records')
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()

    theoretical_used = models.DecimalField(max_digits=10, decimal_places=3)
    actual_used = models.DecimalField(max_digits=10, decimal_places=3)

    variance_quantity = models.DecimalField(max_digits=10, decimal_places=3)
    variance_percentage = models.DecimalField(max_digits=6, decimal_places=2)
    within_tolerance = models.BooleanField(default=True)

    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-period_end']
        indexes = [
            models.Index(fields=['ingredient', 'period_end']),
        ]

    def __str__(self):
        return f"Variance for {self.ingredient.name}: {self.variance_percentage}%"


class WasteLog(models.Model):
    """Track waste, spoilage, and freebies"""

    WASTE_TYPES = [
        ('SPOILAGE', 'Spoilage'),
        ('WASTE', 'Waste'),
        ('FREEBIE', 'Freebie/Giveaway'),
        ('SAMPLE', 'Sample'),
        ('OTHER', 'Other'),
    ]

    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name='waste_logs')
    waste_type = models.CharField(max_length=20, choices=WASTE_TYPES)
    quantity = models.DecimalField(max_digits=10, decimal_places=3)
    reason = models.TextField(help_text="Description of why item was wasted")
    reported_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    waste_date = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-waste_date']
        indexes = [
            models.Index(fields=['ingredient', 'waste_date']),
        ]

    def __str__(self):
        return f"{self.waste_type}: {self.quantity} {self.ingredient.unit} of {self.ingredient.name}"

    @property
    def cost_impact(self):
        """Calculate cost of wasted ingredient"""
        return 0  # Cost calculation not applicable with simplified ingredient system


class PrepBatch(models.Model):
    """Batch conversion from raw ingredients to prepared items"""

    STATUS_CHOICES = [
        ('PLANNED', 'Planned'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]

    name = models.CharField(max_length=200, help_text="e.g., 'Dough Prep Batch 001'")
    recipe = models.ForeignKey(RecipeItem, on_delete=models.CASCADE, related_name='prep_batches')
    quantity_produced = models.IntegerField(help_text="Number of products created")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PLANNED')

    prepared_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    prep_start = models.DateTimeField(null=True, blank=True)
    prep_end = models.DateTimeField(null=True, blank=True)

    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.quantity_produced} units of {self.recipe.product.name}"

    @property
    def expected_ingredient_usage(self):
        """Calculate expected ingredient usage for this batch"""
        usage = {}
        for recipe_ing in self.recipe.ingredients.all():
            usage[recipe_ing.ingredient.name] = recipe_ing.quantity * self.quantity_produced
        return usage
