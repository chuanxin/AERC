from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from tortoise.exceptions import IntegrityError as TortoiseIntegrityError

from src.database.models import AuthNonce

# nonce 保存期。042 的入口憑證以此機制做一次性檢查，其正確性依賴「保存期 ≥ 憑證時效上限」：
# 若保存期較短，nonce 先被清掉而憑證仍在時效內，同一顆憑證就能再用一次——不報錯、無痕跡。
# config/portal_sso.py 於啟動時驗證這個關係，縮短此值前務必一併確認。
NONCE_RETENTION_SECONDS = 600


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

    # 3. 儲存 nonce（保存 NONCE_RETENTION_SECONDS）；捕獲並發競態的 DB UNIQUE 衝突
    try:
        await AuthNonce.create(nonce=nonce, expires_at=now + timedelta(seconds=NONCE_RETENTION_SECONDS))
    except TortoiseIntegrityError:
        raise HTTPException(
            status_code=400,
            detail=_auth_error("REPLAY_ATTACK_DETECTED", "請求已失效，請重新操作"),
        )

    # 4. 懶惰清理過期 nonce
    await AuthNonce.filter(expires_at__lt=now).delete()
