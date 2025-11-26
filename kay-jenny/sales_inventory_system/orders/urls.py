from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.order_list, name='list'),

    # NEW POS Flow (Optimized)
    path('pos/', views.pos_home, name='pos_home'),
    path('pos/add-to-cart/<int:product_id>/', views.pos_add_to_cart, name='pos_add_to_cart'),
    path('pos/remove-from-cart/<int:product_id>/', views.pos_remove_from_cart, name='pos_remove_from_cart'),
    path('pos/update-cart/<int:product_id>/', views.pos_update_cart_quantity, name='pos_update_cart'),
    path('pos/get-cart/', views.pos_get_cart, name='pos_get_cart'),
    path('pos/get-cart-details/', views.pos_get_cart_details, name='pos_get_cart_details'),
    path('pos/cart/', views.pos_cart_view, name='pos_cart'),
    path('pos/checkout/', views.pos_checkout, name='pos_checkout'),
    path('pos/order/<str:order_number>/', views.pos_confirmation, name='pos_confirmation'),

    # OLD POS Flow (Legacy - deprecated)
    path('pos/create/', views.pos_create_order, name='pos_create_order'),

    path('<int:pk>/', views.order_detail, name='detail'),
    path('<int:pk>/update-status/', views.update_order_status, name='update_status'),
    path('<int:pk>/process-payment/', views.process_payment, name='process_payment'),
    path('<int:pk>/quick-payment/', views.quick_payment, name='quick_payment'),
    path('<int:pk>/archive/', views.order_archive, name='archive'),
    path('<int:pk>/unarchive/', views.order_unarchive, name='unarchive'),
]
