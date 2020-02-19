from django.db import models


class Provider(models.Model):
    provider_url = models.URLField(unique=True)
    currency_key = models.CharField(max_length=10)
    rate_key = models.CharField(max_length=10)

    def __str__(self):
        return self.provider_url
