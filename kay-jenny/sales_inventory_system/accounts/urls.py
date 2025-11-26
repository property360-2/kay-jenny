from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('users/', views.user_list, name='user_list'),
    path('users/create/', views.user_create, name='user_create'),
    path('users/<int:pk>/edit/', views.user_edit, name='user_edit'),
    path('users/<int:pk>/archive/', views.user_archive, name='user_archive'),
    path('users/<int:pk>/unarchive/', views.user_unarchive, name='user_unarchive'),
    path('users/<int:pk>/audit/', views.user_audit_trail, name='user_audit_trail'),
]
