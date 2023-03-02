# -*- coding: utf-8 -*-
import lnpayroll as lnp


def test_max_fee_base_fee(db):
    assert lnp.max_fee(amount_msats=10) == 1000


def test_max_fee_pass_through_fee(db):
    assert lnp.max_fee(amount_msats=4000_000) == 2000
