from django.db.models.query import QuerySet
from django.http import HttpResponseRedirect
from django.views.generic.edit import CreateView
from django.views.generic import TemplateView, ListView, DetailView
from .forms import SignUpForm
from django.urls import reverse_lazy
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from payapp.forms import SendForm, RequestForm
from django.contrib import messages
from django.db import transaction
from payapp.models import Transaction

# Create your views here.


class CustomLoginView(LoginView):
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
                    Transaction.objects.create(
                        wallet=sender_wallet,
                        trxn_class="debit",
                        trxn_from=sender,
                        amount=amount,
                        trxn_type="transfer",
                        status="success",
                    )
                    Transaction.objects.create(
                        wallet=receiver_wallet,
                        trxn_class="credit",
                        trxn_from=sender,
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
                    receiver = send_form.cleaned_data["recipient"]
                    amount = send_form.cleaned_data["amount"]

                    Transaction.objects.create(
                        wallet=sender_wallet,
                        trxn_class="credit",
                        trxn_from=sender,
                        amount=amount,
                        trxn_type="request",
                    )
                    Transaction.objects.create(
                        wallet=receiver_wallet,
                        trxn_class="debit",
                        trxn_from=sender,
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


class TransactionsView(LoginRequiredMixin, ListView):
    template_name = "user/transactions.html"
    model = Transaction
    paginate_by = 10

    def get_queryset(self):
        user_wallet = self.request.user.wallet.first()
        self.queryset = user_wallet.transactions.all()
        return super().get_queryset()



class AccountsPageView(LoginRequiredMixin, TemplateView):
    template_name = 'user/account.html'
    