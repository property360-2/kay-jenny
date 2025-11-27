from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('sales-report/', views.sales_report, name='sales_report'),
    path('api/sales-data/', views.sales_data_api, name='sales_data_api'),
    path('forecast/', views.sales_forecast, name='sales_forecast'),
]
