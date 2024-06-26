# Generated by Django 4.2.11 on 2024-04-30 22:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("payapp", "0004_alter_transaction_status"),
    ]

    operations = [
        migrations.AlterField(
            model_name="transaction",
            name="trxn_type",
            field=models.CharField(
                choices=[
                    ("transfer", "TRANSFER"),
                    ("deposit", "DEPOSIT"),
                    ("request", "REQUEST"),
                ],
                max_length=20,
            ),
        ),
    ]
