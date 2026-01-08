from django.urls import path
from . import views

app_name = 'system'

urlpatterns = [
    path('audit/', views.system_audit_trail, name='audit_trail'),
    path('audit-trail/export/', views.export_audit_trail, name='audit_trail_export'),

]
