from django.db import models


class Employee(models.Model):
    key = models.CharField(max_length=16)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField()
    ln_address = models.EmailField()
    lnurlp = models.CharField(max_length=200)


class Payroll(models.Model):
    class Status(models.TextChoices):
        NEW = "new"
        IMPORTED = "imported"

    month = models.DateField()
    file = models.FileField()
    status = models.CharField(max_length=8, choices=Status.choices, default=Status.NEW)
    imported = models.DateTimeField(auto_now_add=True)


class Payment(models.Model):
    class Status(models.TextChoices):
        NEW = "new"
        PROCESSING = "processing"
        PAID = "paid"
        FAILES = "failed"

    payroll = models.ForeignKey(
        "Payroll", on_delete=models.PROTECT, related_name="payroll_payments"
    )
    employee = models.ForeignKey(
        "Employee", on_delete=models.PROTECT, related_name="employee_payments"
    )
    fiat_amount = models.DecimalField(decimal_places=2, max_digits=8)
    lnurlp = models.CharField(max_length=200)
    msats_payed = models.PositiveBigIntegerField(null=True)
    msats_fees = models.PositiveBigIntegerField(null=True)
    memo = models.CharField(max_length=128, blank=True)
    invoice = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.NEW)
    time_payed = models.DateTimeField(null=True)
