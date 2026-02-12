from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal


class BidCreate(BaseModel):
    amount: Decimal


class BidResponse(BaseModel):
    id: int
    auction_id: int
    user_id: int
    amount: Decimal
    is_winning: bool
    created_at: datetime

    class Config:
        from_attributes = True
