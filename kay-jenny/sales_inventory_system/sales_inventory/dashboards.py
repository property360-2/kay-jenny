"""
Dashboard views for different user roles
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import F, Sum, Count, Q
from django.utils import timezone
from sales_inventory_system.products.models import Product
from sales_inventory_system.orders.models import Order, Payment
from decimal import Decimal

def is_admin(user):
    return user.is_authenticated and user.is_admin

def is_cashier(user):
    return user.is_authenticated and user.is_cashier

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    """Admin dashboard with overview statistics"""

    # Get statistics
    total_products = Product.objects.filter(is_archived=False).count()

    # Get low stock products using calculated_stock (accounts for BOM products)
    all_active_products = Product.objects.filter(is_archived=False).select_related(
        'recipe'
    ).prefetch_related(
        'recipe__ingredients__ingredient'
    )
    low_stock_products_list = [p for p in all_active_products if p.calculated_stock < p.threshold]
    low_stock_count = len(low_stock_products_list)
    low_stock_products = low_stock_products_list[:5]

    # Order statistics
    pending_orders = Order.objects.filter(status='PENDING').count()
    in_progress_orders = Order.objects.filter(status='IN_PROGRESS').count()
    today_orders = Order.objects.filter(
        created_at__date=timezone.now().date()
    ).count()

    # Revenue statistics
    total_revenue = Payment.objects.filter(
        status='SUCCESS'
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    today_revenue = Payment.objects.filter(
        status='SUCCESS',
        created_at__date=timezone.now().date()
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    # Recent orders
    recent_orders = Order.objects.all()[:5]

    context = {
        'total_products': total_products,
        'low_stock_count': low_stock_count,
        'low_stock_products': low_stock_products[:5],
        'pending_orders': pending_orders,
        'in_progress_orders': in_progress_orders,
        'today_orders': today_orders,
        'total_revenue': total_revenue,
        'today_revenue': today_revenue,
        'recent_orders': recent_orders,
    }

    return render(request, 'dashboards/admin.html', context)


@login_required
@user_passes_test(is_cashier)
def cashier_pos(request):
    """Cashier POS interface"""

    # Get orders by status with prefetch for efficiency
    pending_orders = Order.objects.filter(status='PENDING').select_related('payment').prefetch_related('items__product').order_by('-created_at')
    in_progress_orders = Order.objects.filter(status='IN_PROGRESS').prefetch_related('items__product').order_by('-created_at')
    finished_orders = Order.objects.filter(status='FINISHED').prefetch_related('items__product').order_by('-created_at')[:10]  # Last 10 finished

    # Today's statistics
    today = timezone.now().date()
    today_orders_count = Order.objects.filter(created_at__date=today).count()
    today_completed = Order.objects.filter(status='FINISHED', created_at__date=today).count()
    today_revenue = Payment.objects.filter(status='SUCCESS', created_at__date=today).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    context = {
        'pending_orders': pending_orders,
        'in_progress_orders': in_progress_orders,
        'finished_orders': finished_orders,
        'today_orders_count': today_orders_count,
        'today_completed': today_completed,
        'today_revenue': today_revenue,
        'pending_count': pending_orders.count(),
    }

    return render(request, 'dashboards/pos.html', context)
