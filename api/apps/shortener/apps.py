import os

from django.apps import AppConfig
import threading


class ShortenerConfig(AppConfig):
    name = 'apps.shortener'

    def ready(self):
        if os.environ.get("RUN_MAIN") != "true":
            return

        from .subscriber import listen

        thread = threading.Thread(
            target=listen,
            daemon=True
        )
        print("SUBSCRIBER STARTED")

        thread.start()
