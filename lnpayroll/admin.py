from django.contrib import admin
from lnpayroll import models


@admin.register(models.Employee)
class EmployeeAdmin(admin.ModelAdmin):
    actions = None
    list_display = ["code", "first_name", "last_name", "payout_amount", "lnurl_raw", "active"]
    list_editable = ["payout_amount", "active"]
    list_filter = ["active"]
    search_fields = ["first_name", "last_name"]


@admin.register(models.Payroll)
class PayrollAdmin(admin.ModelAdmin):
    actions = None
    list_display = ["show_month", "status"]

    def show_month(self, obj):
        return f"{obj.month.year}-{obj.month.month:0>2}"


@admin.register(models.Payment)
class PaymentAdmin(admin.ModelAdmin):
    actions = None
    list_display = ["pk", "employee", "fiat_amount", "msats_payed", "msats_fees", "payroll", "status"]
    list_filter = ["status"]
