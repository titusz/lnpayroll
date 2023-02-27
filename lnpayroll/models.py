from django.db import models
from djmoney.models.fields import MoneyField
from django.utils.translation import gettext_lazy as _


class Employee(models.Model):
    code = models.CharField(
        verbose_name=_("Employee Code"),
        max_length=16,
        blank=True,
        unique=True,
        null=True,
    )
    first_name = models.CharField(verbose_name=_("First Name"), max_length=150)
    last_name = models.CharField(verbose_name=_("Last Name"), max_length=150)
    email = models.EmailField(verbose_name=_("Email Address"), blank=True)
    ln_address = models.EmailField(verbose_name=_("Lightning Address"), blank=True)
    lnurlp = models.CharField(verbose_name=_("LNURLp"), max_length=200, blank=True)
    payout_amount = MoneyField(
        verbose_name=_("Payout Amount"),
        max_digits=20,
        decimal_places=12,
        default_currency="EUR",
    )
    active = models.BooleanField(verbose_name=_("Active"), default=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.code})"


class Payroll(models.Model):
    class Status(models.TextChoices):
        NEW = "new"
        PARTIAL = "partial"
        PAYED = "paid"

    month = models.DateField()
    status = models.CharField(max_length=8, choices=Status.choices, default=Status.NEW)
    created = models.DateTimeField(auto_now_add=True)


class Payment(models.Model):
    class Status(models.TextChoices):
        NEW = "new"
        PROCESSING = "processing"
        PAID = "paid"
        FAILED = "failed"

    payroll = models.ForeignKey(
        "Payroll", on_delete=models.PROTECT, related_name="payroll_payments"
    )
    employee = models.ForeignKey(
        "Employee", on_delete=models.PROTECT, related_name="employee_payments"
    )
    fiat_amount = MoneyField(max_digits=20, decimal_places=12, default_currency="EUR")
    lnurlp = models.CharField(max_length=200)
    msats_payed = models.PositiveBigIntegerField(null=True)
    msats_fees = models.PositiveBigIntegerField(null=True)
    memo = models.CharField(max_length=128, blank=True)
    tx_ref = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.NEW)
    created = models.DateTimeField(auto_now_add=True)
    payed = models.DateTimeField(null=True)
