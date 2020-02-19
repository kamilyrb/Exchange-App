import requests
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import status
from rest_framework.generics import ListCreateAPIView, DestroyAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from common.redis_util import save_to_redis, get_from_redis, get_from_redis_as_json
from exchange import settings
from exchange.enums import CurrencyTypes
from exchange.models import Provider
from exchange.serializers import ProviderSerializer


class ExchangeView(APIView):
    @method_decorator(cache_page(60 * 10))  # cache views 10minutes
    def get(self, request, **kwargs):
        currency = kwargs.get('type')
        if currency not in [CurrencyTypes.EUR.value, CurrencyTypes.USD.value, CurrencyTypes.GBP.value]:
            return Response({'message': 'currency type is invalid'}, status=status.HTTP_400_BAD_REQUEST)

        providers = get_from_redis_as_json(settings.REDIS_KEY_PROVIDER)
        if providers:
            currencies_list = get_provider_currencies(providers)
            min_currency = min(item[currency] for item in currencies_list)
            set_best_transform_is_valid(currency, min_currency)
            return Response({'result': min_currency})

        else:  # Any provider has been setted yet
            return Response({'message': 'There is no provider.Please add a provider before.'},
                            status=status.HTTP_400_BAD_REQUEST)


def get_provider_currencies(providers: dict) -> list:
    '''
    Get currencies list from providers based on their currency and rate keys. Because each provider can have
    different keys for currency and rate fields.
    :param providers: Provider dicts that retrieved data from. Dict contains 'provider_url','currency_key','rate_key'
    :return: currencies list like this format -> [{'usd':2.4,'eur':2.6,'gbp':4.3},....]
    '''
    currencies_list = []
    for id in providers:  # loop in providers that retrieved from redis
        provider = providers[id]
        response = requests.get(url=provider['provider_url'])
        if response.status_code == 200:
            provider_currency_data = {}
            for cr in response.json():  # loop in provider currencies
                provider_currency_data[cr[provider['currency_key']]] = float(cr[provider['rate_key']])
            currencies_list.append(provider_currency_data)
    return currencies_list


def set_best_transform_is_valid(currency_type: str, value: float):
    '''
    This method retrieved data from redis and compare value parameter.If value parameter greater than redis value or
    redis has not key, value is written to redis.
    :param currency_type: it can be one of  ['eur','usd','gbp']
    :param value: currency value as float
    :return:
    '''
    redis_key = '{}-{}'.format(settings.REDIS_KEY_BEST_TRANSFORM, currency_type)
    best_transform = get_from_redis(redis_key)
    if best_transform and float(best_transform) > value:
        return
    save_to_redis(redis_key, str(value), settings.REDIS_TIMEOUT_BEST_TRANSFORMS)


class BestTransformedExchange(APIView):
    def get(self, request, **kwargs):
        currency = kwargs.get('type')
        if currency not in [CurrencyTypes.EUR.value, CurrencyTypes.USD.value, CurrencyTypes.GBP.value]:
            return Response({'message': 'currency type is invalid'}, status=status.HTTP_400_BAD_REQUEST)
        redis_key = '{}-{}'.format(settings.REDIS_KEY_BEST_TRANSFORM, currency)
        best_transformed = get_from_redis(redis_key)
        result = {'result': float(best_transformed)} if best_transformed else {'message': 'No transformation has been '
                                                                                          'made in the last 24 hours'}
        return Response(result)


class ProviderView(ListCreateAPIView):
    queryset = Provider.objects.all()
    serializer_class = ProviderSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ProviderDeleteView(DestroyAPIView):
    queryset = Provider.objects.all()
