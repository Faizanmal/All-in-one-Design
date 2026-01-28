from django.apps import AppConfig


class SlackTeamsIntegrationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'slack_teams_integration'
    verbose_name = 'Slack & Teams Integration'
    
    def ready(self):
        import slack_teams_integration.signals  # noqa
