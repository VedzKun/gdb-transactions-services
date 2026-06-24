from pydantic.dataclasses import dataclass
from pydantic import Field, ConfigDict
from typing import Optional
from datetime import datetime
from decimal import Decimal


@dataclass
class TransferLimitBase:
    daily_limit: Decimal = Field(..., ge=0)
    monthly_limit: Decimal = Field(..., ge=0)
    per_transaction_limit: Decimal = Field(..., ge=0)


@dataclass
class TransferLimitCreate(TransferLimitBase):
    privilege: Optional[str] = None


@dataclass(config=ConfigDict(from_attributes=True))
class TransferLimitResponse(TransferLimitBase):
    id: int
    privilege: Optional[str]
    created_at: datetime
    updated_at: datetime


@dataclass
class LimitCheckRequest:
    account_number: int
    amount: Decimal
    privilege: str
