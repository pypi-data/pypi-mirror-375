import datetime
from typing import Optional

from mytonwallet_pay.methods.base import MTWPayBaseMethod
from mytonwallet_pay.session.aiohttp import AiohttpSession
from mytonwallet_pay.types.Coin import Asset, LiteralAsset
from mytonwallet_pay.types.Invoice import Invoice
from mytonwallet_pay.types.Project import Project
from mytonwallet_pay.types.base import MTWPayBaseType
from mytonwallet_pay.types.error import APIError


class MTWPay:
    _token: str
    _project_id: int
    _session: AiohttpSession

    def __init__(self, token: str, project_id: int) -> None: ...
    def __call__(self, method: MTWPayBaseMethod) -> MTWPayBaseType: ...
    def __auth(self) -> Optional[APIError]: ...

    async def create_invoice(
        self,
        amount: int,
        coin: Asset | LiteralAsset | str,
        validUntil: datetime.datetime,
        description: Optional[str] = None,
    ) -> Invoice: ...

    async def get_invoices(
        self,
        limit: int = 50,
        id: Optional[int] = None,
        user_ton_wallet: Optional[str] = None,
        description: Optional[str] = None,
    ) -> list[Invoice]: ...

    async def get_me(self) -> Project: ...

    async def get_invoice(
        self,
        id: int | None = ...,
        user_ton_wallet: int | None = ...,
        description: int | None = ...,
    ) -> Invoice | None: ...