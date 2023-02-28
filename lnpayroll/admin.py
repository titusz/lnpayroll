from django.http import HttpResponseRedirect
from django.utils.html import format_html
from loguru import logger as log
from django.contrib import admin
from django_object_actions import DjangoObjectActions, action
from lnpayroll import models
from lnpayroll import tasks


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
class PaymentAdmin(DjangoObjectActions, admin.ModelAdmin):
    list_display = [
        "pk",
        "employee",
        "fiat_amount",
        "fx_rate",
        "msats_payed",
        "msats_fees",
        "payroll",
        "status",
        "pay_button",
    ]
    list_filter = ["status"]
    change_actions = ["pay"]

    @action(label="Pay")
    def pay(self, request, obj):
        log.debug(f"Triggered payment {obj}")
        tasks.pay(obj.pk)
        self.message_user(request, "Payed")
        return HttpResponseRedirect("/lnpayroll/payment/")

    def pay_button(self, obj):
        link = f"/lnpayroll/payment/{obj.id}/actions/pay/"
        return format_html(f'<a class="button" href="{link}">Pay</a>')

    pay_button.short_description = "Pay"
