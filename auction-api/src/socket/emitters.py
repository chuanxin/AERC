from src.socket.server import sio


async def broadcast_bid_update(auction_id: int, bid_data: dict):
    await sio.emit("bid_update", bid_data, room=f"auction:{auction_id}")


async def broadcast_auction_end(auction_id: int, result: dict):
    await sio.emit("auction_ended", result, room=f"auction:{auction_id}")
