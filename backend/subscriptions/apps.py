from django.apps import AppConfig


class SubscriptionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'subscriptions'
    
    def ready(self):
        """Import signals when app is ready"""
        try:
            import subscriptions.signals  # noqa
        except ImportError:
            pass
