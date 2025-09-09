from mytonwallet_pay.methods.base import MTWPayBaseMethod
from mytonwallet_pay.types.Project import Project
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import mytonwallet_pay


class getMe:
    """Login method"""

    class getMeMethod(MTWPayBaseMethod[Project]):
        accessToken: str
        projectId: int

        __return_type__ = Project
        __api_method__ = "login"
        __request_type__ = "POST"

    async def get_me(
            self: "mytonwallet_pay.MTWPay"
    ) -> Project:
        """
        getMe method.

        Use this method to get information about your project.
        On success, returns an object of the created :class:`mytonwallet_pay.types.Project`.

        :return: :class:`mytonwallet_pay.types.Project`.
        """
        params = {"accessToken": self._token, "projectId": self._project_id}

        return await self(self.getMeMethod(**params))
