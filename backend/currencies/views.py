from rest_framework import viewsets

from .models import Currency
from .serializers import CurrencySerializer


class CurrencyView(viewsets.ModelViewSet):
    serializer_class = CurrencySerializer
    queryset = Currency.objects.all()
