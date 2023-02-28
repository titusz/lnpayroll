# -*- coding: utf-8 -*-
from decimal import Decimal
import requests
from django.core.cache import cache
from loguru import logger as log
from constance import config
import lnpayroll as lnp

__all__ = ["get_fx_rate"]


class CryptoCompare:
    url = "https://min-api.cryptocompare.com/data/price"

    @classmethod
    def fx_rate(cls, src: str, dst: str) -> Decimal:
        """Return exchange for source to destination currency"""
        params = dict(fsym=src, tsyms=dst)
        response = requests.get(cls.url, params=params)
        fx_rate = Decimal(response.json()[dst])
        return fx_rate


class ExchangeRateHost:
    url = "https://api.exchangerate.host/latest"

    @classmethod
    def fx_rate(cls, src: str, dst: str) -> Decimal:
        """Return exchange for source to destination currency"""
        params = dict(base=src, symbols=dst, source="crypto")
        result = requests.get(cls.url, params=params)
        fx_rate = Decimal(result.json()["rates"][dst])
        return fx_rate


providers = [CryptoCompare, ExchangeRateHost]


def get_fx_rate(src: str, dst: str) -> Decimal:
    """Get cached exchange rate"""
    key = f"{src}:{dst}"
    fx_rate = cache.get(key)
    if fx_rate and fx_rate > 0:
        log.debug(f"Using cached exchangerate {fx_rate}")
        return fx_rate

    # Fetch exchange rate and update cache
    for provider in providers:
        pname = provider.__name__
        try:
            fx_rate = provider.fx_rate(src, dst)
            if not fx_rate > 0:
                raise ValueError(f"Invalid exchange rate from {pname}: {fx_rate}")
            cache.set(key, fx_rate, timeout=config.FX_TIMEOUT)
            log.debug(f"Updated exchange rate {key} to {fx_rate} via {pname}")
            return fx_rate
        except Exception as e:
            log.error(f"Failed to fetch exchange rate from {pname}: {e}")

    raise lnp.ExchangeApiError("Could not aquire exchange rate from any provider!")
