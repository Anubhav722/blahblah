

from django.apps import AppConfig


class AccountsConfig(AppConfig):
    name = 'jarvis.accounts'
    verbose_name = 'accounts app'

    def ready(self):
        # Importing all signal handles for accounts app
        from .signals import handlers
