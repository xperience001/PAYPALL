# Generated by Django 4.2.11 on 2024-05-01 13:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("payapp", "0006_transaction_new_balance"),
    ]

    operations = [
        migrations.AlterField(
            model_name="transaction",
            name="trxn_from",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="sender",
                to="payapp.transaction",
            ),
        ),
    ]
