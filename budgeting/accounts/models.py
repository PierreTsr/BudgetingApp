from pathlib import Path

from currencies.models import Currency
from django.db import models
from users.models import User

from .utils import ofxutils

AccountType = models.IntegerChoices("AccountType", "UNKNOWN BANK CREDIT CASH")


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

    @classmethod
    def create_from_file(cls, user: User, filename: str, **kwargs):
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
        filename = Path(filename)
        if not filename.exists():
            raise FileNotFoundError(
                "Provided file does not exist: {}".format(str(filename))
            )

        if filename.suffix == ".ofx":
            account, transactions = cls.from_ofx_file(user, filename, **kwargs)
        else:
            raise NotImplementedError(
                "File extension not supported: {}".format(filename.suffix)
            )

        account.save()
        for transaction in transactions:
            transaction.save()

        return account

    @classmethod
    def from_ofx_file(cls, user: User, filename: Path, **kwarg):
        """_summary_

        Args:
            user (User): _description_
            filename (Path): _description_
        """
        data = ofxutils.OfxData.from_file(filename)
        account = cls.from_ofx_data(user, data.account, **kwarg)
        transactions = [
            Transaction.from_ofx_data(transaction, account)
            for transaction in data.transactions
        ]
        return account, transactions

    @classmethod
    def from_ofx_data(
        cls,
        user: User,
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
            user=user,
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
    payee = models.CharField(max_length=256)
    memo = models.CharField(max_length=256)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()

    TransactionType = models.IntegerChoices("TransactionType", "DEBIT CREDIT")
    transaction_type = models.IntegerField(choices=TransactionType)

    def __str__(self) -> str:
        return "{} - {} ({} {})".format(
            self.date, self.payee, self.value, self.account.currency.symbol
        )

    @classmethod
    def from_ofx_data(cls, data: dict, account: Account):
        """_summary_

        Args:
            data (dict): _description_
            account (Account | None, optional): _description_. Defaults to None.

        Returns:
            Transaction: _description_
        """
        transaction_type = data["type"]
        transaction_value = data["amount"]

        if transaction_type == "debit":
            transaction_type = 0
            transaction_value = -transaction_value
        elif transaction_type == "credit":
            transaction_type = 1
        else:
            raise NotImplementedError(
                "Transaction type not supported: {}.".format(transaction_type)
            )

        if account.account_type == AccountType.CREDIT:
            transaction_value = -transaction_value

        transaction = cls(
            account=account,
            payee=data["payee"],
            memo=data["memo"],
            date=data["user_date"],
            value=transaction_value,
            transaction_type=transaction_type,
        )
        return transaction
