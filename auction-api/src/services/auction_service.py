from datetime import datetime, timezone

from tortoise.queryset import QuerySet

from src.database.models.auction import Auction, AuctionImage
from src.schemas.auction import AuctionCreate


async def create_auction(seller_id: int, data: AuctionCreate) -> Auction:
    return await Auction.create(
        seller_id=seller_id,
        title=data.title,
        description=data.description,
        category_id=data.category_id,
        starting_price=data.starting_price,
        current_price=data.starting_price,
        reserve_price=data.reserve_price,
        bid_increment=data.bid_increment,
        start_time=data.start_time,
        end_time=data.end_time,
        auto_extend=data.auto_extend,
    )


async def get_active_auctions(
    page: int = 1,
    page_size: int = 20,
    category_id: int | None = None,
) -> tuple[list[Auction], int]:
    qs: QuerySet = Auction.filter(
        status="active",
        end_time__gt=datetime.now(timezone.utc),
    )
    if category_id:
        qs = qs.filter(category_id=category_id)

    total = await qs.count()
    items = await qs.order_by("-created_at").offset((page - 1) * page_size).limit(page_size)
    return items, total


async def get_auction_detail(auction_id: int) -> Auction | None:
    auction = await Auction.get_or_none(id=auction_id)
    if auction:
        auction.images_list = await AuctionImage.filter(auction_id=auction_id).order_by("sort_order")
    return auction


async def activate_auction(auction_id: int, seller_id: int) -> Auction:
    auction = await Auction.get(id=auction_id, seller_id=seller_id)
    if auction.status != "draft":
        raise ValueError("Only draft auctions can be activated")
    auction.status = "active"
    await auction.save()
    return auction
