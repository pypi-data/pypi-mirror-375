import datetime
from typing import Optional, TYPE_CHECKING

from pydantic import field_validator

from mytonwallet_pay.methods.base import MTWPayBaseMethod
from mytonwallet_pay.types.Coin import Coin, Asset
from mytonwallet_pay.types.Invoice import Invoice
from mytonwallet_pay.types.error import APIError

if TYPE_CHECKING:
    import mytonwallet_pay


class createInvoice:
    """Create Invoice method"""
    class createInvoiceMethod(MTWPayBaseMethod[Invoice]):
        amount: str
        coin: str
        validUntil: str
        projectId: int
        description: Optional[str] = None

        __return_type__ = Invoice
        __api_method__ = "invoices"
        __request_type__ = "POST"

        @field_validator("validUntil", mode="before")
        @classmethod
        def parse_datetime(cls, v):
            if isinstance(v, datetime.datetime):
                return v.isoformat()
            return v

        @field_validator("amount", mode="before")
        @classmethod
        def parse_amount(cls, v):
            if isinstance(v, int):
                return str(v)
            return v


        @field_validator("coin", mode="before")
        @classmethod
        def parse_coin(cls, v):
            if v == "TON":
                return Coin.ton
            return Coin.usdt

    async def create_invoice(
            self: "mytonwallet_pay.MTWPay",
            amount: int,
            coin: Asset | str,
            validUntil: datetime.datetime | str,
            description: Optional[str] = None,
    ) -> Invoice:
        """
        Create Invoice method.

        Use this method to create a new invoice.
        On success, returns an object of the created :class:`mytonwallet_pay.types.Invoice`.

        :param amount: integer invoice amount in decimals. If the invoice currency is TON, the amount in TON should be multiplied by 10^9, if in USDT - by 10^6.
        :param coin: ton or jetton address.
        :param validUntil: date until invoice is valid.
        :param description: *Optional*. text description, will be visible in admin panel. Limited to 200 symbols.
        :return: :class:`mytonwallet_pay.types.Invoice`.
        """
        params = locals()
        params['projectId'] = self._project_id

        return await self(self.createInvoiceMethod(**params))


