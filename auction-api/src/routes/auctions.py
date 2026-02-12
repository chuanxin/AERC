from fastapi import APIRouter, Depends, HTTPException, Query

from src.auth.jwthandler import get_current_user
from src.auth.permissions import require_seller
from src.database.models.user import User
from src.schemas.auction import AuctionCreate, AuctionResponse, AuctionListResponse
from src.services.auction_service import (
    create_auction,
    get_active_auctions,
    get_auction_detail,
    activate_auction,
)

router = APIRouter(prefix="/auctions", tags=["auctions"])


@router.get("", response_model=AuctionListResponse)
async def list_auctions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category_id: int | None = None,
):
    items, total = await get_active_auctions(page, page_size, category_id)
    return AuctionListResponse(
        items=[AuctionResponse.model_validate(a, from_attributes=True) for a in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{auction_id}", response_model=AuctionResponse)
async def get_auction(auction_id: int):
    auction = await get_auction_detail(auction_id)
    if not auction:
        raise HTTPException(status_code=404, detail="Auction not found")
    return auction


@router.post("", response_model=AuctionResponse, status_code=201)
async def create(data: AuctionCreate, user: User = Depends(require_seller)):
    auction = await create_auction(user.id, data)
    return auction


@router.post("/{auction_id}/activate", response_model=AuctionResponse)
async def activate(auction_id: int, user: User = Depends(require_seller)):
    try:
        return await activate_auction(auction_id, user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
