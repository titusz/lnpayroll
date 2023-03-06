# -*- coding: utf-8 -*-
"""Export Resources"""
from import_export import resources
from import_export.fields import Field
from lnpayroll.models import Payment
from decimal import Decimal, ROUND_HALF_UP
from constance import config


class RawData(resources.ModelResource):
    class Meta:
        model = Payment
        name = "Raw Data"


class CoinTracking(resources.ModelResource):
    type = Field(column_name="Type")
    buy_amount = Field(attribute="fiat_amount", column_name="Buy Amount")
    buy_currency = Field(attribute="fiat_currency", column_name="Buy Currency")
    sell_amount = Field(attribute="btc_payed", column_name="Sell Amount")
    sell_currency = Field(column_name="Sell Currency")
    fee = Field(column_name="Fee")
    fee_currency = Field(column_name="Fee Currency")
    exchange = Field(column_name="Exchange")
    trade_group = Field(column_name="Trade-Group")
    comment = Field(column_name="Comment")
    date = Field(column_name="Date")
    tx_id = Field(attribute="payment_hash", column_name="Tx-ID")
    buy_value = Field(column_name="Buy Value")
    sell_value = Field(column_name="Sell Value")
    liquidity_pool = Field(column_name="Liquidity Pool")
    employee_number = Field(column_name="Employee Number")

    class Meta:
        model = Payment
        name = "Cointracking Format"
        fields = (
            "type",
            "buy_amount",
            "buy_currency",
            "sell_amount",
            "sell_currency",
            "fee",
            "fee_currency",
            "exchange",
            "trade_group",
            "comment",
            "date",
            "tx_id",
            "buy_value",
            "sell_value",
            "liquidity_pool",
            "employee_number",
        )
        export_order = fields

    def dehydrate_type(self, payment):
        """Cointracking Transaction Type"""
        return "Trade"

    def dehydrate_sell_currency(self, payment):
        """We only spend Bitcoin :)"""
        return "BTC"

    def dehydrate_fee(self, payment):
        """Millisatoshis to BTC conversion"""
        if not payment.msats_fees:
            return Decimal("0")
        btc_fees = Decimal(payment.msats_fees) / Decimal(100000000000)
        fees_rounded = btc_fees.quantize(Decimal(".00000001"), rounding=ROUND_HALF_UP)
        return fees_rounded

    def dehydrate_fee_currency(self, payment):
        """Lithning Fees are allways in bitcoin"""
        return "BTC"

    def dehydrate_exchange(self, payment):
        """Spending is a direct exchange"""
        return config.EXPORT_EXCHANGE_VALUE

    def dehydrate_trade_group(self, payment):
        """The trade groupe is a payroll"""
        return config.EXPORT_TRADE_GROUP_VALUE

    def dehydrate_comment(self, payment):
        """Comment is the employee code + payroll title"""
        comment = f"{payment.employee.code}"
        if payment.payroll.title:
            comment += rf" - {payment.payroll.title}"
        return comment

    def dehydrate_date(self, payment):
        if payment.payed:
            return payment.payed.isoformat(timespec="seconds")
        return ""

    def dehydrate_buy_value(self, paymennt):
        return ""

    def dehydrate_sell_value(self, paymennt):
        return ""

    def dehydrate_liquidity_pool(self, paymennt):
        return ""

    def dehydrate_employee_number(self, payment):
        return payment.employee.code
