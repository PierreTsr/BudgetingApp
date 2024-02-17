from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response

from .models import Account, Transaction
from .serializers import AccountSerializer, OfxSerializer, TransactionSerializer


class AccountView(viewsets.ModelViewSet):
    serializer_class = AccountSerializer
    queryset = Account.objects.all()

    @action(detail=False, methods=["post"])
    def create_from_ofx(self, request) -> Response:
        serializer = OfxSerializer(data=request.data)
        if serializer.is_valid():
            content = serializer.validated_data["content"]
            user = serializer.validated_data["user"]
            account = Account.create_from_file(user, "ofx", content)
            return Response(AccountSerializer(account).data)
        else:
            return Response(serializer.errors)

    @action(detail=True, methods=["post"])
    def update_from_ofx(self, request, pk=None) -> Response:
        account = self.get_object()
        serializer = OfxSerializer(data=request.data)
        if serializer.is_valid():
            if serializer.validated_data["user"].id == account.user.id:
                content = serializer.validated_data["content"]
                transactions = account.update_from_file("ofx", content)
                return Response(TransactionSerializer(transactions, many=True).data)
            else:
                return Response(
                    {"user": "The provided user does not match the targeted account."}
                )
        else:
            return Response(serializer.errors)


class TransactionView(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    queryset = Transaction.objects.all()
    filter_backends = [OrderingFilter, DjangoFilterBackend]
    filterset_fields = ("account",)
    ordering_fields = ("date", "value", "payee")
