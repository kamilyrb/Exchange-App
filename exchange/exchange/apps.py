from __future__ import unicode_literals

from django.apps import AppConfig


class ExchangeConfig(AppConfig):
    name = 'exchange'

    def ready(self):
        import exchange.signals