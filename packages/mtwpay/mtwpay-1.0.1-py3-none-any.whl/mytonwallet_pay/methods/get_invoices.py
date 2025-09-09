from typing import Optional, TYPE_CHECKING
from mytonwallet_pay.methods.base import MTWPayBaseMethod
from mytonwallet_pay.types.Invoice import Invoice

if TYPE_CHECKING:
    import mytonwallet_pay

class getInvoices:
    """Get Invoices method"""
    class getInvoicesMethod(MTWPayBaseMethod[list[Invoice]]):
        projectId: int
        search: int | str | None = None

        __return_type__ = list[Invoice]
        __api_method__ = "invoices"
        __request_type__ = "GET"

    async def get_invoices(
            self: "mytonwallet_pay.MTWPay",
            limit: int = 50,
            id: Optional[int] = None,
            user_ton_wallet: Optional[str] = None,
            description: Optional[str] = None,
    ) -> list[Invoice]:
        """
        Get Invoices method

        Use this method to get invoices.
        On success, returns array of :class:`mytonwallet_pay.types.Invoice`.

        :param limit: *Optional*. Number of invoices. Defaults to 50.
        :param id: *Optional*. invoice ID.
        :param user_ton_wallet: *Optional*. The wallet that the payment was made from.
        :param description: *Optional*. Text description, will be visible in admin panel
        :return: List of :class:`mytonwallet_pay.types.Invoice` objects.
        """
        params = locals()
        params['projectId'] = self._project_id

        if id: params['search'] = id
        if user_ton_wallet: params['search'] = user_ton_wallet
        if description: params['search'] = description

        params.pop('user_ton_wallet')
        params.pop('description')
        params.pop('id')

        return await self(self.getInvoicesMethod(**params))

