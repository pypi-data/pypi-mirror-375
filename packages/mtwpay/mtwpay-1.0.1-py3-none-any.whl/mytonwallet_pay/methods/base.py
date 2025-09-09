from abc import ABC
from typing import ClassVar, Generic, TypeVar, Type
from pydantic import BaseModel, ConfigDict


T = TypeVar("T")

class MTWPayBaseMethod(BaseModel, ABC, Generic[T]):
    """Base MyTonWallet Pay API method class."""

    model_config = ConfigDict(
        extra="ignore",
        frozen=True,
    )

    __return_type__: Type[T]
    __api_method__: ClassVar[str]
    __request_type__: ClassVar[str]
