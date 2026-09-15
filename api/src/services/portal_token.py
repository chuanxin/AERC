"""智慧灌溉入口平台登入憑證的驗證（042 US3，FR-006～FR-008）

憑證**不是標準 JWT**（research.md R1）：Header 帶 iv、Payload 是 AES-CBC 密文、Signature 是
HMAC-SHA256 的十六進位字串。既有 JWT 函式庫一個都用不上，因此手刻，步驟與客戶參考實作
`JwtHelper.ValidateCustomTestJwtToken` + `CryptoHelper.cs` 逐步對齊：

    1. 拆三段                      → format
    2. 解 header 取 iv             → header
    3. HMAC 比對簽章（先驗後解）   → signature
    4. AES-CBC 解密 + PKCS7 去填充 → decrypt
    5. 解析 payload JSON 與必要欄位 → payload
    6. 時效：已過期／超過設定上限  → expired / max_age
    7. 目標系統與發行者             → audience / issuer
    8. 一次性（nonce）              → replay

與參考實作刻意不同的兩處（皆為從嚴）：參考實作不驗 issuer、不限制時效上限。

## 失敗步驟只給診斷，不給呼叫端

`PortalTokenError.step` 只寫進伺服器診斷日誌與本地互通測試夾具的輸出。對外回應一律同一句話，
不透露失敗在哪一步——否則端點就成了驗證預言機。

填充預言（padding oracle）在結構上不存在：先比對簽章、通過才解密（encrypt-then-MAC），
不知道金鑰就產生不出能走到解密那一步的密文（research.md R3）。

## 解碼邏輯與金鑰來源無關

`decode_portal_token()` 是純函式，金鑰由參數傳入。自產測試金鑰與客戶正式金鑰走的是同一段
程式碼；客戶素材到齊後驗證的是「能否與對方互通」，不是重測這段邏輯（見 tests/sso_interop_fixture.py）。
"""

import base64
import hashlib
import hmac
import json
import logging
import time
from dataclasses import dataclass
from typing import Optional

from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from fastapi import HTTPException

from src.auth.nonce import validate_and_store_nonce
from src.config.portal_sso import encryption_key_from, portal_sso_settings, signing_key_from

logger = logging.getLogger(__name__)

_IV_HEX_LENGTH = 32            # 16 bytes
_AES_BLOCK_BYTES = 16
_MAX_TOKEN_LENGTH = 8192       # 正常憑證數百字元；上限只為拒絕異常輸入，不影響合法憑證
_MAX_EXTERNAL_ID_LENGTH = 64   # SsoIdentity.external_id CharField(64)
_MAX_EMAIL_LENGTH = 255        # Users.email CharField(255)
_REQUIRED_STRING_CLAIMS = ("id", "email", "issuer", "audience")


class PortalTokenError(Exception):
    """憑證驗證未通過。`step` 與 `detail` 僅供診斷，不得出現在對外回應。

    `detail` 不得包含憑證原文或金鑰（FR-040）。
    """

    def __init__(self, step: str, detail: str) -> None:
        super().__init__(f"{step}: {detail}")
        self.step = step
        self.detail = detail


@dataclass(frozen=True)
class PortalTokenParts:
    header: str
    payload: str
    signature: str


@dataclass(frozen=True)
class PortalClaims:
    """憑證所載的使用者身分。`external_id` 即 payload 的 `id`（入口平台帳號識別）。"""
    external_id: str
    name: str
    email: str
    issuer: str
    audience: str
    exp: int


# ---------------------------------------------------------------------------
# 各步驟（互通測試夾具逐步呼叫以輸出可歸因的診斷；正式路徑由 decode_portal_token 串接）
# ---------------------------------------------------------------------------

def b64url_decode(segment: str) -> bytes:
    """base64url 解碼，自行補齊等號（對齊 CryptoHelper.DecodeBase64UrlToBytes）。

    長度除以 4 餘 1 在 base64 中不可能合法，C# 端會在 FromBase64String 拋例外；這裡同樣拒絕。
    """
    if len(segment) % 4 == 1:
        raise ValueError("base64url 長度不合法")
    padded = segment.replace("-", "+").replace("_", "/") + "=" * (-len(segment) % 4)
    return base64.b64decode(padded, validate=True)


def split_token(token: Optional[str]) -> PortalTokenParts:
    if not token:
        raise PortalTokenError("format", "未提供憑證")
    if len(token) > _MAX_TOKEN_LENGTH:
        raise PortalTokenError("format", f"憑證長度 {len(token)} 超過上限 {_MAX_TOKEN_LENGTH}")
    parts = token.split(".")
    if len(parts) != 3 or not all(parts):
        raise PortalTokenError("format", f"憑證應為三段，實際為 {len(parts)} 段或含空段")
    return PortalTokenParts(*parts)


def parse_header_iv(header_segment: str) -> bytes:
    try:
        header = json.loads(b64url_decode(header_segment).decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        raise PortalTokenError("header", "header 不是合法的 base64url JSON")
    iv_hex = header.get("iv") if isinstance(header, dict) else None
    if not isinstance(iv_hex, str) or len(iv_hex) != _IV_HEX_LENGTH:
        raise PortalTokenError("header", f"header 缺少 iv，或 iv 不是 {_IV_HEX_LENGTH} 個十六進位字元")
    try:
        return bytes.fromhex(iv_hex)
    except ValueError:
        raise PortalTokenError("header", "iv 含非十六進位字元")


def verify_signature(parts: PortalTokenParts, signing_key: bytes) -> None:
    """HMAC-SHA256(header + "." + payload)，十六進位比對不分大小寫（對齊 OrdinalIgnoreCase）。"""
    message = f"{parts.header}.{parts.payload}".encode("utf-8")
    expected = hmac.new(signing_key, message, hashlib.sha256).hexdigest().encode("ascii")
    presented = parts.signature.lower().encode("utf-8")
    if not hmac.compare_digest(expected, presented):
        raise PortalTokenError("signature", "簽章不符")


def decrypt_payload(payload_segment: str, encryption_key: bytes, iv: bytes) -> bytes:
    """AES-CBC 解密後以 PKCS7 去填充（函式庫實作，不手寫）。

    明文長度恰為 16 的整數倍時，PKCS7 會多附加一整個 0x10 區塊——手寫去填充最容易錯的案例，
    由互通測試夾具的 --self-test 涵蓋。
    """
    try:
        ciphertext = b64url_decode(payload_segment)
    except ValueError:
        raise PortalTokenError("decrypt", "payload 不是合法的 base64url")
    if not ciphertext or len(ciphertext) % _AES_BLOCK_BYTES:
        raise PortalTokenError("decrypt", f"密文長度 {len(ciphertext)} 不是 AES 區塊大小的正整數倍")

    decryptor = Cipher(algorithms.AES(encryption_key), modes.CBC(iv)).decryptor()
    padded = decryptor.update(ciphertext) + decryptor.finalize()
    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    try:
        return unpadder.update(padded) + unpadder.finalize()
    except ValueError:
        raise PortalTokenError("decrypt", "去填充失敗（金鑰或 iv 不符的典型症狀）")


def parse_claims(plaintext: bytes) -> PortalClaims:
    try:
        claims = json.loads(plaintext.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        raise PortalTokenError("payload", "解出的內容不是合法的 UTF-8 JSON")
    if not isinstance(claims, dict):
        raise PortalTokenError("payload", "解出的 JSON 不是物件")

    missing = [key for key in _REQUIRED_STRING_CLAIMS if not isinstance(claims.get(key), str) or not claims[key].strip()]
    if missing:
        raise PortalTokenError("payload", f"缺少或型別不符的欄位：{', '.join(missing)}")
    exp = claims.get("exp")
    # bool 是 int 的子類別，true 會被當成 1，須明確排除
    if not isinstance(exp, int) or isinstance(exp, bool):
        raise PortalTokenError("payload", "exp 缺少或不是整數")

    external_id = claims["id"].strip()
    email = claims["email"].strip()
    # 超長值會在後續 ORM 查詢觸發 ValidationError 冒成 500，在此攔下
    if len(external_id) > _MAX_EXTERNAL_ID_LENGTH or len(email) > _MAX_EMAIL_LENGTH:
        raise PortalTokenError("payload", "id 或 email 超過長度上限")

    name = claims.get("name")
    return PortalClaims(
        external_id=external_id,
        name=name.strip() if isinstance(name, str) else "",
        email=email,
        issuer=claims["issuer"],
        audience=claims["audience"],
        exp=exp,
    )


def check_time(claims: PortalClaims, now_epoch: int, max_token_age_seconds: int) -> None:
    # 參考實作為 exp < now 才算過期，exp == now 仍有效，與之一致
    if claims.exp < now_epoch:
        raise PortalTokenError("expired", f"已過期 {now_epoch - claims.exp} 秒")
    # FR-008：限制憑證遭竊取後的可用窗口。入口預設 5 分鐘；核發時效超過上限者拒收
    remaining = claims.exp - now_epoch
    if remaining > max_token_age_seconds:
        raise PortalTokenError("max_age", f"剩餘時效 {remaining} 秒超過上限 {max_token_age_seconds} 秒")


def check_target(claims: PortalClaims, audience: str, issuer: str) -> None:
    # 發行者、目標系統皆非機密，診斷時列出實際值，方便歸因「入口改了字面值卻未通知」這類問題
    if claims.audience != audience:
        raise PortalTokenError("audience", f"audience 為 {claims.audience!r}，預期 {audience!r}")
    if claims.issuer != issuer:
        raise PortalTokenError("issuer", f"issuer 為 {claims.issuer!r}，預期 {issuer!r}")


# ---------------------------------------------------------------------------
# 組合
# ---------------------------------------------------------------------------

def decode_portal_token(
    token: Optional[str],
    *,
    secret: str,
    audience: str,
    issuer: str,
    max_token_age_seconds: int,
    now_epoch: Optional[int] = None,
) -> PortalClaims:
    """步驟 1–7（不含一次性檢查）。純函式，不觸碰資料庫。"""
    parts = split_token(token)
    iv = parse_header_iv(parts.header)
    verify_signature(parts, signing_key_from(secret))
    plaintext = decrypt_payload(parts.payload, encryption_key_from(secret), iv)
    claims = parse_claims(plaintext)
    check_time(claims, int(time.time()) if now_epoch is None else now_epoch, max_token_age_seconds)
    check_target(claims, audience, issuer)
    return claims


def token_reference(token: Optional[str]) -> str:
    """憑證的雜湊前綴，供日誌與稽核關聯同一顆憑證，不留存原文（FR-040）。"""
    return hashlib.sha256((token or "").encode("utf-8")).hexdigest()[:16]


async def verify_portal_token(token: Optional[str]) -> PortalClaims:
    """以目前設定完整驗證一顆憑證，含一次性檢查（步驟 1–8）。

    未設定共用金鑰時一律拒絕（fail-closed），整合尚未啟用不是設定錯誤。
    """
    if not portal_sso_settings.is_configured:
        raise PortalTokenError("not_configured", "PORTAL_SSO_SECRET 未設定，整合尚未啟用")

    claims = decode_portal_token(
        token,
        secret=portal_sso_settings.secret,
        audience=portal_sso_settings.audience,
        issuer=portal_sso_settings.issuer,
        max_token_age_seconds=portal_sso_settings.max_token_age_seconds,
    )

    # 一次性檢查放在最後：只有完全合法的憑證才佔用 nonce，否則任何人都能用垃圾輸入灌爆 nonce 表。
    # nonce 取簽章段的 SHA-256——存雜湊而非簽章原文，避免憑證素材落入另一張表（FR-040）。
    # 傳入「現在」作為時間戳：時效已由步驟 6 以憑證自身的 exp 檢查過，這裡只借用唯一性保證。
    # 保存期 ≥ 時效上限的前提由 config/portal_sso.py 於啟動時驗證。
    signature = token.rsplit(".", 1)[1].lower()
    nonce = hashlib.sha256(signature.encode("utf-8")).hexdigest()
    try:
        await validate_and_store_nonce(nonce, int(time.time() * 1000))
    except HTTPException:
        raise PortalTokenError("replay", "憑證已使用過")
    return claims
