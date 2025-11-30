"""
Comprehensive seeder data generation for Cafe Kantina Sales & Inventory System.
Generates 30 days of historical sales data (backwards from today) with realistic patterns.
Suitable for Holt-Winters time series regression analysis.

Usage: python manage.py seed_comprehensive_data
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import random
import uuid

from sales_inventory_system.accounts.models import User
from sales_inventory_system.products.models import (
    Product,
    Ingredient,
    RecipeItem,
    RecipeIngredient,
)
from sales_inventory_system.orders.models import Order, OrderItem, Payment, Refund


class Command(BaseCommand):
    help = "Generate comprehensive historical sales data for the past 30 days"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting comprehensive data seeding..."))

        try:
            # Phase 1: Create users
            self.stdout.write("\nPhase 1: Creating users...")
            users = self._create_users()

            # Phase 2: Create products and ingredients
            self.stdout.write("\nPhase 2: Creating products and ingredients...")
            products, ingredients = self._create_products_and_ingredients()

            # Phase 3: Create recipes (BOM)
            self.stdout.write("\nPhase 3: Creating recipes (Bill of Materials)...")
            recipes = self._create_recipes(products, ingredients)

            # Phase 4: Generate 30 days of historical orders
            self.stdout.write("\nPhase 4: Generating 30 days of historical orders...")
            orders_data = self._generate_historical_orders(products, users)

            # Phase 5: Create payments and refunds
            self.stdout.write("\nPhase 5: Creating payments and refunds...")
            self._create_payments_and_refunds(orders_data, users)

            # Summary and statistics
            self._print_summary(users, products, ingredients, recipes, orders_data)

            self.stdout.write(
                self.style.SUCCESS("\nData seeding completed successfully!")
            )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"\nError during seeding: {str(e)}"))
            raise

    def _create_users(self):
        """Create admin, cashiers, and manager users."""
        users = {}

        # Create admin user
        admin, created = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@cafekantina.com",
                "first_name": "Admin",
                "last_name": "User",
                "phone": "09171234567",
                "role": "ADMIN",
                "is_staff": True,
                "is_superuser": True,
            },
        )
        if created:
            admin.set_password("admin123")
            admin.save()
            self.stdout.write(f"  Admin user created: {admin.username}")
        users["admin"] = admin

        # Create manager user
        manager, created = User.objects.get_or_create(
            username="manager",
            defaults={
                "email": "manager@cafekantina.com",
                "first_name": "Manager",
                "last_name": "User",
                "phone": "09171234568",
                "role": "ADMIN",
                "is_staff": True,
            },
        )
        if created:
            manager.set_password("manager123")
            manager.save()
            self.stdout.write(f"  Manager user created: {manager.username}")
        users["manager"] = manager

        # Create cashier users
        cashier_names = ["Maria", "Juan", "Ana", "Carlos", "Rosa"]
        cashiers = []
        for i, name in enumerate(cashier_names):
            username = f"cashier{i + 1}"
            email = f"cashier{i + 1}@cafekantina.com"
            phone = f"0917123456{i}"

            cashier, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": email,
                    "first_name": name,
                    "last_name": "Cashier",
                    "phone": phone,
                    "role": "CASHIER",
                },
            )
            if created:
                cashier.set_password("cashier123")
                cashier.save()
                self.stdout.write(f"  Cashier created: {cashier.username}")
            cashiers.append(cashier)

        users["cashiers"] = cashiers
        return users

    def _create_products_and_ingredients(self):
        """Create products with realistic prices and ingredients."""
        products = []
        ingredients = []

        # Product definitions
        product_data = [
            # Coffee Products
            {
                "name": "Espresso",
                "price": 85,
                "category": "Coffee",
                "requires_bom": True,
            },
            {
                "name": "Americano",
                "price": 95,
                "category": "Coffee",
                "requires_bom": True,
            },
            {
                "name": "Cappuccino",
                "price": 120,
                "category": "Coffee",
                "requires_bom": True,
            },
            {"name": "Latte", "price": 120, "category": "Coffee", "requires_bom": True},
            {
                "name": "Macchiato",
                "price": 110,
                "category": "Coffee",
                "requires_bom": True,
            },
            {
                "name": "Flat White",
                "price": 130,
                "category": "Coffee",
                "requires_bom": True,
            },
            {
                "name": "Affogato",
                "price": 95,
                "category": "Coffee",
                "requires_bom": True,
            },
            # Drinks
            {
                "name": "Iced Coffee",
                "price": 110,
                "category": "Drinks",
                "requires_bom": True,
            },
            {
                "name": "Iced Tea",
                "price": 85,
                "category": "Drinks",
                "requires_bom": True,
            },
            {
                "name": "Fresh Lemonade",
                "price": 95,
                "category": "Drinks",
                "requires_bom": True,
            },
            {
                "name": "Mango Shake",
                "price": 120,
                "category": "Drinks",
                "requires_bom": True,
            },
            {
                "name": "Strawberry Smoothie",
                "price": 120,
                "category": "Drinks",
                "requires_bom": True,
            },
            {
                "name": "Mineral Water",
                "price": 30,
                "category": "Drinks",
                "requires_bom": False,
            },
            # Pastries & Sides
            {
                "name": "Croissant",
                "price": 75,
                "category": "Pastries",
                "requires_bom": True,
            },
            {
                "name": "Chocolate Chip Cookie",
                "price": 60,
                "category": "Pastries",
                "requires_bom": True,
            },
            {
                "name": "Blueberry Muffin",
                "price": 85,
                "category": "Pastries",
                "requires_bom": True,
            },
            {
                "name": "Cinnamon Roll",
                "price": 95,
                "category": "Pastries",
                "requires_bom": True,
            },
            {
                "name": "Cheese Danish",
                "price": 90,
                "category": "Pastries",
                "requires_bom": True,
            },
            # Desserts
            {
                "name": "Tiramisu",
                "price": 150,
                "category": "Desserts",
                "requires_bom": True,
            },
            {
                "name": "Chocolate Cake",
                "price": 140,
                "category": "Desserts",
                "requires_bom": True,
            },
            {
                "name": "Cheesecake",
                "price": 160,
                "category": "Desserts",
                "requires_bom": True,
            },
            {
                "name": "Brownies",
                "price": 120,
                "category": "Desserts",
                "requires_bom": True,
            },
            {
                "name": "Ice Cream",
                "price": 100,
                "category": "Desserts",
                "requires_bom": False,
            },
            # Sides
            {
                "name": "Sandwich",
                "price": 145,
                "category": "Sides",
                "requires_bom": True,
            },
            {"name": "Salad", "price": 130, "category": "Sides", "requires_bom": True},
            {
                "name": "Toast with Jam",
                "price": 70,
                "category": "Sides",
                "requires_bom": True,
            },
            {
                "name": "Bagel with Cream Cheese",
                "price": 95,
                "category": "Sides",
                "requires_bom": True,
            },
        ]

        # Create products
        for item in product_data:
            product, created = Product.objects.get_or_create(
                name=item["name"],
                defaults={
                    "price": Decimal(str(item["price"])),
                    "stock": random.randint(50, 200),
                    "category": item["category"],
                    "requires_bom": item["requires_bom"],
                    "threshold": 10,
                    "description": f"{item['name']} from Cafe Kantina",
                },
            )
            products.append(product)
            if created:
                self.stdout.write(f"  Product: {product.name}")

        # Ingredient definitions
        ingredient_data = [
            {"name": "Arabica Coffee Beans", "unit": "g", "min_stock": 500},
            {"name": "Robusta Coffee Beans", "unit": "g", "min_stock": 300},
            {"name": "Whole Milk", "unit": "ml", "min_stock": 1000},
            {"name": "Skimmed Milk", "unit": "ml", "min_stock": 500},
            {"name": "Cream", "unit": "ml", "min_stock": 200},
            {"name": "Butter", "unit": "g", "min_stock": 200},
            {"name": "Cheese", "unit": "g", "min_stock": 300},
            {"name": "All-purpose Flour", "unit": "g", "min_stock": 2000},
            {"name": "Sugar", "unit": "g", "min_stock": 1000},
            {"name": "Eggs", "unit": "pcs", "min_stock": 50},
            {"name": "Baking Powder", "unit": "g", "min_stock": 200},
            {"name": "Baking Soda", "unit": "g", "min_stock": 200},
            {"name": "Vanilla Extract", "unit": "ml", "min_stock": 100},
            {"name": "Chocolate", "unit": "g", "min_stock": 500},
            {"name": "Cocoa Powder", "unit": "g", "min_stock": 300},
            {"name": "Fresh Mango", "unit": "pcs", "min_stock": 20},
            {"name": "Strawberries", "unit": "g", "min_stock": 500},
            {"name": "Blueberries", "unit": "g", "min_stock": 300},
            {"name": "Lemon", "unit": "pcs", "min_stock": 15},
            {"name": "Cinnamon", "unit": "g", "min_stock": 100},
            {"name": "Vegetable Oil", "unit": "ml", "min_stock": 500},
            {"name": "Honey", "unit": "ml", "min_stock": 200},
            {"name": "Sugar Syrup", "unit": "ml", "min_stock": 300},
            {"name": "Water", "unit": "ml", "min_stock": 5000},
            {"name": "Salt", "unit": "g", "min_stock": 500},
            {"name": "Nuts Mix", "unit": "g", "min_stock": 300},
        ]

        # Create ingredients
        for item in ingredient_data:
            ingredient, created = Ingredient.objects.get_or_create(
                name=item["name"],
                defaults={
                    "unit": item["unit"],
                    "current_stock": Decimal(str(random.randint(500, 2000))),
                    "min_stock": Decimal(str(item["min_stock"])),
                    "variance_allowance": Decimal("10"),
                    "is_active": True,
                    "is_available": True,
                    "description": f"{item['name']} for Cafe Kantina",
                },
            )
            ingredients.append(ingredient)
            if created:
                self.stdout.write(f"  Ingredient: {ingredient.name}")

        return products, ingredients

    def _create_recipes(self, products, ingredients):
        """Create recipes (BOM) for products requiring them."""
        recipes = []

        recipe_mappings = {
            "Espresso": [("Arabica Coffee Beans", 25)],
            "Americano": [("Arabica Coffee Beans", 25), ("Water", 200)],
            "Cappuccino": [
                ("Arabica Coffee Beans", 25),
                ("Whole Milk", 150),
                ("Vanilla Extract", 2),
            ],
            "Latte": [("Arabica Coffee Beans", 25), ("Whole Milk", 200), ("Cream", 50)],
            "Macchiato": [("Arabica Coffee Beans", 30), ("Whole Milk", 50)],
            "Flat White": [("Arabica Coffee Beans", 30), ("Whole Milk", 200)],
            "Affogato": [("Arabica Coffee Beans", 30), ("Sugar", 20)],
            "Iced Coffee": [
                ("Robusta Coffee Beans", 25),
                ("Water", 250),
                ("Sugar Syrup", 30),
            ],
            "Iced Tea": [("Water", 250), ("Sugar Syrup", 40)],
            "Fresh Lemonade": [("Lemon", 2), ("Sugar", 40), ("Water", 300)],
            "Mango Shake": [
                ("Fresh Mango", 1),
                ("Whole Milk", 200),
                ("Sugar", 30),
                ("Vanilla Extract", 2),
            ],
            "Strawberry Smoothie": [
                ("Strawberries", 150),
                ("Whole Milk", 200),
                ("Honey", 30),
            ],
            "Croissant": [
                ("All-purpose Flour", 150),
                ("Butter", 80),
                ("Sugar", 20),
                ("Eggs", 1),
                ("Salt", 2),
            ],
            "Chocolate Chip Cookie": [
                ("All-purpose Flour", 100),
                ("Sugar", 80),
                ("Butter", 60),
                ("Eggs", 1),
                ("Chocolate", 100),
            ],
            "Blueberry Muffin": [
                ("All-purpose Flour", 120),
                ("Sugar", 100),
                ("Eggs", 2),
                ("Blueberries", 150),
                ("Butter", 50),
                ("Baking Powder", 5),
            ],
            "Cinnamon Roll": [
                ("All-purpose Flour", 150),
                ("Sugar", 80),
                ("Butter", 60),
                ("Cinnamon", 10),
                ("Eggs", 1),
                ("Vanilla Extract", 2),
            ],
            "Cheese Danish": [
                ("All-purpose Flour", 140),
                ("Cheese", 100),
                ("Butter", 70),
                ("Sugar", 30),
                ("Eggs", 1),
            ],
            "Tiramisu": [
                ("Cocoa Powder", 30),
                ("Eggs", 3),
                ("Sugar", 80),
                ("Cream", 200),
                ("Vanilla Extract", 3),
            ],
            "Chocolate Cake": [
                ("All-purpose Flour", 200),
                ("Cocoa Powder", 50),
                ("Sugar", 150),
                ("Eggs", 3),
                ("Butter", 100),
                ("Baking Powder", 8),
            ],
            "Cheesecake": [
                ("Cheese", 250),
                ("Sugar", 100),
                ("Eggs", 2),
                ("Cream", 150),
                ("All-purpose Flour", 50),
            ],
            "Brownies": [
                ("All-purpose Flour", 100),
                ("Chocolate", 150),
                ("Sugar", 120),
                ("Eggs", 2),
                ("Butter", 80),
                ("Cocoa Powder", 20),
            ],
            "Sandwich": [
                ("All-purpose Flour", 80),
                ("Cheese", 50),
                ("Butter", 30),
                ("Salt", 2),
            ],
            "Salad": [("Nuts Mix", 50)],
            "Toast with Jam": [("All-purpose Flour", 60), ("Butter", 20)],
            "Bagel with Cream Cheese": [
                ("All-purpose Flour", 100),
                ("Cream", 80),
                ("Salt", 2),
                ("Baking Powder", 3),
            ],
        }

        for product in products:
            if product.requires_bom and product.name in recipe_mappings:
                recipe, created = RecipeItem.objects.get_or_create(
                    product=product,
                    defaults={"created_by": User.objects.filter(role="ADMIN").first()},
                )

                if created:
                    for ingredient_name, quantity in recipe_mappings[product.name]:
                        try:
                            ingredient = Ingredient.objects.get(name=ingredient_name)
                            RecipeIngredient.objects.get_or_create(
                                recipe=recipe,
                                ingredient=ingredient,
                                defaults={"quantity": Decimal(str(quantity))},
                            )
                        except Ingredient.DoesNotExist:
                            pass

                    recipes.append(recipe)
                    self.stdout.write(f"  Recipe: {product.name}")

        return recipes

    def _generate_historical_orders(self, products, users):
        """Generate 30 days of historical orders with realistic patterns."""
        orders_data = {"orders": [], "daily_sales": {}, "daily_counts": {}}

        today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        cashiers = users["cashiers"]
        customer_first_names = [
            "Maria",
            "Juan",
            "Ana",
            "Carlos",
            "Rosa",
            "Miguel",
            "Sofia",
            "Pedro",
            "Lisa",
            "Ramon",
        ]
        customer_last_names = [
            "Santos",
            "Garcia",
            "Lopez",
            "Rodriguez",
            "Reyes",
            "Cruz",
            "Fernandez",
            "Martinez",
        ]

        total_orders_created = 0

        # Generate orders for the past 30 days
        for day_offset in range(30, 0, -1):
            order_date = today - timedelta(days=day_offset)
            is_weekend = order_date.weekday() >= 5
            base_orders = (
                random.randint(16, 23) if not is_weekend else random.randint(15, 22)
            )

            daily_total = Decimal("0")
            daily_count = 0

            # Generate multiple orders throughout the day
            for order_num in range(base_orders):
                hour = random.randint(8, 20)
                minute = random.randint(0, 59)
                order_time = order_date.replace(hour=hour, minute=minute)

                # Generate unique order number (max 20 chars) with UUID suffix to prevent duplicates
                unique_suffix = str(uuid.uuid4())[-4:].upper()
                order_number = f"ORD{order_time.strftime('%m%d')}{order_num + 1:02d}{unique_suffix}"

                status_rand = random.random()
                if status_rand < 0.80:
                    status = "FINISHED"
                elif status_rand < 0.90:
                    status = "CANCELLED"
                else:
                    status = "REFUNDED"

                use_table = random.choice([True, False])
                if use_table:
                    customer_name = f"Table {random.randint(1, 20)}"
                    table_number = str(random.randint(1, 20))
                else:
                    customer_name = f"{random.choice(customer_first_names)} {random.choice(customer_last_names)}"
                    table_number = ""

                order = Order.objects.create(
                    order_number=order_number,
                    customer_name=customer_name,
                    table_number=table_number,
                    status=status,
                    processed_by=random.choice(cashiers),
                    created_at=order_time,
                    updated_at=order_time,
                )

                item_count_rand = random.random()
                if item_count_rand < 0.60:
                    num_items = 1
                elif item_count_rand < 0.90:
                    num_items = 2
                else:
                    num_items = random.randint(3, 4)

                selected_products = random.sample(
                    products, min(num_items, len(products))
                )
                order_subtotal = Decimal("0")

                for product in selected_products:
                    quantity = (
                        random.randint(1, 2) if len(selected_products) == 1 else 1
                    )

                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        product_name=product.name,
                        product_price=product.price,
                        quantity=quantity,
                    )

                    item_total = product.price * quantity
                    order_subtotal += item_total

                order.total_amount = order_subtotal
                order.save()
                orders_data["orders"].append(order)

                if status == "FINISHED":
                    daily_total += order_subtotal
                    daily_count += 1

                total_orders_created += 1

            orders_data["daily_sales"][order_date.date()] = daily_total
            orders_data["daily_counts"][order_date.date()] = daily_count

        self.stdout.write(f"  Total orders created: {total_orders_created}")
        return orders_data

    def _create_payments_and_refunds(self, orders_data, users):
        """Create payment records and refunds for orders."""
        payment_methods = ["CASH", "GCASH", "ONLINE"]
        payment_weights = [0.60, 0.25, 0.15]

        cashiers = users["cashiers"]
        managers = [users["manager"]]

        payments_created = 0
        refunds_created = 0

        for order in orders_data["orders"]:
            payment_method = random.choices(payment_methods, weights=payment_weights)[0]
            payment_status = "COMPLETED" if order.status == "FINISHED" else "FAILED"

            payment = Payment.objects.create(
                order=order,
                method=payment_method,
                status=payment_status,
                amount=order.total_amount,
                processed_by=random.choice(cashiers),
            )
            payments_created += 1

            if order.status == "REFUNDED":
                refund_reasons = [
                    "Changed mind",
                    "Item quality issue",
                    "Customer request",
                    "Wrong order",
                    "Not satisfied",
                ]

                refund = Refund.objects.create(
                    order=order,
                    payment=payment,
                    amount=order.total_amount,
                    reason=random.choice(refund_reasons),
                    approved_by=random.choice(managers),
                )
                refunds_created += 1

        self.stdout.write(f"  Payments created: {payments_created}")
        self.stdout.write(f"  Refunds created: {refunds_created}")

    def _print_summary(self, users, products, ingredients, recipes, orders_data):
        """Print comprehensive summary of seeded data."""
        self.stdout.write(self.style.SUCCESS("\n" + "=" * 60))
        self.stdout.write(self.style.SUCCESS("DATA SEEDING SUMMARY"))
        self.stdout.write(self.style.SUCCESS("=" * 60))

        self.stdout.write(f"\nUsers:")
        self.stdout.write(f"  Total users: {len(users['cashiers']) + 2}")

        self.stdout.write(f"\nInventory:")
        self.stdout.write(f"  Products: {len(products)}")
        self.stdout.write(f"  Ingredients: {len(ingredients)}")
        self.stdout.write(f"  Recipes: {len(recipes)}")

        self.stdout.write(f"\nSales Data (30 Days):")
        self.stdout.write(f"  Total orders: {len(orders_data['orders'])}")

        total_finished_orders = sum(
            count for count in orders_data["daily_counts"].values()
        )
        total_revenue = sum(amount for amount in orders_data["daily_sales"].values())

        self.stdout.write(f"  Finished orders: {total_finished_orders}")
        self.stdout.write(f"  Total revenue: {total_revenue}")
        self.stdout.write(f"  Average orders/day: {total_finished_orders / 30:.1f}")

        payment_methods = {
            "CASH": Payment.objects.filter(method="CASH").count(),
            "GCASH": Payment.objects.filter(method="GCASH").count(),
            "ONLINE": Payment.objects.filter(method="ONLINE").count(),
        }

        self.stdout.write(f"\nPayment Methods:")
        for method, count in payment_methods.items():
            self.stdout.write(f"  {method}: {count}")

        self.stdout.write(f"\nHolt-Winters Readiness: Ready for forecasting")
        self.stdout.write("=" * 60 + "\n")
