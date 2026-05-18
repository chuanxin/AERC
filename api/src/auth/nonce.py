from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from tortoise.exceptions import IntegrityError as TortoiseIntegrityError

from src.database.models import AuthNonce


def _auth_error(code: str, message: str) -> dict:
    return {"error_code": code, "message": message}


async def validate_and_store_nonce(nonce: str, timestamp_ms: int) -> None:
    """驗證 timestamp 在 ±5 分鐘內且 nonce 未被使用；通過後儲存 nonce 並清理過期記錄。
    任何防重放條件不符均拋出 HTTP 400 REPLAY_ATTACK_DETECTED。
    """
    now = datetime.now(timezone.utc)
    now_ms = int(now.timestamp() * 1000)

    # 1. timestamp 驗證（±300 秒 / 300,000 毫秒）
    if abs(now_ms - timestamp_ms) > 300_000:
        raise HTTPException(
            status_code=400,
            detail=_auth_error("REPLAY_ATTACK_DETECTED", "請求已失效，請重新操作"),
        )

    # 2. nonce 唯一性查詢
    if await AuthNonce.filter(nonce=nonce, expires_at__gte=now).exists():
        raise HTTPException(
            status_code=400,
            detail=_auth_error("REPLAY_ATTACK_DETECTED", "請求已失效，請重新操作"),
        )

    # 3. 儲存 nonce（有效期 10 分鐘）；捕獲並發競態的 DB UNIQUE 衝突
    try:
        await AuthNonce.create(nonce=nonce, expires_at=now + timedelta(minutes=10))
    except TortoiseIntegrityError:
        raise HTTPException(
            status_code=400,
            detail=_auth_error("REPLAY_ATTACK_DETECTED", "請求已失效，請重新操作"),
        )

    # 4. 懶惰清理過期 nonce
    await AuthNonce.filter(expires_at__lt=now).delete()
