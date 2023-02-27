# -*- coding: utf-8 -*-
__all__ = ["ln_address_url"]


def ln_address_url(lna: str) -> str:
    name, domain = lna.split("@")
    lnurl = f"https://{domain}/.well-known/lnurlp/{name}"
    return lnurl
