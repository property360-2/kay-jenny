from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.db import transaction
from django.db.models import Q
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import timedelta
from .models import Order, OrderItem, Payment
from sales_inventory_system.products.models import Product

@login_required
def order_list(request):
    """Display list of all orders with search, filter, and pagination"""

    # Auto-expire pending orders older than 1 hour
    Order.expire_old_pending_orders()

    # Get query parameters
    search = request.GET.get('search', '').strip()
    status_filter = request.GET.get('status', '').strip()
    time_range = request.GET.get('time_range', 'all').strip()
    page_number = request.GET.get('page', 1)

    # Base queryset
    orders = Order.objects.all().select_related('payment').prefetch_related('items__product')

    # Apply search filter
    if search:
        orders = orders.filter(
            Q(order_number__icontains=search) |
            Q(customer_name__icontains=search) |
            Q(table_number__icontains=search)
        )

    # Apply status filter
    if status_filter:
        orders = orders.filter(status=status_filter)

    # Apply time range filter
    now = timezone.now()
    if time_range == '1day':
        cutoff_date = now - timedelta(days=1)
        orders = orders.filter(created_at__gte=cutoff_date)
    elif time_range == '7day':
        cutoff_date = now - timedelta(days=7)
        orders = orders.filter(created_at__gte=cutoff_date)
    elif time_range == '30day':
        cutoff_date = now - timedelta(days=30)
        orders = orders.filter(created_at__gte=cutoff_date)
    elif time_range == '60day':
        cutoff_date = now - timedelta(days=60)
        orders = orders.filter(created_at__gte=cutoff_date)
    elif time_range == '90day':
        cutoff_date = now - timedelta(days=90)
        orders = orders.filter(created_at__gte=cutoff_date)
    # 'all' or default: no time filter

    # Order by most recent
    orders = orders.order_by('-created_at')

    # Pagination
    paginator = Paginator(orders, 20)  # 20 orders per page
    page_obj = paginator.get_page(page_number)

    # Check if AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Return JSON for AJAX requests
        orders_data = []
        for order in page_obj:
            # Use prefetched items to avoid N+1 query
            items = list(order.items.all())  # Already prefetched from queryset
            items_list = [f"{item.quantity}x {item.product.name}" for item in items]
            items_summary = ", ".join(items_list[:2])  # First 2 items
            if len(items_list) > 2:
                items_summary += f", +{len(items_list) - 2} more"

            orders_data.append({
                'id': order.id,
                'order_number': order.order_number,
                'customer_name': order.customer_name,
                'table_number': order.table_number or '-',
                'items_summary': items_summary,
                'total_amount': float(order.total_amount),
                'status': order.status,
                'status_display': order.get_status_display(),
                'created_at': order.created_at.strftime('%b %d, %Y %I:%M %p'),
                'payment_status': order.payment.status if hasattr(order, 'payment') else 'PENDING',
            })

        return JsonResponse({
            'success': True,
            'orders': orders_data,
            'pagination': {
                'current_page': page_obj.number,
                'total_pages': paginator.num_pages,
                'total_count': paginator.count,
                'has_previous': page_obj.has_previous(),
                'has_next': page_obj.has_next(),
                'previous_page': page_obj.previous_page_number() if page_obj.has_previous() else None,
                'next_page': page_obj.next_page_number() if page_obj.has_next() else None,
            }
        })

    context = {
        'page_obj': page_obj,
        'orders': page_obj,  # For backward compatibility
        'search': search,
        'status_filter': status_filter,
        'time_range': time_range,
        'status_choices': Order.STATUS_CHOICES,
    }
    return render(request, 'orders/list.html', context)

@login_required
def order_detail(request, pk):
    """Display details of a specific order"""
    # Auto-expire pending orders older than 1 hour
    Order.expire_old_pending_orders()

    order = get_object_or_404(Order, pk=pk)

    context = {
        'order': order,
        'items': order.items.all(),
    }
    return render(request, 'orders/detail.html', context)

@login_required
def update_order_status(request, pk):
    """Update the status of an order"""
    # Auto-expire pending orders older than 1 hour
    Order.expire_old_pending_orders()

    if request.method == 'POST':
        try:
            import json
            order = get_object_or_404(Order, pk=pk)

            # Handle both form-encoded and JSON body
            if request.content_type == 'application/json':
                data = json.loads(request.body)
                new_status = data.get('status')
            else:
                new_status = request.POST.get('status')

            if new_status not in dict(Order.STATUS_CHOICES):
                return JsonResponse({
                    'success': False,
                    'message': 'Invalid status'
                })

            old_status = order.status
            order.status = new_status
            order.processed_by = request.user
            order.save()

messages.success(request, f'Order {order.order_number} status updated to {order.get_status_display()}')

            return JsonResponse({
                'success': True,
                'message': f'Order status updated to {order.get_status_display()}',
                'status': new_status
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            })

    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@login_required
def process_payment(request, pk):
    """Process payment for an order (cashier confirms cash payment)"""
    if request.method == 'POST':
        try:
            from sales_inventory_system.products.inventory_service import BOMService, IngredientDeductionError

            order = get_object_or_404(Order, pk=pk)

            # Check if payment already exists
            try:
                payment = order.payment
            except Payment.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'Payment record not found for this order'
                })

            # Only process if payment is pending
            if payment.status != 'PENDING':
                return JsonResponse({
                    'success': False,
                    'message': f'Payment is already {payment.get_status_display()}'
                })

            with transaction.atomic():
                # Update payment status
                payment.status = 'COMPLETED'
                payment.processed_by = request.user
                payment.save()

                # Update order status
                order.status = 'IN_PROGRESS'
                order.processed_by = request.user
                order.save()

                # Deduct ingredients from order (strict validation via BOMService)
                try:
                    deduction_result = BOMService.deduct_ingredients_for_order(order, request.user)
                except IngredientDeductionError as e:
                    raise ValueError(f'Ingredient deduction failed: {str(e)}')

',
                    data_snapshot={
                        'order_number': order.order_number,
                        'amount': str(payment.amount),
                        'method': payment.method,
                        'ingredients_deducted': len(deduction_result['deductions'])
                    }
                )

                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'message': f'Payment processed for order {order.order_number}'
                    })
                else:
                    messages.success(request, f'Payment processed for order {order.order_number}')
                    return redirect('orders:list')

        except ValueError as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error processing payment: {str(e)}'
            })

    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@login_required
def quick_payment(request, pk):
    """Quick payment processing for orders from order list (AJAX)"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method'})

    try:
        import json
        from sales_inventory_system.products.inventory_service import BOMService, IngredientDeductionError

        order = get_object_or_404(Order, pk=pk)
        data = json.loads(request.body)
        cash_amount = float(data.get('cash_amount', 0))

        if cash_amount <= 0:
            return JsonResponse({'success': False, 'message': 'Invalid cash amount'})

        if cash_amount < float(order.total_amount):
            return JsonResponse({
                'success': False,
                'message': f'Insufficient cash. Need ₱{float(order.total_amount):.2f}'
            })

        # Check if payment already exists
        try:
            payment = order.payment
        except Payment.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Payment record not found for this order'
            })

        # Only process if payment is pending
        if payment.status != 'PENDING':
            return JsonResponse({
                'success': False,
                'message': f'Payment is already {payment.get_status_display()}'
            })

        with transaction.atomic():
            # Update payment status
            payment.status = 'COMPLETED'
            payment.processed_by = request.user
            payment.save()

            # Update order status
            order.status = 'IN_PROGRESS'
            order.processed_by = request.user
            order.save()

            # Deduct ingredients from order
            try:
                deduction_result = BOMService.deduct_ingredients_for_order(order, request.user)
            except IngredientDeductionError as e:
                raise ValueError(f'Ingredient deduction failed: {str(e)}')

            change = cash_amount - float(order.total_amount)
',
                data_snapshot={
                    'order_number': order.order_number,
                    'amount': str(payment.amount),
                    'method': payment.method,
                    'cash_received': str(cash_amount),
                    'change': f'{change:.2f}',
                    'ingredients_deducted': len(deduction_result['deductions'])
                }
            )

            return JsonResponse({
                'success': True,
                'message': f'Payment processed for order {order.order_number}',
                'order_number': order.order_number,
                'change': f'{change:.2f}'
            })

    except ValueError as e:
        return JsonResponse({'success': False, 'message': str(e)})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error processing payment: {str(e)}'})

# ==================== NEW POS VIEWS (Optimized with Session-based Cart) ====================

@login_required
def pos_home(request):
    """POS home - Browse products with images and add to cart (Optimized with Kiosk-like UI)"""
    # Simple fast query without availability checking (lazy evaluation)
    # Availability is checked on-demand in pos_add_to_cart via AJAX
    products = Product.objects.filter(
        is_archived=False
    ).order_by('category', 'name')

    # Initialize cart in session if not exists
    if 'pos_cart' not in request.session:
        request.session['pos_cart'] = {}

    # Mark all as available initially (will be validated in add_to_cart)
    for product in products:
        product.is_available_for_order = True

    context = {
        'products': products,
        'cart': request.session.get('pos_cart', {}),
        'cart_count': len(request.session.get('pos_cart', {})),
    }
    return render(request, 'orders/pos_home.html', context)

@login_required
def pos_add_to_cart(request, product_id):
    """AJAX endpoint to add product to cart"""
    from sales_inventory_system.products.inventory_service import BOMService

    product = get_object_or_404(Product, pk=product_id, is_archived=False)
    quantity = int(request.POST.get('quantity', 1))

    # Check availability for this specific product
    availability = BOMService.check_ingredient_availability(product_id, quantity)

    if not availability['available']:
        return JsonResponse({
            'success': False,
            'message': f'Not enough ingredients available. {availability["shortages"][0]["ingredient"]} is short.',
            'shortages': availability['shortages']
        })

    # Initialize cart if not exists
    if 'pos_cart' not in request.session:
        request.session['pos_cart'] = {}

    cart = request.session['pos_cart']
    product_key = str(product_id)

    # Add or update quantity
    if product_key in cart:
        cart[product_key]['quantity'] += quantity
    else:
        cart[product_key] = {
            'product_id': product_id,
            'name': product.name,
            'price': float(product.price),
            'quantity': quantity,
            'subtotal': float(product.price) * quantity,
        }

    request.session.modified = True

    # Calculate cart total
    total = sum(item['subtotal'] for item in cart.values())

    return JsonResponse({
        'success': True,
        'message': f'{product.name} added to cart!',
        'cart_count': len(cart),
        'total': float(total),
    })

@login_required
def pos_remove_from_cart(request, product_id):
    """AJAX endpoint to remove product from cart"""
    if 'pos_cart' not in request.session:
        return JsonResponse({'success': False, 'message': 'Cart is empty'})

    cart = request.session['pos_cart']
    product_key = str(product_id)

    if product_key in cart:
        del cart[product_key]
        request.session.modified = True

        total = sum(item['subtotal'] for item in cart.values()) if cart else 0

        return JsonResponse({
            'success': True,
            'message': 'Item removed from cart',
            'cart_count': len(cart),
            'total': float(total),
        })

    return JsonResponse({'success': False, 'message': 'Item not found in cart'})

@login_required
def pos_update_cart_quantity(request, product_id):
    """AJAX endpoint to update product quantity in cart"""
    from sales_inventory_system.products.inventory_service import BOMService

    if 'pos_cart' not in request.session:
        return JsonResponse({'success': False, 'message': 'Cart is empty'})

    product = get_object_or_404(Product, pk=product_id, is_archived=False)
    new_quantity = int(request.POST.get('quantity', 1))

    # Validate quantity
    if new_quantity < 1:
        return JsonResponse({'success': False, 'message': 'Quantity must be at least 1'})

    # Check availability for this new quantity
    availability = BOMService.check_ingredient_availability(product_id, new_quantity)

    if not availability['available']:
        return JsonResponse({
            'success': False,
            'message': f'Not enough ingredients. {availability["shortages"][0]["ingredient"]} is short.',
        })

    cart = request.session['pos_cart']
    product_key = str(product_id)

    if product_key in cart:
        cart[product_key]['quantity'] = new_quantity
        cart[product_key]['subtotal'] = float(product.price) * new_quantity
        request.session.modified = True

        total = sum(item['subtotal'] for item in cart.values())

        return JsonResponse({
            'success': True,
            'total': float(total),
            'subtotal': float(product.price) * new_quantity,
        })

    return JsonResponse({'success': False, 'message': 'Item not found in cart'})

@login_required
def pos_get_cart(request):
    """AJAX endpoint to get cart as JSON"""
    cart = request.session.get('pos_cart', {})
    # Return simplified cart data (product_id: quantity)
    simplified_cart = {product_id: item['quantity'] for product_id, item in cart.items()}
    return JsonResponse(simplified_cart)

@login_required
def pos_get_cart_details(request):
    """AJAX endpoint to get detailed product information for cart items"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method'})

    try:
        import json
        data = json.loads(request.body)
        product_ids = data.get('product_ids', [])

        if not product_ids:
            return JsonResponse({'success': True, 'products': {}})

        # Fetch products
        products = Product.objects.filter(id__in=product_ids)
        product_details = {}

        for product in products:
            product_details[str(product.id)] = {
                'id': product.id,
                'name': product.name,
                'price': float(product.price),
                'image': product.image.url if product.image else None,
            }

        return JsonResponse({'success': True, 'products': product_details})

    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@login_required
def pos_cart_view(request):
    """Display POS cart"""
    cart = request.session.get('pos_cart', {})

    # Get all products at once for efficiency
    if cart:
        product_ids = [int(k) for k in cart.keys()]
        products = {p.id: p for p in Product.objects.filter(id__in=product_ids)}
    else:
        products = {}

    total = sum(item['subtotal'] for item in cart.values())

    context = {
        'cart': cart,
        'products': products,
        'total': total,
        'cart_count': len(cart),
    }
    return render(request, 'orders/pos_cart.html', context)

@login_required
def pos_checkout(request):
    """Checkout form with customer details and payment"""
    cart = request.session.get('pos_cart', {})

    if not cart:
        messages.error(request, 'Your cart is empty!')
        return redirect('orders:pos_home')

    if request.method == 'POST':
        try:
            from sales_inventory_system.products.inventory_service import BOMService, IngredientDeductionError

            customer_name = request.POST.get('customer_name', 'Walk-in Customer').strip()
            table_number = request.POST.get('table_number', '').strip()
            notes = request.POST.get('notes', '').strip()
            payment_method = request.POST.get('payment_method', 'CASH')

            # Build cart items
            product_ids = [int(k) for k in cart.keys()]
            products_by_id = {p.id: p for p in Product.objects.filter(id__in=product_ids)}

            cart_items = []
            for product_key, item in cart.items():
                cart_items.append({
                    'product_id': int(product_key),
                    'quantity': item['quantity']
                })

            # Final availability check before creating order
            availability_check = BOMService.check_order_availability(cart_items)
            if not availability_check['available']:
                shortage_msg = 'Cannot complete order - insufficient ingredients:\n'
                for shortage in availability_check['shortages']:
                    shortage_msg += f"• {shortage['product']}: {shortage['ingredient']}\n"
                messages.error(request, shortage_msg)
                return redirect('orders:pos_checkout')

            with transaction.atomic():
                # Calculate total amount FIRST
                total_amount = 0
                order_items = []
                for item_data in cart_items:
                    product = products_by_id[item_data['product_id']]
                    quantity = item_data['quantity']
                    total_amount += product.price * quantity

                # Create order with calculated total
                order = Order.objects.create(
                    customer_name=customer_name,
                    table_number=table_number,
                    notes=notes,
                    status='IN_PROGRESS',
                    total_amount=total_amount,
                    processed_by=request.user
                )

                # Create order items
                for item_data in cart_items:
                    product = products_by_id[item_data['product_id']]
                    quantity = item_data['quantity']

                    order_items.append(OrderItem(
                        order=order,
                        product=product,
                        product_name=product.name,
                        product_price=product.price,
                        quantity=quantity,
                        subtotal=product.price * quantity
                    ))

                if order_items:
                    OrderItem.objects.bulk_create(order_items, batch_size=100)

                # Deduct ingredients
                try:
                    deduction_result = BOMService.deduct_ingredients_for_order(order, request.user)
                except IngredientDeductionError as e:
                    raise ValueError(f'Failed to deduct ingredients: {str(e)}')

                # Create payment record with correct amount
                Payment.objects.create(
                    order=order,
                    method=payment_method,
                    amount=total_amount,
                    status='COMPLETED',
                    processed_by=request.user
                )

,
                        'payment_method': payment_method
                    }
                )

                # Clear cart
                request.session['pos_cart'] = {}
                request.session.modified = True

                messages.success(request, f'Order {order.order_number} created successfully!')
                return redirect('orders:pos_confirmation', order_number=order.order_number)

        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f'Error creating order: {str(e)}')

    # Calculate cart total
    total = sum(item['subtotal'] for item in cart.values())

    context = {
        'cart': cart,
        'total': total,
        'cart_count': len(cart),
    }
    return render(request, 'orders/pos_checkout.html', context)

@login_required
def pos_confirmation(request, order_number):
    """Order confirmation page"""
    order = get_object_or_404(Order, order_number=order_number)

    context = {
        'order': order,
        'order_items': order.items.all(),
    }
    return render(request, 'orders/pos_confirmation.html', context)

# ==================== OLD POS VIEW (Deprecated - keeping for reference) ====================

@login_required
def pos_create_order(request):
    """POS interface for cashiers to create orders directly"""
    products = Product.objects.filter(is_archived=False).order_by('category', 'name')

    if request.method == 'POST':
        try:
            from sales_inventory_system.products.inventory_service import BOMService

            customer_name = request.POST.get('customer_name', 'Walk-in Customer')
            table_number = request.POST.get('table_number', '')
            notes = request.POST.get('notes', '')
            payment_method = request.POST.get('payment_method', 'CASH')

            # Get cart items from POST data
            cart_items = []
            for key in request.POST:
                if key.startswith('quantity_'):
                    product_id = int(key.replace('quantity_', ''))
                    quantity = int(request.POST.get(key, 0))
                    if quantity > 0:
                        cart_items.append({'product_id': product_id, 'quantity': quantity})

            if not cart_items:
                messages.error(request, 'Please add at least one item to the order.')
                return redirect('orders:pos_create_order')

            # VALIDATE INGREDIENTS AVAILABILITY BEFORE CREATING ORDER
            availability_check = BOMService.check_order_availability(cart_items)
            if not availability_check['available']:
                shortage_msg = 'Cannot create order due to ingredient shortages:\n'
                for shortage in availability_check['shortages']:
                    shortage_msg += (
                        f"• {shortage['product']} - {shortage['ingredient']}: "
                        f"Need {shortage['needed']} {shortage['unit']}, "
                        f"Have {shortage['available']} {shortage['unit']}\n"
                    )
                messages.error(request, shortage_msg)
                return redirect('orders:pos_create_order')

            with transaction.atomic():
                # Create order
                order = Order.objects.create(
                    customer_name=customer_name,
                    table_number=table_number,
                    notes=notes,
                    status='IN_PROGRESS',  # POS orders go directly to IN_PROGRESS
                    processed_by=request.user
                )

                total_amount = 0

                # Fetch all products at once (optimization: single query instead of N queries)
                product_ids = [item['product_id'] for item in cart_items]
                products_by_id = {
                    p.id: p for p in Product.objects.filter(id__in=product_ids)
                }

                order_items = []

                # Create order items and calculate total
                for item_data in cart_items:
                    product = products_by_id[item_data['product_id']]
                    quantity = item_data['quantity']

                    # Prepare order item creation
                    order_items.append(OrderItem(
                        order=order,
                        product=product,
                        quantity=quantity
                    ))

                    total_amount += product.price * quantity

                # Bulk create order items
                if order_items:
                    OrderItem.objects.bulk_create(order_items, batch_size=100)

                # Deduct ingredients for the order (strict validation via BOMService)
                from sales_inventory_system.products.inventory_service import BOMService, IngredientDeductionError

                try:
                    deduction_result = BOMService.deduct_ingredients_for_order(order, request.user)
                except IngredientDeductionError as e:
                    raise ValueError(f'Failed to deduct ingredients: {str(e)}')

                # Update order total
                order.calculate_total()

                # Create payment record (already successful)
                Payment.objects.create(
                    order=order,
                    method=payment_method,
                    amount=order.total_amount,
                    status='COMPLETED',
                    processed_by=request.user
                )

                messages.success(request, f'Order {order.order_number} created successfully!')
                return redirect('orders:list')

        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f'Error creating order: {str(e)}')

    # Mark all products as available - validation happens in add_to_cart via AJAX
    # This avoids N+1 queries on page load (50-100+ queries)
    for product in products:
        product.is_available_for_order = True

    # Group products by category for display
    from itertools import groupby
    products_by_category = {}
    for category, items in groupby(products, key=lambda p: p.category or 'Other'):
        products_by_category[category] = list(items)

    context = {
        'products': products,
        'products_by_category': products_by_category,
    }
    return render(request, 'orders/pos_create.html', context)

@login_required
def order_archive(request, pk):
    """Archive an order (admin only)"""
    from django.contrib.auth.decorators import user_passes_test

    def is_admin(user):
        return user.is_authenticated and user.is_admin

    # Check permissions
    if not request.user.is_authenticated or not request.user.is_admin:
        messages.error(request, 'You do not have permission to archive orders!')
        return redirect('orders:list')

    order = get_object_or_404(Order, pk=pk)
    order.is_archived = True
    order.save()

}
    )

    messages.success(request, f'Order "{order.order_number}" archived successfully!')
    return redirect('orders:list')

@login_required
def order_unarchive(request, pk):
    """Restore an archived order (admin only)"""
    def is_admin(user):
        return user.is_authenticated and user.is_admin

    # Check permissions
    if not request.user.is_authenticated or not request.user.is_admin:
        messages.error(request, 'You do not have permission to unarchive orders!')
        return redirect('orders:list')

    order = get_object_or_404(Order, pk=pk, is_archived=True)
    order.is_archived = False
    order.save()

}
    )

    messages.success(request, f'Order "{order.order_number}" restored successfully!')
    return redirect('products:archived_list')
