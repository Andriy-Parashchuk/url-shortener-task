from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    # Change 'users' to the full dotted path 'apps.users'
    name = 'apps.users'
