from django.apps import AppConfig


class DeploymentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'deployments'

    def ready(self) -> None:
        from . import signals
