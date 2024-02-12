from typing import Any

from django.db.models import Sum
from django.views import generic

from .models import Account, Transaction


class IndexView(generic.ListView):
    template_name = "accounts/index.html"


class AccountView(generic.DetailView):
    model = Account

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super(AccountView, self).get_context_data(**kwargs)
        return {
            **context["account"].transaction_set.all().aggregate(balance=Sum("value")),
            **context,
        }


class TransactionView(generic.DetailView):
    model = Transaction
