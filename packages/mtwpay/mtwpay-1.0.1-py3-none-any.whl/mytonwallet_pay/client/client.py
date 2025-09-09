from mytonwallet_pay.loggers import client
from mytonwallet_pay.methods import Methods
from mytonwallet_pay.methods.base import MTWPayBaseMethod
from mytonwallet_pay.session.aiohttp import AiohttpSession
from mytonwallet_pay.tools import Tools, token_validate
from mytonwallet_pay.types.error import APIError


class MTWPay(Methods, Tools):
    """
    The client class for working with the API

    :param token: MyTonWallet Pay API token
    :param project_id: MyTonWallet Pay API Project ID
    """

    def __init__(
            self,
            token: str,
            project_id: int
    ):
        self._token = token
        self._project_id = project_id
        self._session = AiohttpSession()
        self.__auth()

    def __auth(
            self
    ):
        result_auth = token_validate(self)
        if not result_auth:
            raise APIError("Authorization failed", 401)
        client.info("Successful authorization in MyTonWallet Pay API")


    async def __call__(
            self,
            method: MTWPayBaseMethod
    ):
        """
        Request method.

        :param method: MTWPayBaseMethod.
        :return: :class:`mytonwallet_pay.types.MTWPayBaseType` object.
        """
        client.debug(
            "Request: /%s with payload %s",
            method.__class__.__name__,
            method.model_dump_json(),
        )
        if method.__request_type__ == "POST":
            return await self._session.post_request(self, method)
        return await self._session.get_request(self, method)

