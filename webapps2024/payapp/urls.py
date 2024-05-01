from django.urls import path
from .views import TransactionsView, ApproveTransactionView, DeclineTransactionView

app_name = "payapp"

urlpatterns = [
    path("transactions", TransactionsView.as_view(), name="transactions"),
    path(
        "<int:pk>/approve",
        ApproveTransactionView.as_view(),
        name="approve-transaction",
    ),
    path(
        "<int:pk>/decline",
        DeclineTransactionView.as_view(),
        name="decline-transaction",
    ),
]
