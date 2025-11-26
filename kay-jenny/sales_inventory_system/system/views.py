from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import timedelta, datetime
from .models import AuditTrail, Archive


def is_admin(user):
    return user.is_authenticated and user.is_admin


@login_required
@user_passes_test(is_admin)
def audit_trail(request):
    """Display system audit trail with filtering and AJAX support"""

    # Get filter parameters
    action_filter = request.GET.get('action', '')
    model_filter = request.GET.get('model', '')
    user_filter = request.GET.get('user', '')
    date_range = request.GET.get('date_range', '30days')  # Default to 30 days
    date_from_str = request.GET.get('date_from', '')
    date_to_str = request.GET.get('date_to', '')

    # Base query
    audit_logs = AuditTrail.objects.all().select_related('user').order_by('-created_at')

    # Apply filters
    if action_filter:
        audit_logs = audit_logs.filter(action=action_filter)

    if model_filter:
        audit_logs = audit_logs.filter(model_name=model_filter)

    if user_filter:
        audit_logs = audit_logs.filter(user__username__icontains=user_filter)

    # Apply date range filters
    end_date = timezone.now()

    if date_range in ['7days', '30days', '90days']:
        # Handle preset date ranges
        days = int(date_range.replace('days', ''))
        start_date = end_date - timedelta(days=days)
        audit_logs = audit_logs.filter(created_at__gte=start_date, created_at__lte=end_date)
    elif date_range == 'custom':
        # Handle custom date range
        if date_from_str:
            try:
                date_from = datetime.fromisoformat(date_from_str).replace(hour=0, minute=0, second=0, microsecond=0)
                audit_logs = audit_logs.filter(created_at__gte=date_from)
            except (ValueError, TypeError):
                pass

        if date_to_str:
            try:
                date_to = datetime.fromisoformat(date_to_str).replace(hour=23, minute=59, second=59, microsecond=999999)
                audit_logs = audit_logs.filter(created_at__lte=date_to)
            except (ValueError, TypeError):
                pass

    # Pagination
    paginator = Paginator(audit_logs, 50)  # 50 logs per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # Get unique models and actions for filters
    models = AuditTrail.objects.values_list('model_name', flat=True).distinct().order_by('model_name')
    actions = AuditTrail.objects.values_list('action', flat=True).distinct().order_by('action')

    # Handle AJAX requests for async filtering
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Prepare audit logs data for JSON response
        logs_data = []
        for log in page_obj:
            logs_data.append({
                'id': log.id,
                'timestamp': log.created_at.isoformat(),
                'user': log.user.username if log.user else 'System',
                'action': log.action,
                'model_name': log.model_name,
                'record_id': log.record_id,
                'description': log.description,
                'ip_address': log.ip_address or 'N/A'
            })

        return JsonResponse({
            'success': True,
            'filters': {
                'action': action_filter,
                'model': model_filter,
                'user': user_filter,
                'date_range': date_range,
                'date_from': date_from_str,
                'date_to': date_to_str
            },
            'pagination': {
                'page': page_obj.number,
                'total_pages': paginator.num_pages,
                'per_page': 50,
                'total_count': paginator.count,
                'start_index': page_obj.start_index() if page_obj else 0,
                'end_index': page_obj.end_index() if page_obj else 0,
                'has_previous': page_obj.has_previous(),
                'has_next': page_obj.has_next(),
                'previous_page_number': page_obj.previous_page_number() if page_obj.has_previous() else None,
                'next_page_number': page_obj.next_page_number() if page_obj.has_next() else None
            },
            'audit_logs': logs_data,
            'available_actions': list(actions),
            'available_models': list(models)
        })

    context = {
        'audit_logs': page_obj,
        'models': models,
        'actions': actions,
        'action_filter': action_filter,
        'model_filter': model_filter,
        'user_filter': user_filter,
        'date_range': date_range,
        'date_from': date_from_str,
        'date_to': date_to_str,
    }
    return render(request, 'system/audit.html', context)


@login_required
@user_passes_test(is_admin)
def archive_list(request):
    """Display archived items with filtering"""

    # Get filter parameters
    model_filter = request.GET.get('model', '')

    # Base query
    archives = Archive.objects.all().select_related('archived_by').order_by('-created_at')

    # Apply filters
    if model_filter:
        archives = archives.filter(model_name=model_filter)

    # Pagination
    paginator = Paginator(archives, 50)  # 50 archives per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # Get unique models for filter
    models = Archive.objects.values_list('model_name', flat=True).distinct().order_by('model_name')

    context = {
        'archives': page_obj,
        'models': models,
        'model_filter': model_filter,
    }
    return render(request, 'system/archive.html', context)
