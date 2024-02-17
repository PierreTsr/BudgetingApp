from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from users.models import User

from .models import Account, Transaction


class AccountSerializer(serializers.ModelSerializer):
    account_type = serializers.CharField(source="get_account_type_display")
    balance = serializers.ReadOnlyField(source="get_balance")

    class Meta:
        model = Account
        fields = ("id", "user", "name", "currency", "account_type", "balance")
        read_only_fields = ("user", "balance")


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = "__all__"


class OfxSerializer(serializers.Serializer):
    content = serializers.CharField()
    user = serializers.IntegerField()

    def validate_user(self, value):
        try:
            user = User.objects.get(pk=int(value))
            return user
        except ObjectDoesNotExist:
            raise serializers.ValidationError("The provided user does not exists")
