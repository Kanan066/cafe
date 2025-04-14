from django.urls import path
from . import views
from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('', views.cart_detail, name='cart_detail'),
]

urlpatterns = [
    path('', views.cart_summary, name="cart_summary"),
    path('add/', views.cart_add, name="cart_add"),
    path('delete/', views.cart_delete, name="cart_delete"),
    path('update/', views.cart_update, name="cart_update"),
    path('staff/dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('place_order/', views.place_order, name='place_order'),
    path('staff-login/', views.staff_login, name='staff_login'),
    path('order-status/', views.customer_order_status, name='customer_order_status'),
    path('staff/update/<int:order_id>/<str:status>/', views.update_order_status, name='update_order_status'),
      path('update-order/<int:order_id>/<str:status>/', views.update_order_status, name='update_order_status'),
]
