# Generated by Django 4.2.11 on 2024-04-30 22:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("payapp", "0003_wallet_account_number"),
    ]

    operations = [
        migrations.AlterField(
            model_name="transaction",
            name="status",
            field=models.CharField(
                choices=[
                    ("pending", "PENDING"),
                    ("success", "SUCCESS"),
                    ("failed", "FAILED"),
                ],
                default="pending",
                max_length=20,
            ),
        ),
    ]
