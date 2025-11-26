from django.contrib import admin
from .models import (
    Product, Ingredient, RecipeItem, RecipeIngredient,
    StockTransaction, PhysicalCount, VarianceRecord,
    WasteLog, PrepBatch
)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'stock', 'requires_bom', 'category', 'is_low_stock', 'is_archived', 'created_at']
    list_filter = ['requires_bom', 'is_archived', 'category', 'created_at']
    search_fields = ['name', 'description', 'category']
    readonly_fields = ['created_at', 'updated_at']

    def is_low_stock(self, obj):
        return obj.is_low_stock
    is_low_stock.boolean = True
    is_low_stock.short_description = 'Low Stock'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ['name', 'unit', 'current_stock', 'min_stock', 'variance_allowance', 'is_low_stock', 'is_active']
    list_filter = ['unit', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'unit', 'is_active')
        }),
        ('Stock Information', {
            'fields': ('current_stock', 'min_stock')
        }),
        ('Variance Management', {
            'fields': ('variance_allowance',),
            'description': 'Allowable variance percentage for manual portioning (e.g., 10%)'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def is_low_stock(self, obj):
        return obj.is_low_stock
    is_low_stock.boolean = True


class RecipeIngredientInline(admin.TabularInline):
    """Inline admin for recipe ingredients"""
    model = RecipeIngredient
    extra = 1
    fields = ['ingredient', 'quantity']


@admin.register(RecipeItem)
class RecipeItemAdmin(admin.ModelAdmin):
    list_display = ['product', 'created_by', 'total_cost', 'created_at']
    list_filter = ['created_at', 'created_by']
    search_fields = ['product__name']
    readonly_fields = ['created_at', 'updated_at', 'total_cost']
    inlines = [RecipeIngredientInline]

    fieldsets = (
        ('Recipe Information', {
            'fields': ('product', 'created_by')
        }),
        ('Totals', {
            'fields': ('total_cost',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(StockTransaction)
class StockTransactionAdmin(admin.ModelAdmin):
    list_display = ['created_at', 'ingredient', 'transaction_type', 'quantity', 'reference_type', 'recorded_by']
    list_filter = ['transaction_type', 'created_at', 'ingredient']
    search_fields = ['ingredient__name', 'notes']
    readonly_fields = ['created_at']

    fieldsets = (
        ('Transaction Details', {
            'fields': ('ingredient', 'transaction_type', 'quantity', 'unit_cost')
        }),
        ('Reference Information', {
            'fields': ('reference_type', 'reference_id'),
            'description': 'Link to source transaction (order, waste log, etc.)'
        }),
        ('Additional Info', {
            'fields': ('recorded_by', 'notes', 'created_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:  # New object
            obj.recorded_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(PhysicalCount)
class PhysicalCountAdmin(admin.ModelAdmin):
    list_display = ['count_date', 'ingredient', 'physical_quantity', 'theoretical_quantity', 'variance_percentage', 'within_tolerance']
    list_filter = ['count_date', 'ingredient']
    search_fields = ['ingredient__name', 'notes']
    readonly_fields = ['variance_quantity', 'variance_percentage', 'within_tolerance', 'created_at']

    fieldsets = (
        ('Count Information', {
            'fields': ('ingredient', 'count_date', 'counted_by')
        }),
        ('Stock Quantities', {
            'fields': ('physical_quantity', 'theoretical_quantity')
        }),
        ('Variance Analysis', {
            'fields': ('variance_quantity', 'variance_percentage', 'within_tolerance'),
            'classes': ('wide',)
        }),
        ('Notes', {
            'fields': ('notes', 'created_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:  # New object
            obj.counted_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(VarianceRecord)
class VarianceRecordAdmin(admin.ModelAdmin):
    list_display = ['period_end', 'ingredient', 'theoretical_used', 'actual_used', 'variance_percentage', 'within_tolerance']
    list_filter = ['period_end', 'ingredient']
    search_fields = ['ingredient__name', 'notes']
    readonly_fields = ['created_at']

    fieldsets = (
        ('Period', {
            'fields': ('ingredient', 'period_start', 'period_end')
        }),
        ('Usage', {
            'fields': ('theoretical_used', 'actual_used')
        }),
        ('Variance Analysis', {
            'fields': ('variance_quantity', 'variance_percentage', 'within_tolerance'),
        }),
        ('Notes', {
            'fields': ('notes', 'created_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(WasteLog)
class WasteLogAdmin(admin.ModelAdmin):
    list_display = ['waste_date', 'ingredient', 'waste_type', 'quantity', 'cost_impact', 'reported_by']
    list_filter = ['waste_date', 'waste_type', 'ingredient']
    search_fields = ['ingredient__name', 'reason', 'notes']
    readonly_fields = ['cost_impact', 'created_at']

    fieldsets = (
        ('Waste Information', {
            'fields': ('ingredient', 'waste_type', 'waste_date', 'reported_by')
        }),
        ('Details', {
            'fields': ('quantity', 'reason', 'notes')
        }),
        ('Impact', {
            'fields': ('cost_impact',),
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:  # New object
            obj.reported_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(PrepBatch)
class PrepBatchAdmin(admin.ModelAdmin):
    list_display = ['name', 'recipe', 'quantity_produced', 'status', 'prepared_by', 'prep_start']
    list_filter = ['status', 'created_at', 'recipe']
    search_fields = ['name', 'recipe__product__name', 'notes']
    readonly_fields = ['created_at', 'expected_ingredient_usage']

    fieldsets = (
        ('Batch Information', {
            'fields': ('name', 'recipe', 'quantity_produced', 'status')
        }),
        ('Preparation', {
            'fields': ('prepared_by', 'prep_start', 'prep_end')
        }),
        ('Expected Ingredient Usage', {
            'fields': ('expected_ingredient_usage',),
            'classes': ('wide',)
        }),
        ('Notes', {
            'fields': ('notes', 'created_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:  # New object
            obj.prepared_by = request.user
        super().save_model(request, obj, form, change)
