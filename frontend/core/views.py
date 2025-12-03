from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Product, Subscription
import requests
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages


def product_list(request):
    """Display all available products"""
    products = Product.objects.all()
    return render(request, 'core/product_list.html', {'products': products})

def product_detail(request, pk):
    """Display details for a specific product"""
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'core/product_detail.html', {'product': product})

@login_required
def subscribe(request, pk):
    """Subscribe user to a product"""
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        # Check if user already has a subscription
        existing_sub = Subscription.objects.filter(
            user=request.user, 
            product=product
        ).first()
        
        if not existing_sub:
            Subscription.objects.create(
                user=request.user,
                product=product,
                status='active'
            )
        
        return redirect('dashboard')
    
    return redirect('product_detail', pk=pk)

@login_required
def dashboard(request):
    """User dashboard showing their subscriptions"""
    subs = Subscription.objects.filter(user=request.user).select_related('product')
    
    # Try to fetch observations from API
    metrics = {}
    try:
        import requests
        token = request.session.get('jwt_token')
        if token:
            headers = {'Authorization': f'Bearer {token}'}
            API_BASE = 'http://127.0.0.1:5000'
            response = requests.get(f'{API_BASE}/observations', headers=headers, timeout=5)
            
            if response.status_code == 200:
                observations = response.json()
                for obs in observations:
                    sat = obs.get('satellite_id', 'Unknown')
                    metrics[sat] = metrics.get(sat, 0) + 1
    except Exception as e:
        print(f"API Error: {e}")
        metrics = {'No Data': 0}
    
    # Pass metrics as dict (json_script will handle serialization)
    return render(request, 'core/dashboard.html', {
        'subs': subs,
        'metrics': metrics,  # Pass as dict, not JSON string
    })

def user_login(request):
    """
    US-16: Log in to Django AND fetch JWT from Flask API.
    """
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        # 1) Django auth
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)

            # 2) Call Flask API /auth/login to get JWT
            jwt_token = None
            try:
                API_BASE = "http://127.0.0.1:5000"
                resp = requests.post(
                    f"{API_BASE}/auth/login",
                    json={"username": username, "password": password},
                    timeout=5,
                )
                if resp.status_code == 200:
                    jwt_token = resp.json().get("access_token")
                    request.session["jwt_token"] = jwt_token
                    print("JWT saved in session:", request.session.get("jwt_token"))
                else:
                    messages.warning(
                        request,
                        "Logged into website, but API token could not be obtained.",
                    )
            except Exception as e:
                messages.warning(
                    request,
                    f"Logged into website, but API is unavailable ({e}).",
                )

            return redirect("dashboard")

        # Wrong Django username/password
        messages.error(request, "Invalid username or password")
        return redirect("login")

    # GET request – show login form
    return render(request, "core/login.html")


def user_logout(request):
    """
    Log out of Django and clear JWT from session.
    """
    logout(request)
    request.session.pop("jwt_token", None)
    messages.info(request, "You have been logged out.")
    return redirect("login")
