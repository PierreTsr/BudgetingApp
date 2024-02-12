import re
from io import StringIO
from pathlib import Path

from ofxparse import OfxParser

start_pattern = re.compile(r"^.*<OFX>", flags=re.DOTALL)
clean_payee = re.compile(r"\s{2,}")


class OfxData(object):
    def __init__(self, account: dict, transactions: list) -> None:
        self.account = account
        self.transactions = transactions

    def __str__(self) -> str:
        return str(self.__dict__)

    @classmethod
    def from_file(cls, filename: Path):
        try:
            with open(filename) as file:
                content = file.read()
            content = re.sub(start_pattern, "<OFX>", content)
            ofx = OfxParser.parse(StringIO(content))

        except ValueError:
            pass

        transaction_attr = ["type", "payee", "user_date", "amount", "memo"]

        account = {}
        transactions = []

        if hasattr(ofx.account, "type"):
            account["type"] = ofx.account.type
        if hasattr(ofx.account, "institution"):
            account["institution"] = ofx.account.institution.organization

        for transaction_ofx in ofx.account.statement.transactions:
            transaction = {}
            for attr in transaction_attr:
                if hasattr(transaction_ofx, attr):
                    transaction[attr] = getattr(transaction_ofx, attr)
                else:
                    continue
                if attr == "payee":
                    transaction[attr] = re.sub(clean_payee, ", ", transaction[attr])
            transactions.append(transaction)

        return cls(account, transactions)
