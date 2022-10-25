from django.urls import path
from . import views

urlpatterns = [
    path('', views.user_dashboard, name='user-dashboard'),
    path('orders/', views.user_orders, name='user-orders')
]
