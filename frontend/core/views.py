from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import requests
from .models import Product, Subscription

API_BASE = 'http://127.0.0.1:5000'  # Your Flask API

def product_list(request):
    products = Product.objects.all()
    return render(request, 'core/product_list.html', {'products': products})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'core/product_detail.html', {'product': product})

@login_required
def subscribe(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        Subscription.objects.create(user=request.user, product=product)
        return redirect('dashboard')
    return render(request, 'core/subscribe.html', {'product': product})

@login_required
def dashboard(request):
    subs = Subscription.objects.filter(user=request.user)
    try:
        token = request.session.get('jwt_token')
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(f'{API_BASE}/observations', headers=headers)
        observations = response.json() if response.status_code == 200 else []
        metrics = {}
        for obs in observations:
            sat = obs.get('satellite_id', 'Unknown')
            metrics[sat] = metrics.get(sat, 0) + 1
    except:
        metrics = {}
    return render(request, 'core/dashboard.html', {'subs': subs, 'metrics': metrics})