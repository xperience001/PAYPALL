from django.db.models.query import QuerySet
from django.http import HttpResponseRedirect
from django.views.generic.edit import CreateView
from django.views.generic import TemplateView, ListView, DetailView
from .forms import SignUpForm, UpdatePasswordForm, UpdateProfileForm, CustomLoginForm
from django.urls import reverse, reverse_lazy
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from payapp.forms import SendForm, RequestForm, CurrencyForm
from django.contrib import messages
from django.db import transaction
from payapp.models import Transaction
from rest_framework.views import APIView
from django.conf import settings
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
import requests

# Create your views here.


class CustomLoginView(LoginView):
    form_class = CustomLoginForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add your custom context here
        context["title"] = "Account Login"
        return context


class RegisterView(CreateView):
    form_class = SignUpForm
    template_name = "registration/register.html"
    success_url = reverse_lazy("register:dashboard")

    def form_valid(self, form):
        user = form.save()

        if user:
            login(self.request, user)

        return super().form_valid(form)


class DashBoardView(LoginRequiredMixin, TemplateView):
    template_name = "user/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        wallet = user.wallet.first()
        context["username"] = user.user_name
        context["balance"] = wallet.balance
        context["account_number"] = wallet.account_number
        context["account_type"] = wallet.account_type
        context["send_form"] = SendForm()
        context["request_form"] = RequestForm()
        # fetch transactions
        transactions = wallet.transactions.all().order_by("-created_at")
        context["transactions"] = transactions
        self.request.session.pop("success_message", None)
        self.request.session.modified = True
        return context

    def post(self, request, *args, **kwargs):
        send_form = SendForm(request.POST, user=self.request.user)
        request_form = RequestForm(request.POST, user=self.request.user)
        if "receiver" in request.POST:
            if send_form.is_valid():
                with transaction.atomic():
                    sender = self.request.user
                    receiver = send_form.cleaned_data["recipient"]
                    amount = send_form.cleaned_data["amount"]
                    sender_wallet = sender.wallet.first()
                    receiver_wallet = receiver.wallet.first()
                    sender_wallet.balance = sender_wallet.balance - amount
                    sender_wallet.save()
                    receiver_wallet.balance = receiver_wallet.balance + amount
                    sender_wallet.save()
                    receiver_wallet.save()
                    trxn_from = Transaction.objects.create(
                        wallet=sender_wallet,
                        trxn_class="debit",
                        # trxn_from=sender,
                        amount=amount,
                        trxn_type="transfer",
                        status="success",
                    )
                    Transaction.objects.create(
                        wallet=receiver_wallet,
                        trxn_class="credit",
                        trxn_from=trxn_from,
                        amount=amount,
                        trxn_type="deposit",
                        status="success",
                    )
                messages.success(request, "Transfer successful.")
                return HttpResponseRedirect(self.request.path_info)
            else:
                for _, errors in send_form.errors.items():
                    for error in errors:
                        messages.error(request, f"Send error: {error}")
        elif "user" in request.POST:
            if request_form.is_valid():
                with transaction.atomic():
                    sender = self.request.user
                    sender_wallet = sender.wallet.first()
                    receiver = request_form.cleaned_data["recipient"]
                    receiver_wallet = receiver.wallet.first()
                    amount = request_form.cleaned_data["amount"]

                    trxn_from = Transaction.objects.create(
                        wallet=sender_wallet,
                        trxn_class="credit",
                        # trxn_from=sender,
                        amount=amount,
                        trxn_type="request",
                    )
                    Transaction.objects.create(
                        wallet=receiver_wallet,
                        trxn_class="debit",
                        trxn_from=trxn_from,
                        amount=amount,
                        trxn_type="transfer",
                    )

                messages.success(request, "Request successful.")
                return HttpResponseRedirect(self.request.path_info)
            else:
                for _, errors in request_form.errors.items():
                    for error in errors:
                        messages.error(request, f"Request error: {error}")

        return HttpResponseRedirect(self.request.path_info)


class AccountsPageView(LoginRequiredMixin, TemplateView):
    template_name = "user/account.html"

    def get_context_data(self, **kwargs):
        user = self.request.user
        context = super().get_context_data(**kwargs)
        context["account_form"] = UpdateProfileForm(instance=user)
        context["password_form"] = UpdatePasswordForm(instance=user)
        context["currency_form"] = CurrencyForm(user=user)
        return context

    def post(self, request, *args, **kwargs):
        user = self.request.user
        profile_form = UpdateProfileForm(request.POST, instance=user)
        password_form = UpdatePasswordForm(request.POST, instance=user)
        currency_form = CurrencyForm(
            request.POST, user=user, initial={"to": user.wallet.first().account_type}
        )
        if "password" in request.POST:
            if password_form.is_valid():
                user.set_password(password_form.cleaned_data["password1"])
                user.save()
                messages.success(request, "password update successful")
                return HttpResponseRedirect(request.path_info)
            else:
                for _, errors in password_form.errors.items():
                    for error in errors:
                        messages.error(request, f"update error: {error}")
        elif "to" in request.POST:
            if currency_form.is_valid():
                wallet = currency_form.cleaned_data["wallet"]
                acc_type = wallet.account_type
                if acc_type == currency_form.cleaned_data["to"]:
                    messages.success(request, "Currency update successful")
                else:
                    wallet.account_type = currency_form.cleaned_data["to"]
                    wallet.save()
                    messages.success(request, "Currency update successful")
        else:
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, "profile update successful")
                return HttpResponseRedirect(request.path_info)
            else:
                for _, errors in password_form.errors.items():
                    for error in errors:
                        messages.error(request, f"update error: {error}")
        return HttpResponseRedirect(self.request.path_info)
