from django.apps import AppConfig


class ProductsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "sales_inventory_system.products"

    def ready(self):
        """Register signals when app is ready"""
        import sales_inventory_system.products.signals  # noqa
