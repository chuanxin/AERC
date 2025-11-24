"""
CAPTCHA 服務模組 - 使用 HMAC Token 的無狀態實現

完全無狀態設計，支援多進程環境：
- 使用 HMAC 簽名確保 Token 不可偽造
- 時間戳驗證確保過期機制
- 無需資料庫或記憶體存儲
"""

import hmac
import hashlib
import random
import base64
from datetime import datetime, timedelta, timezone
from typing import Tuple
import os


class CaptchaService:
    """CAPTCHA 服務 - 無狀態 HMAC Token 實現"""

    # 驗證碼過期時間（分鐘）
    EXPIRE_MINUTES = 5

    # HMAC 密鑰（生產環境應從環境變數或配置文件讀取）
    _secret_key: bytes = os.environ.get(
        'CAPTCHA_SECRET_KEY',
        'aerc-captcha-secret-key-change-in-production'
    ).encode('utf-8')

    @classmethod
    def generate(cls) -> Tuple[str, str]:
        """
        生成新的驗證碼（同步方法，無狀態）

        Returns:
            Tuple[str, str]: (captcha_token, captcha_code)
            - captcha_token: 包含 HMAC 簽名的 token（傳給前端保存）
            - captcha_code: 4 位數字驗證碼（顯示給用戶）
        """
        # 生成 4 位數字驗證碼
        captcha_code = ''.join([str(random.randint(0, 9)) for _ in range(4)])

        # 設定過期時間戳（Unix timestamp）
        expires_at = int((datetime.now(timezone.utc) + timedelta(minutes=cls.EXPIRE_MINUTES)).timestamp())

        # 生成 HMAC 簽名
        # Token 結構: expires_at:signature
        # signature = HMAC(captcha_code + ":" + expires_at, secret_key)
        message = f"{captcha_code}:{expires_at}".encode('utf-8')
        signature = hmac.new(cls._secret_key, message, hashlib.sha256).hexdigest()

        # 組合 token（base64 編碼以便傳輸）
        token_data = f"{expires_at}:{signature}"
        captcha_token = base64.urlsafe_b64encode(token_data.encode('utf-8')).decode('utf-8')

        return captcha_token, captcha_code

    @classmethod
    def verify(cls, captcha_token: str, user_input: str) -> bool:
        """
        驗證使用者輸入的驗證碼（同步方法，無狀態）

        Args:
            captcha_token: 前端傳回的 token（包含過期時間和簽名）
            user_input: 使用者輸入的驗證碼

        Returns:
            bool: 驗證是否成功
        """
        try:
            # 解碼 token
            token_data = base64.urlsafe_b64decode(captcha_token.encode('utf-8')).decode('utf-8')
            parts = token_data.split(':')

            if len(parts) != 2:
                return False

            expires_at_str, original_signature = parts
            expires_at = int(expires_at_str)

            # 檢查是否過期
            now = int(datetime.now(timezone.utc).timestamp())
            if now > expires_at:
                return False

            # 重新計算 HMAC 簽名
            message = f"{user_input}:{expires_at}".encode('utf-8')
            expected_signature = hmac.new(cls._secret_key, message, hashlib.sha256).hexdigest()

            # 使用時間常數比較防止時序攻擊
            if hmac.compare_digest(original_signature, expected_signature):
                return True

            return False

        except (ValueError, TypeError, UnicodeDecodeError):
            return False

    @classmethod
    def set_secret_key(cls, key: str) -> None:
        """
        設定 HMAC 密鑰（用於初始化或測試）

        Args:
            key: 密鑰字串
        """
        cls._secret_key = key.encode('utf-8')
