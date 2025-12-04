from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Home and Products
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    path('products/<int:pk>/', views.product_detail, name='product_detail'),
    
    # Authentication
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('register/', views.register, name='register'),  #UNCOMMENT/ADD THIS
    
    # Payment
    path('checkout/<int:product_id>/', views.create_checkout_session, name='create_checkout_session'),
    path('payment/success/', views.payment_success, name='payment_success'),
    path('payment/cancel/', views.payment_cancel, name='payment_cancel'),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    path('subscription/<int:pk>/', views.subscription_detail, name='subscription_detail'),
    path('subscription/<int:pk>/pause/', views.pause_subscription, name='pause_subscription'),
    path('subscription/<int:pk>/resume/', views.resume_subscription, name='resume_subscription'),
    path('subscription/<int:pk>/cancel/', views.cancel_subscription, name='cancel_subscription'),
]