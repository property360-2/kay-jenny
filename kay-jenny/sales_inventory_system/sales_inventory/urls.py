"""
URL configuration for sales_inventory project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from .dashboards import admin_dashboard

@login_required
def home_redirect(request):
    """Redirect to appropriate dashboard based on user role"""
    if request.user.is_admin:
        return redirect('admin_dashboard')
    elif request.user.is_cashier:
        return redirect('orders:list')
    return redirect('accounts:login')

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', home_redirect, name='home'),
    path('dashboard/', admin_dashboard, name='admin_dashboard'),
    path('accounts/', include('sales_inventory_system.accounts.urls')),
    path('products/', include('sales_inventory_system.products.urls')),
    path('orders/', include('sales_inventory_system.orders.urls')),
    path('analytics/', include('sales_inventory_system.analytics.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
