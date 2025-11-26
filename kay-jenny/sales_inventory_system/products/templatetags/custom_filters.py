"""
Custom template filters for products app
"""
from django import template

register = template.Library()


@register.filter
def multiply(value, arg):
    """Multiply value by arg"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0


# Alias for multiply to support templates using the shorter name
@register.filter(name="mul")
def mul(value, arg):
    return multiply(value, arg)


@register.filter
def divide(value, arg):
    """Divide value by arg"""
    try:
        divisor = float(arg) if arg else 1
        return float(value) / divisor if divisor != 0 else 0
    except (ValueError, TypeError):
        return 0


@register.filter
def as_float(value):
    """Convert value to float"""
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0


@register.filter
def smart_unit_display(quantity, unit):
    """
    Display quantity with intelligent unit conversion.
    Converts g to kg and ml to L when quantity >= 1000.

    Usage in template: {{ ingredient.current_stock|smart_unit_display:ingredient.unit }}

    Examples:
    - 1500g -> 1.50kg
    - 500g -> 500.00g
    - 2500ml -> 2.50L
    - 750ml -> 750.00ml
    - 15pcs -> 15.00pcs
    """
    try:
        quantity = float(quantity)
    except (ValueError, TypeError):
        return f"{quantity}{unit}"

    # Convert grams to kilograms if >= 1000
    if unit == 'g' and quantity >= 1000:
        kg_value = quantity / 1000
        return f"{kg_value:.2f}kg"

    # Convert milliliters to liters if >= 1000
    if unit == 'ml' and quantity >= 1000:
        liter_value = quantity / 1000
        return f"{liter_value:.2f}L"

    # Return as-is for other cases
    return f"{quantity:.2f}{unit}"
