from django.urls import path
from . import views

urlpatterns = [
    path('zp/request/<str:order_key>/', views.send_request, name='zp-request'),
    path('zp/verify/<str:order_key>/', views.verify, name='zp-verify'),
]
