"""
CAPTCHA 服務模組 - 處理登入驗證碼的生成與驗證

簡單實用的實現：
- 使用內存緩存存儲驗證碼
- 自動過期機制（5分鐘）
- 線程安全的存取
"""

import random
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Tuple
import threading


class CaptchaService:
    """CAPTCHA 服務 - 生成與驗證登入驗證碼"""

    # 類級別的緩存（單例模式）
    _cache: Dict[str, Tuple[str, datetime]] = {}
    _lock = threading.Lock()

    # 驗證碼過期時間（分鐘）
    EXPIRE_MINUTES = 5

    @classmethod
    def generate(cls) -> Tuple[str, str]:
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

        # 存入緩存
        with cls._lock:
            # 清理過期的驗證碼
            cls._cleanup_expired()

            # 存儲新驗證碼
            cls._cache[captcha_id] = (captcha_code, expires_at)

        return captcha_id, captcha_code

    @classmethod
    def verify(cls, captcha_id: str, user_input: str) -> bool:
        """
        驗證使用者輸入的驗證碼

        Args:
            captcha_id: 驗證碼 session ID
            user_input: 使用者輸入的驗證碼

        Returns:
            bool: 驗證是否成功
        """
        with cls._lock:
            if captcha_id not in cls._cache:
                return False

            captcha_code, expires_at = cls._cache[captcha_id]

            # 檢查是否過期
            if expires_at < datetime.now(timezone.utc):
                # 過期則刪除
                del cls._cache[captcha_id]
                return False

            # 驗證碼比對（使用後即刪除，防止重複使用）
            if captcha_code == user_input:
                del cls._cache[captcha_id]
                return True

            return False

    @classmethod
    def _cleanup_expired(cls) -> None:
        """清理過期的驗證碼（內部方法，需在 lock 內調用）"""
        now = datetime.now(timezone.utc)
        expired_keys = [
            key for key, (_, expires_at) in cls._cache.items()
            if expires_at < now
        ]
        for key in expired_keys:
            del cls._cache[key]

    @classmethod
    def get_cache_size(cls) -> int:
        """取得目前緩存中的驗證碼數量（用於監控）"""
        with cls._lock:
            return len(cls._cache)
