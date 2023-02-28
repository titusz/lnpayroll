__all__ = [
    "ExchangeApiError",
    "InvalidPaymentAddress",
    "PaymentError",
]


class LnPayrollExeption(Exception):
    pass


class ExchangeApiError(LnPayrollExeption):
    pass


class InvalidPaymentAddress(LnPayrollExeption):
    pass


class PaymentError(LnPayrollExeption):
    pass
