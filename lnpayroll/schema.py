# -*- coding: utf-8 -*-
"""Internal objects"""
from pydantic import BaseModel, Field, condecimal
from decimal import Decimal
from datetime import datetime

__all__ = [
    """FxRate""",
]


class FxRate(BaseModel):
    """Exchange Rate"""

    src: str
    rate: condecimal(gt=Decimal("0"))
    provider: str
    dst: str = Field(default="BTC")
    time: datetime = Field(default_factory=datetime.utcnow)
