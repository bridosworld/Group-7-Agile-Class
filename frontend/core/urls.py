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
  
    # Token Management URLs
    path('subscription/<int:subscription_id>/generate-token/', views.generate_token, name='generate_token'),
    path('token/<int:token_id>/revoke/', views.revoke_token, name='revoke_token'),
    path('token/<int:token_id>/refresh/', views.refresh_token, name='refresh_token'),

    # API Tokens
    path('api-tokens/', views.api_tokens, name='api_tokens'),
    path('api-tokens/generate/', views.generate_token, name='generate_token'),
    path('api-tokens/<int:token_id>/revoke/', views.revoke_token, name='revoke_token'),
    path('api-tokens/<int:token_id>/delete/', views.delete_token, name='delete_token'),
    path('api-tokens/<int:token_id>/copy/', views.copy_token, name='copy_token'),

    # API Endpoints (require JWT token from Authorization header)
    path('api/health/', views.api_health_check, name='api_health_check'),
    path('api/profile/', views.api_user_profile, name='api_user_profile'),
    path('api/subscriptions/', views.api_subscriptions, name='api_subscriptions'),
    path('api/subscriptions/<int:subscription_id>/', views.api_subscription_detail, name='api_subscription_detail'),
    path('api/tokens/', views.api_tokens_list, name='api_tokens_list'),
    path('api/usage/', views.api_usage_stats, name='api_usage_stats'),
    path('api/token-refresh/', views.api_token_refresh, name='api_token_refresh'),
]