from datetime import datetime, timedelta, timezone
from decimal import Decimal

from tortoise.transactions import in_transaction

from src.config.settings import AUCTION_AUTO_EXTEND_MINUTES
from src.database.models.auction import Auction
from src.database.models.bid import Bid
from src.schemas.bid import BidResponse
from src.socket.emitters import broadcast_bid_update


class BidError(Exception):
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message


async def place_bid(auction_id: int, user_id: int, amount: Decimal) -> BidResponse:
    """
    Atomic bid placement with SELECT FOR UPDATE.
    No race conditions. No partial states.
    """
    async with in_transaction():
        auction = await Auction.select_for_update().get_or_none(id=auction_id)

        if not auction:
            raise BidError("NOT_FOUND", "Auction not found")

        if auction.status != "active":
            raise BidError("NOT_ACTIVE", "Auction is not active")

        if auction.seller_id == user_id:
            raise BidError("SELF_BID", "Cannot bid on your own auction")

        now = datetime.now(timezone.utc)
        if now >= auction.end_time:
            raise BidError("EXPIRED", "Auction has ended")

        min_bid = auction.current_price + auction.bid_increment
        if amount < min_bid:
            raise BidError("TOO_LOW", f"Minimum bid is {min_bid}")

        # Create bid and update auction atomically
        bid = await Bid.create(
            auction_id=auction_id,
            user_id=user_id,
            amount=amount,
            is_winning=True,
        )

        await Bid.filter(
            auction_id=auction_id, is_winning=True
        ).exclude(id=bid.id).update(is_winning=False)

        auction.current_price = amount
        auction.bid_count += 1
        auction.winner_id = user_id

        # Auto-extend if bid placed in final minutes
        if auction.auto_extend:
            remaining = (auction.end_time - now).total_seconds()
            extend_threshold = AUCTION_AUTO_EXTEND_MINUTES * 60
            if remaining < extend_threshold:
                auction.end_time += timedelta(minutes=AUCTION_AUTO_EXTEND_MINUTES)

        await auction.save()

    await broadcast_bid_update(auction_id, {
        "bid_id": bid.id,
        "amount": str(amount),
        "user_id": user_id,
        "bid_count": auction.bid_count,
        "current_price": str(auction.current_price),
        "end_time": auction.end_time.isoformat(),
    })

    return BidResponse(
        id=bid.id,
        auction_id=auction_id,
        user_id=user_id,
        amount=amount,
        is_winning=True,
        created_at=bid.created_at,
    )
