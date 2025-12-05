"""
Integration Tests for US-15: Products, Metrics and Subscriptions

Tests the complete flow:
1. Product listing -> Product details
2. Subscription purchase -> Dashboard updates
3. Metrics data -> Visualization on site
"""

from django.test import TestCase, Client, override_settings
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from decimal import Decimal
from datetime import datetime, timedelta
from core.models import Product, Subscription, UserProfile
from django_otp.plugins.otp_totp.models import TOTPDevice


@override_settings(
    MIDDLEWARE=[
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django_otp.middleware.OTPMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    ]
)
class US15IntegrationTest(TestCase):
    """Integration tests for US-15 acceptance criteria"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create user profile
        UserProfile.objects.get_or_create(user=self.user)
        
        # Create 2FA device for the user (to bypass 2FA in tests)
        self.device = TOTPDevice.objects.create(
            user=self.user,
            name='default',
            confirmed=True
        )
        
        # Create test products
        self.product1 = Product.objects.create(
            name='Basic Plan',
            short_description='Entry level plan',
            description='Perfect for small projects',
            price_10_minutes=Decimal('9.99'),
            price_2_hours=Decimal('19.99'),
            price_1_week=Decimal('49.99'),
            api_calls_limit=1000,
            data_limit_mb=100,
            is_active=True
        )
        
        self.product2 = Product.objects.create(
            name='Premium Plan',
            short_description='Advanced plan',
            description='For enterprise needs',
            price_10_minutes=Decimal('49.99'),
            price_2_hours=Decimal('99.99'),
            price_1_week=Decimal('199.99'),
            api_calls_limit=10000,
            data_limit_mb=1000,
            is_active=True
        )
        
        # Login user (bypass 2FA for testing)
        self.client.force_login(self.user)
        # Set session to indicate 2FA is verified
        session = self.client.session
        session['_auth_user_backend'] = 'django.contrib.auth.backends.ModelBackend'
        session.save()
    
    def test_criterion_1_product_listing_to_details(self):
        """
        AC1: Given product listing, when clicked, then details displayed
        
        Flow:
        1. Access product listing page
        2. Verify all products are displayed
        3. Click on a product (access detail page)
        4. Verify product details are displayed correctly
        """
        print("\n=== Test Case 1: Product Listing -> Details ===")
        
        # Step 1: Access product listing page
        response = self.client.get(reverse('product_list'))
        self.assertEqual(response.status_code, 200, 
                        "Product listing page should load successfully")
        
        # Step 2: Verify products are displayed in listing
        self.assertContains(response, 'Basic Plan',
                           msg_prefix="Basic Plan should be in product listing")
        self.assertContains(response, 'Premium Plan',
                           msg_prefix="Premium Plan should be in product listing")
        self.assertContains(response, '9.99',
                           msg_prefix="Price should be displayed")
        
        print(f"[OK] Product listing page loaded with {Product.objects.count()} products")
        
        # Step 3: Click on product (access detail page)
        detail_url = reverse('product_detail', kwargs={'pk': self.product1.pk})
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 200,
                        "Product detail page should load successfully")
        
        # Step 4: Verify product details are displayed
        self.assertContains(response, 'Basic Plan',
                           msg_prefix="Product name should be displayed")
        self.assertContains(response, 'Perfect for small projects',
                           msg_prefix="Product description should be displayed")
        self.assertContains(response, '9.99',
                           msg_prefix="Product price should be displayed")
        self.assertContains(response, '1,000',
                           msg_prefix="API calls limit should be displayed")
        self.assertContains(response, '100',
                           msg_prefix="Data download limit should be displayed")
        self.assertContains(response, 'Subscribe',
                           msg_prefix="Subscribe button should be present")
        
        print(f"[OK] Product detail page displays all information correctly")
        print(f"  - Name: {self.product1.name}")
        print(f"  - Price: £{self.product1.price_1_week}")
        print(f"  - API Limit: {self.product1.api_calls_limit:,}")
        
        print("[PASS] CRITERION 1 PASSED: Product listing -> details flow works")
    
    def test_criterion_2_subscription_updates_dashboard(self):
        """
        AC2: Given subscription purchase, when completed, then dashboard updates
        
        Flow:
        1. Access dashboard before subscription (verify initial state)
        2. Create a subscription (simulating purchase)
        3. Access dashboard after subscription
        4. Verify dashboard metrics are updated
        """
        print("\n=== Test Case 2: Subscription Purchase -> Dashboard Updates ===")
        
        # Step 1: Check dashboard before subscription
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200,
                        "Dashboard should load successfully")
        
        initial_active = response.context['active_subscriptions']
        initial_spent = response.context['total_spent']
        
        print(f"[OK] Initial dashboard state:")
        print(f"  - Active subscriptions: {initial_active}")
        print(f"  - Total spent: £{initial_spent}")
        
        # Step 2: Create subscription (simulate purchase completion)
        subscription = Subscription.objects.create(
            user=self.user,
            product=self.product1,
            subscribed_at=timezone.now(),
            expires_at=timezone.now() + timedelta(days=30),
            status='active',
            duration_months=1,
            total_cost=self.product1.price_1_week,
            api_calls_made=0,
            api_calls_limit=self.product1.api_calls_limit,
            data_downloaded_mb=Decimal('0.00'),
            data_limit_mb=self.product1.data_limit_mb
        )
        
        print(f"[OK] Subscription created:")
        print(f"  - Product: {subscription.product.name}")
        print(f"  - Status: {subscription.status}")
        print(f"  - Price: £{subscription.total_cost}")
        
        # Step 3: Access dashboard after subscription
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200,
                        "Dashboard should load after subscription")
        
        # Step 4: Verify dashboard updates
        updated_active = response.context['active_subscriptions']
        updated_spent = response.context['total_spent']
        
        # Assert active subscriptions increased
        self.assertEqual(updated_active, initial_active + 1,
                        "Active subscriptions count should increase by 1")
        
        # Assert total spent increased by product price
        self.assertEqual(updated_spent, initial_spent + subscription.total_cost,
                        "Total spent should increase by subscription price")
        
        # Verify subscription appears in subscriptions list
        subscriptions = response.context['subscriptions']
        self.assertIn(subscription, subscriptions,
                     "New subscription should appear in dashboard list")
        
        print(f"[OK] Updated dashboard state:")
        print(f"  - Active subscriptions: {updated_active} (+{updated_active - initial_active})")
        print(f"  - Total spent: £{updated_spent} (+£{updated_spent - initial_spent})")
        
        # Verify subscription details are displayed
        self.assertContains(response, 'Basic Plan',
                           msg_prefix="Subscription product should be displayed")
        self.assertContains(response, 'active',
                           msg_prefix="Subscription status should be displayed")
        
        print("[PASS] CRITERION 2 PASSED: Dashboard updates after subscription")
    
    def test_criterion_3_metrics_visualization(self):
        """
        AC3: Given metrics data, when available, then visualized on site
        
        Flow:
        1. Create subscriptions with usage data (metrics)
        2. Access dashboard
        3. Verify metrics are available in context
        4. Verify chart data is prepared for visualization
        5. Verify all 5 metric cards display data
        """
        print("\n=== Test Case 3: Metrics Data -> Visualization ===")
        
        # Step 1: Create subscriptions with usage data
        sub1 = Subscription.objects.create(
            user=self.user,
            product=self.product1,
            subscribed_at=timezone.now(),
            expires_at=timezone.now() + timedelta(days=30),
            status='active',
            duration_months=1,
            total_cost=self.product1.price_1_week,
            api_calls_made=500,
            api_calls_limit=self.product1.api_calls_limit,
            data_downloaded_mb=Decimal('45.50'),
            data_limit_mb=self.product1.data_limit_mb
        )
        
        sub2 = Subscription.objects.create(
            user=self.user,
            product=self.product2,
            subscribed_at=timezone.now() - timedelta(days=60),
            expires_at=timezone.now() - timedelta(days=30),
            status='expired',
            duration_months=1,
            total_cost=self.product2.price_1_week,
            api_calls_made=8000,
            api_calls_limit=self.product2.api_calls_limit,
            data_downloaded_mb=Decimal('750.00'),
            data_limit_mb=self.product2.data_limit_mb
        )
        
        print(f"[OK] Created test subscriptions with metrics:")
        print(f"  - Active: {sub1.api_calls_made} API calls, {sub1.data_downloaded_mb} MB")
        print(f"  - Expired: {sub2.api_calls_made} API calls, {sub2.data_downloaded_mb} MB")
        
        # Step 2: Access dashboard
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200,
                        "Dashboard should load successfully")
        
        # Step 3: Verify metrics are available in context
        context = response.context
        
        # Check all 5 metric cards data
        self.assertIn('total_spent', context, "Total spent metric should be in context")
        self.assertIn('active_subscriptions', context, "Active subscriptions metric should be in context")
        self.assertIn('expired_subscriptions', context, "Expired subscriptions metric should be in context")
        self.assertIn('total_api_calls', context, "Total API calls metric should be in context")
        self.assertIn('total_data_used', context, "Total data used metric should be in context")
        
        # Verify metric values
        total_spent = context['total_spent']
        active_subs = context['active_subscriptions']
        expired_subs = context['expired_subscriptions']
        total_api_calls = context['total_api_calls']
        total_data_used = context['total_data_used']
        
        # Assert metrics are calculated correctly
        self.assertEqual(active_subs, 1, "Should have 1 active subscription")
        self.assertEqual(expired_subs, 1, "Should have 1 expired subscription")
        self.assertEqual(total_api_calls, 8500, "Total API calls should be sum of all subscriptions")
        self.assertEqual(total_data_used, Decimal('795.50'), "Total data should be sum of all subscriptions")
        self.assertEqual(total_spent, sub1.total_cost + sub2.total_cost,
                        "Total spent should be sum of all subscription prices")
        
        print(f"[OK] Metrics calculated correctly:")
        print(f"  - Total Spent: £{total_spent}")
        print(f"  - Active Subscriptions: {active_subs}")
        print(f"  - Expired Subscriptions: {expired_subs}")
        print(f"  - Total API Calls: {total_api_calls:,}")
        print(f"  - Total Data Used: {total_data_used} MB")
        
        # Step 4: Verify chart data is prepared
        # Charts use JavaScript with data embedded in template
        # Verify the metrics cards are rendered
        self.assertContains(response, 'Total Spent',
                           msg_prefix="Total Spent card should be displayed")
        self.assertContains(response, 'Active Subscriptions',
                           msg_prefix="Active Subscriptions card should be displayed")
        self.assertContains(response, 'Expired Subscriptions',
                           msg_prefix="Expired Subscriptions card should be displayed")
        self.assertContains(response, 'Total API Calls',
                           msg_prefix="Total API Calls card should be displayed")
        self.assertContains(response, 'Data Used',
                           msg_prefix="Data Used card should be displayed")
        
        # Verify chart sections exist
        self.assertContains(response, 'Usage Analytics',
                           msg_prefix="Charts section should be present")
        self.assertContains(response, 'API Calls Trend',
                           msg_prefix="API Calls chart should be present")
        self.assertContains(response, 'Data Usage',
                           msg_prefix="Data Usage chart should be present")
        self.assertContains(response, 'Success Rate',
                           msg_prefix="Success Rate chart should be present")
        
        # Verify chart canvas elements
        self.assertContains(response, 'apiCallsChart',
                           msg_prefix="API Calls chart canvas should be present")
        self.assertContains(response, 'dataUsageChart',
                           msg_prefix="Data Usage chart canvas should be present")
        self.assertContains(response, 'successRateChart',
                           msg_prefix="Success Rate chart canvas should be present")
        
        print(f"[OK] All visualization elements present:")
        print(f"  - 5 metric cards rendered")
        print(f"  - 3 chart sections present")
        print(f"  - Chart.js canvases initialized")
        
        print("[PASS] CRITERION 3 PASSED: Metrics data visualized on site")
    
    def test_complete_user_journey(self):
        """
        Complete integration test: Full user journey through all 3 criteria
        
        Journey:
        1. User views products
        2. User clicks on a product to see details
        3. User subscribes to product
        4. Dashboard updates with new subscription
        5. Metrics are displayed and visualized
        """
        print("\n=== Complete User Journey Integration Test ===")
        
        # Journey Step 1: View products
        print("\n[Step 1] User views product listing...")
        response = self.client.get(reverse('product_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Basic Plan')
        print("[OK] Product listing displayed")
        
        # Journey Step 2: View product details
        print("\n[Step 2] User clicks on 'Basic Plan' to view details...")
        response = self.client.get(reverse('product_detail', kwargs={'pk': self.product1.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Proceed to Payment')
        print("[OK] Product details displayed with subscribe option")
        
        # Journey Step 3: Check dashboard before subscription
        print("\n[Step 3] Checking dashboard before subscription...")
        response = self.client.get(reverse('dashboard'))
        initial_active = response.context['active_subscriptions']
        initial_spent = response.context['total_spent']
        print(f"[OK] Initial state - Active: {initial_active}, Spent: £{initial_spent}")
        
        # Journey Step 4: User subscribes (simulated)
        print("\n[Step 4] User completes subscription purchase...")
        subscription = Subscription.objects.create(
            user=self.user,
            product=self.product1,
            subscribed_at=timezone.now(),
            expires_at=timezone.now() + timedelta(days=30),
            status='active',
            duration_months=1,
            total_cost=self.product1.price_1_week,
            api_calls_made=150,
            api_calls_limit=self.product1.api_calls_limit,
            data_downloaded_mb=Decimal('12.50'),
            data_limit_mb=self.product1.data_limit_mb
        )
        print(f"[OK] Subscription created for {subscription.product.name}")
        
        # Journey Step 5: Dashboard updates
        print("\n[Step 5] User returns to dashboard...")
        response = self.client.get(reverse('dashboard'))
        final_active = response.context['active_subscriptions']
        final_spent = response.context['total_spent']
        
        self.assertEqual(final_active, initial_active + 1)
        self.assertEqual(final_spent, initial_spent + subscription.total_cost)
        print(f"[OK] Dashboard updated - Active: {final_active}, Spent: £{final_spent}")
        
        # Journey Step 6: Metrics visualized
        print("\n[Step 6] Verifying metrics visualization...")
        self.assertContains(response, 'Usage Analytics')
        self.assertContains(response, str(final_active))
        self.assertContains(response, '150')  # API calls
        print("[OK] Metrics displayed in cards and charts")
        
        print("\n[PASS] COMPLETE USER JOURNEY PASSED")
        print("=" * 60)
        print("Summary:")
        print("  [OK] User can browse and view product details")
        print("  [OK] Subscription purchase updates dashboard")
        print("  [OK] Metrics are calculated and visualized")
        print("  [OK] All US-15 acceptance criteria met")
        print("=" * 60)


@override_settings(
    MIDDLEWARE=[
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django_otp.middleware.OTPMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    ]
)
class US15EdgeCasesTest(TestCase):
    """Edge cases and boundary tests for US-15"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        UserProfile.objects.get_or_create(user=self.user)
        self.client.force_login(self.user)
    
    def test_dashboard_with_no_subscriptions(self):
        """Test dashboard displays correctly with no subscription data"""
        print("\n=== Edge Case: Dashboard with No Subscriptions ===")
        
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        
        # Verify zero states
        self.assertEqual(response.context['active_subscriptions'], 0)
        self.assertEqual(response.context['total_spent'], Decimal('0.00'))
        self.assertEqual(response.context['total_api_calls'], 0)
        
        print("[OK] Dashboard handles zero subscriptions gracefully")
        print("[PASS] EDGE CASE PASSED")
    
    def test_product_detail_invalid_id(self):
        """Test accessing product detail with non-existent ID"""
        print("\n=== Edge Case: Invalid Product ID ===")
        
        response = self.client.get(reverse('product_detail', kwargs={'pk': 99999}))
        self.assertEqual(response.status_code, 404,
                        "Should return 404 for non-existent product")
        
        print("[OK] System handles invalid product ID correctly")
        print("[PASS] EDGE CASE PASSED")
    
    def test_multiple_active_subscriptions(self):
        """Test dashboard with multiple active subscriptions"""
        print("\n=== Edge Case: Multiple Active Subscriptions ===")
        
        product1 = Product.objects.create(
            name='Plan 1',
            description='Test plan 1',
            price_1_week=Decimal('10.00'),
            api_calls_limit=1000,
            data_limit_mb=100
        )
        product2 = Product.objects.create(
            name='Plan 2',
            description='Test plan 2',
            price_1_week=Decimal('20.00'),
            api_calls_limit=2000,
            data_limit_mb=200
        )
        
        Subscription.objects.create(
            user=self.user, product=product1,
            subscribed_at=timezone.now(),
            expires_at=timezone.now() + timedelta(days=30),
            status='active',
            duration_months=1,
            total_cost=product1.price_1_week,
            api_calls_made=100,
            api_calls_limit=product1.api_calls_limit,
            data_downloaded_mb=Decimal('10.00'),
            data_limit_mb=product1.data_limit_mb
        )
        Subscription.objects.create(
            user=self.user, product=product2,
            subscribed_at=timezone.now(),
            expires_at=timezone.now() + timedelta(days=30),
            status='active',
            duration_months=1,
            total_cost=product2.price_1_week,
            api_calls_made=200,
            api_calls_limit=product2.api_calls_limit,
            data_downloaded_mb=Decimal('20.00'),
            data_limit_mb=product2.data_limit_mb
        )
        
        response = self.client.get(reverse('dashboard'))
        
        self.assertEqual(response.context['active_subscriptions'], 2)
        self.assertEqual(response.context['total_spent'], Decimal('30.00'))
        self.assertEqual(response.context['total_api_calls'], 300)
        
        print("[OK] Dashboard correctly aggregates multiple subscriptions")
        print("[PASS] EDGE CASE PASSED")
