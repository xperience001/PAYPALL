from typing import Any
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from django.contrib.auth import get_user_model

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
        data = super().clean()
        username = data.get("receiver")
        amount = data.get("amount")
        if not amount.isdigit():
            raise forms.ValidationError("amount must be above 100")
        user = self.user
        wallet = user.wallet.first()
        if int(amount) > wallet.balance:
            raise forms.ValidationError("insufficient funds")
        fetch_recipient = User.objects.filter(user_name=username)
        if not fetch_recipient.exists():
            raise forms.ValidationError("recipient does not exist")
        data["amount"] = int(amount)
        data["recipient"] = fetch_recipient.first()
        return data


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
        data = super().clean()
        username = data.get("user")
        amount = data.get("amount")
        if not amount.isdigit():
            raise forms.ValidationError("amount must be above 100")

        fetch_recipient = User.objects.filter(user_name=username)
        if not fetch_recipient.exists():
            raise forms.ValidationError("user does not exist")
        wallet = fetch_recipient.first().wallet.first()
        if int(amount) > wallet.balance:
            raise forms.ValidationError("insufficient funds")

        data["amount"] = int(amount)
        data["recipient"] = fetch_recipient.first()
        return data
