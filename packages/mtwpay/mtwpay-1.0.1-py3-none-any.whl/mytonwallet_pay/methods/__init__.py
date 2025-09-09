from .create_invoice import createInvoice
from .get_invoices import getInvoices
from .get_me import getMe

class Methods(
    createInvoice,
    getMe,
    getInvoices
):
    pass


__all__ = [
    "createInvoice",
    "getMe",
    "getInvoices"
]
