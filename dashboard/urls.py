from django.urls import path
from . import views

urlpatterns = [
    path('', views.user_dashboard, name='user-dashboard'),
    path('orders/', views.user_orders, name='user-orders'),
    path('orders/<str:order_key>', views.view_order, name='view-order'),
    path('profile/', views.user_profile, name='profile'),
    path('chpwd/', views.change_pass, name='user-chpwd'),

]
