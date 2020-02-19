from django.urls import path

from exchange.views import ExchangeView, ProviderView, ProviderDeleteView, BestTransformedExchange

urlpatterns = [
    path('exchange/<slug:type>', ExchangeView.as_view(), name='exchange'),
    path('best-transformed-exchange/<slug:type>', BestTransformedExchange.as_view(), name='best-transformed-exchange'),
    path('provider', ProviderView.as_view(), name='provider'),
    path('provider/<int:pk>', ProviderDeleteView.as_view(), name='provider-delete'),
]
