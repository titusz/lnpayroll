from django.contrib import admin
from django.forms import TextInput
from django.db.models import CharField

from lnpayroll import models


@admin.register(models.Employee)
class EmployeeAdmin(admin.ModelAdmin):
    actions = None
    list_display = [
        "code",
        "first_name",
        "last_name",
        "payout_amount",
        "lnurl_raw",
        "active",
    ]
    list_editable = ["payout_amount", "active"]
    list_filter = ["active"]
    search_fields = ["first_name", "last_name"]
    fieldsets = (
        ("Employee Data", {"fields": ("code", "first_name", "last_name", "email")}),
        (
            "Payment Settings",
            {
                "classes": ("wide",),
                "fields": ("ln_address", "lnurlp", "payout_amount", "active"),
            },
        ),
    )


@admin.register(models.Payroll)
class PayrollAdmin(admin.ModelAdmin):
    actions = None
    list_display = ["show_month", "status"]

    def show_month(self, obj):
        return f"{obj.month.year}-{obj.month.month:0>2}"


@admin.register(models.Payment)
class PaymentAdmin(admin.ModelAdmin):
    actions = None
    list_display = [
        "pk",
        "employee",
        "fiat_amount",
        "fx_rate",
        "msats_payed",
        "msats_fees",
        "payroll",
        "status",
    ]
    list_filter = ["status"]
