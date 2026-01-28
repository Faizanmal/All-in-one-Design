from django.apps import AppConfig

class CommentingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'commenting'
    verbose_name = 'Enhanced Commenting & Review'
    
    def ready(self):
        import commenting.signals  # noqa
