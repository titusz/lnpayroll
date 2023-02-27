from django.contrib import admin
from lnpayroll import models


@admin.register(models.Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ["code", "first_name", "last_name", "payout_amount", "active"]
    list_editable = ["payout_amount", "active"]


@admin.register(models.Payroll)
class PayrollAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Payment)
class PaymentAdmin(admin.ModelAdmin):
    pass
