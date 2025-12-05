#!/usr/bin/env python
"""
Script to update product prices for the new pricing model
"""
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'terrascope.settings')
django.setup()

from core.models import Product

def update_product_prices():
    """Update all products with new pricing"""
    products = Product.objects.all()
    
    if not products.exists():
        print("No products found in the database.")
        return
    
    print(f"Found {products.count()} product(s). Updating prices...")
    
    for product in products:
        product.price_10_minutes = 10.00
        product.price_2_hours = 25.00
        product.price_1_week = 50.00
        product.save()
        print(f"✓ Updated prices for: {product.name}")
    
    print("\n✓ All products updated successfully!")
    
    # Display updated products
    print("\nUpdated Products:")
    print("-" * 60)
    for product in Product.objects.all():
        print(f"\n{product.name}:")
        print(f"  - 10 Minutes: £{product.price_10_minutes}")
        print(f"  - 2 Hours:    £{product.price_2_hours}")
        print(f"  - 1 Week:     £{product.price_1_week}")

if __name__ == "__main__":
    update_product_prices()
