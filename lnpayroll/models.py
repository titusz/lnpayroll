from django.contrib.admin import display
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from .validators import validate_lnurl, validate_ln_address
import lnpayroll as lnp
from datetime import date
from decimal import Decimal
from constance import config


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
    ln_address = models.EmailField(
        verbose_name=_("Lightning Address"),
        blank=True,
        validators=[validate_ln_address],
    )
    lnurlp = models.CharField(
        verbose_name=_("LNURLp"),
        max_length=200,
        blank=True,
        validators=[validate_lnurl],
    )
    payout_amount = models.DecimalField(
        verbose_name=_("Payout Amount"),
        max_digits=8,
        decimal_places=2,
    )
    active = models.BooleanField(verbose_name=_("Active"), default=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def clean(self):
        if not self.lnurlp and not self.ln_address:
            raise ValidationError(_("Either an LNURLp or a Lightning Address is required"))
        if self.lnurlp and self.ln_address:
            raise ValidationError(
                _("Cannot use Lightning Address and LNURLp at the same time. Choose one!")
            )

    @property
    def lnurl_raw(self):
        address = self.lnurlp or self.ln_address
        return lnp.decode_payment_address(address)


class Payroll(models.Model):
    title = models.CharField(verbose_name=_("Title"), max_length=256, blank=True)
    date = models.DateField(default=date.today)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.date.year}-{self.date.month:0>2}-{self.date.day} - {self.title}"

    def save(self, *args, **kwargs):
        """Autocreate payments for new Payroll"""
        new = True if self.id is None else False
        super(Payroll, self).save(*args, **kwargs)
        if new:
            for employee in Employee.objects.filter(active=True):
                Payment.objects.create(
                    payroll=self,
                    employee=employee,
                    fiat_amount=employee.payout_amount,
                    lnurl_raw=employee.lnurl_raw,
                )


class Payment(models.Model):
    class Status(models.TextChoices):
        NEW = "new"
        PROCESSING = "processing"
        PAID = "paid"
        FAILED = "failed"

    payroll = models.ForeignKey(
        "Payroll", on_delete=models.CASCADE, related_name="payroll_payments"
    )
    employee = models.ForeignKey(
        "Employee", on_delete=models.PROTECT, related_name="employee_payments"
    )
    fiat_amount = models.DecimalField(verbose_name=_("Fiat Amount"), max_digits=8, decimal_places=2)
    fx_rate = models.DecimalField(
        verbose_name=_("Exchange Rate"), max_digits=12, decimal_places=8, null=True
    )
    fx_rate_time = models.DateTimeField(_("Exchange Rate Time"), null=True)
    fx_rate_provider = models.CharField(_("Exchange Rate Provider"), max_length=16, blank=True)
    invoice = models.CharField(_("BOLT11 Invoice"), max_length=1024)
    lnurl_raw = models.CharField(max_length=200)
    msats_payed = models.PositiveBigIntegerField(null=True)
    msats_fees = models.PositiveBigIntegerField(null=True)
    memo = models.CharField(max_length=128, blank=True)
    payment_hash = models.CharField(verbose_name=_("Payment Hash"), max_length=64, blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.NEW)
    created = models.DateTimeField(auto_now_add=True)
    payed = models.DateTimeField(null=True)

    def __str__(self):
        return f"Payment ({self.fiat_amount} -> {self.employee})"

    def fiat_currency(self):
        return config.BASE_CURRENCY

    @property
    def msats_total(self) -> int:
        total = 0
        if self.msats_payed is not None:
            total += self.msats_payed
        if self.msats_fees is not None:
            total += self.msats_fees
        return total

    @display(description="₿ Payed", ordering="msats_payed")
    def btc_payed(self):
        if self.msats_payed:
            value = Decimal(self.msats_payed * 0.00000000001).quantize(Decimal(".00000001"))
            return f"{value:.8f}"

    @display(description="Fee (SAT)", ordering="msats_fees")
    def fee_sats(self):
        if self.msats_fees:
            return self.msats_fees / 1000
        return 0

    @display(description="Fee (PPM)", ordering="msats_fees")
    def fee_ppm(self):
        if self.msats_payed and self.msats_fees:
            return round((self.msats_fees / self.msats_payed) * 1000000)
        return 0
