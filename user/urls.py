from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('dashboard/', views.user_dashboard, name='user-dashboard'),
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('reset_password_permission/<uidb64>/<token>/', views.reset_password_permission, name='reset_password_permission'),
    path('reset_password/', views.reset_password, name='reset_password'),

]
