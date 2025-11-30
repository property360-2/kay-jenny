"""
Management command to populate the database with comprehensive demo data for Cafe Kantina
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from sales_inventory_system.accounts.models import User
from sales_inventory_system.products.models import Product
from sales_inventory_system.orders.models import Order, OrderItem, Payment
from sales_inventory_system.system.models import AuditTrail


class Command(BaseCommand):
    help = 'Populate database with comprehensive demo data for Cafe Kantina'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting demo data population...'))

        with transaction.atomic():
            # Create users
            self.create_users()

            # Create products
            self.create_products()

            # Create sample orders
            self.create_orders()

        self.stdout.write(self.style.SUCCESS('\n✅ Demo data created successfully!'))
        self.stdout.write(self.style.SUCCESS('\nLogin credentials:'))
        self.stdout.write('  Admin: username=admin, password=admin123')
        self.stdout.write('  Cashier 1: username=cashier, password=cashier123')
        self.stdout.write('  Cashier 2: username=maria, password=maria123')
        self.stdout.write('  Cashier 3: username=jose, password=jose123')

    def create_users(self):
        """Create demo users"""
        self.stdout.write('\n📝 Creating users...')

        users_data = [
            {
                'username': 'cashier',
                'email': 'cashier@fjccoffee.com',
                'password': 'cashier123',
                'first_name': 'John',
                'last_name': 'Doe',
                'phone': '+63 917 123 4567',
                'role': 'CASHIER'
            },
            {
                'username': 'maria',
                'email': 'maria@fjccoffee.com',
                'password': 'maria123',
                'first_name': 'Maria',
                'last_name': 'Santos',
                'phone': '+63 918 234 5678',
                'role': 'CASHIER'
            },
            {
                'username': 'jose',
                'email': 'jose@fjccoffee.com',
                'password': 'jose123',
                'first_name': 'Jose',
                'last_name': 'Reyes',
                'phone': '+63 919 345 6789',
                'role': 'CASHIER'
            },
            {
                'username': 'manager',
                'email': 'manager@fjccoffee.com',
                'password': 'manager123',
                'first_name': 'Ana',
                'last_name': 'Garcia',
                'phone': '+63 920 456 7890',
                'role': 'ADMIN'
            },
        ]

        for user_data in users_data:
            if not User.objects.filter(username=user_data['username']).exists():
                user = User.objects.create_user(**user_data)
                self.stdout.write(f'  ✓ Created {user_data["role"].lower()}: {user.username}')

    def create_products(self):
        """Create demo coffee products"""
        self.stdout.write('\n🍕 Creating products...')

        products_data = [
            # Coffees
            {
                'name': 'Margherita Coffee',
                'description': 'Classic coffee with tomato sauce, mozzarella, and fresh basil',
                'price': Decimal('299.00'),
                'stock': 50,
                'threshold': 10,
                'category': 'Coffee'
            },
            {
                'name': 'Pepperoni Coffee',
                'description': 'Loaded with pepperoni slices and mozzarella cheese',
                'price': Decimal('349.00'),
                'stock': 45,
                'threshold': 10,
                'category': 'Coffee'
            },
            {
                'name': 'Hawaiian Coffee',
                'description': 'Ham, pineapple, and mozzarella cheese',
                'price': Decimal('329.00'),
                'stock': 40,
                'threshold': 10,
                'category': 'Coffee'
            },
            {
                'name': 'Supreme Coffee',
                'description': 'Loaded with pepperoni, sausage, bell peppers, onions, and olives',
                'price': Decimal('399.00'),
                'stock': 35,
                'threshold': 10,
                'category': 'Coffee'
            },
            {
                'name': 'Four Cheese Coffee',
                'description': 'Mozzarella, parmesan, gouda, and cheddar cheese blend',
                'price': Decimal('379.00'),
                'stock': 30,
                'threshold': 10,
                'category': 'Coffee'
            },
            {
                'name': 'BBQ Chicken Coffee',
                'description': 'Grilled chicken, BBQ sauce, onions, and mozzarella',
                'price': Decimal('389.00'),
                'stock': 25,
                'threshold': 10,
                'category': 'Coffee'
            },
            {
                'name': 'Veggie Supreme Coffee',
                'description': 'Mushrooms, bell peppers, onions, olives, and tomatoes',
                'price': Decimal('339.00'),
                'stock': 28,
                'threshold': 10,
                'category': 'Coffee'
            },
            {
                'name': 'Meat Lovers Coffee',
                'description': 'Pepperoni, sausage, bacon, ham, and ground beef',
                'price': Decimal('429.00'),
                'stock': 20,
                'threshold': 8,
                'category': 'Coffee'
            },

            # Sides
            {
                'name': 'Garlic Bread',
                'description': 'Toasted bread with garlic butter and herbs',
                'price': Decimal('89.00'),
                'stock': 100,
                'threshold': 20,
                'category': 'Sides'
            },
            {
                'name': 'Chicken Wings (6pcs)',
                'description': 'Crispy chicken wings with your choice of sauce',
                'price': Decimal('199.00'),
                'stock': 60,
                'threshold': 15,
                'category': 'Sides'
            },
            {
                'name': 'Mozzarella Sticks',
                'description': 'Breaded mozzarella sticks with marinara sauce',
                'price': Decimal('149.00'),
                'stock': 75,
                'threshold': 15,
                'category': 'Sides'
            },
            {
                'name': 'French Fries',
                'description': 'Crispy golden french fries',
                'price': Decimal('79.00'),
                'stock': 120,
                'threshold': 25,
                'category': 'Sides'
            },
            {
                'name': 'Onion Rings',
                'description': 'Crispy battered onion rings',
                'price': Decimal('99.00'),
                'stock': 80,
                'threshold': 20,
                'category': 'Sides'
            },
            {
                'name': 'Caesar Salad',
                'description': 'Fresh romaine lettuce with Caesar dressing and croutons',
                'price': Decimal('129.00'),
                'stock': 40,
                'threshold': 10,
                'category': 'Sides'
            },

            # Drinks
            {
                'name': 'Coca-Cola (500ml)',
                'description': 'Ice-cold Coca-Cola',
                'price': Decimal('49.00'),
                'stock': 200,
                'threshold': 50,
                'category': 'Drinks'
            },
            {
                'name': 'Sprite (500ml)',
                'description': 'Refreshing lemon-lime soda',
                'price': Decimal('49.00'),
                'stock': 180,
                'threshold': 50,
                'category': 'Drinks'
            },
            {
                'name': 'Iced Tea (500ml)',
                'description': 'Fresh brewed iced tea',
                'price': Decimal('39.00'),
                'stock': 150,
                'threshold': 40,
                'category': 'Drinks'
            },
            {
                'name': 'Bottled Water (500ml)',
                'description': 'Pure mineral water',
                'price': Decimal('29.00'),
                'stock': 300,
                'threshold': 75,
                'category': 'Drinks'
            },
            {
                'name': 'Orange Juice (500ml)',
                'description': 'Freshly squeezed orange juice',
                'price': Decimal('69.00'),
                'stock': 90,
                'threshold': 25,
                'category': 'Drinks'
            },

            # Desserts
            {
                'name': 'Chocolate Brownie',
                'description': 'Warm chocolate brownie with vanilla ice cream',
                'price': Decimal('129.00'),
                'stock': 40,
                'threshold': 10,
                'category': 'Desserts'
            },
            {
                'name': 'Tiramisu',
                'description': 'Classic Italian coffee-flavored dessert',
                'price': Decimal('149.00'),
                'stock': 30,
                'threshold': 8,
                'category': 'Desserts'
            },
            {
                'name': 'Cheesecake',
                'description': 'Creamy New York style cheesecake',
                'price': Decimal('139.00'),
                'stock': 35,
                'threshold': 8,
                'category': 'Desserts'
            },

            # Low stock items for testing
            {
                'name': 'Buffalo Wings (12pcs)',
                'description': 'Spicy buffalo wings with ranch dressing',
                'price': Decimal('279.00'),
                'stock': 5,  # Low stock
                'threshold': 10,
                'category': 'Sides'
            },
        ]

        for product_data in products_data:
            product, created = Product.objects.get_or_create(
                name=product_data['name'],
                defaults=product_data
            )
            if created:
                status = ' [LOW STOCK]' if product.stock < product.threshold else ''
                self.stdout.write(f'  ✓ Created product: {product.name}{status}')

    def create_orders(self):
        """Create sample orders for demonstration"""
        self.stdout.write('\n📦 Creating orders...')

        try:
            admin = User.objects.get(username='admin')
            cashier = User.objects.filter(username='cashier').first()
            products = list(Product.objects.all())

            if not products or len(products) < 4:
                self.stdout.write(self.style.WARNING('  ⚠ Not enough products found, skipping order creation'))
                return

            # Sample customer names
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

                order.calculate_total()

                # Create payment
                Payment.objects.create(
                    order=order,
                    method=payment_method,
                    status=payment_status,
                    amount=order.total_amount,
                    processed_by=processed_by
                )

                self.stdout.write(f'  ✓ Created order: {order.order_number} ({status}, {payment_method})')

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ✗ Error creating orders: {str(e)}'))
