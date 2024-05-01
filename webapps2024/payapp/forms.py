from typing import Any, Mapping
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from django.contrib.auth import get_user_model
from django.forms.renderers import BaseRenderer
from django.forms.utils import ErrorList

User = get_user_model()


class SendForm(forms.Form):
    receiver = forms.CharField(help_text="enter receiving user (i.e username)")
    amount = forms.CharField(help_text="enter amount")

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)

        super(SendForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            "receiver",
            "amount",
        )
        self.helper.form_method = "POST"
        self.helper.add_input(
            Submit("submit", "Continue", css_class="btn btn-success col-12 mx-auto")
        )

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("receiver")
        amount = cleaned_data.get("amount")
        if not amount.isdigit():
            raise forms.ValidationError("amount must be above 100")
        user = self.user
        wallet = user.wallet.first()
        if int(amount) > wallet.balance:
            raise forms.ValidationError("insufficient funds")
        fetch_recipient = User.objects.filter(user_name=username)
        if not fetch_recipient.exists():
            raise forms.ValidationError("recipient does not exist")
        if self.user == fetch_recipient.first():
            raise forms.ValidationError("can send money to self")
        cleaned_data["amount"] = int(amount)
        cleaned_data["recipient"] = fetch_recipient.first()
        return cleaned_data


class RequestForm(forms.Form):
    user = forms.CharField(help_text="enter receiving user (i.e username)")
    amount = forms.CharField(help_text="enter amount")

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super(RequestForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            "user",
            "amount",
        )
        self.helper.form_method = "POST"
        self.fields["user"].label = "Request from user?"

        self.helper.add_input(
            Submit("submit", "Continue", css_class=" btn btn-success col-12 mx-auto")
        )

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("user")
        amount = cleaned_data.get("amount")
        if not amount.isdigit():
            raise forms.ValidationError("amount must be above 100")

        fetch_recipient = User.objects.filter(user_name=username)
        if not fetch_recipient.exists():
            raise forms.ValidationError("user does not exist")
        wallet = fetch_recipient.first().wallet.first()
        if int(amount) > wallet.balance:
            raise forms.ValidationError("insufficient funds")
        if self.user == fetch_recipient.first():
            raise forms.ValidationError("can not request from self")
        cleaned_data["amount"] = int(amount)
        cleaned_data["recipient"] = fetch_recipient.first()
        return cleaned_data


class CurrencyForm(forms.Form):
    to = forms.ChoiceField(
        widget=forms.Select,
        choices=(
            ("usd", "USD"),
            ("gbp", "GBP"),
        ),
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout("to", Submit("submit", "Save"))
        if not self.user:
            raise forms.ValidationError("authentication required")
        self.initial = kwargs.pop("initial", {})

    def clean(self):
        cleaned_data = super().clean()
        wallet = self.user.wallet.first()
        cleaned_data["wallet"] = wallet
        return cleaned_data
