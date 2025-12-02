from django.urls import path
from . import views

urlpatterns = [
    path('products/', views.product_list, name='product_list'),
    path('products/<int:pk>/', views.product_detail, name='product_detail'),
    path('subscribe/<int:pk>/', views.subscribe, name='subscribe'),
    path('dashboard/', views.dashboard, name='dashboard'),
]