from django.apps import AppConfig


class UserConfig(AppConfig):
    name = 'django_apps.user'

    def ready(self):
        import django_apps.user.signals
