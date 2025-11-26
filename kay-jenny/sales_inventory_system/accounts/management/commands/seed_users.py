from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    help = "Create baseline admin and cashier accounts (idempotent)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset-passwords",
            action="store_true",
            help="Reset passwords for existing seeded users.",
        )

    def handle(self, *args, **options):
        User = get_user_model()
        reset_passwords = options["reset_passwords"]

        seed_users = [
            {
                "username": "admin",
                "email": "admin@fjcpizza.com",
                "password": "admin123",
                "first_name": "System",
                "last_name": "Admin",
                "phone": "+63 900 000 0000",
                "role": "ADMIN",
                "is_staff": True,
                "is_superuser": True,
                "is_active": True,
            },
            {
                "username": "cashier",
                "email": "cashier@fjcpizza.com",
                "password": "cashier123",
                "first_name": "John",
                "last_name": "Doe",
                "phone": "+63 917 123 4567",
                "role": "CASHIER",
                "is_staff": True,
                "is_superuser": False,
                "is_active": True,
            },
            {
                "username": "maria",
                "email": "maria@fjcpizza.com",
                "password": "maria123",
                "first_name": "Maria",
                "last_name": "Santos",
                "phone": "+63 918 234 5678",
                "role": "CASHIER",
                "is_staff": True,
                "is_superuser": False,
                "is_active": True,
            },
            {
                "username": "jose",
                "email": "jose@fjcpizza.com",
                "password": "jose123",
                "first_name": "Jose",
                "last_name": "Reyes",
                "phone": "+63 919 345 6789",
                "role": "CASHIER",
                "is_staff": True,
                "is_superuser": False,
                "is_active": True,
            },
        ]

        created_count = 0
        updated_count = 0

        with transaction.atomic():
            for user_data in seed_users:
                username = user_data["username"]
                password = user_data["password"]
                defaults = {k: v for k, v in user_data.items() if k != "password"}

                user, created = User.objects.get_or_create(
                    username=username, defaults=defaults
                )

                if created:
                    user.set_password(password)
                    user.save()
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f"Created user '{username}' ({user.role})")
                    )
                    continue

                # Update key fields if they drift from defaults
                dirty = False
                for field, value in defaults.items():
                    if getattr(user, field) != value:
                        setattr(user, field, value)
                        dirty = True

                if reset_passwords:
                    user.set_password(password)
                    dirty = True

                if dirty:
                    user.save()
                    updated_count += 1
                    self.stdout.write(
                        self.style.WARNING(
                            f"Updated user '{username}' (fields/password refreshed)"
                        )
                    )
                else:
                    self.stdout.write(f"User '{username}' already up to date")

        self.stdout.write(
            self.style.SUCCESS(
                f"User seeding complete. Created: {created_count}, Updated: {updated_count}"
            )
        )
