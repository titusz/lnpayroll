# -*- coding: utf-8 -*-
"""Export Resources"""
from import_export import resources
from import_export.fields import Field
from lnpayroll.models import Payment


class PaymentResource(resources.ModelResource):
    fiat_currency = Field(attribute="fiat_currency", column_name="fiat_currency")
    btc_amount = Field(attribute="btc_payed", column_name="btc_payed")
    fee_sats = Field(attribute="fee_sats", column_name="fee_sats")

    class Meta:
        model = Payment
        fields = (
            "id",
            "payroll__date",
            "payroll__title",
            "employee__code",
            "fiat_currency",
            "fiat_amount",
            "fx_rate",
            "btc_amount",
            "fee_sats",
            "status",
            "payed",
            "payment_hash",
        )
        export_order = fields
