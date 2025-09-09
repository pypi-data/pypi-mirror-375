from enum import Enum


class InvoiceStatus(str, Enum):
    """Cryptocurrency"""

    awaiting = "awaiting"
    paid = "paid"
    expired = "expired"
