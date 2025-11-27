from django.db.models import F
from .models import Product, Ingredient


def low_stock_notifications(request):
    """
    Add low stock notifications to all templates
    Available to both admin and cashier users
    """
    if not request.user.is_authenticated:
        return {'low_stock_count': 0, 'low_stock_items': []}

    low_stock_items = []

    # Check products with low calculated_stock (limit check for performance)
    try:
        products = Product.objects.filter(is_archived=False).prefetch_related('recipe__ingredients__ingredient')[:50]
        for product in products:
            try:
                calc_stock = product.calculated_stock
                if calc_stock < product.threshold:
                    low_stock_items.append({
                        'type': 'product',
                        'name': product.name,
                        'current': calc_stock,
                        'threshold': product.threshold,
                        'id': product.id,
                        'unit': 'units'
                    })
            except Exception:
                # Skip products with calculation errors
                continue
    except Exception:
        pass

    # Check ingredients with low stock
    try:
        ingredients = Ingredient.objects.filter(
            is_active=True,
            current_stock__lt=F('min_stock')
        )[:50]

        for ingredient in ingredients:
            low_stock_items.append({
                'type': 'ingredient',
                'name': ingredient.name,
                'current': float(ingredient.current_stock),
                'threshold': float(ingredient.min_stock),
                'unit': ingredient.unit,
                'id': ingredient.id
            })
    except Exception:
        pass

    # Sort by severity (lowest stock first) and limit to 10
    low_stock_items.sort(key=lambda x: (x['current'] / x['threshold']) if x['threshold'] > 0 else 0)
    low_stock_items = low_stock_items[:10]

    return {
        'low_stock_count': len(low_stock_items),
        'low_stock_items': low_stock_items
    }
