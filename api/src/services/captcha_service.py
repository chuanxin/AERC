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
import io
from datetime import datetime, timedelta, timezone
from typing import Tuple
import os

from PIL import Image, ImageDraw, ImageFont


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
    def generate_image(cls) -> Tuple[str, str, int]:
        """
        生成圖形驗證碼（037-login-captcha-image）：明文不外流，僅回傳圖片與到期秒數

        Returns:
            Tuple[str, str, int]: (captcha_token, captcha_image_data_uri, expires_in_seconds)
        """
        captcha_token, captcha_code = cls.generate()
        captcha_image = cls._render_image(captcha_code)
        expires_in_seconds = cls.EXPIRE_MINUTES * 60
        return captcha_token, captcha_image, expires_in_seconds

    @staticmethod
    def _render_image(code: str) -> str:
        """將驗證碼明文渲染為含視覺干擾的 PNG 圖片，回傳 base64 data URI"""
        width, height = 110, 40
        image = Image.new('RGB', (width, height), (255, 255, 255))
        font = ImageFont.load_default(size=26)

        char_spacing = width // len(code)
        for index, char in enumerate(code):
            char_image = CaptchaService._render_rotated_char(char, font)
            x = index * char_spacing + random.randint(-3, 3)
            y = (height - char_image.height) // 2 + random.randint(-3, 3)
            image.paste(char_image, (x, y), char_image)

        draw = ImageDraw.Draw(image)
        CaptchaService._draw_noise_points(draw, width, height)
        CaptchaService._draw_interference_lines(draw, width, height)

        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        encoded = base64.b64encode(buffer.getvalue()).decode('utf-8')
        return f"data:image/png;base64,{encoded}"

    @staticmethod
    def _render_rotated_char(char: str, font: ImageFont.ImageFont) -> Image.Image:
        """單一字元獨立繪製後隨機旋轉，逐字元變形比整體傾斜更難辨識"""
        char_canvas = Image.new('RGBA', (26, 32), (255, 255, 255, 0))
        draw = ImageDraw.Draw(char_canvas)
        color = (
            random.randint(0, 100),
            random.randint(0, 100),
            random.randint(0, 100),
        )
        draw.text((3, 2), char, font=font, fill=color)
        angle = random.randint(-20, 20)
        return char_canvas.rotate(angle, expand=True, resample=Image.BICUBIC)

    @staticmethod
    def _draw_noise_points(draw: ImageDraw.ImageDraw, width: int, height: int) -> None:
        for _ in range(200):
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)
            gray = random.randint(150, 220)
            draw.point((x, y), fill=(gray, gray, gray))

    @staticmethod
    def _draw_interference_lines(draw: ImageDraw.ImageDraw, width: int, height: int) -> None:
        for _ in range(random.randint(2, 4)):
            start = (random.randint(0, width), random.randint(0, height))
            end = (random.randint(0, width), random.randint(0, height))
            color = (
                random.randint(100, 180),
                random.randint(100, 180),
                random.randint(100, 180),
            )
            draw.line([start, end], fill=color, width=1)

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
