from django.contrib import admin
from .models import Order, OrderItem, Payment

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product_name', 'product_price', 'subtotal']

    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        return super().get_queryset(request).select_related('product')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'customer_name', 'status', 'total_amount', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['order_number', 'customer_name', 'table_number']
    readonly_fields = ['order_number', 'created_at', 'updated_at']
    inlines = [OrderItemInline]

    def get_queryset(self, request):
        """Optimize queryset with select_related for foreign keys"""
        return super().get_queryset(request).select_related('processed_by', 'payment')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['order', 'method', 'status', 'amount', 'created_at']
    list_filter = ['method', 'status', 'created_at']
    search_fields = ['order__order_number', 'reference_number']
    readonly_fields = ['created_at', 'updated_at']

    def get_queryset(self, request):
        """Optimize queryset with select_related for foreign keys"""
        return super().get_queryset(request).select_related('order', 'processed_by')
