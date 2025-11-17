"""
CAPTCHA 服務模組 - 處理登入驗證碼的生成與驗證

使用資料庫存儲驗證碼，支援多進程（Worker）環境：
- 跨進程共享驗證碼狀態
- 自動過期機制（5分鐘）
- 防止重複使用
"""

import random
import uuid
from datetime import datetime, timedelta, timezone

from ..database.models import Captcha


class CaptchaService:
    """CAPTCHA 服務 - 生成與驗證登入驗證碼（使用資料庫存儲）"""

    # 驗證碼過期時間（分鐘）
    EXPIRE_MINUTES = 5

    @classmethod
    async def generate(cls) -> tuple[str, str]:
        """
        生成新的驗證碼

        Returns:
            Tuple[str, str]: (captcha_id, captcha_code)
        """
        # 生成 4 位數字驗證碼
        captcha_code = ''.join([str(random.randint(0, 9)) for _ in range(4)])

        # 生成唯一的 session ID
        captcha_id = str(uuid.uuid4())

        # 設定過期時間
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=cls.EXPIRE_MINUTES)

        # 清理過期的驗證碼（背景維護）
        await cls._cleanup_expired()

        # 存入資料庫
        await Captcha.create(
            captcha_id=captcha_id,
            captcha_code=captcha_code,
            expires_at=expires_at
        )

        return captcha_id, captcha_code

    @classmethod
    async def verify(cls, captcha_id: str, user_input: str) -> bool:
        """
        驗證使用者輸入的驗證碼

        Args:
            captcha_id: 驗證碼 session ID
            user_input: 使用者輸入的驗證碼

        Returns:
            bool: 驗證是否成功
        """
        # 從資料庫查詢驗證碼
        captcha = await Captcha.filter(captcha_id=captcha_id).first()

        if not captcha:
            return False

        # 檢查是否過期
        if captcha.expires_at < datetime.now(timezone.utc):
            # 過期則刪除
            await captcha.delete()
            return False

        # 驗證碼比對
        if captcha.captcha_code == user_input:
            # 使用後即刪除，防止重複使用
            await captcha.delete()
            return True

        return False

    @classmethod
    async def _cleanup_expired(cls) -> None:
        """清理過期的驗證碼"""
        now = datetime.now(timezone.utc)
        await Captcha.filter(expires_at__lt=now).delete()

    @classmethod
    async def get_cache_size(cls) -> int:
        """取得目前資料庫中的驗證碼數量（用於監控）"""
        return await Captcha.all().count()
