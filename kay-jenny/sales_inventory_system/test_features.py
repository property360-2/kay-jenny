#!/usr/bin/env python
"""
Comprehensive test script for the three implemented features:
1. Product duplicate name validation
2. Forecast enhancement (dropdowns + ingredient forecasting)
3. Audit trail system
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sales_inventory.settings')
django.setup()

from django.contrib.auth import get_user_model
from products.models import Product, Ingredient, StockTransaction
from system.models import AuditLog
from analytics.forecasting import forecast_ingredient_stock
from django.test import Client
from django.urls import reverse
import json

User = get_user_model()

print("=" * 80)
print("FEATURE TESTING SUITE")
print("=" * 80)

# Get or create admin user for testing
try:
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        admin_user = User.objects.create_superuser(
            username='testadmin',
            email='admin@test.com',
            password='testpass123'
        )
    print(f"\n✓ Using admin user: {admin_user.username}")
except Exception as e:
    print(f"\n✗ Error getting admin user: {e}")

# Initialize test client
client = Client()

print("\n" + "=" * 80)
print("FEATURE 1: Product Duplicate Name Validation")
print("=" * 80)

try:
    # Test 1: Check API endpoint exists
    print("\n[Test 1.1] Testing duplicate check API endpoint...")

    # Create a test product
    test_product = Product.objects.create(
        name="Test Coffee",
        category="BEVERAGES",
        price=100.00,
        is_archived=False
    )
    print(f"  ✓ Created test product: {test_product.name} (ID: {test_product.id})")

    # Login as admin
    client.login(username=admin_user.username, password='testpass123')

    # Test duplicate check
    response = client.get('/products/api/check-product-name/', {
        'name': 'test coffee',  # Case-insensitive
        'product_id': ''
    })

    if response.status_code == 200:
        data = json.loads(response.content)
        if data.get('exists') == True:
            print(f"  ✓ API correctly detected duplicate: {data.get('duplicate_name')}")
        else:
            print(f"  ✗ API failed to detect duplicate")
    else:
        print(f"  ✗ API endpoint returned status {response.status_code}")

    # Test 2: Verify archived products are excluded
    print("\n[Test 1.2] Testing archived product exclusion...")
    test_product.is_archived = True
    test_product.save()

    response = client.get('/products/api/check-product-name/', {
        'name': 'test coffee',
        'product_id': ''
    })

    if response.status_code == 200:
        data = json.loads(response.content)
        if data.get('exists') == False:
            print(f"  ✓ Archived products correctly excluded from duplicate check")
        else:
            print(f"  ✗ Archived product incorrectly flagged as duplicate")

    # Cleanup
    test_product.delete()

except Exception as e:
    print(f"  ✗ Error in Feature 1 tests: {e}")

print("\n" + "=" * 80)
print("FEATURE 2: Forecast Enhancement")
print("=" * 80)

try:
    # Test 1: Verify forecast view has dropdown options
    print("\n[Test 2.1] Testing forecast page with dropdowns...")

    response = client.get('/analytics/forecast/')

    if response.status_code == 200:
        content = response.content.decode('utf-8')

        # Check for dropdown elements
        has_historical_dropdown = 'id="days_back"' in content and '<select' in content
        has_forecast_dropdown = 'id="days_ahead"' in content

        if has_historical_dropdown and has_forecast_dropdown:
            print(f"  ✓ Forecast page contains dropdown selectors")
        else:
            print(f"  ✗ Dropdowns not found in forecast page")

        # Check for dropdown options
        has_7days = '7 days' in content
        has_14days = '14 days' in content
        has_30days = '1 month (30 days)' in content
        has_90days = '3 months (90 days)' in content

        if has_7days and has_14days and has_30days and has_90days:
            print(f"  ✓ All dropdown options present (7/14/30/90 days)")
        else:
            print(f"  ✗ Missing dropdown options")
    else:
        print(f"  ✗ Forecast page returned status {response.status_code}")

    # Test 2: Test ingredient forecasting function
    print("\n[Test 2.2] Testing ingredient stock forecasting...")

    result = forecast_ingredient_stock(days_ahead=7)

    if result.get('success'):
        print(f"  ✓ Ingredient forecast function executed successfully")
        print(f"    - Total ingredients: {result.get('total_ingredients', 0)}")
        print(f"    - Critical warnings: {result.get('critical_count', 0)}")
        print(f"    - Warning count: {result.get('warning_count', 0)}")
        print(f"    - Low stock warnings: {len(result.get('low_stock_warnings', []))}")
    else:
        print(f"  ✗ Ingredient forecast failed: {result.get('message', 'Unknown error')}")

    # Test 3: Verify ingredient forecast in template
    print("\n[Test 2.3] Testing ingredient forecast display in template...")

    response = client.get('/analytics/forecast/')

    if response.status_code == 200:
        content = response.content.decode('utf-8')

        has_ingredient_section = 'Ingredient Stock Forecast' in content
        has_ingredient_table = 'Daily Usage' in content or 'daily_usage_rate' in content

        if has_ingredient_section:
            print(f"  ✓ Ingredient forecast section present in template")
        else:
            print(f"  ✗ Ingredient forecast section not found")

except Exception as e:
    print(f"  ✗ Error in Feature 2 tests: {e}")

print("\n" + "=" * 80)
print("FEATURE 3: Audit Trail System")
print("=" * 80)

try:
    # Test 1: Verify AuditLog model exists and is accessible
    print("\n[Test 3.1] Testing AuditLog model...")

    audit_count = AuditLog.objects.count()
    print(f"  ✓ AuditLog model accessible (Current logs: {audit_count})")

    # Test 2: Test signal tracking by creating a product
    print("\n[Test 3.2] Testing automatic audit logging via signals...")

    initial_count = AuditLog.objects.count()

    # Create a product (should trigger CREATE audit log)
    test_product2 = Product.objects.create(
        name="Audit Test Product",
        category="BEVERAGES",
        price=150.00,
        is_archived=False
    )

    new_count = AuditLog.objects.count()

    if new_count > initial_count:
        latest_log = AuditLog.objects.first()
        print(f"  ✓ Audit log created automatically (Action: {latest_log.action})")
        print(f"    - Model: {latest_log.model_name}")
        print(f"    - Record ID: {latest_log.record_id}")
        print(f"    - User: {latest_log.user.username if latest_log.user else 'System'}")
    else:
        print(f"  ✗ No audit log created for product creation")

    # Test 3: Test UPDATE action
    print("\n[Test 3.3] Testing UPDATE audit logging...")

    initial_count = AuditLog.objects.count()
    test_product2.price = 175.00
    test_product2.save()

    new_count = AuditLog.objects.count()

    if new_count > initial_count:
        latest_log = AuditLog.objects.first()
        if latest_log.action == 'UPDATE':
            print(f"  ✓ UPDATE audit log created")
            if latest_log.data_before and latest_log.data_after:
                print(f"    - Before/After snapshots captured")
        else:
            print(f"  ✗ Expected UPDATE but got {latest_log.action}")
    else:
        print(f"  ✗ No audit log created for product update")

    # Test 4: Test ARCHIVE action
    print("\n[Test 3.4] Testing ARCHIVE audit logging...")

    initial_count = AuditLog.objects.count()
    test_product2._audit_action = 'ARCHIVE'
    test_product2.is_archived = True
    test_product2.save()

    new_count = AuditLog.objects.count()

    if new_count > initial_count:
        latest_log = AuditLog.objects.first()
        if latest_log.action == 'ARCHIVE':
            print(f"  ✓ ARCHIVE audit log created")
        else:
            print(f"  ✗ Expected ARCHIVE but got {latest_log.action}")
    else:
        print(f"  ✗ No audit log created for product archive")

    # Test 5: Test system-wide audit trail view
    print("\n[Test 3.5] Testing system-wide audit trail page...")

    response = client.get('/system/audit/')

    if response.status_code == 200:
        print(f"  ✓ System audit trail page accessible")
        content = response.content.decode('utf-8')

        has_filters = 'model-filter' in content or 'action-filter' in content
        has_table = 'audit' in content.lower() and 'table' in content.lower()

        if has_filters:
            print(f"    - Filter controls present")
        if has_table:
            print(f"    - Audit log table present")
    else:
        print(f"  ✗ System audit trail returned status {response.status_code}")

    # Test 6: Test user-specific audit trail
    print("\n[Test 3.6] Testing user-specific audit trail page...")

    response = client.get(f'/accounts/users/{admin_user.id}/audit/')

    if response.status_code == 200:
        print(f"  ✓ User audit trail page accessible")
        content = response.content.decode('utf-8')

        has_user_info = admin_user.username in content
        has_audit_logs = 'audit' in content.lower()

        if has_user_info:
            print(f"    - User information displayed")
        if has_audit_logs:
            print(f"    - User audit logs present")
    else:
        print(f"  ✗ User audit trail returned status {response.status_code}")

    # Test 7: Test navigation link
    print("\n[Test 3.7] Testing audit trail navigation link...")

    response = client.get('/dashboard/')

    if response.status_code == 200:
        content = response.content.decode('utf-8')

        has_audit_nav = 'Audit Trail' in content and 'system:audit_trail' in content

        if has_audit_nav:
            print(f"  ✓ Audit Trail navigation link present in sidebar")
        else:
            print(f"  ✗ Audit Trail navigation link not found")
    else:
        print(f"  Note: Dashboard returned status {response.status_code}")

    # Cleanup
    test_product2.delete()

except Exception as e:
    print(f"  ✗ Error in Feature 3 tests: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("TEST SUITE COMPLETE")
print("=" * 80)
print("\nAll three features have been tested:")
print("  1. Product Duplicate Name Validation")
print("  2. Forecast Enhancement (Dropdowns + Ingredient Forecasting)")
print("  3. Audit Trail System")
print("\n" + "=" * 80)
