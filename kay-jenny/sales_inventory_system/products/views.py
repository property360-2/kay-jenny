from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import F, Q, Prefetch
from django.core.paginator import Paginator
from .models import Product, Ingredient, RecipeItem, RecipeIngredient
from sales_inventory_system.system.models import AuditTrail
import json
from decimal import Decimal

def is_admin(user):
    return user.is_authenticated and user.is_admin

@login_required
@user_passes_test(is_admin)
def product_detail(request, pk):
    """Display product details including recipe/BOM"""
    product = get_object_or_404(Product, pk=pk, is_archived=False)

    # Get or create recipe
    recipe_item, _ = RecipeItem.objects.get_or_create(product=product)

    context = {
        'product': product,
        'recipe_item': recipe_item,
        'recipe_ingredients': recipe_item.ingredients.all(),
    }
    return render(request, 'products/detail.html', context)

@login_required
@user_passes_test(is_admin)
def product_list(request):
    """List all products with search, filter, and pagination"""

    # Get query parameters
    search = request.GET.get('search', '').strip()
    category = request.GET.get('category', '').strip()
    stock_status = request.GET.get('stock_status', '').strip()
    page_number = request.GET.get('page', 1)

    # Base queryset with optimizations to reduce N+1 queries
    products = Product.objects.filter(is_archived=False).select_related(
        'recipe'
    ).prefetch_related(
        'recipe__ingredients__ingredient'
    )

    # Apply search filter
    if search:
        products = products.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search) |
            Q(category__icontains=search)
        )

    # Apply category filter
    if category:
        products = products.filter(category=category)

    # Apply stock status filter
    if stock_status == 'low':
        products = products.filter(stock__lt=F('threshold'), stock__gt=0)
    elif stock_status == 'out':
        products = products.filter(stock=0)
    elif stock_status == 'in_stock':
        products = products.filter(stock__gte=F('threshold'))

    # Get all categories for filter dropdown
    categories = Product.objects.filter(
        is_archived=False
    ).values_list('category', flat=True).distinct().order_by('category')
    categories = [c for c in categories if c]  # Remove empty categories

    # Calculate statistics
    # For low_stock_count, filter products where calculated_stock is below threshold
    all_active_products = Product.objects.filter(is_archived=False).select_related(
        'recipe'
    ).prefetch_related(
        'recipe__ingredients__ingredient'
    )
    low_stock_products = [p for p in all_active_products if p.calculated_stock < p.threshold and p.calculated_stock > 0]
    total_count = products.count()

    # Pagination
    paginator = Paginator(products.order_by('category', 'name'), 12)  # 12 products per page
    page_obj = paginator.get_page(page_number)

    # Check if AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Return JSON for AJAX requests
        products_data = []
        for product in page_obj:
            products_data.append({
                'id': product.id,
                'name': product.name,
                'description': product.description or '',
                'price': float(product.price),
                'stock': product.stock,
                'calculated_stock': product.calculated_stock,
                'threshold': product.threshold,
                'category': product.category or '',
                'is_low_stock': product.is_low_stock,
                'image_url': product.image.url if product.image else None,
            })

        return JsonResponse({
            'success': True,
            'products': products_data,
            'pagination': {
                'current_page': page_obj.number,
                'total_pages': paginator.num_pages,
                'total_count': total_count,
                'has_previous': page_obj.has_previous(),
                'has_next': page_obj.has_next(),
                'previous_page': page_obj.previous_page_number() if page_obj.has_previous() else None,
                'next_page': page_obj.next_page_number() if page_obj.has_next() else None,
            }
        })

    # Regular page load
    context = {
        'page_obj': page_obj,
        'products': page_obj,  # For backward compatibility
        'categories': categories,
        'low_stock_count': len(low_stock_products),
        'total_count': total_count,
        'search': search,
        'selected_category': category,
        'selected_stock_status': stock_status,
    }
    return render(request, 'products/list.html', context)

@login_required
@user_passes_test(is_admin)
def product_create(request):
    """Create a new product (with or without BOM)"""
    if request.method == 'POST':
        from django.db import transaction

        try:
            name = request.POST.get('name')
            description = request.POST.get('description', '')
            price = request.POST.get('price')
            category = request.POST.get('category', '')
            image = request.FILES.get('image')
            requires_bom = request.POST.get('requires_bom') == 'on'
            ingredients_json_str = request.POST.get('ingredients_json', '[]')

            # Parse ingredients JSON
            try:
                ingredients_data = json.loads(ingredients_json_str)
            except json.JSONDecodeError:
                ingredients_data = []

            # Validate based on product type
            if requires_bom:
                # Manufactured product: requires BOM/ingredients
                if not ingredients_data:
                    messages.error(request, 'Manufactured products must have at least one ingredient in the recipe.')
                    return render(request, 'products/form.html', {
                        'action': 'Create',
                        'form_data': {
                            'name': name,
                            'description': description,
                            'price': price,
                            'category': category,
                        }
                    })
                stock = 0  # Stock for manufactured products starts at 0
                threshold = request.POST.get('threshold', 10)
            else:
                # Simple product: requires stock
                stock_str = request.POST.get('stock', '')
                threshold = request.POST.get('threshold', 10)
                try:
                    stock = int(stock_str) if stock_str else 0
                    if stock < 0:
                        messages.error(request, 'Simple products must have a stock quantity >= 0.')
                        return render(request, 'products/form.html', {
                            'action': 'Create',
                            'form_data': {
                                'name': name,
                                'description': description,
                                'price': price,
                                'stock': stock,
                                'category': category,
                                'threshold': threshold,
                            }
                        })
                except (ValueError, TypeError):
                    messages.error(request, 'Simple products must have a valid stock quantity.')
                    return render(request, 'products/form.html', {
                        'action': 'Create',
                        'form_data': {
                            'name': name,
                            'description': description,
                            'price': price,
                            'stock': stock_str,
                            'category': category,
                            'threshold': threshold,
                        }
                    })

            with transaction.atomic():
                # Create product
                product = Product.objects.create(
                    name=name,
                    description=description,
                    price=price,
                    stock=stock,
                    threshold=threshold,
                    category=category,
                    image=image,
                    requires_bom=requires_bom
                )

                # Create recipe item for the product (always created)
                recipe_item = RecipeItem.objects.create(product=product)

                # Create recipe ingredients only if BOM is required
                ingredients_count = 0
                if requires_bom and ingredients_data:
                    for ing_data in ingredients_data:
                        try:
                            ingredient = Ingredient.objects.get(id=ing_data.get('id'))
                            RecipeIngredient.objects.create(
                                recipe=recipe_item,
                                ingredient=ingredient,
                                quantity=Decimal(str(ing_data.get('quantity', 0)))
                            )
                            ingredients_count += 1
                        except (Ingredient.DoesNotExist, ValueError, KeyError):
                            # Skip invalid ingredients
                            continue

                # Create audit log
                product_type = 'Manufactured (with BOM)' if requires_bom else 'Simple stock item'
                AuditTrail.objects.create(
                    user=request.user,
                    action='CREATE',
                    model_name='Product',
                    record_id=product.id,
                    description=f'Created {product_type}: {product.name}',
                    data_snapshot={
                        'name': name,
                        'price': str(price),
                        'stock': stock,
                        'requires_bom': requires_bom,
                        'ingredients_count': ingredients_count
                    }
                )

                success_msg = f'Product "{product.name}" created successfully!'
                if requires_bom:
                    success_msg += f' Recipe with {ingredients_count} ingredient(s) added.'
                messages.success(request, success_msg)
                return redirect('products:list')

        except Exception as e:
            import traceback
            error_detail = str(e)
            print(f"Product creation error: {error_detail}")
            print(traceback.format_exc())
            messages.error(request, f'Error creating product: {error_detail}')
            return render(request, 'products/form.html', {
                'action': 'Create',
                'form_data': {
                    'name': name,
                    'description': description,
                    'price': price,
                    'stock': request.POST.get('stock', 0),
                    'category': category,
                    'threshold': request.POST.get('threshold', 10),
                }
            })

    return render(request, 'products/form.html', {'action': 'Create'})

@login_required
@user_passes_test(is_admin)
def product_edit(request, pk):
    """Edit an existing product (simple or with BOM)"""
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        old_stock = product.stock
        old_requires_bom = product.requires_bom

        product.name = request.POST.get('name')
        product.description = request.POST.get('description', '')
        product.price = request.POST.get('price')
        product.category = request.POST.get('category', '')
        product.requires_bom = request.POST.get('requires_bom') == 'on'
        product.threshold = request.POST.get('threshold', 10)

        # Handle stock based on product type
        if not product.requires_bom:
            # Simple product: allow stock updates
            product.stock = request.POST.get('stock', 0)
        else:
            # Manufactured product: keep stock at 0
            product.stock = 0

        if request.FILES.get('image'):
            product.image = request.FILES.get('image')

        product.save()

        # Create audit log
        description = f'Updated product: {product.name}'
        changes = []
        if old_stock != int(product.stock):
            changes.append(f'Stock: {old_stock} → {product.stock}')
        if old_requires_bom != product.requires_bom:
            bom_status = 'with BOM' if product.requires_bom else 'without BOM'
            changes.append(f'Type: {bom_status}')

        if changes:
            description += f' ({", ".join(changes)})'

        AuditTrail.objects.create(
            user=request.user,
            action='UPDATE',
            model_name='Product',
            record_id=product.id,
            description=description,
            data_snapshot={
                'name': product.name,
                'price': str(product.price),
                'stock': product.stock,
                'requires_bom': product.requires_bom,
                'old_stock': old_stock,
                'old_requires_bom': old_requires_bom
            }
        )

        messages.success(request, f'Product "{product.name}" updated successfully!')
        return redirect('products:list')

    context = {'product': product, 'action': 'Edit'}
    return render(request, 'products/form.html', context)

@login_required
@user_passes_test(is_admin)
def product_archive(request, pk):
    """Archive a product"""
    product = get_object_or_404(Product, pk=pk)
    product.is_archived = True
    product.save()

    # Create audit log
    AuditTrail.objects.create(
        user=request.user,
        action='ARCHIVE',
        model_name='Product',
        record_id=product.id,
        description=f'Archived product: {product.name}',
        data_snapshot={'name': product.name, 'price': str(product.price)}
    )

    messages.success(request, f'Product "{product.name}" archived successfully!')
    return redirect('products:list')


@login_required
@user_passes_test(is_admin)
def archived_products_list(request):
    """List all archived products with search and filtering"""

    # Get query parameters
    search = request.GET.get('search', '').strip()
    category = request.GET.get('category', '').strip()
    page_number = request.GET.get('page', 1)

    # Base queryset - only archived products
    archived_products = Product.objects.filter(is_archived=True).select_related('recipe').prefetch_related('recipe__ingredients__ingredient')

    # Apply search filter
    if search:
        archived_products = archived_products.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search) |
            Q(category__icontains=search)
        )

    # Apply category filter
    if category:
        archived_products = archived_products.filter(category=category)

    # Distinct categories for filter dropdown (non-empty only)
    categories = Product.objects.filter(
        is_archived=True
    ).values_list('category', flat=True).distinct().order_by('category')
    categories = [c for c in categories if c]

    # Order by name
    archived_products = archived_products.order_by('name')

    # Get archive info from AuditTrail
    archive_info = {}
    audit_records = AuditTrail.objects.filter(
        action='ARCHIVE',
        model_name='Product'
    ).order_by('-created_at')

    for record in audit_records:
        if record.record_id not in archive_info:
            archive_info[record.record_id] = {
                'archived_by': record.user.username if record.user else 'Unknown',
                'archived_at': record.created_at,
            }

    # Pagination
    paginator = Paginator(archived_products, 12)  # 12 products per page
    page_obj = paginator.get_page(page_number)

    # Attach archive info to each product
    for product in page_obj:
        if product.id in archive_info:
            product.archive_info = archive_info[product.id]
        else:
            product.archive_info = {
                'archived_by': 'Unknown',
                'archived_at': 'Unknown date'
            }

    # AJAX response for async filtering
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        products_data = []
        for product in page_obj:
            archived_at_val = product.archive_info.get('archived_at')
            if hasattr(archived_at_val, 'strftime'):
                archived_at_display = archived_at_val.strftime("%Y-%m-%d %H:%M")
            else:
                archived_at_display = archived_at_val or 'Unknown date'

            products_data.append({
                'id': product.id,
                'name': product.name,
                'description': product.description or '',
                'category': product.category or 'N/A',
                'price': float(product.price),
                'archived_by': product.archive_info.get('archived_by', 'Unknown'),
                'archived_at': archived_at_display,
                'image_url': product.image.url if product.image else '',
            })

        return JsonResponse({
            'success': True,
            'products': products_data,
            'pagination': {
                'page': page_obj.number,
                'total_pages': paginator.num_pages,
                'total_count': paginator.count,
                'has_previous': page_obj.has_previous(),
                'has_next': page_obj.has_next(),
                'previous_page_number': page_obj.previous_page_number() if page_obj.has_previous() else None,
                'next_page_number': page_obj.next_page_number() if page_obj.has_next() else None,
                'first_page': 1,
                'last_page': paginator.num_pages,
            },
            'filters': {
                'search': search,
                'category': category,
            }
        })

    # Regular page load
    context = {
        'page_obj': page_obj,
        'products': page_obj,
        'total_count': paginator.count,
        'search': search,
        'categories': categories,
        'selected_category': category,
    }
    return render(request, 'products/archived_list.html', context)


@login_required
@user_passes_test(is_admin)
def product_unarchive(request, pk):
    """Restore an archived product"""
    product = get_object_or_404(Product, pk=pk, is_archived=True)
    product.is_archived = False
    product.save()

    # Create audit log
    AuditTrail.objects.create(
        user=request.user,
        action='RESTORE',
        model_name='Product',
        record_id=product.id,
        description=f'Restored product: {product.name}',
        data_snapshot={'name': product.name, 'price': str(product.price)}
    )

    messages.success(request, f'Product "{product.name}" restored successfully!')
    return redirect('products:archived_list')


# ==================== Ingredient Management Views ====================

@login_required
@user_passes_test(is_admin)
def ingredient_list(request):
    """List all ingredients with search and filtering"""
    search = request.GET.get('search', '').strip()
    status = request.GET.get('status', '').strip()
    page_number = request.GET.get('page', 1)

    # Base queryset
    ingredients = Ingredient.objects.all()

    # Apply search filter
    if search:
        ingredients = ingredients.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search)
        )

    # Apply status filter
    if status == 'active':
        ingredients = ingredients.filter(is_active=True)
    elif status == 'inactive':
        ingredients = ingredients.filter(is_active=False)
    elif status == 'low':
        ingredients = ingredients.filter(current_stock__lt=F('min_stock'))

    # Order by name
    ingredients = ingredients.order_by('name')

    # Pagination
    paginator = Paginator(ingredients, 20)
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'ingredients': page_obj,
        'search': search,
        'status': status,
    }
    return render(request, 'products/ingredient_list.html', context)


@login_required
@user_passes_test(is_admin)
def ingredient_create(request):
    """Create a new ingredient"""
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            description = request.POST.get('description', '')
            unit = request.POST.get('unit', 'g')
            current_stock = Decimal(request.POST.get('current_stock', '0.00'))
            min_stock = Decimal(request.POST.get('min_stock', '10.00'))
            variance_allowance = Decimal(request.POST.get('variance_allowance', '10.00'))

            if not name:
                raise ValueError('Ingredient name is required')

            ingredient = Ingredient.objects.create(
                name=name,
                description=description,
                unit=unit,
                current_stock=current_stock,
                min_stock=min_stock,
                variance_allowance=variance_allowance,
                is_active=True
            )

            messages.success(request, f'Ingredient "{ingredient.name}" created successfully!')
            return redirect('products:ingredient_list')

        except Exception as e:
            messages.error(request, f'Error creating ingredient: {str(e)}')

    context = {
        'action': 'Create',
        'units': ['g', 'ml', 'pcs']
    }
    return render(request, 'products/ingredient_form.html', context)


@login_required
@user_passes_test(is_admin)
def ingredient_edit(request, pk):
    """Edit an existing ingredient"""
    ingredient = get_object_or_404(Ingredient, pk=pk)

    if request.method == 'POST':
        try:
            ingredient.name = request.POST.get('name')
            ingredient.description = request.POST.get('description', '')
            ingredient.unit = request.POST.get('unit', 'g')
            ingredient.current_stock = Decimal(request.POST.get('current_stock', '0.00'))
            ingredient.min_stock = Decimal(request.POST.get('min_stock', '10.00'))
            ingredient.variance_allowance = Decimal(request.POST.get('variance_allowance', '10.00'))
            ingredient.is_active = request.POST.get('is_active') == 'on'
            ingredient.save()

            messages.success(request, f'Ingredient "{ingredient.name}" updated successfully!')
            return redirect('products:ingredient_list')

        except Exception as e:
            messages.error(request, f'Error updating ingredient: {str(e)}')

    context = {
        'ingredient': ingredient,
        'action': 'Edit',
        'units': ['g', 'ml', 'pcs']
    }
    return render(request, 'products/ingredient_form.html', context)


@login_required
@user_passes_test(is_admin)
def ingredient_delete(request, pk):
    """Delete an ingredient"""
    ingredient = get_object_or_404(Ingredient, pk=pk)
    name = ingredient.name
    ingredient.delete()

    messages.success(request, f'Ingredient "{name}" deleted successfully!')
    return redirect('products:ingredient_list')


# ==================== Recipe/BOM Management Views ====================

@login_required
@user_passes_test(is_admin)
def recipe_edit(request, pk):
    """Edit product recipe/BOM"""
    from django.db import transaction

    product = get_object_or_404(Product, pk=pk)

    # Get or create recipe item
    recipe_item, created = RecipeItem.objects.get_or_create(product=product)

    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Delete existing ingredients
                recipe_item.ingredients.all().delete()

                # Add new ingredients from form
                ingredients_data = request.POST.getlist('ingredient_id')
                quantities_data = request.POST.getlist('quantity')

                for ing_id, qty in zip(ingredients_data, quantities_data):
                    if ing_id and qty:
                        try:
                            ingredient = Ingredient.objects.get(id=ing_id)
                            RecipeIngredient.objects.create(
                                recipe=recipe_item,
                                ingredient=ingredient,
                                quantity=Decimal(qty)
                            )
                        except (Ingredient.DoesNotExist, ValueError):
                            pass

                messages.success(request, f'Recipe for "{product.name}" updated successfully!')
                return redirect('products:edit', pk=product.id)

        except Exception as e:
            messages.error(request, f'Error updating recipe: {str(e)}')

    # Get all active ingredients
    all_ingredients = Ingredient.objects.filter(is_active=True).order_by('name')

    # Get current recipe ingredients
    recipe_ingredients = recipe_item.ingredients.all()

    context = {
        'product': product,
        'recipe_item': recipe_item,
        'recipe_ingredients': recipe_ingredients,
        'all_ingredients': all_ingredients,
    }
    return render(request, 'products/recipe_form.html', context)


@login_required
@user_passes_test(is_admin)
def api_list_ingredients(request):
    """API endpoint for listing all ingredients (for product creation form)"""
    # Get all active ingredients
    ingredients = Ingredient.objects.filter(is_active=True).order_by('name')

    results = []
    for ingredient in ingredients:
        results.append({
            'id': ingredient.id,
            'name': ingredient.name,
            'unit': ingredient.unit,
            'current_stock': float(ingredient.current_stock),
        })

    return JsonResponse(results, safe=False)


@login_required
@user_passes_test(is_admin)
def api_create_ingredient(request):
    """API endpoint for creating a new ingredient"""
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'message': 'Only POST method is allowed'
        }, status=405)

    try:
        name = request.POST.get('name', '').strip()
        unit = request.POST.get('unit', '').strip()
        current_stock_str = request.POST.get('current_stock', '0')

        # Validate required fields
        if not name:
            return JsonResponse({
                'success': False,
                'message': 'Ingredient name is required'
            })

        if not unit:
            return JsonResponse({
                'success': False,
                'message': 'Unit of measurement is required'
            })

        try:
            current_stock = Decimal(current_stock_str)
        except (ValueError, TypeError):
            return JsonResponse({
                'success': False,
                'message': 'Stock must be a valid number'
            })

        # Check if ingredient already exists
        if Ingredient.objects.filter(name=name).exists():
            return JsonResponse({
                'success': False,
                'message': f'Ingredient "{name}" already exists'
            })

        # Create the ingredient with defaults
        ingredient = Ingredient.objects.create(
            name=name,
            unit=unit,
            current_stock=current_stock,
            min_stock=Decimal('0'),  # Default min stock
            variance_allowance=Decimal('10'),  # Default variance allowance
            is_active=True
        )

        return JsonResponse({
            'success': True,
            'ingredient': {
                'id': ingredient.id,
                'name': ingredient.name,
                'unit': ingredient.unit,
                'current_stock': float(ingredient.current_stock),
            },
            'message': f'Ingredient "{ingredient.name}" created successfully'
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error creating ingredient: {str(e)}'
        })


@login_required
@user_passes_test(is_admin)
def api_search_ingredients(request):
    """API endpoint for searching ingredients (async search)"""
    query = request.GET.get('q', '').strip()

    if not query or len(query) < 1:
        return JsonResponse({'results': []})

    # Search ingredients by name or unit
    ingredients = Ingredient.objects.filter(
        is_active=True
    ).filter(
        Q(name__icontains=query) |
        Q(description__icontains=query) |
        Q(unit__icontains=query)
    ).order_by('name')[:10]  # Limit to 10 results

    results = []
    for ingredient in ingredients:
        results.append({
            'id': ingredient.id,
            'name': ingredient.name,
            'unit': ingredient.unit,
            'cost_per_unit': 0,
            'current_stock': float(ingredient.current_stock),
            'display': f"{ingredient.name} ({ingredient.unit})"
        })

    return JsonResponse({'results': results})


@login_required
@user_passes_test(is_admin)
def api_list_categories(request):
    """API endpoint for listing all product categories"""
    # Get all unique categories from non-archived products
    all_categories = Product.objects.filter(
        is_archived=False
    ).values_list('category', flat=True).distinct().order_by('category')
    all_categories = [c for c in all_categories if c]  # Remove empty categories

    results = [{'name': cat} for cat in all_categories]
    return JsonResponse(results, safe=False)


@login_required
@user_passes_test(is_admin)
def api_create_category(request):
    """API endpoint for creating a new product category"""
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'message': 'Only POST method is allowed'
        }, status=405)

    try:
        category_name = request.POST.get('category', '').strip()

        if not category_name:
            return JsonResponse({
                'success': False,
                'message': 'Category name is required'
            })

        # Return the category name for immediate use
        return JsonResponse({
            'success': True,
            'category': category_name,
            'message': f'Category "{category_name}" created successfully'
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error creating category: {str(e)}'
        })


@login_required
@user_passes_test(is_admin)
def api_search_categories(request):
    """API endpoint for searching product categories (async search)"""
    query = request.GET.get('q', '').strip()

    # Get all unique categories
    all_categories = Product.objects.filter(
        is_archived=False
    ).values_list('category', flat=True).distinct().order_by('category')
    all_categories = [c for c in all_categories if c]  # Remove empty categories

    # Filter based on query
    if query:
        matching_categories = [c for c in all_categories if query.lower() in c.lower()]
    else:
        matching_categories = list(all_categories)

    # Limit to 10 results
    matching_categories = matching_categories[:10]

    results = [{'name': cat} for cat in matching_categories]
    return JsonResponse({'results': results})


@login_required
@user_passes_test(is_admin)
def api_search_archives(request):
    """API endpoint for searching all archived items (products, users, orders)"""
    from accounts.models import User
    from orders.models import Order

    query = request.GET.get('q', '').strip()
    archive_type = request.GET.get('type', 'all').strip().lower()

    results = {
        'products': [],
        'users': [],
        'orders': [],
        'query': query
    }

    if not query:
        return JsonResponse(results)

    # Search archived products
    if archive_type in ['all', 'products']:
        archived_products = Product.objects.filter(is_archived=True).filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__icontains=query)
        ).order_by('name')[:10]

        for product in archived_products:
            results['products'].append({
                'id': product.id,
                'name': product.name,
                'category': product.category or 'N/A',
                'price': float(product.price),
                'type': 'product'
            })

    # Search archived users/staff
    if archive_type in ['all', 'users']:
        archived_users = User.objects.filter(is_archived=True).filter(
            Q(username__icontains=query) |
            Q(email__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        ).order_by('username')[:10]

        for user in archived_users:
            results['users'].append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'full_name': f"{user.first_name} {user.last_name}".strip() or user.username,
                'role': user.get_role_display(),
                'type': 'user'
            })

    # Search archived orders
    if archive_type in ['all', 'orders']:
        archived_orders = Order.objects.filter(is_archived=True).filter(
            Q(order_number__icontains=query) |
            Q(customer_name__icontains=query)
        ).order_by('-created_at')[:10]

        for order in archived_orders:
            results['orders'].append({
                'id': order.id,
                'order_number': order.order_number,
                'customer_name': order.customer_name or 'N/A',
                'status': order.get_status_display(),
                'total_amount': float(order.total_amount),
                'created_at': order.created_at.strftime("%Y-%m-%d %H:%M"),
                'type': 'order'
            })

    return JsonResponse(results)
