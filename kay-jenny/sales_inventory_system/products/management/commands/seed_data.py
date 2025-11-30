from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal
import random
from datetime import timedelta

from sales_inventory_system.accounts.models import User
from sales_inventory_system.products.models import (
    Product, Ingredient, RecipeItem, RecipeIngredient,
    StockTransaction, PhysicalCount, VarianceRecord,
    WasteLog, PrepBatch
)
from sales_inventory_system.orders.models import Order, OrderItem, Payment
from sales_inventory_system.system.models import AuditTrail, Archive


class Command(BaseCommand):
    help = 'Seed comprehensive test data for the Cafe Kantina system'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting comprehensive data seeding...'))

        try:
            # Create users
            self.stdout.write('Creating users...')
            admin_user, cashier_users = self.create_users()

            # Create ingredients
            self.stdout.write('Creating ingredients...')
            ingredients = self.create_ingredients(admin_user)

            # Create products
            self.stdout.write('Creating products...')
            products = self.create_products()

            # Create recipes/BOM
            self.stdout.write('Creating recipes and BOM...')
            recipes = self.create_recipes(products, ingredients, admin_user)

            # Create stock transactions
            self.stdout.write('Creating stock transactions...')
            self.create_stock_transactions(ingredients, admin_user)

            # Create physical counts
            self.stdout.write('Creating physical counts...')
            self.create_physical_counts(ingredients, admin_user)

            # Create variance records
            self.stdout.write('Creating variance records...')
            self.create_variance_records(ingredients)

            # Create waste logs
            self.stdout.write('Creating waste logs...')
            self.create_waste_logs(ingredients, admin_user)

            # Create prep batches
            self.stdout.write('Creating prep batches...')
            self.create_prep_batches(recipes, admin_user)

            # Create orders and payments
            self.stdout.write('Creating orders...')
            self.create_orders(products, cashier_users, admin_user)

            # Create audit trails
            self.stdout.write('Creating audit trails...')
            self.create_audit_trails(admin_user, cashier_users)

            self.stdout.write(self.style.SUCCESS('âœ“ Data seeding completed successfully!'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error during seeding: {str(e)}'))
            raise

    def create_users(self):
        """Create admin and cashier users"""
        # Create or get admin user
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'first_name': 'Admin',
                'last_name': 'User',
                'email': 'admin@fjccoffee.com',
                'phone': '555-0001',
                'role': 'ADMIN',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(f'  Created admin user: {admin_user.username}')
        else:
            self.stdout.write(f'  Admin user already exists: {admin_user.username}')

        # Create cashier users
        cashier_users = []
        cashier_names = [
            ('Maria', 'Garcia'),
            ('John', 'Smith'),
            ('Sarah', 'Johnson'),
            ('Carlos', 'Martinez'),
        ]

        for i, (first_name, last_name) in enumerate(cashier_names):
            username = f'cashier{i+1}'
            cashier, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': f'{username}@fjccoffee.com',
                    'phone': f'555-000{i+2}',
                    'role': 'CASHIER',
                }
            )
            if created:
                cashier.set_password('cashier123')
                cashier.save()
                self.stdout.write(f'  Created cashier: {cashier.username}')
            cashier_users.append(cashier)

        return admin_user, cashier_users

    def create_ingredients(self, created_by_user):
        """Create coffee ingredients"""
        ingredients_data = [
            {
                'name': 'Coffee Flour',
                'unit': 'g',
                'current_stock': Decimal('50000.000'),
                'min_stock': Decimal('10000.000'),
                'variance_allowance': Decimal('5.00'),
            },
            {
                'name': 'Mozzarella Cheese',
                'unit': 'g',
                'current_stock': Decimal('30000.000'),
                'min_stock': Decimal('5000.000'),
                'variance_allowance': Decimal('3.00'),
            },
            {
                'name': 'Tomato Sauce',
                'unit': 'ml',
                'current_stock': Decimal('25000.000'),
                'min_stock': Decimal('5000.000'),
                'variance_allowance': Decimal('2.00'),
            },
            {
                'name': 'Pepperoni',
                'unit': 'g',
                'current_stock': Decimal('10000.000'),
                'min_stock': Decimal('3000.000'),
                'variance_allowance': Decimal('2.00'),
            },
            {
                'name': 'Fresh Basil',
                'unit': 'g',
                'current_stock': Decimal('500.000'),
                'min_stock': Decimal('100.000'),
                'variance_allowance': Decimal('10.00'),
            },
            {
                'name': 'Olive Oil',
                'unit': 'ml',
                'current_stock': Decimal('20000.000'),
                'min_stock': Decimal('3000.000'),
                'variance_allowance': Decimal('2.00'),
            },
            {
                'name': 'Mushrooms',
                'unit': 'g',
                'current_stock': Decimal('8000.000'),
                'min_stock': Decimal('2000.000'),
                'variance_allowance': Decimal('5.00'),
            },
            {
                'name': 'Bell Peppers',
                'unit': 'g',
                'current_stock': Decimal('6000.000'),
                'min_stock': Decimal('2000.000'),
                'variance_allowance': Decimal('8.00'),
            },
            {
                'name': 'Onions',
                'unit': 'g',
                'current_stock': Decimal('15000.000'),
                'min_stock': Decimal('3000.000'),
                'variance_allowance': Decimal('5.00'),
            },
            {
                'name': 'Yeast',
                'unit': 'g',
                'current_stock': Decimal('200.000'),
                'min_stock': Decimal('50.000'),
                'variance_allowance': Decimal('10.00'),
            },
            {
                'name': 'Salt',
                'unit': 'g',
                'current_stock': Decimal('10000.000'),
                'min_stock': Decimal('2000.000'),
                'variance_allowance': Decimal('5.00'),
            },
            {
                'name': 'Water',
                'unit': 'ml',
                'current_stock': Decimal('100000.000'),
                'min_stock': Decimal('20000.000'),
                'variance_allowance': Decimal('3.00'),
            },
        ]

        ingredients = {}
        for data in ingredients_data:
            ingredient, created = Ingredient.objects.get_or_create(
                name=data['name'],
                defaults={
                    'description': f'Ingredient: {data["name"]}',
                    'unit': data['unit'],
                    'current_stock': data['current_stock'],
                    'min_stock': data['min_stock'],
                    'variance_allowance': data['variance_allowance'],
                    'is_active': True,
                }
            )
            if created:
                self.stdout.write(f'  Created ingredient: {ingredient.name}')
            ingredients[data['name']] = ingredient

        return ingredients

    def create_products(self):
        """Create coffee products"""
        products_data = [
            {
                'name': 'Margherita Coffee',
                'description': 'Classic coffee with tomato sauce, mozzarella, and basil',
                'price': Decimal('12.99'),
                'stock': 20,
                'threshold': 5,
                'category': 'Coffees',
            },
            {
                'name': 'Pepperoni Coffee',
                'description': 'Coffee with tomato sauce, mozzarella, and pepperoni',
                'price': Decimal('14.99'),
                'stock': 15,
                'threshold': 5,
                'category': 'Coffees',
            },
            {
                'name': 'Vegetarian Coffee',
                'description': 'Coffee with vegetables including mushrooms, peppers, onions',
                'price': Decimal('13.99'),
                'stock': 10,
                'threshold': 5,
                'category': 'Coffees',
            },
            {
                'name': 'Supreme Coffee',
                'description': 'Loaded coffee with multiple toppings',
                'price': Decimal('16.99'),
                'stock': 8,
                'threshold': 3,
                'category': 'Coffees',
            },
            {
                'name': 'Cola',
                'description': 'Cold cola beverage',
                'price': Decimal('2.99'),
                'stock': 50,
                'threshold': 10,
                'category': 'Beverages',
            },
            {
                'name': 'Lemonade',
                'description': 'Fresh lemonade',
                'price': Decimal('3.49'),
                'stock': 40,
                'threshold': 10,
                'category': 'Beverages',
            },
            {
                'name': 'Garlic Bread',
                'description': 'Crispy garlic bread',
                'price': Decimal('4.99'),
                'stock': 25,
                'threshold': 5,
                'category': 'Sides',
            },
            {
                'name': 'Caesar Salad',
                'description': 'Fresh caesar salad with croutons',
                'price': Decimal('7.99'),
                'stock': 15,
                'threshold': 5,
                'category': 'Sides',
            },
        ]

        products = {}
        for data in products_data:
            product, created = Product.objects.get_or_create(
                name=data['name'],
                defaults={
                    'description': data['description'],
                    'price': data['price'],
                    'stock': data['stock'],
                    'threshold': data['threshold'],
                    'category': data['category'],
                }
            )
            if created:
                self.stdout.write(f'  Created product: {product.name}')
            products[data['name']] = product

        return products

    def create_recipes(self, products, ingredients, created_by_user):
        """Create recipes/BOM for all products (coffees, beverages, sides)"""
        recipes = {}

        for product in products.values():
            recipe, created = RecipeItem.objects.get_or_create(
                product=product,
                defaults={'created_by': created_by_user}
            )

            if created:
                self.stdout.write(f'  Created recipe for: {product.name}')

                # Define BOM based on product type and name
                if product.name == 'Margherita Coffee':
                    recipe_ingredients = [
                        (ingredients['Coffee Flour'], Decimal('0.400')),
                        (ingredients['Tomato Sauce'], Decimal('0.150')),
                        (ingredients['Mozzarella Cheese'], Decimal('0.200')),
                        (ingredients['Fresh Basil'], Decimal('5.000')),
                        (ingredients['Olive Oil'], Decimal('0.015')),
                        (ingredients['Yeast'], Decimal('5.000')),
                        (ingredients['Salt'], Decimal('0.005')),
                        (ingredients['Water'], Decimal('0.120')),
                    ]
                elif product.name == 'Pepperoni Coffee':
                    recipe_ingredients = [
                        (ingredients['Coffee Flour'], Decimal('0.400')),
                        (ingredients['Tomato Sauce'], Decimal('0.150')),
                        (ingredients['Mozzarella Cheese'], Decimal('0.200')),
                        (ingredients['Pepperoni'], Decimal('0.100')),
                        (ingredients['Olive Oil'], Decimal('0.015')),
                        (ingredients['Yeast'], Decimal('5.000')),
                        (ingredients['Salt'], Decimal('0.005')),
                        (ingredients['Water'], Decimal('0.120')),
                    ]
                elif product.name == 'Vegetarian Coffee':
                    recipe_ingredients = [
                        (ingredients['Coffee Flour'], Decimal('0.400')),
                        (ingredients['Tomato Sauce'], Decimal('0.150')),
                        (ingredients['Mozzarella Cheese'], Decimal('0.200')),
                        (ingredients['Mushrooms'], Decimal('0.080')),
                        (ingredients['Bell Peppers'], Decimal('0.060')),
                        (ingredients['Onions'], Decimal('0.050')),
                        (ingredients['Olive Oil'], Decimal('0.015')),
                        (ingredients['Yeast'], Decimal('5.000')),
                        (ingredients['Salt'], Decimal('0.005')),
                        (ingredients['Water'], Decimal('0.120')),
                    ]
                elif product.name == 'Supreme Coffee':
                    recipe_ingredients = [
                        (ingredients['Coffee Flour'], Decimal('0.400')),
                        (ingredients['Tomato Sauce'], Decimal('0.150')),
                        (ingredients['Mozzarella Cheese'], Decimal('0.250')),
                        (ingredients['Pepperoni'], Decimal('0.080')),
                        (ingredients['Mushrooms'], Decimal('0.080')),
                        (ingredients['Bell Peppers'], Decimal('0.060')),
                        (ingredients['Onions'], Decimal('0.050')),
                        (ingredients['Olive Oil'], Decimal('0.020')),
                        (ingredients['Yeast'], Decimal('5.000')),
                        (ingredients['Salt'], Decimal('0.005')),
                        (ingredients['Water'], Decimal('0.120')),
                    ]
                elif product.name == 'Garlic Bread':
                    recipe_ingredients = [
                        (ingredients['Coffee Flour'], Decimal('0.300')),
                        (ingredients['Olive Oil'], Decimal('0.050')),
                        (ingredients['Salt'], Decimal('0.003')),
                        (ingredients['Water'], Decimal('0.100')),
                        (ingredients['Yeast'], Decimal('3.000')),
                    ]
                elif product.name == 'Caesar Salad':
                    recipe_ingredients = [
                        (ingredients['Onions'], Decimal('0.100')),
                        (ingredients['Bell Peppers'], Decimal('0.080')),
                        (ingredients['Olive Oil'], Decimal('0.030')),
                        (ingredients['Salt'], Decimal('0.002')),
                    ]
                elif product.name == 'Cola':
                    # Beverages have simplified BOMs (just syrup + water)
                    recipe_ingredients = [
                        (ingredients['Water'], Decimal('0.250')),
                        (ingredients['Salt'], Decimal('0.001')),
                    ]
                elif product.name == 'Lemonade':
                    recipe_ingredients = [
                        (ingredients['Water'], Decimal('0.300')),
                        (ingredients['Salt'], Decimal('0.001')),
                    ]
                else:
                    recipe_ingredients = []

                for ingredient, quantity in recipe_ingredients:
                    RecipeIngredient.objects.get_or_create(
                        recipe=recipe,
                        ingredient=ingredient,
                        defaults={'quantity': quantity}
                    )

            recipes[product.name] = recipe

        return recipes

    def create_stock_transactions(self, ingredients, user):
        """Create stock transaction history"""
        transaction_count = 0
        base_date = timezone.now() - timedelta(days=30)

        for ingredient in ingredients.values():
            num_transactions = random.randint(3, 5)
            for i in range(num_transactions):
                transaction_type = random.choice(['PURCHASE', 'ADJUSTMENT', 'WASTE', 'PREP'])
                quantity = Decimal(str(round(random.uniform(1, 10), 3)))

                StockTransaction.objects.create(
                    ingredient=ingredient,
                    transaction_type=transaction_type,
                    quantity=quantity,
                    unit_cost=None,
                    reference_type='order' if transaction_type == 'PREP' else 'adjustment',
                    notes=f'{transaction_type} transaction for {ingredient.name}',
                    recorded_by=user,
                    created_at=base_date + timedelta(days=random.randint(0, 30))
                )
                transaction_count += 1

        self.stdout.write(f'  Created {transaction_count} stock transactions')

    def create_physical_counts(self, ingredients, user):
        """Create physical stock count records"""
        count_count = 0
        for ingredient in ingredients.values():
            num_counts = random.randint(1, 2)
            for _ in range(num_counts):
                physical_qty = ingredient.current_stock * Decimal(str(round(random.uniform(0.95, 1.05), 3)))

                PhysicalCount.objects.create(
                    ingredient=ingredient,
                    counted_by=user,
                    physical_quantity=physical_qty,
                    theoretical_quantity=ingredient.current_stock,
                    count_date=timezone.now() - timedelta(days=random.randint(1, 7)),
                    notes='Physical stock count'
                )
                count_count += 1

        self.stdout.write(f'  Created {count_count} physical counts')

    def create_variance_records(self, ingredients):
        """Create variance records"""
        variance_count = 0
        base_date = timezone.now() - timedelta(days=30)

        for ingredient in ingredients.values():
            num_records = random.randint(1, 2)
            for _ in range(num_records):
                theoretical = ingredient.current_stock * Decimal(str(round(random.uniform(0.8, 1.0), 3)))
                actual = theoretical * Decimal(str(round(random.uniform(0.95, 1.05), 3)))
                variance = actual - theoretical
                variance_pct = (variance / theoretical * 100) if theoretical > 0 else Decimal('0')

                VarianceRecord.objects.create(
                    ingredient=ingredient,
                    period_start=base_date - timedelta(days=random.randint(15, 30)),
                    period_end=base_date + timedelta(days=random.randint(0, 15)),
                    theoretical_used=theoretical,
                    actual_used=actual,
                    variance_quantity=variance,
                    variance_percentage=abs(variance_pct),
                    within_tolerance=abs(variance_pct) <= ingredient.variance_allowance,
                    notes='Automated variance record'
                )
                variance_count += 1

        self.stdout.write(f'  Created {variance_count} variance records')

    def create_waste_logs(self, ingredients, user):
        """Create waste log entries"""
        waste_count = 0
        waste_types = ['SPOILAGE', 'WASTE', 'FREEBIE', 'SAMPLE']

        for ingredient in list(ingredients.values())[:6]:
            num_waste = random.randint(1, 3)
            for _ in range(num_waste):
                WasteLog.objects.create(
                    ingredient=ingredient,
                    waste_type=random.choice(waste_types),
                    quantity=Decimal(str(round(random.uniform(0.5, 3), 3))),
                    reason=f'Waste log entry for {ingredient.name}',
                    reported_by=user,
                    waste_date=timezone.now() - timedelta(days=random.randint(1, 30)),
                    notes='Logged waste entry'
                )
                waste_count += 1

        self.stdout.write(f'  Created {waste_count} waste log entries')

    def create_prep_batches(self, recipes, user):
        """Create prep batch records"""
        batch_count = 0

        for recipe in recipes.values():
            num_batches = random.randint(1, 3)
            for i in range(num_batches):
                status = random.choice(['PLANNED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED'])
                prep_start = timezone.now() - timedelta(days=random.randint(1, 30))
                prep_end = prep_start + timedelta(hours=random.randint(1, 4)) if status in ['IN_PROGRESS', 'COMPLETED'] else None

                PrepBatch.objects.create(
                    name=f'{recipe.product.name} Batch {i+1}',
                    recipe=recipe,
                    quantity_produced=random.randint(5, 20),
                    status=status,
                    prepared_by=user if status != 'PLANNED' else None,
                    prep_start=prep_start if status != 'PLANNED' else None,
                    prep_end=prep_end,
                    notes=f'Batch preparation for {recipe.product.name}'
                )
                batch_count += 1

        self.stdout.write(f'  Created {batch_count} prep batches')

    def create_orders(self, products, cashier_users, admin_user):
        """Create orders and payments"""
        order_count = 0
        base_date = timezone.now() - timedelta(days=30)

        num_orders = random.randint(20, 30)
        for _ in range(num_orders):
            order = Order.objects.create(
                customer_name=random.choice(['John Doe', 'Jane Smith', 'Bob Johnson', 'Alice Williams', 'Carlos Lopez']),
                table_number=str(random.randint(1, 20)),
                status=random.choice(['PENDING', 'IN_PROGRESS', 'FINISHED', 'CANCELLED']),
                notes='Customer order',
                processed_by=random.choice(cashier_users),
                created_at=base_date + timedelta(days=random.randint(0, 30))
            )

            num_items = random.randint(1, 4)
            selected_products = random.sample(list(products.values()), min(num_items, len(products)))

            for product in selected_products:
                quantity = random.randint(1, 3)
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    product_name=product.name,
                    product_price=product.price,
                    quantity=quantity,
                    subtotal=product.price * quantity
                )

            order.calculate_total()

            if order.status in ['FINISHED', 'IN_PROGRESS']:
                Payment.objects.create(
                    order=order,
                    method=random.choice(['CASH', 'ONLINE']),
                    status=random.choice(['SUCCESS', 'PENDING']),
                    amount=order.total_amount,
                    reference_number=f'REF-{order.order_number}',
                    processed_by=random.choice(cashier_users),
                )

            order_count += 1

        self.stdout.write(f'  Created {order_count} orders with items and payments')

    def create_audit_trails(self, admin_user, cashier_users):
        """Create audit trail entries"""
        all_users = [admin_user] + cashier_users
        audit_count = 0

        actions = ['CREATE', 'UPDATE', 'DELETE', 'ARCHIVE', 'RESTORE']
        model_names = ['Product', 'Order', 'Payment', 'Ingredient', 'Recipe']

        for _ in range(30):
            AuditTrail.objects.create(
                user=random.choice(all_users),
                action=random.choice(actions),
                model_name=random.choice(model_names),
                record_id=random.randint(1, 100),
                description=f'Test audit trail entry',
                ip_address='192.168.1.1',
            )
            audit_count += 1

        self.stdout.write(f'  Created {audit_count} audit trail entries')

