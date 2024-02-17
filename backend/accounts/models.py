from currencies.models import Currency
from django.db import models
from django.db.models import Sum
from django.db.utils import IntegrityError
from django.utils.translation import gettext_lazy as _
from users.models import User

from .utils import ofxutils, uuid


class AccountType(models.IntegerChoices):
    UNKNOWN = 1, _("Unknown")
    BANK = 2, _("Bank Account")
    CREDIT = 3, _("Credit Card")
    CASH = 4, _("Cash")


class Account(models.Model):
    user = models.ForeignKey(
        User,
        models.CASCADE,
        verbose_name="Owner of the account.",
    )
    currency = models.ForeignKey(
        Currency,
        models.PROTECT,
        verbose_name="Currency of the account.",
        blank=True,
    )
    name = models.CharField(
        max_length=128,
        verbose_name="Name of the account.",
    )

    account_type = models.IntegerField(choices=AccountType, default=AccountType.UNKNOWN)

    def __str__(self) -> str:
        return "{} ({})".format(self.name, self.currency.identifier)

    def get_balance(self):
        transactions = self.transaction_set.all()
        return transactions.aggregate(balance=Sum("value", default=0))["balance"]

    @classmethod
    def create_from_file(cls, user: User, filetype: str, content: str, **kwargs):
        """_summary_

        Args:
            user (User): _description_
            filename (str): _description_

        Raises:
            FileNotFoundError: _description_
            NotImplementedError: _description_

        Returns:
            _type_: _description_
        """
        if filetype == "ofx":
            account, transactions = cls.from_ofx_file(content, **kwargs)
        else:
            raise NotImplementedError(
                "File extension not supported: {}".format(filetype)
            )

        account.user = user
        account.save()
        for transaction in transactions:
            try:
                transaction.save()
            except IntegrityError:
                continue

        return account

    def update_from_file(self, filetype: str, content: str, **kwargs):
        """_summary_

        Args:
            user (User): _description_
            filename (str): _description_

        Raises:
            FileNotFoundError: _description_
            NotImplementedError: _description_

        Returns:
            _type_: _description_
        """
        if filetype == "ofx":
            transactions = self.transactions_from_ofx_file(content, **kwargs)
        else:
            raise NotImplementedError(
                "File extension not supported: {}".format(filetype)
            )

        written_transactions = []
        for transaction in transactions:
            try:
                transaction.save()
                written_transactions.append(transaction)
            except IntegrityError:
                continue

        return written_transactions

    def transactions_from_ofx_file(self, content: str, **kwarg):
        """_summary_

        Args:
            user (User): _description_
            filename (Path): _description_
        """
        data = ofxutils.OfxData.from_file(content)
        transactions = [
            Transaction.from_ofx_data(transaction, self)
            for transaction in data.transactions
        ]
        return transactions

    @classmethod
    def from_ofx_file(cls, content: str, **kwarg):
        """_summary_

        Args:
            user (User): _description_
            filename (Path): _description_
        """
        data = ofxutils.OfxData.from_file(content)
        account = cls.from_ofx_data(data.account, **kwarg)
        transactions = [
            Transaction.from_ofx_data(transaction, account)
            for transaction in data.transactions
        ]
        return account, transactions

    @classmethod
    def from_ofx_data(
        cls,
        data: dict,
        currency: Currency = Currency(identifier="USD"),
        name: str = None,
    ):
        """_summary_

        Args:
            user (User): _description_
            data (ofxutils.OfxData): _description_
            currency (str, optional): _description_. Defaults to "USD".
            name (str, optional): _description_. Defaults to None.

        Returns:
            Account: _description_
        """
        account = cls(
            currency=currency,
            name=name if name is not None else data["institution"],
            account_type=data["type"] + 1,
        )
        return account


class Transaction(models.Model):
    account = models.ForeignKey(
        Account,
        models.CASCADE,
        verbose_name="The account on which this transaction was operated.",
    )
    # category = models.ForeignKey(
    #     "categories.Category",
    #     models.RESTRICT,
    # )
    payee = models.CharField(max_length=128)
    memo = models.CharField(max_length=128)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    transaction_hash = models.UUIDField(editable=False, unique=True)

    def __str__(self) -> str:
        return "{} - {} ({} {})".format(
            self.date, self.payee, self.value, self.account.currency.symbol
        )

    def get_hash(self):
        content = str(self.account.id) + self.payee + str(self.value) + str(self.date)
        return uuid.create_uuid_from_string(content)

    def save(self, *args, **kwargs):
        self.transaction_hash = self.get_hash()
        super().save(*args, **kwargs)

    @classmethod
    def from_ofx_data(cls, data: dict, account: Account):
        """_summary_

        Args:
            data (dict): _description_
            account (Account | None, optional): _description_. Defaults to None.

        Returns:
            Transaction: _description_
        """
        transaction_value = data["amount"]

        if account.account_type == AccountType.CREDIT:
            if data["type"] == "credit":
                transaction_value = -transaction_value
        else:
            if data["type"] == "debit":
                transaction_value = -transaction_value

        transaction = cls(
            account=account,
            payee=data["payee"],
            memo=data["memo"],
            date=data["user_date"].date(),
            value=transaction_value,
        )
        return transaction
