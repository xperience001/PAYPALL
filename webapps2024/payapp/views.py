from typing import Any
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse
from django.urls import reverse
from django.views.generic import TemplateView, ListView, DetailView
from .models import Transaction
from django.contrib import messages
from django.http.response import Http404, HttpResponseRedirect
from django.db import transaction

# Create your views here.


class TransactionsView(LoginRequiredMixin, ListView):
    template_name = "user/transactions.html"
    model = Transaction
    paginate_by = 10

    def get_queryset(self):
        user_wallet = self.request.user.wallet.first()
        self.queryset = user_wallet.transactions.all().order_by("-created_at")
        return super().get_queryset()


class ApproveTransactionView(LoginRequiredMixin, DetailView):
    queryset = Transaction.objects.all()
    template_name = "user/redirect.html"

    def get_object(self, *args, **kwargs):
        data = super().get_object(*args, **kwargs)
        if data.wallet.user != self.request.user:
            raise Http404()
        return data

    def get(self, request, pk=None, *args, **kwargs):
        referer = request.META.get("HTTP_REFERER")
        if referer:
            request.session["previous_url"] = referer

        data = self.get_object()
        with transaction.atomic():
            sender = data.wallet.user
            reciever = data.trxn_from.wallet.user
            reciever_trxn = data.trxn_from
            sender_wallet = sender.wallet.first()
            reciever_wallet = reciever.wallet.first()
            sender_wallet.balance = sender_wallet.balance - data.amount
            reciever_wallet.balance = reciever_wallet.balance + data.amount
            data.status = "success"
            data.new_balance = int(data.new_balance) - data.amount
            reciever_trxn.new_balance = (
                int(reciever_trxn.new_balance) + reciever_trxn.amount
            )
            reciever_trxn.status = "success"
            sender_wallet.save()
            reciever_wallet.save()
            data.save()
            reciever_trxn.save()
            messages.success(request, "Transaction successful")

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        previous_url = self.request.session.get("previous_url")
        if previous_url:
            return previous_url
        return reverse("register:dashboard")


class DeclineTransactionView(LoginRequiredMixin, DetailView):
    queryset = Transaction.objects.all()
    template_name = "user/redirect.html"

    def get_object(self, *args, **kwargs):
        data = super().get_object(*args, **kwargs)
        if data.wallet.user != self.request.user:
            raise Http404()
        return data

    def get(self, request, pk=None, *args, **kwargs):
        referer = request.META.get("HTTP_REFERER")
        if referer:
            request.session["previous_url"] = referer

        data = self.get_object()
        with transaction.atomic():
            reciever = data.trxn_from
            reciever.status = "failed"
            data.status = "failed"
            data.save()
            reciever.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        previous_url = self.request.session.get("previous_url")
        if previous_url:
            return previous_url
        return reverse("register:dashboard")
