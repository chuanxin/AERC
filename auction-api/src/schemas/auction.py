from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal


class AuctionCreate(BaseModel):
    title: str
    description: str | None = None
    category_id: int | None = None
    starting_price: Decimal
    reserve_price: Decimal | None = None
    bid_increment: Decimal
    start_time: datetime
    end_time: datetime
    auto_extend: bool = True


class AuctionUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    category_id: int | None = None
    reserve_price: Decimal | None = None


class AuctionResponse(BaseModel):
    id: int
    seller_id: int
    title: str
    description: str | None
    category_id: int | None
    starting_price: Decimal
    current_price: Decimal
    bid_increment: Decimal
    bid_count: int
    status: str
    start_time: datetime
    end_time: datetime
    auto_extend: bool
    winner_id: int | None
    created_at: datetime
    images: list[dict] = []

    class Config:
        from_attributes = True


class AuctionListResponse(BaseModel):
    items: list[AuctionResponse]
    total: int
    page: int
    page_size: int
