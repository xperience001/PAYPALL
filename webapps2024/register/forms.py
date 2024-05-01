from typing import Any
from django import forms
from .models import CustomUser
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Div, HTML
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.hashers import check_password


class CustomLoginForm(AuthenticationForm):
    def __init__(self, request, *args, **kwargs):
        super().__init__(request, *args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            "username",
            "password",
            Div(
                Submit("submit", "Login", css_class="btn btn-primary mr-2"),
                HTML('<a href="/register">Register</a>'),
                css_class="d-flex justify-content-between",
            ),
        )


class SignUpForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ["first_name", "last_name", "user_name", "email", "password"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column("first_name", css_class="form-group col-md-6 mb-0"),
                Column("last_name", css_class="form-group col-md-6 mb-0"),
                css_class="form-row",
            ),
            Row(
                Column("email", css_class="form-group col-md-6 mb-0"),
                Column("user_name", css_class="form-group col-md-6 mb-0"),
                css_class="form-row",
            ),
            "password",
            Div(
                Submit("submit", "Sign Up", css_class="btn btn-primary mr-2"),
                HTML('<a href="/login">Login</a>'),
                css_class="d-flex justify-content-between",
            ),
        )
        self.fields["user_name"].label = "Username"


class UpdateProfileForm(forms.ModelForm):

    class Meta:
        model = CustomUser
        fields = ["first_name", "last_name", "email", "user_name"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column("first_name", css_class="form-group col-md-6 mb-0"),
                Column("last_name", css_class="form-group col-md-6 mb-0"),
                css_class="form-row",
            ),
            Row(
                Column("email", css_class="form-group col-md-6 mb-0"),
                Column("user_name", css_class="form-group col-md-6 mb-0"),
                css_class="form-row",
            ),
            Submit("submit", "Save"),
        )


class UpdatePasswordForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Current password")
    password1 = forms.CharField(widget=forms.PasswordInput, label="Enter new password")
    password2 = forms.CharField(
        widget=forms.PasswordInput, label="Confirm new password"
    )

    class Meta:
        model = CustomUser
        fields = ["password"]

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            "password",
            Row(
                Column("password1", css_class="form-group col-md-6 mb-0"),
                Column("password2", css_class="form-group col-md-6 mb-0"),
                css_class="form-row",
            ),
            Submit("submit", "Save"),
        )

    def clean(self):
        cleaned_data = super().clean()
        old_password = cleaned_data["password"]
        if not check_password(old_password, self.instance.password):
            raise forms.ValidationError("incorrect old password")
        if cleaned_data["password1"] != cleaned_data["password2"]:
            raise forms.ValidationError("passwords do not match")
        return cleaned_data
