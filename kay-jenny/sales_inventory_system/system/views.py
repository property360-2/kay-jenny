from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import timedelta

from sales_inventory_system.accounts.models import User
from sales_inventory_system.accounts.views import is_admin
from .models import AuditLog


@login_required
@user_passes_test(is_admin)
def system_audit_trail(request):
    """System-wide audit trail with filtering"""

    # Get filter parameters
    user_filter = request.GET.get('user', '')
    action_filter = request.GET.get('action', '')
    model_filter = request.GET.get('model', '')
    date_range = request.GET.get('date_range', '30')  # Default: last 30 days

    # Base queryset
    audit_logs = AuditLog.objects.select_related('user', 'content_type').all()

    # Apply filters
    if user_filter:
        try:
            audit_logs = audit_logs.filter(user_id=int(user_filter))
        except (ValueError, TypeError):
            pass

    if action_filter:
        audit_logs = audit_logs.filter(action=action_filter)

    if model_filter:
        audit_logs = audit_logs.filter(model_name=model_filter)

    # Date range filter
    if date_range != 'all':
        try:
            days = int(date_range)
            start_date = timezone.now() - timedelta(days=days)
            audit_logs = audit_logs.filter(created_at__gte=start_date)
        except (ValueError, TypeError):
            pass

    # Get unique users and models for filter dropdowns
    users = User.objects.filter(audit_logs__isnull=False).distinct().order_by('username')
    models = AuditLog.objects.values_list('model_name', flat=True).distinct().order_by('model_name')

    # Pagination
    paginator = Paginator(audit_logs, 50)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'users': users,
        'models': models,
        'user_filter': user_filter,
        'action_filter': action_filter,
        'model_filter': model_filter,
        'date_range': date_range,
        'total_count': audit_logs.count(),
    }

    return render(request, 'system/audit.html', context)


@login_required
@user_passes_test(is_admin)
def user_audit_trail(request, pk):
    """User-specific audit trail"""

    user = get_object_or_404(User, pk=pk)

    # Get all audit logs for this user
    audit_logs = AuditLog.objects.filter(user=user).select_related('content_type')

    # Date range filter
    date_range = request.GET.get('date_range', '30')
    if date_range != 'all':
        try:
            days = int(date_range)
            start_date = timezone.now() - timedelta(days=days)
            audit_logs = audit_logs.filter(created_at__gte=start_date)
        except (ValueError, TypeError):
            pass

    # Model filter
    model_filter = request.GET.get('model', '')
    if model_filter:
        audit_logs = audit_logs.filter(model_name=model_filter)

    # Get unique models for this user
    models = AuditLog.objects.filter(user=user).values_list('model_name', flat=True).distinct().order_by('model_name')

    # Pagination
    paginator = Paginator(audit_logs, 50)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # Get statistics
    stats = {
        'total_actions': AuditLog.objects.filter(user=user).count(),
        'creates': AuditLog.objects.filter(user=user, action='CREATE').count(),
        'updates': AuditLog.objects.filter(user=user, action='UPDATE').count(),
        'deletes': AuditLog.objects.filter(user=user, action='DELETE').count(),
        'archives': AuditLog.objects.filter(user=user, action='ARCHIVE').count(),
        'restores': AuditLog.objects.filter(user=user, action='RESTORE').count(),
    }

    context = {
        'audit_user': user,
        'page_obj': page_obj,
        'models': models,
        'model_filter': model_filter,
        'date_range': date_range,
        'stats': stats,
        'total_count': audit_logs.count(),
    }

    return render(request, 'accounts/user_audit_trail.html', context)
