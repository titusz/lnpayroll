from django.db.models import Sum, Count, Q
from django.http import HttpResponseRedirect
from django.utils.html import format_html
from loguru import logger as log
from django.contrib import admin
from django_object_actions import DjangoObjectActions, action
from lnpayroll import models
from lnpayroll import lightning
from constance import config


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


class PaymentInline(admin.TabularInline):
    model = models.Payment
    extra = 0
    fields = [
        "employee",
        "fiat_amount",
        "fx_rate",
        "msats_payed",
        "msats_fees",
        "status_label",
        "payed",
    ]
    readonly_fields = fields

    colors = {
        "new": "red",
        "processing": "oragne",
        "paid": "green",
        "failed": "crimson",
    }
    can_delete = False

    def has_add_permission(self, request, obj):
        return False

    def status_label(self, obj):
        color = self.colors[obj.status]
        label = f'<span class="button" style="background-color: {color}">&nbsp;{obj.status}&nbsp;</span>'
        return format_html(label)

    status_label.allow_tags = True
    status_label.short_description = "status"


@admin.register(models.Payroll)
class PayrollAdmin(admin.ModelAdmin):
    list_display = ["date", "title", "total_fiat", "number", "paid", "status_label"]
    inlines = [PaymentInline]

    def show_month(self, obj):
        return f"{obj.month.year}-{obj.month.month:0>2}"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.annotate(number=Count("payroll_payments"))
        qs = qs.annotate(total_fiat=Sum("payroll_payments__fiat_amount"))
        qs = qs.annotate(
            paid=Count(
                "payroll_payments", filter=Q(payroll_payments__status=models.Payment.Status.PAID)
            )
        )
        return qs

    @admin.display(description=f"Total ({config.BASE_CURRENCY})")
    def total_fiat(self, obj):
        return f"{obj.total_fiat:.2f}"

    def number(self, obj):
        return obj.number

    def paid(self, obj):
        return obj.paid

    @admin.display(description="Status")
    def status_label(self, obj):
        label = '<span class="button" style="background-color: {color}">&nbsp;{status}&nbsp;</span>'
        if obj.paid == 0:
            color = "red"
            status = "new"
        elif obj.paid < obj.number:
            color = "orange"
            status = "partial"
        elif obj.number == obj.paid:
            color = "green"
            status = "payed"
        else:
            color = "blue"
            status = "undefined"
        return format_html(label, color=color, status=status)

    status_label.allow_tags = True
    status_label.short_description = "status"


@admin.register(models.Payment)
class PaymentAdmin(DjangoObjectActions, admin.ModelAdmin):
    list_display = [
        "status_label",
        "get_payroll_date",
        "get_payroll_title",
        "employee",
        "fiat_amount",
        "fx_rate",
        "msats_payed",
        "msats_fees",
        "payed",
        "pay_button",
    ]
    list_filter = ["status", "payroll__title"]
    change_actions = ["pay"]
    readonly_fields = ("fx_rate",)
    date_hierarchy = "payroll__date"

    colors = {
        "new": "red",
        "processing": "oragne",
        "paid": "green",
        "failed": "crimson",
    }

    @admin.display(description="Payroll Date", ordering="payroll__date")
    def get_payroll_date(self, obj):
        return obj.payroll.date

    @admin.display(description="Payroll Title", ordering="payroll__title")
    def get_payroll_title(self, obj):
        return obj.payroll.title

    def status_label(self, obj):
        color = self.colors[obj.status]
        label = f'<span class="button" style="background-color: {color}">&nbsp;{obj.status}&nbsp;</span>'
        return format_html(label)

    status_label.allow_tags = True
    status_label.short_description = "status"

    @action(label="Pay")
    def pay(self, request, obj):
        log.debug(f"Triggered payment {obj}")
        msg = lightning.pay(obj.pk)
        self.message_user(request, msg.msg, level=msg.lvl)
        return HttpResponseRedirect("/lnpayroll/payment/")

    def pay_button(self, obj):
        link = f"/lnpayroll/payment/{obj.id}/actions/pay/"
        if obj.status in (models.Payment.Status.NEW, models.Payment.Status.FAILED):
            return format_html(f'<a class="button" href="{link}">Pay</a>')
        return ""

    pay_button.short_description = "Pay"
