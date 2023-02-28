# -*- coding: utf-8 -*-
from typing import Protocol
from decimal import Decimal

__all__ = [
    "FxProvider",
    "Money",
]


class FxProvider(Protocol):
    """Exchange Rate Provider"""

    def fx_rate(self, src: str, dst: str) -> Decimal:
        """Return exchange for source to destination currency"""


class Money(Protocol):
    """Monetary amount"""

    @property
    def amount(self) -> int:
        pass

    @property
    def currency(self) -> str:
        pass
