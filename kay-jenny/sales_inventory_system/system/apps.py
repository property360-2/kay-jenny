from django.apps import AppConfig


class SystemConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "sales_inventory_system.system"
    verbose_name = "System Administration"

    def ready(self):
        """Import signals when app is ready"""
        import sales_inventory_system.system.signals
