from django.apps import AppConfig


class VectorEditingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'vector_editing'
    verbose_name = 'Advanced Vector Editing'
    
    def ready(self):
        # Import signals when app is ready
        pass
