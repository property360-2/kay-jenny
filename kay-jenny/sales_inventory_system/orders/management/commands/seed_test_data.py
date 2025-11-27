from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from accounts.models import User
from products.models import Product, Ingredient
from orders.models import Order, OrderItem, Payment


class Command(BaseCommand):
    help = "Seed comprehensive test data (users, products, ingredients, orders, payments)"

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("Seeding Cafe Cantina test data..."))

        admin, cashier = self._seed_users()
        ingredients = self._seed_ingredients()
        products = self._seed_products()
        self._seed_orders(products, admin, cashier)

        self.stdout.write(self.style.SUCCESS("✅ Seeding complete"))

    def _seed_users(self):
        admin, _ = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@cafecantina.com",
                "first_name": "Ava",
                "last_name": "Lopez",
                "role": "ADMIN",
            },
        )
        admin.set_password("admin123")
        admin.save()

        cashier, _ = User.objects.get_or_create(
            username="cashier",
            defaults={
                "email": "cashier@cafecantina.com",
                "first_name": "Ben",
                "last_name": "Reyes",
                "role": "CASHIER",
            },
        )
        cashier.set_password("cashier123")
        cashier.save()

        self.stdout.write(f"- Users ensured: admin/admin123, cashier/cashier123")
        return admin, cashier

    def _seed_ingredients(self):
        base_ingredients = [
            ("Espresso Beans", "g", 5000, 1000),
            ("Milk", "ml", 8000, 2000),
            ("Croissant Dough", "pcs", 120, 30),
            ("Cheddar Cheese", "g", 3000, 800),
            ("Ham", "g", 2500, 600),
        ]
        objs = []
        for name, unit, stock, min_stock in base_ingredients:
            ing, _ = Ingredient.objects.get_or_create(
                name=name,
                defaults={
                    "unit": unit,
                    "current_stock": Decimal(stock),
                    "min_stock": Decimal(min_stock),
                    "variance_allowance": Decimal("5.0"),
                },
            )
            objs.append(ing)
        self.stdout.write(f"- Ingredients ensured: {len(objs)}")
        return objs

    def _seed_products(self):
        product_data = [
            ("Cappuccino", "Coffee", "Classic cappuccino", "160.00", 60, 15),
            ("Flat White", "Coffee", "Smooth espresso with milk", "180.00", 50, 12),
            ("Iced Latte", "Coffee", "Chilled espresso and milk", "170.00", 70, 15),
            ("Chocolate Croissant", "Pastry", "Buttery croissant with chocolate", "120.00", 40, 10),
            ("Almond Croissant", "Pastry", "Filled with almond cream", "130.00", 35, 8),
            ("Ham & Cheese Sandwich", "Sandwich", "Toasted ham and cheddar", "190.00", 45, 12),
            ("Turkey Club", "Sandwich", "Turkey with greens", "210.00", 30, 10),
            ("Cold Brew", "Drink", "Slow steeped coffee", "150.00", 80, 20),
        ]

        objs = []
        for name, category, desc, price, stock, threshold in product_data:
            prod, _ = Product.objects.get_or_create(
                name=name,
                defaults={
                    "description": desc,
                    "price": Decimal(price),
                    "stock": stock,
                    "threshold": threshold,
                    "category": category,
                    "requires_bom": False,
                    "is_archived": False,
                },
            )
            objs.append(prod)
        self.stdout.write(f"- Products ensured: {len(objs)}")
        return objs

    def _seed_orders(self, products, admin, cashier):
        if not products:
            self.stdout.write(self.style.WARNING("No products available to create orders."))
            return

        Order.objects.all().delete()
        Payment.objects.all().delete()
        OrderItem.objects.all().delete()

        now = timezone.now()
        sample_orders = [
            ("Alice Santos", "PENDING", "CASH", [("Cappuccino", 2), ("Chocolate Croissant", 1)]),
            ("Brian Cruz", "IN_PROGRESS", "CASH", [("Flat White", 1), ("Ham & Cheese Sandwich", 1)]),
            ("Cara Lim", "FINISHED", "CASH", [("Cold Brew", 2), ("Almond Croissant", 2)]),
            ("Diego Tan", "FINISHED", "ONLINE_DEMO", [("Iced Latte", 2), ("Turkey Club", 1)]),
            ("Ella Reyes", "FINISHED", "ONLINE_DEMO", [("Cappuccino", 1), ("Chocolate Croissant", 2)]),
        ]

        name_to_product = {p.name: p for p in products}
        created = 0
        for idx, (customer, status, pay_method, items) in enumerate(sample_orders):
            order = Order.objects.create(
                customer_name=customer,
                table_number=f"T{idx+1:02d}",
                status=status,
                notes="Test order",
                processed_by=cashier if status != "PENDING" else None,
                created_at=now - timezone.timedelta(hours=idx),
            )

            total = Decimal("0.00")
            for prod_name, qty in items:
                product = name_to_product.get(prod_name)
                if not product:
                    continue
                item = OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=qty,
                    product_name=product.name,
                    product_price=product.price,
                )
                total += item.subtotal

            order.total_amount = total
            order.save()

            Payment.objects.create(
                order=order,
                method=pay_method,
                status="COMPLETED" if status != "PENDING" else "PENDING",
                amount=total,
                processed_by=cashier if status != "PENDING" else None,
            )
            created += 1

        self.stdout.write(f"- Orders created: {created}")
