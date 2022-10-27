from django.urls import path
from . import views

urlpatterns = [
    path('', views.user_dashboard, name='user-dashboard'),
    path('orders/', views.user_orders, name='user-orders'),
    path('profile/', views.profile, name='user-profile'),
    path('chpwd/', views.change_pass, name='user-chpwd'),

]
