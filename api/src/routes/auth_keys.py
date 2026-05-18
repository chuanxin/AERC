import base64
import os

from cryptography.hazmat.primitives.serialization import (
    Encoding,
    PublicFormat,
    load_pem_private_key,
)
from fastapi import APIRouter, HTTPException

router = APIRouter(tags=["Auth Keys"])


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


@router.get("/auth/public-key")
async def get_public_key():
    """Tier A 公開端點：回傳當前有效 RSA 公鑰與 kid（供前端 Hybrid Encryption 使用）。"""
    pem = os.environ.get("AUTH_PRIVATE_KEY_PEM", "").replace("\\n", "\n")
    kid = os.environ.get("AUTH_PUBLIC_KEY_KID", "")

    if not pem or not kid:
        raise HTTPException(
            status_code=503,
            detail={"error_code": "KEY_NOT_CONFIGURED", "message": "伺服器金鑰尚未設定，請聯繫管理員"},
        )

    try:
        private_key = load_pem_private_key(pem.encode(), password=None)
        public_key_der = private_key.public_key().public_bytes(Encoding.DER, PublicFormat.SubjectPublicKeyInfo)
    except Exception:
        raise HTTPException(
            status_code=503,
            detail={"error_code": "KEY_NOT_CONFIGURED", "message": "伺服器金鑰設定錯誤，請聯繫管理員"},
        )

    return {
        "kid": kid,
        "public_key": _b64url_encode(public_key_der),
        "algorithm": "RSA-OAEP-SHA256",
    }
