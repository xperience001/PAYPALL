from typing import Iterable
from django.db import models

from django.utils.translation import gettext_lazy as _


class Wallet(models.Model):
    """
    CustomUser Wallet Table
    """

    user = models.ForeignKey(
        "register.customuser",
        on_delete=models.DO_NOTHING,
        verbose_name=_("Wallet Owner"),
        null=True,
        related_name="wallet",
    )
    balance = models.PositiveIntegerField(default=1000)
    account_type = models.CharField(
        max_length=20,
        choices=(
            ("gbp", "GBP"),
            ("usd", "USD"),
        ),
    )
    account_number = models.CharField(max_length=10, null=True)

    def __str__(self):
        return "{} Wallet".format(self.user.email)


class Transaction(models.Model):
    wallet = models.ForeignKey(
        Wallet,
        on_delete=models.CASCADE,
        related_name="transactions",
        verbose_name="Trxn Wallet",
    )
    trxn_class = models.CharField(
        max_length=20, choices=(("debit", "DEBIT"), ("credit", "CREDIT"))
    )
    trxn_from = models.ForeignKey(
        "register.customuser",
        null=True,
        on_delete=models.CASCADE,
        related_name="sender",
    )
    amount = models.PositiveIntegerField()
    trxn_type = models.CharField(
        max_length=20,
        choices=(
            # ("withdraw", "WITHDRAW"),
            ("transfer", "TRANSFER"),
            ("deposit", "DEPOSIT"),
            # ("payment", "PAYMENT"),
            ("request", "REQUEST"),
        ),
    )
    new_balance = models.CharField(max_length=50, null=True)
    status = models.CharField(
        max_length=20,
        choices=(
            ("pending", "PENDING"),
            ("success", "SUCCESS"),
            ("failed", "FAILED"),
        ),
        default="pending",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, force_insert, force_update, using, update_fields):
        if not self.pk or (not self.new_balance and self.status == "success"):
            self.new_balance = self.wallet.balance
        return super().save(force_insert, force_update, using, update_fields)


class Notification(models.Model):
    trxn = models.ForeignKey(
        Transaction, on_delete=models.CASCADE, related_name="notification"
    )
    is_read = models.BooleanField(default=False)
