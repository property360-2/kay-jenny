from django.urls import path
from . import views
from . import bom_views
from . import cashier_views

app_name = 'products'

urlpatterns = [
    path('', views.product_list, name='list'),
    path('create/', views.product_create, name='create'),
    path('<int:pk>/', views.product_detail, name='detail'),
    path('<int:pk>/edit/', views.product_edit, name='edit'),
    path('<int:pk>/archive/', views.product_archive, name='archive'),
    path('archives/', views.archived_products_list, name='archived_list'),
    path('<int:pk>/unarchive/', views.product_unarchive, name='unarchive'),
    path('unified-archives/', views.archived_products_list, name='unified_archives'),

    # Ingredient Management
    path('ingredients/', views.ingredient_list, name='ingredient_list'),
    path('ingredients/create/', views.ingredient_create, name='ingredient_create'),
    path('ingredients/<int:pk>/edit/', views.ingredient_edit, name='ingredient_edit'),
    path('ingredients/<int:pk>/delete/', views.ingredient_delete, name='ingredient_delete'),

    # Recipe Management
    path('<int:pk>/recipe/', views.recipe_edit, name='recipe_edit'),

    # BOM (Bill of Materials) routes
    path('bom/dashboard/', bom_views.bom_dashboard, name='bom_dashboard'),
    path('bom/usage-report/', bom_views.ingredient_usage_report, name='bom_usage_report'),
    path('bom/variance-analysis/', bom_views.variance_analysis_report, name='bom_variance'),
    path('bom/low-stock/', bom_views.low_stock_report, name='bom_low_stock'),
    path('bom/waste/', bom_views.waste_report, name='bom_waste'),

    # Cashier routes
    path('cashier/ingredients/', cashier_views.cashier_ingredients, name='cashier_ingredients'),

    # API routes
    path('api/ingredients/', views.api_list_ingredients, name='api_list_ingredients'),
    path('api/ingredients/create/', views.api_create_ingredient, name='api_create_ingredient'),
    path('api/ingredient-availability/', bom_views.api_ingredient_availability, name='api_ingredient_availability'),
    path('api/search-ingredients/', views.api_search_ingredients, name='api_search_ingredients'),
    path('api/categories/', views.api_list_categories, name='api_list_categories'),
    path('api/categories/create/', views.api_create_category, name='api_create_category'),
    path('api/search-categories/', views.api_search_categories, name='api_search_categories'),
    path('api/search-archives/', views.api_search_archives, name='api_search_archives'),

    # Cashier API routes
    path('api/cashier/ingredients/', cashier_views.api_get_ingredients, name='api_cashier_ingredients'),
    path('api/cashier/ingredients/toggle/', cashier_views.api_toggle_ingredient_availability, name='api_toggle_ingredient'),
]
