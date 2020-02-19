import json

from django.urls import reverse
from rest_framework.test import APITestCase

from exchange.models import Provider


class ProvidersApiTest(APITestCase):
    test_data = None

    def test_get_providers(self):
        response = self.client.get(reverse('provider'))
        self.assertEqual(response.status_code, 200)

    def test_post_providers(self):
        request_data = [
            {
                "provider_url": "http://www.mocky.io/v2/5d19ec692f00002c00fd7324",
                "currency_key": "code",
                "rate_key": "rate"
            }
        ]
        response = self.client.post(reverse('provider'), json.dumps(request_data), content_type='application/json')
        self.assertEqual(response.status_code, 201)

    def test_provider_delete(self):
        Provider.objects.create(id=0, provider_url='http://www.mocky.io/v2/5d19ec692f00002c00fd7324',
                                currency_key='code',
                                rate_key='rate')
        response = self.client.delete(reverse('provider-delete', args=[0]))

        self.assertEqual(response.status_code, 204)


class ExchangeApiTest(APITestCase):
    def setUp(self) -> None:
        Provider.objects.create(provider_url='http://www.mocky.io/v2/5d19ec692f00002c00fd7324', currency_key='code',
                                rate_key='rate')

    def test_exchange_get(self):
        response = self.client.get(reverse('exchange', args=['usd']))
        self.assertEqual(response.status_code, 200)

    def test_exchange_get_with_unvalid_type(self):
        response = self.client.get(reverse('exchange', args=['us53qef']))
        self.assertEqual(response.status_code, 400)

    def test_best_transformed_exchange(self):
        response = self.client.get(reverse('best-transformed-exchange', args=['usd']))
        self.assertEqual(response.status_code, 200)

    def test_best_transformed_exchange_with_unvalid_type(self):
        response = self.client.get(reverse('best-transformed-exchange', args=['wef']))
        self.assertEqual(response.status_code, 400)
