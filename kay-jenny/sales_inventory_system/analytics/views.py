from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.db.models import Sum, Count, F, Q, Case, When, Value, DecimalField, Prefetch
from django.db.models.functions import Cast, Coalesce, TruncDate
from django.utils import timezone
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from datetime import timedelta, datetime
from decimal import Decimal
from sales_inventory_system.orders.models import Order, Payment, OrderItem
from sales_inventory_system.products.models import Product
from .forecasting import forecast_sales


def is_admin(user):
    return user.is_authenticated and user.is_admin


@login_required
@user_passes_test(is_admin)
@cache_page(300)  # Cache for 5 minutes
def dashboard(request):
    """Display analytics dashboard with comprehensive sales data"""

    # Date ranges
    today = timezone.now().date()
    today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)

    # Optimize: Combine all revenue queries into single query with Case/When
    revenue_stats = Payment.objects.filter(
        status='SUCCESS'
    ).aggregate(
        # Total revenue (all time)
        total_revenue=Coalesce(Sum('amount'), Decimal('0.00')),
        # Today's revenue
        today_revenue=Coalesce(
            Sum(
                Case(
                    When(created_at__gte=today_start, then='amount'),
                    default=Value(0),
                    output_field=DecimalField()
                )
            ),
            Decimal('0.00')
        ),
        # Week revenue
        week_revenue=Coalesce(
            Sum(
                Case(
                    When(created_at__date__gte=week_ago, then='amount'),
                    default=Value(0),
                    output_field=DecimalField()
                )
            ),
            Decimal('0.00')
        ),
        # Month revenue
        month_revenue=Coalesce(
            Sum(
                Case(
                    When(created_at__date__gte=month_ago, then='amount'),
                    default=Value(0),
                    output_field=DecimalField()
                )
            ),
            Decimal('0.00')
        ),
    )

    total_revenue = revenue_stats['total_revenue']
    today_revenue = revenue_stats['today_revenue']
    week_revenue = revenue_stats['week_revenue']
    month_revenue = revenue_stats['month_revenue']

    # Optimize: Combine all order count queries into single query with Case/When
    order_stats = Order.objects.aggregate(
        # Total orders
        total_orders=Count('id'),
        # Today's orders
        today_orders=Count(
            Case(
                When(created_at__gte=today_start, then=1)
            )
        ),
        # Week orders
        week_orders=Count(
            Case(
                When(created_at__date__gte=week_ago, then=1)
            )
        ),
        # Status counts
        pending_orders=Count(
            Case(
                When(status='PENDING', then=1)
            )
        ),
        in_progress_orders=Count(
            Case(
                When(status='IN_PROGRESS', then=1)
            )
        ),
        completed_orders=Count(
            Case(
                When(status='FINISHED', then=1)
            )
        ),
    )

    total_orders = order_stats['total_orders']
    today_orders = order_stats['today_orders']
    week_orders = order_stats['week_orders']
    pending_orders = order_stats['pending_orders']
    in_progress_orders = order_stats['in_progress_orders']
    completed_orders = order_stats['completed_orders']

    # Average order value
    avg_order_value = Decimal('0.00')
    if total_orders > 0:
        avg_order_value = total_revenue / total_orders

    # Average daily revenue (week)
    avg_daily_revenue = Decimal('0.00')
    if week_revenue > 0:
        avg_daily_revenue = week_revenue / 7

    # Get max quantity for progress bar calculation (before limiting to 10)
    max_product_result = OrderItem.objects.values(
        'product__name'
    ).annotate(
        total_quantity=Sum('quantity')
    ).order_by('-total_quantity').first()

    max_product_quantity = int(max_product_result['total_quantity']) if max_product_result and max_product_result['total_quantity'] else 1

    # Top selling products
    top_products_qs = OrderItem.objects.values(
        'product__name',
        'product__price'
    ).annotate(
        total_quantity=Sum('quantity'),
        total_revenue=Sum('subtotal')
    ).order_by('-total_quantity')[:10]

    # Calculate width percentage for each product
    top_products = []
    for product in top_products_qs:
        width_percent = (int(product['total_quantity'] or 0) / max_product_quantity * 100) if max_product_quantity > 0 else 0
        product['width_percent'] = int(width_percent)
        top_products.append(product)

    # Low stock products - optimized with prefetch_related to avoid N+1 queries
    # Prefetch recipe and ingredients data upfront to avoid multiple database queries
    low_stock_products_qs = Product.objects.filter(
        is_archived=False
    ).prefetch_related('recipe__ingredients__ingredient')

    low_stock_products = []
    for product in low_stock_products_qs:
        # Use calculated_stock which now uses prefetched data instead of making new queries
        if product.calculated_stock < product.threshold:
            low_stock_products.append(product)

    # Sort by calculated stock and limit to 10
    low_stock_products.sort(key=lambda p: p.calculated_stock)
    low_stock_products = low_stock_products[:10]

    # Recent orders - optimized with prefetch_related for order items
    recent_orders = Order.objects.select_related('payment').prefetch_related(
        'items__product'
    ).order_by('-created_at')[:10]

    context = {
        # Revenue metrics
        'total_revenue': total_revenue,
        'today_revenue': today_revenue,
        'week_revenue': week_revenue,
        'month_revenue': month_revenue,
        'avg_daily_revenue': avg_daily_revenue,

        # Order metrics
        'total_orders': total_orders,
        'today_orders': today_orders,
        'week_orders': week_orders,
        'pending_orders': pending_orders,
        'in_progress_orders': in_progress_orders,
        'completed_orders': completed_orders,
        'avg_order_value': avg_order_value,

        # Product metrics
        'top_products': top_products,
        'max_product_quantity': max_product_quantity,
        'low_stock_products': low_stock_products,

        # Recent activity
        'recent_orders': recent_orders,
    }
    return render(request, 'analytics/dashboard.html', context)


@login_required
@user_passes_test(is_admin)
@cache_page(60)  # Cache for 1 minute
def sales_data_api(request):
    """API endpoint for sales data (for charts) - Optimized to use single query"""
    from django.db.models.functions import TruncDate, TruncHour

    period = request.GET.get('period', 'week')  # day, week, month
    today = timezone.now().date()

    data = []

    if period == 'day':
        # Last 24 hours by hour - optimized with single database query
        hourly_data = Payment.objects.filter(
            status='SUCCESS',
            created_at__gte=timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        ).annotate(
            hour=TruncHour('created_at')
        ).values('hour').annotate(
            total=Sum('amount')
        ).order_by('hour')

        # Create hour lookup for easy access
        hour_dict = {
            item['hour'].hour: float(item['total'] or 0)
            for item in hourly_data
        }

        for hour in range(24):
            revenue = hour_dict.get(hour, 0)
            data.append({
                'label': f'{hour:02d}:00',
                'value': revenue
            })

    elif period == 'week':
        # Last 7 days - optimized with single database query
        week_start = today - timedelta(days=6)
        daily_data = Payment.objects.filter(
            status='SUCCESS',
            created_at__date__gte=week_start
        ).annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            total=Sum('amount')
        ).order_by('date')

        # Create date lookup
        date_dict = {
            item['date']: float(item['total'] or 0)
            for item in daily_data
        }

        for i in range(7):
            day = week_start + timedelta(days=i)
            revenue = date_dict.get(day, 0)
            data.append({
                'label': day.strftime('%a'),
                'value': revenue
            })

    else:  # month
        # Last 30 days - optimized with single database query
        month_start = today - timedelta(days=29)
        daily_data = Payment.objects.filter(
            status='SUCCESS',
            created_at__date__gte=month_start
        ).annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            total=Sum('amount')
        ).order_by('date')

        # Create date lookup
        date_dict = {
            item['date']: float(item['total'] or 0)
            for item in daily_data
        }

        for i in range(30):
            day = month_start + timedelta(days=i)
            revenue = date_dict.get(day, 0)
            data.append({
                'label': day.strftime('%m/%d'),
                'value': revenue
            })

    return JsonResponse({
        'success': True,
        'data': data
    })


@login_required
@user_passes_test(is_admin)
def sales_forecast(request):
    """Display sales forecasting using Holt-Winters Exponential Smoothing"""

    # Get parameters from request (with defaults)
    days_back = int(request.GET.get('days_back', 30))
    days_ahead = int(request.GET.get('days_ahead', 7))

    # Validate parameters
    days_back = max(7, min(days_back, 90))  # Between 7 and 90 days
    days_ahead = max(1, min(days_ahead, 30))  # Between 1 and 30 days

    # Check cache first (expensive operation)
    cache_key = f'forecast_{days_back}_{days_ahead}'
    forecast_result = cache.get(cache_key)

    if forecast_result is None:
        # Generate forecast only if not cached
        forecast_result = forecast_sales(days_back=days_back, days_ahead=days_ahead)
        # Cache for 30 minutes
        cache.set(cache_key, forecast_result, 1800)

    context = {
        'forecast_result': forecast_result,
        'days_back': days_back,
        'days_ahead': days_ahead,
    }

    return render(request, 'analytics/forecast.html', context)
