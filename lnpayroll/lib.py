# -*- coding: utf-8 -*-
import lnurl
import lnpayroll as lnp

__all__ = [
    "decode_payment_address",
    "ln_address_url",
]


def ln_address_url(lna: str) -> str:
    name, domain = lna.split("@")
    lnurlp = f"https://{domain}/.well-known/lnurlp/{name}"
    return lnurlp


def decode_payment_address(pa):
    # type: (str) -> str
    """Decode LNURLp or Lightning Address to a raw Lightning Service HTTPS url."""

    pa = pa.strip()

    # Raw LNURL (LUD 17)
    if pa.startswith("https://"):
        return pa
    if pa.startswith("lnurlp://"):
        url = pa.replace("lnurlp://", "https://")
        if ".onion" in url:
            raise lnp.InvalidPaymentAddress(url)
        else:
            return url

    # Lightning Address
    if "@" in pa:
        name, domain = pa.split("@")
        return f"https://{domain}/.well-known/lnurlp/{name}"

    # Bech32 LNURL
    try:
        url = str(lnurl.decode(pa))
    except Exception as e:
        raise lnp.InvalidPaymentAddress(f"{e} - {pa}")

    # Validate decoded raw LNURL
    if not url.startswith("https://"):
        raise lnp.InvalidPaymentAddress(pa)

    if url.endswith(".onion"):
        raise lnp.InvalidPaymentAddress(pa)

    return url

