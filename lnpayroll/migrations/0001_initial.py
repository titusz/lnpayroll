# Generated by Django 4.1.7 on 2023-02-28 07:24

from django.db import migrations, models
import django.db.models.deletion
import djmoney.models.fields
import lnpayroll.validators


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Employee",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "code",
                    models.CharField(
                        blank=True,
                        max_length=16,
                        null=True,
                        unique=True,
                        verbose_name="Employee Code",
                    ),
                ),
                (
                    "first_name",
                    models.CharField(max_length=150, verbose_name="First Name"),
                ),
                (
                    "last_name",
                    models.CharField(max_length=150, verbose_name="Last Name"),
                ),
                (
                    "email",
                    models.EmailField(
                        blank=True, max_length=254, verbose_name="Email Address"
                    ),
                ),
                (
                    "ln_address",
                    models.EmailField(
                        blank=True,
                        max_length=254,
                        validators=[lnpayroll.validators.validate_ln_address],
                        verbose_name="Lightning Address",
                    ),
                ),
                (
                    "lnurlp",
                    models.CharField(
                        blank=True,
                        max_length=200,
                        validators=[lnpayroll.validators.validate_lnurl],
                        verbose_name="LNURLp",
                    ),
                ),
                (
                    "payout_amount_currency",
                    djmoney.models.fields.CurrencyField(
                        choices=[
                            ("XBT", "Bitcoin"),
                            ("EUR", "Euro"),
                            ("USD", "US Dollar"),
                        ],
                        default="EUR",
                        editable=False,
                        max_length=3,
                    ),
                ),
                (
                    "payout_amount",
                    djmoney.models.fields.MoneyField(
                        decimal_places=12,
                        default_currency="EUR",
                        max_digits=20,
                        verbose_name="Payout Amount",
                    ),
                ),
                ("active", models.BooleanField(default=True, verbose_name="Active")),
            ],
        ),
        migrations.CreateModel(
            name="Payroll",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("month", models.DateField()),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("new", "New"),
                            ("partial", "Partial"),
                            ("paid", "Payed"),
                        ],
                        default="new",
                        max_length=8,
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="Payment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "fiat_amount_currency",
                    djmoney.models.fields.CurrencyField(
                        choices=[
                            ("XBT", "Bitcoin"),
                            ("EUR", "Euro"),
                            ("USD", "US Dollar"),
                        ],
                        default="EUR",
                        editable=False,
                        max_length=3,
                    ),
                ),
                (
                    "fiat_amount",
                    djmoney.models.fields.MoneyField(
                        decimal_places=12, default_currency="EUR", max_digits=20
                    ),
                ),
                ("lnurl_raw", models.CharField(max_length=200)),
                ("msats_payed", models.PositiveBigIntegerField(null=True)),
                ("msats_fees", models.PositiveBigIntegerField(null=True)),
                ("memo", models.CharField(blank=True, max_length=128)),
                ("tx_ref", models.CharField(blank=True, max_length=200)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("new", "New"),
                            ("processing", "Processing"),
                            ("paid", "Paid"),
                            ("failed", "Failed"),
                        ],
                        default="new",
                        max_length=10,
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("payed", models.DateTimeField(null=True)),
                (
                    "employee",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="employee_payments",
                        to="lnpayroll.employee",
                    ),
                ),
                (
                    "payroll",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="payroll_payments",
                        to="lnpayroll.payroll",
                    ),
                ),
            ],
        ),
    ]
