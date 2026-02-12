import asyncio
from datetime import datetime, timezone

from src.tasks.celery_app import celery_app
from src.database.models.auction import Auction
from src.socket.emitters import broadcast_auction_end


def _run_async(coro):
    """Run async code in Celery sync worker."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(name="end_auction")
def end_auction(auction_id: int):
    """Called by Celery Beat when auction end_time is reached."""
    _run_async(_end_auction(auction_id))


async def _end_auction(auction_id: int):
    auction = await Auction.get_or_none(id=auction_id)
    if not auction or auction.status != "active":
        return

    now = datetime.now(timezone.utc)
    if now < auction.end_time:
        return  # Extended, reschedule

    has_winner = auction.bid_count > 0
    meets_reserve = (
        auction.reserve_price is None
        or auction.current_price >= auction.reserve_price
    )

    if has_winner and meets_reserve:
        auction.status = "sold"
    else:
        auction.status = "ended"
        auction.winner_id = None

    await auction.save()

    await broadcast_auction_end(auction_id, {
        "auction_id": auction_id,
        "status": auction.status,
        "winner_id": auction.winner_id,
        "final_price": str(auction.current_price),
    })
