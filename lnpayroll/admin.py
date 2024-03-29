from django.db.models import Sum, Count, Q
from django.http import HttpResponseRedirect
from django.utils.html import format_html
from loguru import logger as log
from django.contrib import admin
from django_object_actions import DjangoObjectActions, action
from lnpayroll import models
from lnpayroll import lightning
from constance import config
from import_export.admin import ExportMixin, ImportExportModelAdmin
from lnpayroll.export import CoinTracking, RawData, EmployeeResource
from decimal import Decimal


@admin.register(models.Employee)
class EmployeeAdmin(ImportExportModelAdmin):
    resource_classes = [EmployeeResource]
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
    list_display = [
        "date",
        "title",
        "total_fiat",
        "total_btc",
        "total_fees",
        "number",
        "paid",
        "status_label",
    ]
    inlines = [PaymentInline]

    def show_month(self, obj):
        return f"{obj.month.year}-{obj.month.month:0>2}"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.annotate(number=Count("payroll_payments"))
        qs = qs.annotate(total_fiat=Sum("payroll_payments__fiat_amount"))
        qs = qs.annotate(msats_payed=Sum("payroll_payments__msats_payed"))
        qs = qs.annotate(msats_fees=Sum("payroll_payments__msats_fees"))
        qs = qs.annotate(
            paid=Count(
                "payroll_payments", filter=Q(payroll_payments__status=models.Payment.Status.PAID)
            )
        )
        return qs

    @admin.display(description=f"Total ({config.BASE_CURRENCY})")
    def total_fiat(self, obj):
        if obj.total_fiat:
            return f"{obj.total_fiat:.2f}"

    @admin.display(description=f"Payed (BTC)")
    def total_btc(self, obj):
        if obj.msats_payed:
            value = Decimal(obj.msats_payed * 0.00000000001).quantize(Decimal(".00000001"))
            return f"{value:.8f}"

    @admin.display(description=f"Fees (BTC)")
    def total_fees(self, obj):
        if obj.msats_fees:
            value = Decimal(obj.msats_fees * 0.00000000001).quantize(Decimal(".00000001"))
            return f"{value:.8f}"

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

    def has_delete_permission(self, request, obj=None):
        if (
            obj
            and obj.payroll_payments.filter(
                status__in=(models.Payment.Status.PAID, models.Payment.Status.PROCESSING)
            ).exists()
        ):
            return False
        return super().has_delete_permission(request, obj)


@admin.register(models.Payment)
class PaymentAdmin(DjangoObjectActions, ExportMixin, admin.ModelAdmin):
    resource_classes = [CoinTracking, RawData]
    fields = (
        "payroll",
        "employee",
        "fiat_amount",
        "fx_rate",
        "fx_rate_time",
        "fx_rate_provider",
        "invoice",
        "lnurl_raw",
        "msats_payed",
        "msats_fees",
        "memo",
        "payment_hash",
        "status",
        "created",
        "payed",
    )

    readonly_fields = ["created"]

    list_display = [
        "status_label",
        "get_payroll_date",
        "get_payroll_title",
        "employee",
        "fiat_amount",
        "fx_rate",
        "btc_payed",
        "fee_sats",
        "fee_ppm",
        "payed",
        "pay_button",
    ]
    list_filter = ["status", "payroll__title"]
    change_actions = ["pay"]

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
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

    def pay_button(self, obj):
        link = f"/lnpayroll/payment/{obj.id}/actions/pay/"
        if obj.status in (models.Payment.Status.NEW, models.Payment.Status.FAILED):
            return format_html(f'<a class="button" href="{link}">Pay</a>')
        return ""

    pay_button.short_description = "Pay"

    def has_delete_permission(self, request, obj=None):
        if obj and obj.status in (models.Payment.Status.PAID, models.Payment.Status.PROCESSING):
            return False
        else:
            return super().has_delete_permission(request, obj)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return True
