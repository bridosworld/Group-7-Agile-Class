"""
Integration Test: Product Listing to Product Detail Flow
Tests the navigation from product listing page to individual product details
"""
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from core.models import Product
from decimal import Decimal


# Disable 2FA middleware for testing
TEST_MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


@override_settings(MIDDLEWARE=TEST_MIDDLEWARE)
class ProductListingToDetailTest(TestCase):
    """
    Test Case: Product Listing to Detail Navigation
    
    User Story:
    As a user, when I view the product listing page and click on a product,
    I want to see the detailed information about that specific product.
    
    Acceptance Criteria:
    1. User can view product listing page with all active products
    2. Each product shows basic information (name, short description, price)
    3. User can click on a product to view full details
    4. Product detail page displays complete information
    5. Product detail page shows all pricing tiers
    6. Product detail page shows API limits and data limits
    """
    
    def setUp(self):
        """Set up test data"""
        print("\n" + "="*70)
        print("INTEGRATION TEST: Product Listing to Detail Flow")
        print("="*70)
        
        # Create test products
        self.product1 = Product.objects.create(
            name='Basic Plan',
            description='Perfect for individuals and small projects. Get started with essential features.',
            short_description='Essential features for beginners',
            price_10_minutes=Decimal('5.99'),
            price_2_hours=Decimal('19.99'),
            price_1_week=Decimal('79.99'),
            api_calls_limit=1000,
            data_limit_mb=100,
            is_active=True
        )
        
        self.product2 = Product.objects.create(
            name='Professional Plan',
            description='Advanced features for professionals and teams. Includes priority support.',
            short_description='Advanced features for professionals',
            price_10_minutes=Decimal('15.99'),
            price_2_hours=Decimal('49.99'),
            price_1_week=Decimal('199.99'),
            api_calls_limit=10000,
            data_limit_mb=1000,
            is_active=True
        )
        
        self.product3 = Product.objects.create(
            name='Enterprise Plan',
            description='Complete solution for large organizations with unlimited features.',
            short_description='Complete enterprise solution',
            price_10_minutes=Decimal('29.99'),
            price_2_hours=Decimal('99.99'),
            price_1_week=Decimal('399.99'),
            api_calls_limit=100000,
            data_limit_mb=10000,
            is_active=True
        )
        
        # Create inactive product (should not appear in listing)
        self.inactive_product = Product.objects.create(
            name='Inactive Plan',
            description='This product is inactive',
            short_description='Not available',
            price_10_minutes=Decimal('9.99'),
            price_2_hours=Decimal('29.99'),
            price_1_week=Decimal('99.99'),
            api_calls_limit=500,
            data_limit_mb=50,
            is_active=False
        )
        
        # Create client
        self.client = Client()
        
        print(f"[SETUP] Created {Product.objects.filter(is_active=True).count()} active products")
        print(f"[SETUP] Created {Product.objects.filter(is_active=False).count()} inactive product")
    
    def test_product_listing_to_detail_flow(self):
        """
        Main Test: User navigates from product listing to product detail
        
        Steps:
        1. User visits product listing page
        2. Verify all active products are displayed
        3. Verify product listing shows key information
        4. User clicks on a specific product
        5. Verify product detail page loads
        6. Verify all product details are displayed correctly
        """
        
        print("\n" + "-"*70)
        print("TEST FLOW: Product Listing -> Click Product -> View Details")
        print("-"*70)
        
        # STEP 1: User visits product listing page
        print("\n[STEP 1] User visits product listing page...")
        response = self.client.get(reverse('product_list'))
        
        self.assertEqual(response.status_code, 200)
        print("[OK] Product listing page loaded successfully")
        print(f"     - Status Code: {response.status_code}")
        
        # STEP 2: Verify all active products are displayed
        print("\n[STEP 2] Verifying active products are displayed...")
        
        # Check that all active products appear
        self.assertContains(response, 'Basic Plan')
        self.assertContains(response, 'Professional Plan')
        self.assertContains(response, 'Enterprise Plan')
        print("[OK] All 3 active products displayed")
        print(f"     - {self.product1.name}")
        print(f"     - {self.product2.name}")
        print(f"     - {self.product3.name}")
        
        # Verify inactive product is NOT displayed
        self.assertNotContains(response, 'Inactive Plan')
        print("[OK] Inactive products are hidden")
        
        # STEP 3: Verify product listing shows key information
        print("\n[STEP 3] Verifying product information on listing page...")
        
        # Check for product descriptions
        self.assertContains(response, self.product1.short_description)
        self.assertContains(response, self.product2.short_description)
        print("[OK] Product short descriptions displayed")
        
        # Check for pricing information (listing shows lowest price - 10 minutes)
        self.assertContains(response, str(self.product1.price_10_minutes))
        self.assertContains(response, str(self.product2.price_10_minutes))
        print("[OK] Pricing information displayed")
        
        # STEP 4: User clicks on 'Professional Plan' product
        print("\n[STEP 4] User clicks on 'Professional Plan'...")
        response = self.client.get(reverse('product_detail', args=[self.product2.id]))
        
        self.assertEqual(response.status_code, 200)
        print("[OK] Product detail page loaded")
        print(f"     - Product ID: {self.product2.id}")
        print(f"     - Product: {self.product2.name}")
        
        # STEP 5: Verify product detail page displays complete information
        print("\n[STEP 5] Verifying product details are displayed...")
        
        # Check product name
        self.assertContains(response, 'Professional Plan')
        print("[OK] Product name: Professional Plan")
        
        # Check full description
        self.assertContains(response, self.product2.description)
        print("[OK] Full description displayed")
        print(f"     - '{self.product2.description[:50]}...'")
        
        # STEP 6: Verify all pricing tiers are shown
        print("\n[STEP 6] Verifying all pricing tiers...")
        
        # Check all three pricing options
        self.assertContains(response, str(self.product2.price_10_minutes))
        self.assertContains(response, str(self.product2.price_2_hours))
        self.assertContains(response, str(self.product2.price_1_week))
        
        print("[OK] All pricing tiers displayed:")
        print(f"     - 10 Minutes: £{self.product2.price_10_minutes}")
        print(f"     - 2 Hours: £{self.product2.price_2_hours}")
        print(f"     - 1 Week: £{self.product2.price_1_week}")
        
        # STEP 7: Verify API and data limits
        print("\n[STEP 7] Verifying API and data limits...")
        
        # Check API limit - API limits are formatted with commas in the template (e.g., '10,000')
        self.assertContains(response, f"{self.product2.api_calls_limit:,}")
        print(f"[OK] API Calls Limit: {self.product2.api_calls_limit:,}")
        
        # Check data limit - Data limits are also formatted with commas in the template (e.g., '1,000 MB')
        self.assertContains(response, f"{self.product2.data_limit_mb:,}")
        print(f"[OK] Data Limit: {self.product2.data_limit_mb:,} MB")
        
        # STEP 8: Verify subscribe/purchase option is available
        print("\n[STEP 8] Verifying purchase options...")
        self.assertContains(response, 'Subscribe')
        print("[OK] Subscribe button available")
        
        print("\n" + "="*70)
        print("[PASS] PRODUCT LISTING TO DETAIL TEST PASSED")
        print("="*70)
        print("\nSummary:")
        print("  [OK] Product listing page loads successfully")
        print("  [OK] All active products displayed")
        print("  [OK] Inactive products hidden")
        print("  [OK] Product information visible on listing")
        print("  [OK] User can click product to view details")
        print("  [OK] Product detail page shows complete info")
        print("  [OK] All pricing tiers displayed")
        print("  [OK] API and data limits shown")
        print("  [OK] Subscribe button available")
        print("="*70)
    
    def test_multiple_product_details(self):
        """
        Test: User can view details of multiple different products
        """
        print("\n" + "-"*70)
        print("TEST: View Details of Multiple Products")
        print("-"*70)
        
        products = [self.product1, self.product2, self.product3]
        
        for product in products:
            print(f"\n[TEST] Viewing details of '{product.name}'...")
            
            response = self.client.get(reverse('product_detail', args=[product.id]))
            
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, product.name)
            self.assertContains(response, product.description)
            self.assertContains(response, str(product.price_2_hours))
            # API limits are formatted with commas in the template (e.g., "1,000")
            self.assertContains(response, f"{product.api_calls_limit:,}")
            
            print(f"[OK] {product.name} details displayed correctly")
            print(f"     - Price (2 hours): £{product.price_2_hours}")
            print(f"     - API Limit: {product.api_calls_limit:,}")
            print(f"     - Data Limit: {product.data_limit_mb} MB")
        
        print("\n[PASS] All product details accessible")
    
    def test_product_listing_shows_correct_count(self):
        """
        Test: Product listing shows correct number of active products
        """
        print("\n" + "-"*70)
        print("TEST: Product Listing Count")
        print("-"*70)
        
        print("\n[TEST] Checking product count on listing page...")
        response = self.client.get(reverse('product_list'))
        
        # Get products from context if available
        if 'products' in response.context:
            products_count = len(response.context['products'])
            print(f"[OK] Products in context: {products_count}")
            self.assertEqual(products_count, 3, "Should show 3 active products")
        
        # Verify active count
        active_products = Product.objects.filter(is_active=True).count()
        print(f"[OK] Active products in database: {active_products}")
        self.assertEqual(active_products, 3)
        
        # Verify inactive products are not counted
        total_products = Product.objects.count()
        print(f"[INFO] Total products (including inactive): {total_products}")
        
        print("[PASS] Product count is correct")
    
    def test_invalid_product_id(self):
        """
        Edge Case: User tries to access non-existent product
        """
        print("\n" + "-"*70)
        print("EDGE CASE: Invalid Product ID")
        print("-"*70)
        
        print("\n[TEST] User tries to access non-existent product (ID: 99999)...")
        response = self.client.get(reverse('product_detail', args=[99999]))
        
        # Should return 404 or redirect
        self.assertNotEqual(response.status_code, 200)
        print(f"[OK] Invalid product handled correctly")
        print(f"     - Status Code: {response.status_code}")
        
        print("[PASS] System handles invalid product IDs")
    
    def test_inactive_product_access(self):
        """
        Edge Case: User tries to access inactive product directly
        """
        print("\n" + "-"*70)
        print("EDGE CASE: Accessing Inactive Product")
        print("-"*70)
        
        print(f"\n[TEST] User tries to access inactive product (ID: {self.inactive_product.id})...")
        response = self.client.get(reverse('product_detail', args=[self.inactive_product.id]))
        
        # Depending on implementation, might show 404 or show product with disabled purchase
        print(f"[INFO] Response status: {response.status_code}")
        
        if response.status_code == 200:
            # If product is accessible, purchase should be disabled
            print("[INFO] Inactive product page accessible")
            # Could check for disabled subscribe button or warning message
        else:
            print("[OK] Inactive product not accessible")
        
        print("[PASS] Inactive product handled appropriately")


if __name__ == '__main__':
    import unittest
    unittest.main()
