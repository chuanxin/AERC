import base64
import copy
import os
import secrets

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

GRANT_PII_FIELDS = frozenset({"applicant_name", "applicant_id", "applicant_phone", "applicant_phone2", "address"})
# 含前端原始鍵名（name/id/phone/phone2），供 grant_history 遮罩使用
GRANT_PII_HISTORY_FIELDS = GRANT_PII_FIELDS | {"name", "id", "phone", "phone2"}


class DataEncryptionService:
    PREFIX = "ENC:v1:"

    def __init__(self) -> None:
        raw = os.environ.get("DATA_ENCRYPTION_KEY", "")
        if not raw:
            raise ValueError(
                "DATA_ENCRYPTION_KEY 環境變數未設定。"
                "服務需要 32-byte AES-256 金鑰（hex 或 base64 格式）。"
            )
        key_bytes = self._parse_key(raw)
        if len(key_bytes) != 32:
            raise ValueError(
                f"DATA_ENCRYPTION_KEY 長度不正確：期望 32 bytes，實際 {len(key_bytes)} bytes。"
                "請提供 64 個 hex 字元或 44 個 base64 字元（無填充）的金鑰。"
            )
        self._aesgcm = AESGCM(key_bytes)

    @staticmethod
    def _parse_key(raw: str) -> bytes:
        raw = raw.strip()
        if len(raw) == 64 and all(c in "0123456789abcdefABCDEF" for c in raw):
            return bytes.fromhex(raw)
        padding_needed = (4 - len(raw) % 4) % 4
        return base64.b64decode(raw + "=" * padding_needed)

    def encrypt(self, plaintext: str | None) -> str | None:
        """None 或空字串直通不加密。每次呼叫生成新的隨機 nonce。"""
        if not plaintext:
            return plaintext
        nonce = secrets.token_bytes(12)
        ciphertext_with_tag = self._aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)
        payload = base64.urlsafe_b64encode(nonce + ciphertext_with_tag).rstrip(b"=").decode("ascii")
        return self.PREFIX + payload

    def decrypt(self, value: str | None) -> str | None:
        """不以 PREFIX 開頭的值視為明文直通（遷移期兼容）。解密失敗拋出 ValueError。"""
        if not value:
            return value
        if not value.startswith(self.PREFIX):
            return value
        payload_b64 = value[len(self.PREFIX):]
        padding_needed = (4 - len(payload_b64) % 4) % 4
        payload = base64.urlsafe_b64decode(payload_b64 + "=" * padding_needed)
        nonce = payload[:12]
        ciphertext_with_tag = payload[12:]
        plaintext_bytes = self._aesgcm.decrypt(nonce, ciphertext_with_tag, None)
        return plaintext_bytes.decode("utf-8")

    def is_encrypted(self, value: str | None) -> bool:
        return bool(value and value.startswith(self.PREFIX))

    def encrypt_jsonb_pii(self, steps_data: dict) -> dict:
        """加密 steps['1'] 中的 PII 欄位，返回新的 dict（不修改輸入）。"""
        result = copy.deepcopy(steps_data)
        step1 = result.get("1")
        if not isinstance(step1, dict):
            return result
        for key in GRANT_PII_FIELDS:
            if key in step1 and step1[key] is not None:
                step1[key] = self.encrypt(step1[key])
        return result

    def decrypt_jsonb_pii(self, steps_data: dict) -> dict:
        """解密 steps['1'] 中的 PII 欄位，返回新的 dict（不修改輸入）。
        任一欄位 auth_tag 驗證失敗時拋出 ValueError，包含失敗欄位名稱。
        """
        result = copy.deepcopy(steps_data)
        step1 = result.get("1")
        if not isinstance(step1, dict):
            return result
        for key in GRANT_PII_FIELDS:
            if key in step1 and step1[key] is not None:
                try:
                    step1[key] = self.decrypt(step1[key])
                except Exception as exc:
                    raise ValueError(f"JSONB PII 欄位 '{key}' 解密失敗") from exc
        return result


data_encryption_service = DataEncryptionService()
