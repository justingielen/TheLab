from django.apps import AppConfig

class TheLabConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'thelab'

    # import signal handlers here to ensure they are connected when the app is ready
    def ready(self):
        import thelab.signals