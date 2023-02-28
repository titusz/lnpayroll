# -*- coding: utf-8 -*-
from typing import Protocol
from decimal import Decimal

__all__ = ["FxProvider"]


class FxProvider(Protocol):
    """Exchange Rate Provider"""

    def fx_rate(self, src: str, dst: str) -> Decimal:
        """Return exchange for source to destination currency"""
