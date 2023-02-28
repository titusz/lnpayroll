# -*- coding: utf-8 -*-
import lnurl
from django.core.exceptions import ValidationError
from lnurl import LnurlPayResponse
from django.utils.translation import gettext_lazy as _
import lnpayroll as lnp

__all__ = [
    "validate_lnurl",
    "validate_ln_address",
]


def validate_ln_address(value):
    lnurlp = lnp.ln_address_url(value)
    try:
        result = lnurl.get(lnurlp)
    except Exception as e:
        raise ValidationError(
            _("Faled to handle %(value)s: %(e)s"),
            params={"value": value, "e": e},
        )
    if not isinstance(result, LnurlPayResponse):
        raise ValidationError(
            _("%(value)s LNURL is not of type payRequest: %(result)s"),
            params={"value": value, "result": result},
        )


def validate_lnurl(value):
    try:
        result = lnurl.handle(value)
    except Exception as e:
        raise ValidationError(
            _("Faled to handle %(value)s: %(e)s"),
            params={"value": value, "e": e},
        )
    if not isinstance(result, LnurlPayResponse):
        raise ValidationError(
            _("%(value)s LNURL is not of type payRequest: %(result)s"),
            params={"value": value, "result": result},
        )
