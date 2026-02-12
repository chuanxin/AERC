from fastapi import APIRouter, Depends, HTTPException

from src.auth.jwthandler import get_current_user
from src.database.models.bid import Bid
from src.database.models.user import User
from src.schemas.bid import BidCreate, BidResponse
from src.services.bid_service import place_bid, BidError

router = APIRouter(prefix="/auctions/{auction_id}/bids", tags=["bids"])


@router.post("", response_model=BidResponse, status_code=201)
async def create_bid(
    auction_id: int,
    data: BidCreate,
    user: User = Depends(get_current_user),
):
    try:
        return await place_bid(auction_id, user.id, data.amount)
    except BidError as e:
        status_map = {
            "NOT_FOUND": 404,
            "NOT_ACTIVE": 400,
            "SELF_BID": 403,
            "EXPIRED": 400,
            "TOO_LOW": 422,
        }
        raise HTTPException(
            status_code=status_map.get(e.code, 400),
            detail=e.message,
        )


@router.get("", response_model=list[BidResponse])
async def list_bids(auction_id: int, limit: int = 50):
    bids = await Bid.filter(auction_id=auction_id).order_by("-created_at").limit(limit)
    return bids
