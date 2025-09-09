import ssl
from typing import TYPE_CHECKING
import certifi
from aiohttp import ClientSession, TCPConnector
from pydantic import ValidationError
from mytonwallet_pay.methods.base import MTWPayBaseMethod
from mytonwallet_pay.types.base import Response
from mytonwallet_pay.types.error import APIError

if TYPE_CHECKING:
    import mytonwallet_pay


class AiohttpSession:
    """HTTP session on aiohttp"""

    def __init__(self):
        self.base_url = "https://pay.mytonwallet.io/api/v1/{method}"
        self._session: ClientSession | None = None

    async def post_request(
            self,
            mtw_pay: "mytonwallet_pay.MTWPay",
            method: "MTWPayBaseMethod"
    ):
        """Make POST http request."""

        ssl_context = ssl.create_default_context(cafile=certifi.where())
        self._session = ClientSession(
            connector=TCPConnector(
                ssl_context=ssl_context,
            ),
        )
        async with self._session as session:
            resp = await session.post(
                url=self.base_url.format(method=method.__api_method__),
                json=method.model_dump(exclude_none=True),
                headers={
                    "X-Project-Api-Key": mtw_pay._token,
                    "Content-Type": "application/json"
                },
            )
            response = self.check_response(mtw_pay, method, await resp.json())
        return response.result

    async def get_request(
            self,
            mtw_pay: "mytonwallet_pay.MTWPay",
            method: "MTWPayBaseMethod"
    ):
        """Make GET http request."""

        ssl_context = ssl.create_default_context(cafile=certifi.where())
        self._session = ClientSession(
            connector=TCPConnector(
                ssl_context=ssl_context,
            ),
        )
        async with self._session as session:
            resp = await session.get(
                url=self.base_url.format(method=method.__api_method__),
                params=method.model_dump(exclude_none=True),
                headers={
                    "X-Project-Api-Key": mtw_pay._token
                },
            )
            response = self.check_response(mtw_pay, method, await resp.json())
        return response.result

    def check_response(
            self,
            mtw_pay_client: "mytonwallet_pay.MTWPay",
            method: "MTWPayBaseMethod",
            result: dict
    ):
        try:
            response = Response[method.__return_type__].model_validate(
                result,
                context={"client": mtw_pay_client},
            )
        except ValidationError as e:
            raise APIError(message=e)


        if not response.ok:
            error_message: str = response.message
            raise APIError(message=error_message)
        return response


