# -*- coding: utf-8 -*-
from decimal import Decimal, getcontext
import requests
from django.core.cache import cache
from loguru import logger as log
from constance import config
import lnpayroll as lnp

__all__ = [
    "get_fx_rate",
    "to_msats",
]


class CryptoCompare:
    url = "https://min-api.cryptocompare.com/data/price"

    @classmethod
    def fx_rate(cls, src: str, dst: str) -> lnp.FxRate:
        """Return exchange for source to destination currency"""
        params = dict(fsym=src, tsyms=dst)
        response = requests.get(cls.url, params=params)
        fx_rate = Decimal(response.json()[dst])
        fx_rate_obj = lnp.FxRate(src=src, rate=fx_rate, dst=dst, provider=cls.__name__)
        return fx_rate_obj


class ExchangeRateHost:
    url = "https://api.exchangerate.host/latest"

    @classmethod
    def fx_rate(cls, src: str, dst: str) -> lnp.FxRate:
        """Return exchange for source to destination currency"""
        params = dict(base=src, symbols=dst, source="crypto")
        result = requests.get(cls.url, params=params)
        fx_rate = Decimal(result.json()["rates"][dst])
        fx_rate_obj = lnp.FxRate(src=src, rate=fx_rate, dst=dst, provider=cls.__name__)
        return fx_rate_obj


providers = [CryptoCompare, ExchangeRateHost]


def get_fx_rate(src: str, dst: str) -> lnp.FxRate:
    """Get cached exchange rate"""
    key = f"{src}:{dst}"
    fx_rate = cache.get(key)
    if fx_rate:
        log.debug(f"Using cached exchangerate {fx_rate}")
        return fx_rate

    # Fetch exchange rate and update cache
    for provider in providers:
        try:
            fx_rate = provider.fx_rate(src, dst)
            cache.set(key, fx_rate, timeout=config.FX_TIMEOUT)
            log.debug(f"Updated exchange rate {key} to {fx_rate.rate} via {fx_rate.provider}")
            return fx_rate
        except Exception as e:
            log.error(f"Failed to fetch exchange rate from {provider.__name__}: {e}")

    raise lnp.ExchangeApiError("Could not aquire exchange rate from any provider!")


def to_msats(amount, fx_rate):
    # type: (Decimal, lnp.FxRate) -> int
    """Convert any monetary amount to millisatoshis"""
    getcontext().prec = 8
    amount_btc = amount * fx_rate.rate
    amount_sats = int(amount_btc * 100_000_000)
    amount_msats = amount_sats * 1000
    return amount_msats
