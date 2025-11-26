from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from decimal import Decimal
from sales_inventory_system.products.models import Product, Ingredient, RecipeItem, RecipeIngredient

User = get_user_model()


class Command(BaseCommand):
    help = 'Seeds the database with pizza products and ingredients'

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
        """Create all ingredients needed for the pizzas"""
        ingredients_data = [
            # Dough/Base
            {'name': 'Pizza dough (small)', 'unit': 'pcs', 'min_stock': 5},
            {'name': 'Pizza dough (medium)', 'unit': 'pcs', 'min_stock': 5},
            {'name': 'Pizza dough (large)', 'unit': 'pcs', 'min_stock': 5},

            # Sauces
            {'name': 'Tomato sauce', 'unit': 'ml', 'min_stock': 100},

            # Cheeses
            {'name': 'Mozzarella cheese', 'unit': 'g', 'min_stock': 200},
            {'name': 'Cheddar cheese', 'unit': 'g', 'min_stock': 150},
            {'name': 'Parmesan cheese', 'unit': 'g', 'min_stock': 100},
            {'name': 'Cream cheese', 'unit': 'g', 'min_stock': 50},

            # Meats
            {'name': 'Pepperoni', 'unit': 'g', 'min_stock': 100},
            {'name': 'Ham', 'unit': 'g', 'min_stock': 100},

            # Other toppings
            {'name': 'Pineapple tidbits', 'unit': 'g', 'min_stock': 50},
            {'name': 'Olive oil', 'unit': 'ml', 'min_stock': 50},
            {'name': 'Oregano', 'unit': 'g', 'min_stock': 20},
            {'name': 'Italian seasoning', 'unit': 'g', 'min_stock': 20},
            {'name': 'Basil', 'unit': 'g', 'min_stock': 10},
            {'name': 'Chili flakes', 'unit': 'g', 'min_stock': 10},
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
            # CHEESE PIZZA SERIES
            {
                'name': 'Small Cheese Pizza',
                'description': 'A compact classic topped with rich tomato sauce and a smooth layer of melted mozzarella. Perfect for a quick, satisfying cheesy bite.',
                'category': 'small',
                'price': Decimal('199.00'),
                'cooking_time': '10-12 mins',
                'cooking_style': 'Classic Baked',
                'bom': [
                    ('Pizza dough (small)', Decimal('1')),
                    ('Tomato sauce', Decimal('45')),
                    ('Mozzarella cheese', Decimal('80')),
                    ('Cheddar cheese', Decimal('20')),
                    ('Olive oil', Decimal('5')),
                    ('Oregano', Decimal('1')),
                ]
            },
            {
                'name': 'Medium Cheese Deluxe',
                'description': 'A richer, fuller cheese pizza baked on a stone surface for extra crispiness. Features mozzarella, cheddar, and parmesan for layered flavor.',
                'category': 'medium',
                'price': Decimal('299.00'),
                'cooking_time': '12-14 mins',
                'cooking_style': 'Stone-Baked',
                'bom': [
                    ('Pizza dough (medium)', Decimal('1')),
                    ('Tomato sauce', Decimal('60')),
                    ('Mozzarella cheese', Decimal('120')),
                    ('Cheddar cheese', Decimal('40')),
                    ('Parmesan cheese', Decimal('20')),
                    ('Olive oil', Decimal('5')),
                    ('Italian seasoning', Decimal('1')),
                ]
            },
            {
                'name': 'Large Four Cheese Supreme',
                'description': 'A bold, cheesy masterpiece blending mozzarella, parmesan, cheddar, and cream cheese. Brick-oven inspired baking produces a smoky, crisp crust with gooey cheese pull.',
                'category': 'large',
                'price': Decimal('399.00'),
                'cooking_time': '15-17 mins',
                'cooking_style': 'Brick Oven Style',
                'bom': [
                    ('Pizza dough (large)', Decimal('1')),
                    ('Tomato sauce', Decimal('90')),
                    ('Mozzarella cheese', Decimal('180')),
                    ('Parmesan cheese', Decimal('30')),
                    ('Cheddar cheese', Decimal('40')),
                    ('Cream cheese', Decimal('40')),
                    ('Olive oil', Decimal('15')),
                    ('Oregano', Decimal('1')),
                    ('Basil', Decimal('1')),
                ]
            },
            # PEPPERONI PIZZA SERIES
            {
                'name': 'Small Pepperoni Classic',
                'description': 'A simple but flavorful pizza topped with crisp pepperoni slices and melted mozzarella on a tomato base.',
                'category': 'small',
                'price': Decimal('229.00'),
                'cooking_time': '10-12 mins',
                'cooking_style': 'Classic Baked',
                'bom': [
                    ('Pizza dough (small)', Decimal('1')),
                    ('Tomato sauce', Decimal('45')),
                    ('Mozzarella cheese', Decimal('80')),
                    ('Pepperoni', Decimal('30')),
                    ('Olive oil', Decimal('5')),
                    ('Oregano', Decimal('1')),
                ]
            },
            {
                'name': 'Medium Pepperoni Crispy Edge',
                'description': 'A pan-style pizza with slightly fried edges for an extra crispy bite, topped generously with pepperoni and cheese.',
                'category': 'medium',
                'price': Decimal('329.00'),
                'cooking_time': '13-15 mins',
                'cooking_style': 'Pan-Fried Baked',
                'bom': [
                    ('Pizza dough (medium)', Decimal('1')),
                    ('Tomato sauce', Decimal('60')),
                    ('Mozzarella cheese', Decimal('120')),
                    ('Pepperoni', Decimal('45')),
                    ('Olive oil', Decimal('5')),
                    ('Italian seasoning', Decimal('1')),
                ]
            },
            {
                'name': 'Large Double Pepperoni Overload',
                'description': 'A feast for pepperoni lovers—double meat, double cheese, and a smoky brick-oven style bake.',
                'category': 'large',
                'price': Decimal('429.00'),
                'cooking_time': '15-17 mins',
                'cooking_style': 'Brick Oven',
                'bom': [
                    ('Pizza dough (large)', Decimal('1')),
                    ('Tomato sauce', Decimal('90')),
                    ('Mozzarella cheese', Decimal('180')),
                    ('Pepperoni', Decimal('75')),
                    ('Olive oil', Decimal('15')),
                    ('Chili flakes', Decimal('2')),
                ]
            },
            # HAWAIIAN PIZZA SERIES
            {
                'name': 'Small Hawaiian Sweetbite',
                'description': 'A sweet and savory combination of ham, pineapple, and mozzarella—perfect for bite-sized cravings.',
                'category': 'small',
                'price': Decimal('239.00'),
                'cooking_time': '10-12 mins',
                'cooking_style': 'Classic',
                'bom': [
                    ('Pizza dough (small)', Decimal('1')),
                    ('Tomato sauce', Decimal('45')),
                    ('Mozzarella cheese', Decimal('80')),
                    ('Ham', Decimal('40')),
                    ('Pineapple tidbits', Decimal('30')),
                    ('Olive oil', Decimal('5')),
                ]
            },
            {
                'name': 'Medium Hawaiian Classic',
                'description': 'A balanced Hawaiian pizza with the perfect blend of sweetness and savoriness on a soft hand-tossed crust.',
                'category': 'medium',
                'price': Decimal('349.00'),
                'cooking_time': '12-14 mins',
                'cooking_style': 'Hand-Tossed',
                'bom': [
                    ('Pizza dough (medium)', Decimal('1')),
                    ('Tomato sauce', Decimal('60')),
                    ('Mozzarella cheese', Decimal('120')),
                    ('Ham', Decimal('60')),
                    ('Pineapple tidbits', Decimal('40')),
                    ('Olive oil', Decimal('5')),
                ]
            },
            {
                'name': 'Large Hawaiian Premium',
                'description': 'A premium take on Hawaiian—ham, pineapple, mozzarella, and cheddar baked to smoky perfection.',
                'category': 'large',
                'price': Decimal('449.00'),
                'cooking_time': '15-17 mins',
                'cooking_style': 'Brick Oven Style',
                'bom': [
                    ('Pizza dough (large)', Decimal('1')),
                    ('Tomato sauce', Decimal('90')),
                    ('Mozzarella cheese', Decimal('180')),
                    ('Cheddar cheese', Decimal('20')),
                    ('Ham', Decimal('80')),
                    ('Pineapple tidbits', Decimal('60')),
                    ('Olive oil', Decimal('15')),
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
