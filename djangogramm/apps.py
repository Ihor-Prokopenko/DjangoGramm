from django.apps import AppConfig


class DjangogrammConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'djangogramm'

    def ready(self):
        import djangogramm.signals
        import djangogramm.fake_fill_db
