from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list, name='home'),  # Handles root URL
    path('products/', views.product_list, name='product_list'),
    path('products/<int:pk>/', views.product_detail, name='product_detail'),
    path('subscribe/<int:pk>/', views.subscribe, name='subscribe'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),

]