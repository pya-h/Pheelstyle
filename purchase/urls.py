from django.urls import path
from . import views

urlpatterns = [
    path('submit_order/', views.submit_order, name='submit_order'),
    path('preview/', views.preview, name='preview'),
    path('<str:order_key>/check', views.check_order, name='check_order'),
    path('<str:order_key>/accept', views.accept_order, name="accept_order"),
    path('<str:order_key>/receipt', views.take_receipt, name="order_receipt"),
    path('reserve/', views.reserve_order, name="reserve_order"),

]
