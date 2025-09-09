from mytonwallet_pay.methods.base import MTWPayBaseMethod
from typing import TYPE_CHECKING

from mytonwallet_pay.types.Invoice import Invoice

if TYPE_CHECKING:
    import mytonwallet_pay

class getInvoice:
    """Get Invoice method"""

    async def get_invoice(
            self: "mytonwallet_pay.MTWPay",
            id: int | None = None,
            user_ton_wallet: int | None = None,
            description: int | None = None,
    ) -> Invoice | None:
        """
        Get Invoice method

        Use this method to get invoice by ID.
        On success, returns :class:`mytonwallet_pay.types.Invoice`.

        :param id: *Optional* invoice ID.
        :param user_ton_wallet: *Optional* The wallet that the payment was made from.
        :param description: *Optional* Text description, will be visible in admin panel
        :return: :class:`mytonwallet_pay.types.Invoice` objects.
        """

        if id: invoices = await self.get_invoices(id=id)
        if description: invoices = await self.get_invoices(description=description)
        if user_ton_wallet: invoices = await self.get_invoices(user_ton_wallet=user_ton_wallet)

        if invoices:
            return invoices[0]
        return None


