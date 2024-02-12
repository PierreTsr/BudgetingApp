from django.views import generic
from rest_framework import viewsets

from .models import Account, Transaction
from .serializers import AccountSerializer


class IndexView(generic.ListView):
    template_name = "accounts/index.html"


# class AccountView(generic.DetailView):
#     model = Account

#     def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
#         context = super(AccountView, self).get_context_data(**kwargs)
#         return {
#             **context["account"].transaction_set.all().aggregate(balance=Sum("value")),
#             **context,
#         }


class AccountView(viewsets.ModelViewSet):
    serializer_class = AccountSerializer
    queryset = Account.objects.all()


class TransactionView(generic.DetailView):
    model = Transaction
