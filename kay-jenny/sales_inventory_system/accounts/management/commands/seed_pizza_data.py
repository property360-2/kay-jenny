from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from decimal import Decimal
from sales_inventory_system.products.models import Product, Ingredient, RecipeItem, RecipeIngredient

User = get_user_model()


class Command(BaseCommand):
    help = 'Seeds the database with coffee products and ingredients'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing products and ingredients before seeding',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write("Clearing existing data...")
            Product.objects.all().delete()
            Ingredient.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("Data cleared"))

        # Create ingredients
        self.stdout.write("Creating ingredients...")
        ingredients = self._create_ingredients()
        self.stdout.write(self.style.SUCCESS(f"Created {len(ingredients)} ingredients"))

        # Create products and recipes
        self.stdout.write("Creating products and recipes...")
        products_count = self._create_products(ingredients)
        self.stdout.write(self.style.SUCCESS(f"Created {products_count} products with recipes"))

        self.stdout.write(self.style.SUCCESS("Seeding completed successfully!"))

    def _create_ingredients(self):
        """Create all ingredients needed for the coffees"""
        ingredients_data = [
            # Coffee Base
            {'name': 'Arabica beans (small)', 'unit': 'pcs', 'min_stock': 5},
            {'name': 'Arabica beans (medium)', 'unit': 'pcs', 'min_stock': 5},
            {'name': 'Arabica beans (large)', 'unit': 'pcs', 'min_stock': 5},

            # Coffee Types
            {'name': 'Espresso', 'unit': 'ml', 'min_stock': 100},

            # Milk & Cream
            {'name': 'Whole milk', 'unit': 'ml', 'min_stock': 200},
            {'name': 'Condensed milk', 'unit': 'ml', 'min_stock': 150},
            {'name': 'Evaporated milk', 'unit': 'ml', 'min_stock': 100},
            {'name': 'Whipped cream', 'unit': 'g', 'min_stock': 50},

            # Toppings & Add-ons
            {'name': 'Cocoa powder', 'unit': 'g', 'min_stock': 100},
            {'name': 'Cinnamon powder', 'unit': 'g', 'min_stock': 100},

            # Syrups & Flavors
            {'name': 'Caramel syrup', 'unit': 'ml', 'min_stock': 50},
            {'name': 'Vanilla syrup', 'unit': 'ml', 'min_stock': 50},
            {'name': 'Hazelnut syrup', 'unit': 'ml', 'min_stock': 20},
            {'name': 'Chocolate syrup', 'unit': 'ml', 'min_stock': 20},
            {'name': 'Sugar', 'unit': 'g', 'min_stock': 10},
            {'name': 'Coffee salt', 'unit': 'g', 'min_stock': 10},
        ]

        ingredients = {}
        for ing_data in ingredients_data:
            ingredient, created = Ingredient.objects.get_or_create(
                name=ing_data['name'],
                defaults={
                    'unit': ing_data['unit'],
                    'min_stock': Decimal(ing_data['min_stock']),
                    'current_stock': Decimal(ing_data['min_stock'] * 3),  # Stock at 3x minimum
                    'is_active': True,
                    'is_available': True,
                    'variance_allowance': Decimal('5'),  # 5% allowance
                }
            )
            ingredients[ing_data['name']] = ingredient
            if created:
                self.stdout.write(f"  Created ingredient: {ing_data['name']}")
            else:
                self.stdout.write(f"  Ingredient already exists: {ing_data['name']}")

        return ingredients

    def _create_products(self, ingredients):
        """Create all pizza products with their recipes"""
        user = User.objects.first()  # Use first available user or create one
        if not user:
            user = User.objects.create_superuser('admin', 'admin@example.com', 'admin')
            self.stdout.write(f"  Created default admin user")

        products_data = [
            # CLASSIC COFFEE SERIES
            {
                'name': 'Small Arabica Brew',
                'description': 'A classic small coffee made with premium Arabica beans, smooth and aromatic. Perfect for a quick coffee break.',
                'category': 'small',
                'price': Decimal('99.00'),
                'cooking_time': '3-5 mins',
                'cooking_style': 'Brewed',
                'bom': [
                    ('Arabica beans (small)', Decimal('1')),
                    ('Espresso', Decimal('45')),
                    ('Whole milk', Decimal('80')),
                    ('Condensed milk', Decimal('20')),
                    ('Sugar', Decimal('5')),
                    ('Cinnamon powder', Decimal('1')),
                ]
            },
            {
                'name': 'Medium Arabica Premium',
                'description': 'A richer, fuller Arabica coffee with a smooth crema. Features whole milk and condensed milk for a creamy texture.',
                'category': 'medium',
                'price': Decimal('129.00'),
                'cooking_time': '4-6 mins',
                'cooking_style': 'Espresso-Based',
                'bom': [
                    ('Arabica beans (medium)', Decimal('1')),
                    ('Espresso', Decimal('60')),
                    ('Whole milk', Decimal('120')),
                    ('Condensed milk', Decimal('40')),
                    ('Evaporated milk', Decimal('20')),
                    ('Sugar', Decimal('5')),
                    ('Chocolate syrup', Decimal('1')),
                ]
            },
            {
                'name': 'Large Arabica Supreme',
                'description': 'A bold, rich coffee masterpiece blending Arabica with multiple milk types and premium toppings. Topped with whipped cream.',
                'category': 'large',
                'price': Decimal('159.00'),
                'cooking_time': '5-7 mins',
                'cooking_style': 'Specialty Brew',
                'bom': [
                    ('Arabica beans (large)', Decimal('1')),
                    ('Espresso', Decimal('90')),
                    ('Whole milk', Decimal('180')),
                    ('Evaporated milk', Decimal('30')),
                    ('Condensed milk', Decimal('40')),
                    ('Whipped cream', Decimal('40')),
                    ('Sugar', Decimal('15')),
                    ('Cinnamon powder', Decimal('1')),
                    ('Cocoa powder', Decimal('1')),
                ]
            },
            # CARAMEL COFFEE SERIES
            {
                'name': 'Small Caramel Latte',
                'description': 'A sweet and smooth small coffee with caramel syrup and velvety milk foam. Perfect for caramel lovers.',
                'category': 'small',
                'price': Decimal('119.00'),
                'cooking_time': '4-6 mins',
                'cooking_style': 'Latte',
                'bom': [
                    ('Arabica beans (small)', Decimal('1')),
                    ('Espresso', Decimal('45')),
                    ('Whole milk', Decimal('80')),
                    ('Caramel syrup', Decimal('30')),
                    ('Sugar', Decimal('5')),
                    ('Cinnamon powder', Decimal('1')),
                ]
            },
            {
                'name': 'Medium Caramel Deluxe',
                'description': 'A pan-style coffee with rich caramel flavor, topped generously with whipped cream and caramel drizzle.',
                'category': 'medium',
                'price': Decimal('149.00'),
                'cooking_time': '5-7 mins',
                'cooking_style': 'Caramel Macchiato',
                'bom': [
                    ('Arabica beans (medium)', Decimal('1')),
                    ('Espresso', Decimal('60')),
                    ('Whole milk', Decimal('120')),
                    ('Caramel syrup', Decimal('45')),
                    ('Sugar', Decimal('5')),
                    ('Vanilla syrup', Decimal('1')),
                ]
            },
            {
                'name': 'Large Caramel Overload',
                'description': 'A feast for caramel lovers—rich espresso, multiple milks, caramel syrup, and whipped cream with caramel sauce.',
                'category': 'large',
                'price': Decimal('189.00'),
                'cooking_time': '6-8 mins',
                'cooking_style': 'Specialty Caramel',
                'bom': [
                    ('Arabica beans (large)', Decimal('1')),
                    ('Espresso', Decimal('90')),
                    ('Whole milk', Decimal('180')),
                    ('Caramel syrup', Decimal('75')),
                    ('Sugar', Decimal('15')),
                    ('Whipped cream', Decimal('30')),
                ]
            },
            # CHOCOLATE COFFEE SERIES
            {
                'name': 'Small Mocha Sweetbite',
                'description': 'A sweet chocolate and coffee combination with cocoa powder and condensed milk—perfect for bite-sized indulgence.',
                'category': 'small',
                'price': Decimal('109.00'),
                'cooking_time': '4-5 mins',
                'cooking_style': 'Mocha',
                'bom': [
                    ('Arabica beans (small)', Decimal('1')),
                    ('Espresso', Decimal('45')),
                    ('Whole milk', Decimal('80')),
                    ('Cocoa powder', Decimal('40')),
                    ('Chocolate syrup', Decimal('30')),
                    ('Sugar', Decimal('5')),
                ]
            },
            {
                'name': 'Medium Mocha Classic',
                'description': 'A balanced mocha coffee with the perfect blend of chocolate richness and coffee depth on a creamy base.',
                'category': 'medium',
                'price': Decimal('139.00'),
                'cooking_time': '5-7 mins',
                'cooking_style': 'Hot Mocha',
                'bom': [
                    ('Arabica beans (medium)', Decimal('1')),
                    ('Espresso', Decimal('60')),
                    ('Whole milk', Decimal('120')),
                    ('Cocoa powder', Decimal('60')),
                    ('Chocolate syrup', Decimal('40')),
                    ('Sugar', Decimal('5')),
                ]
            },
            {
                'name': 'Large Mocha Premium',
                'description': 'A premium mocha masterpiece—rich espresso, chocolate flavors, multiple milks, and whipped cream topping.',
                'category': 'large',
                'price': Decimal('179.00'),
                'cooking_time': '6-8 mins',
                'cooking_style': 'Premium Mocha',
                'bom': [
                    ('Arabica beans (large)', Decimal('1')),
                    ('Espresso', Decimal('90')),
                    ('Whole milk', Decimal('180')),
                    ('Condensed milk', Decimal('20')),
                    ('Cocoa powder', Decimal('80')),
                    ('Chocolate syrup', Decimal('60')),
                    ('Whipped cream', Decimal('30')),
                ]
            },
        ]

        products_count = 0
        for product_data in products_data:
            bom = product_data.pop('bom')
            cooking_time = product_data.pop('cooking_time')
            cooking_style = product_data.pop('cooking_style')

            product, created = Product.objects.get_or_create(
                name=product_data['name'],
                defaults={
                    'description': product_data['description'],
                    'category': product_data['category'],
                    'price': product_data['price'],
                    'stock': 0,
                    'threshold': 2,
                    'requires_bom': True,
                    'is_archived': False,
                }
            )

            if created:
                self.stdout.write(f"  Created product: {product.name}")
                products_count += 1
            else:
                self.stdout.write(f"  Product already exists: {product.name}")

            # Create recipe if it doesn't exist
            recipe, recipe_created = RecipeItem.objects.get_or_create(
                product=product,
                defaults={'created_by': user}
            )

            if recipe_created:
                # Add ingredients to recipe
                for ingredient_name, quantity in bom:
                    if ingredient_name in ingredients:
                        RecipeIngredient.objects.get_or_create(
                            recipe=recipe,
                            ingredient=ingredients[ingredient_name],
                            defaults={'quantity': quantity}
                        )
                self.stdout.write(f"    Created recipe with {len(bom)} ingredients")
            else:
                self.stdout.write(f"    Recipe already exists for {product.name}")

        return products_count
