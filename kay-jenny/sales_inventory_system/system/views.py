from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.http import JsonResponse
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
    total_count = audit_logs.count()
    paginator = Paginator(audit_logs, 50)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # Handle AJAX requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        logs_data = []
        for log in page_obj:
            logs_data.append({
                'id': log.id,
                'user': log.user.username if log.user else 'System',
                'action': log.action,
                'model_name': log.model_name,
                'record_id': log.record_id,
                'description': log.description[:100] if log.description else '',
                'created_at': log.created_at.strftime('%b %d, %g:%M %p'),
            })

        return JsonResponse({
            'success': True,
            'logs': logs_data,
            'pagination': {
                'current_page': page_obj.number,
                'total_pages': paginator.num_pages,
                'total_count': total_count,
                'has_previous': page_obj.has_previous(),
                'has_next': page_obj.has_next(),
                'previous_page': page_obj.previous_page_number() if page_obj.has_previous() else None,
                'next_page': page_obj.next_page_number() if page_obj.has_next() else None,
                'start_index': page_obj.start_index(),
                'end_index': page_obj.end_index(),
            },
            'filters': {
                'user': user_filter,
                'action': action_filter,
                'model': model_filter,
                'date_range': date_range,
            }
        })

    context = {
        'page_obj': page_obj,
        'users': users,
        'models': models,
        'user_filter': user_filter,
        'action_filter': action_filter,
        'model_filter': model_filter,
        'date_range': date_range,
        'total_count': total_count,
    }

    return render(request, 'system/audit.html', context)

import csv
from django.http import HttpResponse

@login_required
@user_passes_test(is_admin)
def export_audit_trail(request):
    user_filter = request.GET.get('user', '')
    action_filter = request.GET.get('action', '')
    model_filter = request.GET.get('model', '')
    date_range = request.GET.get('date_range', '30')

    audit_logs = AuditLog.objects.select_related('user').all()

    if user_filter:
        audit_logs = audit_logs.filter(user_id=user_filter)

    if action_filter:
        audit_logs = audit_logs.filter(action=action_filter)

    if model_filter:
        audit_logs = audit_logs.filter(model_name=model_filter)

    if date_range != 'all':
        try:
            days = int(date_range)
            start_date = timezone.now() - timedelta(days=days)
            audit_logs = audit_logs.filter(created_at__gte=start_date)
        except:
            pass

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="audit_trail.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Timestamp',
        'User',
        'Action',
        'Model',
        'Record ID',
        'Description'
    ])

    for log in audit_logs:
        writer.writerow([
            log.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            log.user.username if log.user else 'System',
            log.action,
            log.model_name,
            log.record_id,
            log.description
        ])

    return response

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
    total_count = audit_logs.count()
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

    # Handle AJAX requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        logs_data = []
        for log in page_obj:
            logs_data.append({
                'id': log.id,
                'action': log.action,
                'model_name': log.model_name,
                'record_id': log.record_id,
                'description': log.description[:100] if log.description else '',
                'created_at': log.created_at.strftime('%b %d, %Y %I:%M %p'),
            })

        return JsonResponse({
            'success': True,
            'logs': logs_data,
            'stats': stats,
            'pagination': {
                'current_page': page_obj.number,
                'total_pages': paginator.num_pages,
                'total_count': total_count,
                'has_previous': page_obj.has_previous(),
                'has_next': page_obj.has_next(),
                'previous_page': page_obj.previous_page_number() if page_obj.has_previous() else None,
                'next_page': page_obj.next_page_number() if page_obj.has_next() else None,
                'start_index': page_obj.start_index(),
                'end_index': page_obj.end_index(),
            },
            'filters': {
                'model': model_filter,
                'date_range': date_range,
            }
        })

    context = {
        'audit_user': user,
        'page_obj': page_obj,
        'models': models,
        'model_filter': model_filter,
        'date_range': date_range,
        'stats': stats,
        'total_count': total_count,
    }

    return render(request, 'accounts/user_audit_trail.html', context)
