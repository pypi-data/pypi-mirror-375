import datetime
from typing import Optional, Union
from pydantic import BaseModel, field_validator
from mytonwallet_pay.types.InvoiceStatus import InvoiceStatus


class Invoice(BaseModel):
    """Invoice object"""
    createdAt: datetime.datetime | str
    """Creation date"""
    id: Optional[int]
    """Invoice ID"""
    projectId: Optional[int]
    """Project ID"""
    amount: Optional[int]
    """Invoice amount"""
    coin: Optional[str]
    """Invoice asset"""
    amountUsd: Optional[str]
    """Invoice amount in USD"""
    validUntil: Optional[Union[datetime.datetime, str]]
    """Validity date"""
    description: Optional[str]
    """Previously provided data for this invoice"""
    status: Optional[Union[InvoiceStatus, str]] = None
    """Invoice status"""
    invoiceLink: Optional[str] = None
    """Payment link"""
    paidByAddress:  Optional[str] = None
    """The address from which the payment was made"""
    txId:  Optional[str] = None
    """TON blockchain transaction ID"""

    @field_validator("createdAt", "validUntil", mode="before")
    @classmethod
    def parse_datetime(cls, v):
        """Преобразование строки в datetime object"""
        if isinstance(v, str):
            return datetime.datetime.fromisoformat(v)
        return v
