from django import template
from payapp.models import Wallet
from django.conf import settings

register = template.Library()


@register.filter
def to_value(number, user):
    user_data = Wallet.objects.get(user=user)
    if user_data.account_type == "usd":
        return number * 1
    else:
        return float(number) * float(settings.EURO_RATE)
