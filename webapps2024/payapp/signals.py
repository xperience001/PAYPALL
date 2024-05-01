from django.db.models.signals import post_save
from django.dispatch import receiver
from register.models import CustomUser
from .models import Wallet
import random


def generate_account_number():
    while True:
        account_number = "".join([str(random.randint(0, 9)) for _ in range(9)])
        if not Wallet.objects.filter(account_number=account_number).exists():
            return account_number


@receiver(post_save, sender=CustomUser)
def create_wallet(sender, instance, created, *args, **kwargs):
    if created:
        num = generate_account_number()
        Wallet.objects.create(user=instance, account_number=num, account_type="usd")
