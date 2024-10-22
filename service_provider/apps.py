from django.apps import AppConfig


class ServiceProviderConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'service_provider'
    def ready(self):
        import service_provider.signals  # Import signals to activate
