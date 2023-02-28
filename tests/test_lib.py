# -*- coding: utf-8 -*-
import pytest
import lnpayroll as lnp


def test_decode_payment_address_empty():
    with pytest.raises(lnp.InvalidPaymentAddress):
        lnp.decode_payment_address("")


def test_decode_payment_address_raw():
    assert (
        lnp.decode_payment_address("https://example.com/ln") == "https://example.com/ln"
    )


def test_decode_payment_address_lnurlp():
    assert (
        lnp.decode_payment_address("lnurlp://example.com/ln")
        == "https://example.com/ln"
    )


def test_decode_payment_address_lnaddress():
    assert (
        lnp.decode_payment_address("ln@example.com")
        == "https://example.com/.well-known/lnurlp/ln"
    )


def test_decode_payment_address_bech32():
    b = "lnurl1dp68gurn8ghj7ampd3kx2ar0veekzar0wd5xjtnrdakj7tnhv4kxctttdehhwm30d3h82unvwqhkv6tcv4j8gmmhv4erqdg7u5nxk"
    assert (
        lnp.decode_payment_address(b)
        == "https://walletofsatoshi.com/.well-known/lnurlp/fixedtower05"
    )
