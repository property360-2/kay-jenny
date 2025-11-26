"""
Management command to expire pending orders that are older than 1 hour
Run with: python manage.py expire_pending_orders
"""
from django.core.management.base import BaseCommand
from sales_inventory_system.orders.models import Order


class Command(BaseCommand):
    help = 'Expire pending orders that have been pending for more than 1 hour'

    def handle(self, *args, **options):
        expired_count = Order.expire_old_pending_orders()

        if expired_count > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully expired {expired_count} pending order(s)'
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING('No pending orders to expire')
            )
