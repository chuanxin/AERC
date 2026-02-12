import socketio
from jose import JWTError, jwt

from src.config.settings import SECRET_KEY, JWT_ALGORITHM, REDIS_URL
from src.database.models.user import User

sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=[],
    client_manager=socketio.AsyncRedisManager(REDIS_URL),
)

socket_app = socketio.ASGIApp(sio)


@sio.event
async def connect(sid, environ, auth):
    token = auth.get("token") if auth else None
    if not token:
        raise socketio.exceptions.ConnectionRefusedError("Authentication required")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        username = payload.get("sub")
        user = await User.get_or_none(username=username, is_active=True)
        if not user:
            raise socketio.exceptions.ConnectionRefusedError("User not found")
        await sio.save_session(sid, {"user_id": user.id, "username": username})
    except JWTError:
        raise socketio.exceptions.ConnectionRefusedError("Invalid token")


@sio.event
async def join_auction(sid, data):
    auction_id = data.get("auction_id")
    if auction_id:
        await sio.enter_room(sid, f"auction:{auction_id}")


@sio.event
async def leave_auction(sid, data):
    auction_id = data.get("auction_id")
    if auction_id:
        await sio.leave_room(sid, f"auction:{auction_id}")


@sio.event
async def disconnect(sid):
    pass
