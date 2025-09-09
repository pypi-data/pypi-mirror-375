from pydantic import BaseModel, PrivateAttr, ConfigDict
from typing import TYPE_CHECKING, Optional, Generic, TypeVar


if TYPE_CHECKING:
    import mytonwallet_pay


class MTWPayBaseType(BaseModel):
    """Base object"""

    _client: Optional["mytonwallet_pay.MTWPay"] = PrivateAttr()

    model_config = ConfigDict(
        extra="ignore",
        arbitrary_types_allowed=True,
        populate_by_name=True
    )

    def model_post_init(self, ctx: dict) -> None:
        self._client = ctx.get("client")


T = TypeVar("T")

class Response(BaseModel, Generic[T]):
    """API response model."""

    ok: bool
    result: T | list[T] | None = None
    error: Optional[str] = None
    message: Optional[str] = None
    details: Optional[list] = None

