# -*- coding: utf-8 -*-
import json
import requests
from loguru import logger as log
from dataclasses import dataclass
from lnpayroll.models import Payment
from django.contrib import messages
import lnpayroll as lnp
from constance import config
from django.conf import settings
import bolt11
from datetime import datetime
from urllib.parse import quote


_lnd = None


def lnd():
    global _lnd
    if _lnd is None:
        _lnd = requests.Session()
        with open(settings.LND_MACAROON, "rb") as infile:
            macaroon = infile.read().hex()
        headers = {"Grpc-Metadata-macaroon": macaroon}
        _lnd.headers.update(headers)
        _lnd.verify = settings.LND_CERT
    return _lnd


@dataclass
class Message:
    """Backoffice User Message"""

    lvl: int
    msg: str


def pay(pk):
    # type: (int) -> Message
    """Process payment and return status message"""
    # Lock Payment
    locked = Payment.objects.filter(
        pk=pk, status__in=(Payment.Status.NEW, Payment.Status.FAILED)
    ).update(status=Payment.Status.PROCESSING)

    # Retrieve Payment object from database
    try:
        p_obj = Payment.objects.get(pk=pk)
    except Payment.DoesNotExist:
        return Message(messages.ERROR, f"Payment with id {pk} does not exist")

    # Validate payment object status
    if locked != 1:
        return Message(messages.ERROR, f"Unprocessable payment status '{p_obj.status}'")

    # Get Exchange Rate
    fx_rate = lnp.get_fx_rate(config.BASE_CURRENCY, "BTC")
    p_obj.fx_rate = fx_rate.rate
    p_obj.fx_rate_time = fx_rate.time
    p_obj.fx_rate_provider = fx_rate.provider

    # Calculate MSATS
    msats = lnp.to_msats(p_obj.fiat_amount, fx_rate)
    p_obj.msats_payed = msats

    p_obj.save()

    # Get Callback
    headers = {"Accept": "application/json"}
    try:
        resp = requests.get(p_obj.lnurl_raw, headers=headers).json()
        log.debug(f"LNURLp Response: {resp}")
        callback = resp["callback"]
    except Exception as e:
        p_obj.status = Payment.Status.FAILED
        p_obj.save()
        return Message(messages.ERROR, f"Failed to acquire payRequest: {e}")

    # Check LUD 12 - Comments in payRequest support
    comment_chars = resp.get("commentAllowed", 0)

    # Build Callback URL
    sep = "&" if "?" in callback else "?"
    url = callback + sep + f"amount={msats}"
    if comment_chars:
        comment = f"{p_obj.fiat_amount} {config.BASE_CURRENCY}"
        if p_obj.payroll.title:
            comment += f" - {p_obj.payroll.title}"
        comment = comment[:comment_chars]
        comment = quote(comment.encode("utf8"))
        url += f"&comment={comment}"

    log.debug(f"Constructed callback URL: {url}")

    # Get Invoice
    try:
        resp = requests.get(url, headers=headers).json()
        log.debug(f"Callback Response: {resp}")
        if resp.get("status") == "ERROR":
            p_obj.status = Payment.Status.FAILED
            p_obj.save()
            return Message(messages.ERROR, f"LNURL callback error: {resp.get('reason')}")
        invoice = resp["pr"]
    except Exception as e:
        p_obj.status = Payment.Status.FAILED
        p_obj.save()
        return Message(messages.ERROR, f"Failed to acquire Invoice: {e}")

    p_obj.invoice = invoice
    p_obj.save()

    # Validate Invoice
    try:
        invoice_obj = bolt11.decode(invoice)
        log.debug(invoice_obj)
        assert invoice_obj.amount == msats
        assert invoice_obj.is_mainnet()
    except Exception as e:
        p_obj.status = Payment.Status.FAILED
        p_obj.save()
        return Message(messages.ERROR, f"Invalid BOLT11 invoice: {e}")

    # Pay Invoice´
    endpoint = f"{settings.LND_REST_URL}/v2/router/send"

    max_fee = lnp.max_fee(msats)
    payload = {
        "payment_request": invoice,
        "fee_limit_msat": f"{max_fee}",
        "timeout_seconds": config.TX_TIMEOUT,
    }

    try:
        stream = lnd().post(endpoint, data=json.dumps(payload), timeout=None, stream=True)

        for idx, payment_update in enumerate(stream.iter_lines()):
            resp = json.loads(payment_update)
            log.debug(resp)
            log.debug(f"Payment Status: {resp['result']['status']}")
            if idx == 0:
                p_obj.payment_hash = resp["result"]["payment_hash"]
                p_obj.save()
            if resp["result"]["status"] == "FAILED":
                p_obj.status = Payment.Status.FAILED
                p_obj.save()
                return Message(
                    messages.ERROR, f"Payment failed: {resp['result']['failure_reason']}"
                )
            elif resp["result"]["status"] == "SUCCEEDED":
                p_obj.msats_fees = resp["result"]["fee_msat"]
                p_obj.payed = datetime.utcnow()
                p_obj.status = Payment.Status.PAID
                p_obj.save()
                return Message(messages.SUCCESS, "Payment sent successfully")
    except Exception as e:
        p_obj.status = Payment.Status.FAILED
        p_obj.save()
        return Message(messages.ERROR, f"Payment failed: {e}")
