import base64
import os

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from fastapi import HTTPException


def _b64url_decode(s: str) -> bytes:
    padding_needed = (4 - len(s) % 4) % 4
    return base64.urlsafe_b64decode(s + "=" * padding_needed)


def _load_private_key_pem() -> str:
    """優先讀 AUTH_PRIVATE_KEY_PATH（檔案），不存在則 fallback 到 AUTH_PRIVATE_KEY_PEM（環境變數）。"""
    path = os.environ.get("AUTH_PRIVATE_KEY_PATH", "")
    if path:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    pem = os.environ.get("AUTH_PRIVATE_KEY_PEM", "").replace("\\n", "\n")
    if not pem:
        raise ValueError("AUTH_PRIVATE_KEY_PEM not set and AUTH_PRIVATE_KEY_PATH not configured")
    return pem


def get_private_key_by_kid(kid: str):
    """載入 RSA 私鑰；kid 不符則拋出 ValueError。"""
    known_kid = os.environ.get("AUTH_PUBLIC_KEY_KID", "")
    if kid != known_kid:
        raise ValueError(f"Unknown kid: {kid}")
    return load_pem_private_key(_load_private_key_pem().encode(), password=None)


def decrypt_password(
    encrypted_password: str,
    encrypted_key: str,
    iv: str,
    kid: str,
) -> str:
    """Hybrid 解密：RSA-OAEP-SHA256 解 AES 金鑰，AES-GCM 解密碼明文。
    任何解密失敗均轉換為 400 INVALID_ENCRYPTED_FORMAT，不洩漏原始例外。
    解密所得明文不得寫入任何 log 或持久化儲存。
    """
    try:
        private_key = get_private_key_by_kid(kid)

        aes_key_bytes = private_key.decrypt(
            _b64url_decode(encrypted_key),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )

        aesgcm = AESGCM(aes_key_bytes)
        plaintext = aesgcm.decrypt(
            _b64url_decode(iv),
            _b64url_decode(encrypted_password),
            None,
        )
        return plaintext.decode("utf-8")

    except (ValueError, InvalidTag, Exception):
        raise HTTPException(
            status_code=400,
            detail={"error_code": "INVALID_ENCRYPTED_FORMAT", "message": "請求格式不符，解密失敗"},
        )
