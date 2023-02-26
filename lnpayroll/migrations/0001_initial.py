# Generated by Django 4.1.7 on 2023-02-26 12:30

from django.db import migrations, models
import django.db.models.deletion


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
                ("key", models.CharField(max_length=16)),
                ("first_name", models.CharField(max_length=150)),
                ("last_name", models.CharField(max_length=150)),
                ("email", models.EmailField(max_length=254)),
                ("ln_address", models.EmailField(max_length=254)),
                ("lnurlp", models.CharField(max_length=200)),
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
                ("file", models.FileField(upload_to="")),
                (
                    "status",
                    models.CharField(
                        choices=[("new", "New"), ("imported", "Imported")],
                        default="new",
                        max_length=8,
                    ),
                ),
                ("imported", models.DateTimeField(auto_now_add=True)),
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
                ("fiat_amount", models.DecimalField(decimal_places=2, max_digits=8)),
                ("lnurlp", models.CharField(max_length=200)),
                ("msats_payed", models.PositiveBigIntegerField(null=True)),
                ("msats_fees", models.PositiveBigIntegerField(null=True)),
                ("memo", models.CharField(blank=True, max_length=128)),
                ("invoice", models.CharField(blank=True, max_length=200)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("new", "New"),
                            ("processing", "Processing"),
                            ("paid", "Paid"),
                            ("failed", "Failes"),
                        ],
                        default="new",
                        max_length=10,
                    ),
                ),
                ("time_payed", models.DateTimeField(null=True)),
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
