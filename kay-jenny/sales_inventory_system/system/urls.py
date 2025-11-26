from django.urls import path
from . import views

app_name = 'system'

urlpatterns = [
    path('audit/', views.audit_trail, name='audit'),
    path('archive/', views.archive_list, name='archive'),
]
