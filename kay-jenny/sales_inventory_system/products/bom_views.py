"""
Views for Bill of Materials reports and management
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.db.models import Q, Sum, F, Avg, Max, Min, Count, Case, When, DecimalField
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from .models import (
    Ingredient, RecipeItem, StockTransaction, WasteLog,
    PhysicalCount, VarianceRecord, Product
)
from .inventory_service import BOMService
import json
import csv
from io import StringIO


@login_required
def bom_dashboard(request):
    """
    Main BOM dashboard showing inventory status and key metrics.
    """
    # Low stock ingredients
    low_stock = BOMService.get_low_stock_ingredients()[:5]

    # Low stock products (calculated from ingredients) - optimized with prefetch_related
    all_active_products = Product.objects.filter(
        is_archived=False
    ).prefetch_related('recipe__ingredients__ingredient')
    low_stock_products = [p for p in all_active_products if p.calculated_stock < p.threshold][:5]

    # Stock transactions this week
    week_ago = timezone.now() - timedelta(days=7)
    recent_transactions = StockTransaction.objects.filter(
        created_at__gte=week_ago
    ).select_related('ingredient').order_by('-created_at')[:10]

    # Variance overview
    today = timezone.now()
    month_start = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    variance_records = VarianceRecord.objects.filter(
        period_end__gte=month_start
    ).select_related('ingredient').order_by('within_tolerance')[:5]

    # Calculate total waste cost this month (actual from WasteLog)
    month_waste_logs = WasteLog.objects.filter(
        waste_date__gte=month_start
    )
    month_waste_cost = sum(float(waste.cost_impact) for waste in month_waste_logs) if month_waste_logs.exists() else 0

    context = {
        'low_stock_count': Ingredient.objects.filter(
            Q(current_stock__lt=F('min_stock')) & Q(is_active=True)
        ).count(),
        'low_stock_ingredients': low_stock,
        'low_stock_products': low_stock_products,
        'recent_transactions': recent_transactions,
        'variance_issues': variance_records,
        'total_ingredients': Ingredient.objects.filter(is_active=True).count(),
        'month_waste_cost': month_waste_cost,
    }

    return render(request, 'products/bom_dashboard.html', context)


@login_required
def ingredient_usage_report(request):
    """
    Comprehensive ingredient usage report for all active ingredients.
    Shows usage analytics directly on the page.
    Optimized to use single database query for all transactions.
    """
    days = int(request.GET.get('days', 30))
    download = request.GET.get('download', '').lower()

    end_date = timezone.now()
    start_date = end_date - timedelta(days=days)

    # Get all transactions in a single database query - optimized for performance
    all_transactions = StockTransaction.objects.filter(
        created_at__gte=start_date,
        created_at__lte=end_date,
        ingredient__is_active=True
    ).select_related('ingredient').order_by('ingredient', '-created_at')

    # Group transactions by ingredient in Python
    ingredients_transactions = {}
    for trans in all_transactions:
        ing_id = trans.ingredient.id
        if ing_id not in ingredients_transactions:
            ingredients_transactions[ing_id] = {
                'ingredient': trans.ingredient,
                'transactions': [],
                'transaction_stats': {},
                'total_quantity': 0,
            }
        ingredients_transactions[ing_id]['transactions'].append(trans)

    # Calculate statistics for each ingredient
    usage_summary = []
    total_used = 0
    total_cost = 0

    for ing_id, data in ingredients_transactions.items():
        ingredient = data['ingredient']
        transactions = data['transactions']

        # Calculate totals by transaction type and total used
        transaction_stats = {}
        total_quantity = 0

        for trans in transactions:
            trans_type = trans.get_transaction_type_display()
            transaction_stats[trans_type] = transaction_stats.get(trans_type, 0) + float(trans.quantity)
            if trans.transaction_type in ['DEDUCTION', 'PREP']:
                total_quantity += float(trans.quantity)

        # Calculate cost
        # Note: cost calculation not applicable with simplified ingredient system
        ingredient_cost = 0

        usage_summary.append({
            'ingredient': ingredient,
            'total_quantity': total_quantity,
            'cost': ingredient_cost,
            'transaction_stats': transaction_stats,
            'transactions': transactions[:10],  # Latest 10 transactions
            'transactions_count': len(transactions),
        })

        total_used += total_quantity
        total_cost += ingredient_cost

    # Calculate average cost per unit used
    avg_cost = total_cost / total_used if total_used > 0 else 0

    # Sort data for insights (do this in view, not template)
    sorted_by_cost = sorted(usage_summary, key=lambda x: x['cost'], reverse=True)
    sorted_by_quantity = sorted(usage_summary, key=lambda x: x['total_quantity'], reverse=True)
    top_cost_items = sorted_by_cost[:5]
    top_used_items = sorted_by_quantity[:5]

    # Handle AJAX requests for async filtering
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Prepare data for JSON response
        usage_data = []
        total_cost_value = float(total_cost) if total_cost > 0 else 0

        for item in sorted_by_cost:
            percentage = (item['cost'] / total_cost_value * 100) if total_cost_value > 0 else 0
            usage_data.append({
                'ingredient_id': item['ingredient'].id,
                'ingredient_name': item['ingredient'].name,
                'ingredient_unit': item['ingredient'].unit,
                'total_quantity': float(item['total_quantity']),
                'cost': float(item['cost']),
                'transactions_count': item['transactions_count'],
                'percentage_of_total': percentage
            })

        # Prepare top cost items
        top_cost_data = []
        for item in top_cost_items:
            percentage = (item['cost'] / total_cost_value * 100) if total_cost_value > 0 else 0
            top_cost_data.append({
                'ingredient_id': item['ingredient'].id,
                'ingredient_name': item['ingredient'].name,
                'total_quantity': float(item['total_quantity']),
                'cost': float(item['cost']),
                'percentage_of_total': percentage
            })

        # Prepare top used items
        top_used_data = []
        for item in top_used_items:
            top_used_data.append({
                'ingredient_id': item['ingredient'].id,
                'ingredient_name': item['ingredient'].name,
                'total_quantity': float(item['total_quantity']),
                'unit': item['ingredient'].unit
            })

        return JsonResponse({
            'success': True,
            'days': days,
            'period_start': start_date.strftime('%Y-%m-%d'),
            'period_end': end_date.strftime('%Y-%m-%d'),
            'summary_stats': {
                'total_ingredients': len(usage_summary),
                'total_used': float(total_used),
                'total_cost': float(total_cost),
                'avg_cost': float(avg_cost)
            },
            'usage_summary': usage_data,
            'top_cost_items': top_cost_data,
            'top_used_items': top_used_data
        })

    # Handle downloads
    if download == 'csv':
        return generate_usage_csv_download(usage_summary, days)
    elif download == 'detailed':
        return generate_usage_detailed_csv(usage_summary, days)

    context = {
        'usage_summary': sorted_by_cost,  # Default sort by cost descending
        'top_cost_items': top_cost_items,
        'top_used_items': top_used_items,
        'days': days,
        'total_used': total_used,
        'total_cost': total_cost,
        'avg_cost': avg_cost,
        'period_start': start_date,
        'period_end': end_date,
        'total_ingredients': len(usage_summary),
    }

    return render(request, 'products/ingredient_usage_report_enhanced.html', context)


def generate_usage_csv_download(usage_summary, days):
    """Generate CSV report for ingredient usage"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="ingredient_usage_{timezone.now().strftime("%Y%m%d")}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Ingredient', 'Unit', 'Total Used', 'Transactions'])

    for item in usage_summary:
        writer.writerow([
            item['ingredient'].name,
            item['ingredient'].unit,
            f"{item['total_quantity']:.3f}",
            item['transactions_count']
        ])

    return response


def generate_usage_detailed_csv(usage_summary, days):
    """Generate detailed CSV report with all transactions"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="ingredient_usage_detailed_{timezone.now().strftime("%Y%m%d")}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Ingredient', 'Date', 'Type', 'Quantity', 'Notes'])

    for item in usage_summary:
        for trans in item['transactions']:
            writer.writerow([
                item['ingredient'].name,
                trans.created_at.strftime("%Y-%m-%d %H:%M"),
                trans.get_transaction_type_display(),
                f"{trans.quantity:.3f}",
                trans.notes or ''
            ])

    return response


@login_required
def variance_analysis_report(request):
    """
    Comprehensive variance analysis report for all active ingredients.
    Shows analytics directly on the page with download option.
    Optimized to use database aggregation for statistics.
    """
    days = int(request.GET.get('days', 30))
    download = request.GET.get('download', '').lower()

    end_date = timezone.now()
    start_date = end_date - timedelta(days=days)

    # Get all variance records for the date range with related ingredient data
    all_variance_records = VarianceRecord.objects.filter(
        period_end__gte=start_date,
        ingredient__is_active=True
    ).select_related('ingredient').order_by('-period_end')

    # If no records exist, return empty state
    if not all_variance_records.exists():
        context = {
            'variance_summary': [],
            'best_performing': [],
            'outside_tolerance': [],
            'days': days,
            'total_records': 0,
            'avg_of_avgs': 0,
            'overall_within_tolerance': 0,
            'period_start': start_date,
            'period_end': end_date,
        }
        if download:
            return render(request, 'products/variance_analysis_report.html', context)
        return render(request, 'products/variance_analysis_report.html', context)

    # Aggregate statistics by ingredient using database queries
    variance_stats = VarianceRecord.objects.filter(
        period_end__gte=start_date,
        ingredient__is_active=True
    ).values('ingredient').annotate(
        records_count=Count('id'),
        avg_variance=Avg('variance_percentage'),
        max_variance=Max('variance_percentage'),
        min_variance=Min('variance_percentage'),
        within_tolerance_count=Count(
            Case(When(within_tolerance=True, then=1))
        ),
        ingredient_name=F('ingredient__name'),
        variance_allowance=F('ingredient__variance_allowance')
    ).order_by('-avg_variance')

    # Get latest 5 variance records per ingredient
    variance_summary = []
    total_records = 0
    within_tolerance_count = 0
    ingredients_data = {}

    # First pass: get aggregated stats from database query
    for stat in variance_stats:
        ing_id = stat['ingredient']
        if ing_id not in ingredients_data:
            ingredients_data[ing_id] = {
                'ingredient_id': ing_id,
                'records_count': stat['records_count'],
                'avg_variance': float(stat['avg_variance'] or 0),
                'max_variance': float(stat['max_variance'] or 0),
                'min_variance': float(stat['min_variance'] or 0),
                'within_tolerance_count': stat['within_tolerance_count'],
                'variance_allowance': float(stat['variance_allowance']),
            }

    # Second pass: get latest 5 records per ingredient and ingredient object
    all_records_by_ing = {}
    for record in all_variance_records:
        ing_id = record.ingredient.id
        if ing_id not in all_records_by_ing:
            all_records_by_ing[ing_id] = {
                'ingredient': record.ingredient,
                'variance_records': []
            }
        # Keep only latest 5
        if len(all_records_by_ing[ing_id]['variance_records']) < 5:
            all_records_by_ing[ing_id]['variance_records'].append(record)

    # Build final variance summary
    for ing_id, data in ingredients_data.items():
        records_count = data['records_count']
        within_tolerance = (data['within_tolerance_count'] / records_count * 100) if records_count > 0 else 0

        variance_summary.append({
            'ingredient': all_records_by_ing[ing_id]['ingredient'],
            'records_count': records_count,
            'avg_variance': data['avg_variance'],
            'max_variance': data['max_variance'],
            'min_variance': data['min_variance'],
            'within_tolerance_pct': within_tolerance,
            'variance_records': all_records_by_ing[ing_id]['variance_records'],
            'tolerance_threshold_1_5x': data['variance_allowance'] * 1.5
        })

        total_records += records_count
        within_tolerance_count += data['within_tolerance_count']

    # Calculate overall statistics
    if variance_summary:
        avg_of_avgs = sum(v['avg_variance'] for v in variance_summary) / len(variance_summary)
        overall_within_tolerance = (within_tolerance_count / total_records * 100) if total_records > 0 else 0
    else:
        avg_of_avgs = 0
        overall_within_tolerance = 0

    # Sort by avg_variance for insights
    best_performing = sorted(variance_summary, key=lambda x: x['avg_variance'])[:3]
    outside_tolerance = [v for v in variance_summary if v['avg_variance'] > v['ingredient'].variance_allowance]

    # Handle download
    if download == 'csv':
        return generate_variance_csv_download(variance_summary, days)
    elif download == 'detailed':
        return generate_variance_detailed_csv(variance_summary, days)

    context = {
        'variance_summary': variance_summary,
        'best_performing': best_performing,
        'outside_tolerance': outside_tolerance,
        'days': days,
        'total_records': total_records,
        'avg_of_avgs': avg_of_avgs,
        'overall_within_tolerance': overall_within_tolerance,
        'period_start': start_date,
        'period_end': end_date,
    }

    return render(request, 'products/variance_analysis_report.html', context)


def generate_variance_csv_download(variance_summary, days):
    """Generate CSV report for variance analysis"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="variance_analysis_{timezone.now().strftime("%Y%m%d")}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Ingredient', 'Avg Variance %', 'Max Variance %', 'Min Variance %', 'Within Tolerance %', 'Records'])

    for item in variance_summary:
        writer.writerow([
            item['ingredient'].name,
            f"{item['avg_variance']:.2f}",
            f"{item['max_variance']:.2f}",
            f"{item['min_variance']:.2f}",
            f"{item['within_tolerance_pct']:.2f}",
            item['records_count']
        ])

    return response


def generate_variance_detailed_csv(variance_summary, days):
    """Generate detailed CSV report with all variance records"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="variance_detailed_{timezone.now().strftime("%Y%m%d")}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Ingredient', 'Period End', 'Theoretical Used', 'Actual Used', 'Variance %', 'Status'])

    for item in variance_summary:
        for record in item['variance_records']:
            writer.writerow([
                item['ingredient'].name,
                record.period_end.strftime("%Y-%m-%d"),
                f"{record.theoretical_used:.3f}",
                f"{record.actual_used:.3f}",
                f"{record.variance_percentage:.2f}",
                'Within Tolerance' if record.within_tolerance else 'Outside Tolerance'
            ])

    return response


@login_required
def low_stock_report(request):
    """
    Report of all ingredients below minimum stock level.
    """
    low_stock_ingredients = BOMService.get_low_stock_ingredients()

    # Calculate total value of low stock
    # Note: cost calculation not applicable with simplified ingredient system
    total_value = 0

    # Get recent transactions for context
    week_ago = timezone.now() - timedelta(days=7)
    recent_purchases = StockTransaction.objects.filter(
        transaction_type='PURCHASE',
        created_at__gte=week_ago
    ).select_related('ingredient').count()

    context = {
        'low_stock_ingredients': low_stock_ingredients,
        'total_count': low_stock_ingredients.count(),
        'total_value': total_value,
        'recent_purchases': recent_purchases,
    }

    return render(request, 'products/low_stock_report.html', context)


@login_required
def waste_report(request):
    """
    Report of waste, spoilage, and freebies.
    Supports both regular page loads and AJAX requests for async filtering.
    """
    days = int(request.GET.get('days', 30))
    waste_type = request.GET.get('waste_type', 'ALL')

    end_date = timezone.now()
    start_date = end_date - timedelta(days=days)

    waste_logs = WasteLog.objects.filter(
        waste_date__gte=start_date,
        waste_date__lte=end_date
    ).select_related('ingredient', 'reported_by')

    if waste_type != 'ALL':
        waste_logs = waste_logs.filter(waste_type=waste_type)

    waste_logs = waste_logs.order_by('-waste_date')

    # Aggregate by type
    waste_by_type = {}
    total_cost = 0
    for waste in waste_logs:
        waste_t = waste.get_waste_type_display()
        if waste_t not in waste_by_type:
            waste_by_type[waste_t] = {
                'count': 0,
                'quantity': 0,
                'cost': 0
            }
        waste_by_type[waste_t]['count'] += 1
        waste_by_type[waste_t]['quantity'] += float(waste.quantity)
        waste_by_type[waste_t]['cost'] += float(waste.cost_impact)
        total_cost += float(waste.cost_impact)

    # Check if this is an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Return JSON for async filtering
        waste_logs_data = []
        for waste in waste_logs[:20]:  # Latest 20
            waste_logs_data.append({
                'id': waste.id,
                'ingredient_name': waste.ingredient.name if waste.ingredient else 'Unknown',
                'waste_type': waste.get_waste_type_display(),
                'quantity': float(waste.quantity),
                'unit': waste.ingredient.unit if waste.ingredient else '',
                'cost_impact': float(waste.cost_impact),
                'reason': waste.reason or '',
                'waste_date': waste.waste_date.strftime('%b %d, %Y %I:%M %p'),
                'reported_by': waste.reported_by.username if waste.reported_by else 'Unknown',
            })

        return JsonResponse({
            'success': True,
            'waste_logs': waste_logs_data,
            'waste_by_type': waste_by_type,
            'total_cost': float(total_cost),
            'days': days,
            'waste_type': waste_type,
        })

    # Regular page load - return HTML
    context = {
        'waste_logs': waste_logs[:20],  # Show latest 20
        'waste_by_type': waste_by_type,
        'total_cost': total_cost,
        'days': days,
        'waste_type': waste_type,
        'waste_types': WasteLog.WASTE_TYPES,
    }

    return render(request, 'products/waste_report.html', context)


@login_required
def api_ingredient_availability(request):
    """
    API endpoint to check ingredient availability for a product.
    """
    product_id = request.GET.get('product_id')
    quantity = int(request.GET.get('quantity', 1))

    if not product_id:
        return JsonResponse({'error': 'product_id required'}, status=400)

    availability = BOMService.check_ingredient_availability(product_id, quantity)

    return JsonResponse({
        'available': availability['available'],
        'has_recipe': availability['has_recipe'],
        'shortages': availability['shortages'],
        'total_shortages': availability['total_shortages']
    })
