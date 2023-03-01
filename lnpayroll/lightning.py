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


_lnd = None


def lnd():
    global _lnd
    if _lnd is None:
        _lnd = requests.Session()
        with open(settings.LND_MACAROON_PATH, "rb") as infile:
            macaroon = infile.read().hex()
        headers = {"Grpc-Metadata-macaroon": macaroon}
        _lnd.headers.update(headers)
        _lnd.verify = settings.LND_CERT_PATH.as_posix()
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

    # Get Invoice
    sep = "&" if "?" in callback else "?"
    url = callback + sep + f"amount={msats}"
    try:
        resp = requests.get(url, headers=headers).json()
        log.debug(f"Callback Response: {resp}")
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
    endpoint = f"{settings.LND_REST_SERVER}/v2/router/send"

    payload = {
        "payment_request": invoice,
        "fee_limit_msat": f"{config.MAX_FEE_MSATS}",
        "timeout_seconds": config.TX_TIMEOUT,
    }

    try:
        stream = lnd().post(endpoint, data=json.dumps(payload), timeout=None, stream=True)
        for idx, payment_update in enumerate(stream.iter_lines()):
            resp = json.loads(payment_update)
            log.debug(resp)
            if idx == 0:
                p_obj.payment_hash = resp["result"]["payment_hash"]
                p_obj.save()
        result = resp["result"]
        if result["status"] == "SUCCEEDED":
            p_obj.msats_fees = result["fee_msat"]
            p_obj.payed = datetime.utcnow()
            p_obj.status = Payment.Status.PAID
            p_obj.save()
            return Message(messages.SUCCESS, "Payment sent succesfully")
        else:
            return Message(messages.ERROR, f"Payment failed: {result['failure_reason']}")
    except Exception as e:
        p_obj.status = Payment.Status.FAILED
        p_obj.save()
        return Message(messages.ERROR, f"Payment failed: {e}")
