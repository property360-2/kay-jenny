#!/usr/bin/env python
"""
Comprehensive Data Seeder for FJC Pizza Sales & Inventory System

This script validates the Django environment and models before seeding data.
It checks for:
- Required model files existence
- Database migrations status
- Model imports
- Existing data to prevent duplicates

Usage:
    python seed_data.py

Requirements:
    - Django project must be properly set up
    - All migrations must be applied
    - Virtual environment activated (if used)
"""

import os
import sys
import django
from pathlib import Path
from datetime import timedelta
from decimal import Decimal

# Setup Django environment
def setup_django():
    """Setup Django settings and environment"""
    try:
        # Add project directory to Python path
        project_root = Path(__file__).resolve().parent
        project_dir = project_root / 'sales_inventory_system'

        if not project_dir.exists():
            print(f"❌ Project directory not found: {project_dir}")
            return False

        sys.path.insert(0, str(project_dir))

        # Set Django settings module
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sales_inventory.settings')
        django.setup()

        print("✅ Django environment setup successful")
        return True
    except Exception as e:
        print(f"❌ Error setting up Django: {e}")
        import traceback
        traceback.print_exc()
        return False


def validate_model_files():
    """Validate that all required model files exist"""
    print("\n🔍 Validating model files...")

    project_dir = Path(__file__).parent / 'sales_inventory_system'
    required_files = [
        'accounts/models.py',
        'analytics/models.py',
        'orders/models.py',
        'products/models.py',
        'system/models.py',
    ]

    missing_files = []
    for file_path in required_files:
        full_path = project_dir / file_path
        if not full_path.exists():
            missing_files.append(file_path)
            print(f"  ❌ Missing: {file_path}")
        else:
            print(f"  ✅ Found: {file_path}")

    if missing_files:
        print(f"\n❌ Validation failed: {len(missing_files)} model file(s) missing")
        return False

    print("✅ All model files found")
    return True


def validate_models():
    """Validate that all required models can be imported"""
    print("\n🔍 Validating models...")

    try:
        from accounts.models import User
        print("  ✅ User model imported")

        from products.models import Product
        print("  ✅ Product model imported")

        from orders.models import Order, OrderItem, Payment
        print("  ✅ Order, OrderItem, Payment models imported")

        from system.models import AuditTrail, Archive
        print("  ✅ AuditTrail, Archive models imported")

        print("✅ All models validated successfully")
        return True
    except ImportError as e:
        print(f"❌ Model import error: {e}")
        return False


def check_migrations():
    """Check if all migrations are applied"""
    print("\n🔍 Checking database migrations...")

    try:
        from django.core.management import call_command
        from io import StringIO

        # Capture migration status
        out = StringIO()
        call_command('showmigrations', '--plan', stdout=out)
        output = out.getvalue()

        # Check for unapplied migrations
        if '[ ]' in output:
            print("❌ Unapplied migrations found!")
            print("\nPlease run: python manage.py migrate")
            return False

        print("✅ All migrations applied")
        return True
    except Exception as e:
        print(f"⚠️  Warning: Could not verify migrations: {e}")
        return True  # Continue anyway


def seed_users():
    """Create demo users"""
    from accounts.models import User

    print("\n👥 Seeding users...")

    users_data = [
        {
            'username': 'cashier',
            'email': 'cashier@fjcpizza.com',
            'password': 'cashier123',
            'first_name': 'John',
            'last_name': 'Doe',
            'phone': '+63 917 123 4567',
            'role': 'CASHIER'
        },
        {
            'username': 'maria',
            'email': 'maria@fjcpizza.com',
            'password': 'maria123',
            'first_name': 'Maria',
            'last_name': 'Santos',
            'phone': '+63 918 234 5678',
            'role': 'CASHIER'
        },
        {
            'username': 'jose',
            'email': 'jose@fjcpizza.com',
            'password': 'jose123',
            'first_name': 'Jose',
            'last_name': 'Reyes',
            'phone': '+63 919 345 6789',
            'role': 'CASHIER'
        },
        {
            'username': 'manager',
            'email': 'manager@fjcpizza.com',
            'password': 'manager123',
            'first_name': 'Ana',
            'last_name': 'Garcia',
            'phone': '+63 920 456 7890',
            'role': 'ADMIN'
        },
    ]

    created_count = 0
    skipped_count = 0

    for user_data in users_data:
        if User.objects.filter(username=user_data['username']).exists():
            print(f"  ⏭️  Skipped: {user_data['username']} (already exists)")
            skipped_count += 1
        else:
            User.objects.create_user(**user_data)
            print(f"  ✅ Created: {user_data['username']} ({user_data['role']})")
            created_count += 1

    print(f"\n📊 Users: {created_count} created, {skipped_count} skipped")
    return created_count


def seed_products():
    """Create demo products"""
    from products.models import Product

    print("\n🍕 Seeding products...")

    products_data = [
        # Pizzas
        {'name': 'Margherita Pizza', 'description': 'Classic pizza with tomato sauce, mozzarella, and fresh basil', 'price': Decimal('299.00'), 'stock': 50, 'threshold': 10, 'category': 'Pizza'},
        {'name': 'Pepperoni Pizza', 'description': 'Loaded with pepperoni slices and mozzarella cheese', 'price': Decimal('349.00'), 'stock': 45, 'threshold': 10, 'category': 'Pizza'},
        {'name': 'Hawaiian Pizza', 'description': 'Ham, pineapple, and mozzarella cheese', 'price': Decimal('329.00'), 'stock': 40, 'threshold': 10, 'category': 'Pizza'},
        {'name': 'Supreme Pizza', 'description': 'Loaded with pepperoni, sausage, bell peppers, onions, and olives', 'price': Decimal('399.00'), 'stock': 35, 'threshold': 10, 'category': 'Pizza'},
        {'name': 'Four Cheese Pizza', 'description': 'Mozzarella, parmesan, gouda, and cheddar cheese blend', 'price': Decimal('379.00'), 'stock': 30, 'threshold': 10, 'category': 'Pizza'},
        {'name': 'BBQ Chicken Pizza', 'description': 'Grilled chicken, BBQ sauce, onions, and mozzarella', 'price': Decimal('389.00'), 'stock': 25, 'threshold': 10, 'category': 'Pizza'},
        {'name': 'Veggie Supreme Pizza', 'description': 'Mushrooms, bell peppers, onions, olives, and tomatoes', 'price': Decimal('339.00'), 'stock': 28, 'threshold': 10, 'category': 'Pizza'},
        {'name': 'Meat Lovers Pizza', 'description': 'Pepperoni, sausage, bacon, ham, and ground beef', 'price': Decimal('429.00'), 'stock': 20, 'threshold': 8, 'category': 'Pizza'},

        # Sides
        {'name': 'Garlic Bread', 'description': 'Toasted bread with garlic butter and herbs', 'price': Decimal('89.00'), 'stock': 100, 'threshold': 20, 'category': 'Sides'},
        {'name': 'Chicken Wings (6pcs)', 'description': 'Crispy chicken wings with your choice of sauce', 'price': Decimal('199.00'), 'stock': 60, 'threshold': 15, 'category': 'Sides'},
        {'name': 'Mozzarella Sticks', 'description': 'Breaded mozzarella sticks with marinara sauce', 'price': Decimal('149.00'), 'stock': 75, 'threshold': 15, 'category': 'Sides'},
        {'name': 'French Fries', 'description': 'Crispy golden french fries', 'price': Decimal('79.00'), 'stock': 120, 'threshold': 25, 'category': 'Sides'},
        {'name': 'Onion Rings', 'description': 'Crispy battered onion rings', 'price': Decimal('99.00'), 'stock': 80, 'threshold': 20, 'category': 'Sides'},
        {'name': 'Caesar Salad', 'description': 'Fresh romaine lettuce with Caesar dressing and croutons', 'price': Decimal('129.00'), 'stock': 40, 'threshold': 10, 'category': 'Sides'},

        # Drinks
        {'name': 'Coca-Cola (500ml)', 'description': 'Ice-cold Coca-Cola', 'price': Decimal('49.00'), 'stock': 200, 'threshold': 50, 'category': 'Drinks'},
        {'name': 'Sprite (500ml)', 'description': 'Refreshing lemon-lime soda', 'price': Decimal('49.00'), 'stock': 180, 'threshold': 50, 'category': 'Drinks'},
        {'name': 'Iced Tea (500ml)', 'description': 'Fresh brewed iced tea', 'price': Decimal('39.00'), 'stock': 150, 'threshold': 40, 'category': 'Drinks'},
        {'name': 'Bottled Water (500ml)', 'description': 'Pure mineral water', 'price': Decimal('29.00'), 'stock': 300, 'threshold': 75, 'category': 'Drinks'},
        {'name': 'Orange Juice (500ml)', 'description': 'Freshly squeezed orange juice', 'price': Decimal('69.00'), 'stock': 90, 'threshold': 25, 'category': 'Drinks'},

        # Desserts
        {'name': 'Chocolate Brownie', 'description': 'Warm chocolate brownie with vanilla ice cream', 'price': Decimal('129.00'), 'stock': 40, 'threshold': 10, 'category': 'Desserts'},
        {'name': 'Tiramisu', 'description': 'Classic Italian coffee-flavored dessert', 'price': Decimal('149.00'), 'stock': 30, 'threshold': 8, 'category': 'Desserts'},
        {'name': 'Cheesecake', 'description': 'Creamy New York style cheesecake', 'price': Decimal('139.00'), 'stock': 35, 'threshold': 8, 'category': 'Desserts'},

        # Low stock item for testing
        {'name': 'Buffalo Wings (12pcs)', 'description': 'Spicy buffalo wings with ranch dressing', 'price': Decimal('279.00'), 'stock': 5, 'threshold': 10, 'category': 'Sides'},
    ]

    created_count = 0
    skipped_count = 0
    low_stock_count = 0

    for product_data in products_data:
        if Product.objects.filter(name=product_data['name']).exists():
            print(f"  ⏭️  Skipped: {product_data['name']} (already exists)")
            skipped_count += 1
        else:
            product = Product.objects.create(**product_data)
            status = " [LOW STOCK]" if product.is_low_stock else ""
            print(f"  ✅ Created: {product.name}{status}")
            created_count += 1
            if product.is_low_stock:
                low_stock_count += 1

    print(f"\n📊 Products: {created_count} created, {skipped_count} skipped, {low_stock_count} low stock")
    return created_count


def seed_orders():
    """Create sample orders"""
    from django.utils import timezone
    from accounts.models import User
    from products.models import Product
    from orders.models import Order, OrderItem, Payment

    print("\n📦 Seeding orders...")

    try:
        # Get admin and cashier users
        admin = User.objects.filter(username='admin').first()
        cashier = User.objects.filter(username='cashier').first()

        if not admin:
            print("  ⚠️  Admin user not found, using first superuser")
            admin = User.objects.filter(is_superuser=True).first()

        if not admin:
            print("  ❌ No admin/superuser found. Please create admin first.")
            return 0

        # Get all products
        products = list(Product.objects.all())

        if len(products) < 4:
            print(f"  ⚠️  Only {len(products)} products found. Need at least 4 for varied orders.")
            print("  ⏭️  Skipping order creation")
            return 0

        # Sample customer data
        customers = [
            ('Alice Johnson', 'T01'),
            ('Bob Smith', 'T02'),
            ('Carol Williams', 'T03'),
            ('David Brown', 'T04'),
            ('Emma Davis', 'T05'),
            ('Frank Miller', 'T06'),
            ('Grace Lee', 'T07'),
            ('Henry Wilson', 'T08'),
        ]

        created_count = 0
        existing_count = Order.objects.count()

        # Create 10 varied orders
        for i in range(10):
            customer_name, table = customers[i % len(customers)]

            # Vary the order status
            if i < 2:
                status = 'PENDING'
                payment_status = 'PENDING'
                payment_method = 'CASH'
                processed_by = None
            elif i < 5:
                status = 'IN_PROGRESS'
                payment_status = 'SUCCESS'
                payment_method = 'CASH' if i % 2 == 0 else 'ONLINE'
                processed_by = cashier or admin
            else:
                status = 'FINISHED'
                payment_status = 'SUCCESS'
                payment_method = 'ONLINE' if i % 3 == 0 else 'CASH'
                processed_by = cashier or admin

            # Create order
            order = Order.objects.create(
                customer_name=customer_name,
                table_number=table,
                status=status,
                notes='Extra napkins' if i % 3 == 0 else '',
                processed_by=processed_by,
                created_at=timezone.now() - timedelta(hours=i)
            )

            # Add 2-4 random items
            num_items = 2 + (i % 3)
            for j in range(num_items):
                product_index = (i * 3 + j) % len(products)
                OrderItem.objects.create(
                    order=order,
                    product=products[product_index],
                    quantity=1 + (j % 2)
                )

            # Calculate total
            order.calculate_total()

            # Create payment
            Payment.objects.create(
                order=order,
                method=payment_method,
                status=payment_status,
                amount=order.total_amount,
                processed_by=processed_by
            )

            print(f"  ✅ Created: {order.order_number} ({status}, {payment_method})")
            created_count += 1

        print(f"\n📊 Orders: {created_count} created, {existing_count} already existed")
        return created_count

    except Exception as e:
        print(f"  ❌ Error creating orders: {e}")
        import traceback
        traceback.print_exc()
        return 0


def print_summary():
    """Print summary of seeded data"""
    from accounts.models import User
    from products.models import Product
    from orders.models import Order

    print("\n" + "="*60)
    print("📊 DATABASE SUMMARY")
    print("="*60)

    # Users
    total_users = User.objects.count()
    admins = User.objects.filter(role='ADMIN').count()
    cashiers = User.objects.filter(role='CASHIER').count()
    print(f"\n👥 Users: {total_users} total ({admins} admins, {cashiers} cashiers)")

    # Products
    total_products = Product.objects.count()
    low_stock = Product.objects.filter(stock__lt=models.F('threshold')).count()
    categories = Product.objects.values_list('category', flat=True).distinct()
    print(f"🍕 Products: {total_products} total, {low_stock} low stock")
    print(f"   Categories: {', '.join(filter(None, categories))}")

    # Orders
    total_orders = Order.objects.count()
    pending = Order.objects.filter(status='PENDING').count()
    in_progress = Order.objects.filter(status='IN_PROGRESS').count()
    finished = Order.objects.filter(status='FINISHED').count()
    print(f"📦 Orders: {total_orders} total")
    print(f"   - {pending} pending")
    print(f"   - {in_progress} in progress")
    print(f"   - {finished} finished")

    print("\n" + "="*60)
    print("🔑 LOGIN CREDENTIALS")
    print("="*60)
    print("\nAdmin:")
    print("  Username: admin")
    print("  Password: admin123")
    print("\nCashiers:")
    print("  cashier / cashier123")
    print("  maria / maria123")
    print("  jose / jose123")
    print("\nManager:")
    print("  manager / manager123")
    print("\n" + "="*60)


def main():
    """Main seeding function"""
    print("="*60)
    print("🌱 FJC PIZZA DATA SEEDER")
    print("="*60)

    # Setup Django
    if not setup_django():
        sys.exit(1)

    # Import models here (after Django setup)
    from django.db import models
    globals()['models'] = models

    # Validate model files
    if not validate_model_files():
        sys.exit(1)

    # Validate models
    if not validate_models():
        sys.exit(1)

    # Check migrations
    if not check_migrations():
        sys.exit(1)

    # Confirm before seeding
    print("\n⚠️  This will add demo data to your database.")
    response = input("Continue? (y/N): ")

    if response.lower() != 'y':
        print("\n❌ Seeding cancelled")
        sys.exit(0)

    # Start seeding
    print("\n🚀 Starting data seeding...\n")

    try:
        # Seed data
        users_created = seed_users()
        products_created = seed_products()
        orders_created = seed_orders()

        # Print summary
        print_summary()

        print("\n✅ Data seeding completed successfully!")
        print("\n💡 Tip: Run 'python manage.py runserver' to start the application")

    except Exception as e:
        print(f"\n❌ Error during seeding: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
