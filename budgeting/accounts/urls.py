from django.urls import path

from . import views

app_name = "accounts"
urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("<int:pk>/", views.AccountView.as_view(), name="account_detail"),
    path(
        "<int:account_id>/transactions/<int:pk>",
        views.TransactionView.as_view(),
        name="transaction_detail",
    ),
]
