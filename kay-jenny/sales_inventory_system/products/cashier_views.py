from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from .models import Ingredient


def is_cashier(user):
    """Check if user is a cashier"""
    return user.is_authenticated and (user.is_cashier or user.is_admin)


@login_required
@user_passes_test(is_cashier)
def cashier_ingredients(request):
    """Display cashier ingredients management page with availability toggles"""

    # Get all active ingredients with their current stock
    ingredients = Ingredient.objects.filter(is_active=True).order_by('name')

    context = {
        'ingredients': ingredients,
    }
    return render(request, 'products/cashier_ingredients.html', context)


@login_required
@user_passes_test(is_cashier)
def api_toggle_ingredient_availability(request):
    """API endpoint to toggle ingredient availability"""

    if request.method == 'POST':
        try:
            ingredient_id = request.POST.get('ingredient_id')

            if not ingredient_id:
                return JsonResponse({
                    'success': False,
                    'error': 'Ingredient ID is required'
                })

            ingredient = Ingredient.objects.get(id=ingredient_id)

            # Toggle availability
            ingredient.is_available = not ingredient.is_available
            ingredient.save()

            return JsonResponse({
                'success': True,
                'ingredient_id': ingredient.id,
                'is_available': ingredient.is_available,
                'message': f"Ingredient '{ingredient.name}' marked as {'Available' if ingredient.is_available else 'Unavailable'}"
            })

        except Ingredient.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Ingredient not found'
            }, status=404)

        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)

    return JsonResponse({
        'success': False,
        'error': 'POST method required'
    }, status=400)


@login_required
@user_passes_test(is_cashier)
def api_get_ingredients(request):
    """API endpoint to get all ingredients with current availability"""

    try:
        ingredients = Ingredient.objects.filter(is_active=True).order_by('name')

        ingredients_data = []
        for ingredient in ingredients:
            ingredients_data.append({
                'id': ingredient.id,
                'name': ingredient.name,
                'unit': ingredient.unit,
                'current_stock': float(ingredient.current_stock),
                'is_available': ingredient.is_available,
                'is_low_stock': ingredient.is_low_stock,
                'min_stock': float(ingredient.min_stock),
            })

        return JsonResponse({
            'success': True,
            'ingredients': ingredients_data,
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
