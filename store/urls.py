from django.urls import path
from . import views

urlpatterns = [
    path('', views.store, name="store"),
    path('<slug:category_filter>/', views.store, name="filtered_by_category"),
    path('<slug:category_filter>/<slug:product_slug>', views.product, name="single_product"),
    path('post_review/<uuid:product_id>/', views.post_review, name='post_review')
]