import json

from django.db.models.signals import post_save, post_delete

from common.redis_util import save_to_redis, delete_from_redis
from exchange import settings
from exchange.models import Provider
import sys



def refresh_provider_cache(sender, **kwargs):
    provider_urls = {}
    for p in Provider.objects.all():
        provider_urls[p.id] = {'provider_url': p.provider_url, 'rate_key': p.rate_key, 'currency_key': p.currency_key}
    if len(provider_urls) > 0:
        save_to_redis(settings.REDIS_KEY_PROVIDER, json.dumps(provider_urls), None)
    else:
        delete_from_redis(settings.REDIS_KEY_PROVIDER)


if not 'test' in sys.argv:
    post_save.connect(refresh_provider_cache, sender=Provider,)
    post_delete.connect(refresh_provider_cache, sender=Provider)
