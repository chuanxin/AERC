"""智慧灌溉入口平台 SSO 整合設定（042）

金鑰處理方式由客戶於 2026-09-08 確認：**共用金鑰直接使用，不做任何雜湊處理**。

這個確認在數學上要求金鑰恰為 64 個十六進位字元——內容解密需要一把 32 位元組的
AES 金鑰，在「不做雜湊」的前提下該金鑰只能由共用金鑰本身十六進位解碼取得。客戶自己
的參考實作 JwtHelper.cs 之所以多做一次 SHA-256，作用正是把任意設定值整形成這個形式；
客戶表示不需要那一步，就等同於表示金鑰本身已是該形式。

⚠️ 形式錯誤的症狀極難歸因：HMAC 接受任意長度金鑰，所以**簽章驗證照樣會通過**，只有
AES 解密失敗。表面現象是「簽章對得上卻解不開內容」，第一直覺會往編碼、資料損毀、
AES 模式的方向查，而真因只是一個設定值的形式不對。因此本模組在啟動時就驗證形式並
明確拒絕啟動（FR-006a），不留到每次驗證憑證時才失敗。

同一把金鑰在兩處以**不同方式**轉為位元組，這不是可選項，是參考實作 CryptoHelper.cs
的既定行為（見 specs/042-portal-sso-integration/research.md R2）：

    簽章（HMAC-SHA256）：Encoding.UTF8.GetBytes(KeyStr)  → 十六進位字串的 ASCII，64 bytes
    解密（AES-CBC）    ：HexStringToBytes(KeyStr)         → 十六進位解碼結果，32 bytes
"""

import binascii
import logging
import os
import re

from src.auth.nonce import NONCE_RETENTION_SECONDS

logger = logging.getLogger(__name__)

# 64 個十六進位字元 —— 十六進位解碼後恰為 AES-256 所需的 32 位元組
_SECRET_PATTERN = re.compile(r"^[0-9a-fA-F]{64}$")

# 客戶規格書第 4 頁 payload 範例明定「智慧灌溉入口網固定為 IAMA-PortalWebsite」，
# 全文唯一出現且無衝突值。audience 則相反——客戶文件出現三個互相矛盾的值
# （system-cloud / sys_irr / sys_water），依系統對照表取 sys_irr。
_DEFAULT_AUDIENCE = "sys_irr"
_DEFAULT_ISSUER = "IAMA-PortalWebsite"

# 客戶文件的措辭是「exp：Unix Timestamp **預設** 5 分鐘過期」——預設，不是強制值。
# 因此上限設為可設定：入口日後若調整時效，AERC 應以設定變更因應，而不是改程式。
_DEFAULT_MAX_TOKEN_AGE_SECONDS = 300


def is_valid_secret_form(secret: str) -> bool:
    """共用金鑰形式是否合法（FR-006a）。啟動驗證與互通測試夾具共用此判準。"""
    return bool(_SECRET_PATTERN.match(secret or ""))


def signing_key_from(secret: str) -> bytes:
    """簽章金鑰：十六進位字串本身的 UTF-8 位元組（64 bytes）。

    注意這裡刻意**不做**十六進位解碼——參考實作在此處用的是 Encoding.UTF8.GetBytes()，
    與解密端的取法不同。兩處統一採用其中一種，必有一處對不起來。
    """
    return secret.encode("utf-8")


def encryption_key_from(secret: str) -> bytes:
    """解密金鑰：十六進位解碼後的 32 位元組（AES-256）。形式不合時拋 binascii.Error。"""
    return binascii.unhexlify(secret)


def _split_csv(raw: str) -> frozenset:
    """逗號分隔字串 → 去空白、去空值的集合"""
    return frozenset(item.strip() for item in raw.split(",") if item.strip())


class PortalSsoSettings:
    """入口平台 SSO 整合的設定值。

    未設定共用金鑰時，本整合視為「尚未啟用」而非「設定錯誤」——AERC 在客戶交付金鑰
    之前必須能正常啟動與部署。此狀態下三支對外端點會因為驗不出任何憑證、也通不過來源
    驗證而一律拒絕請求，是 fail-closed，不會造成安全破口。

    設定了但形式錯誤則是另一回事：那是明確的設定錯誤，必須立刻拒絕啟動。
    """

    def __init__(self) -> None:
        self.secret = os.environ.get("PORTAL_SSO_SECRET", "").strip() or None
        self.audience = os.environ.get("PORTAL_SSO_AUDIENCE", "").strip() or _DEFAULT_AUDIENCE
        self.issuer = os.environ.get("PORTAL_SSO_ISSUER", "").strip() or _DEFAULT_ISSUER
        self.max_token_age_seconds = self._parse_max_token_age()
        self.webhook_secrets = _split_csv(os.environ.get("PORTAL_WEBHOOK_SECRET", ""))
        self.allowed_ips = _split_csv(os.environ.get("PORTAL_ALLOWED_IPS", ""))

    @staticmethod
    def _parse_max_token_age() -> int:
        raw = os.environ.get("PORTAL_SSO_MAX_TOKEN_AGE_SECONDS", "").strip()
        if not raw:
            return _DEFAULT_MAX_TOKEN_AGE_SECONDS
        try:
            value = int(raw)
        except ValueError:
            raise RuntimeError(
                f"PORTAL_SSO_MAX_TOKEN_AGE_SECONDS 必須為整數秒數，實際值為 {raw!r}"
            )
        if value <= 0:
            raise RuntimeError(
                f"PORTAL_SSO_MAX_TOKEN_AGE_SECONDS 必須為正整數，實際值為 {value}"
            )
        return value

    @property
    def is_configured(self) -> bool:
        """共用金鑰是否已設定。未設定時對外端點一律拒絕請求。"""
        return self.secret is not None

    @property
    def signing_key(self) -> bytes:
        """簽章金鑰，取法見 signing_key_from()。"""
        if self.secret is None:
            raise RuntimeError("PORTAL_SSO_SECRET 未設定")
        return signing_key_from(self.secret)

    @property
    def encryption_key(self) -> bytes:
        """解密金鑰，取法見 encryption_key_from()。"""
        if self.secret is None:
            raise RuntimeError("PORTAL_SSO_SECRET 未設定")
        return encryption_key_from(self.secret)

    def validate(self) -> None:
        """啟動時的形式驗證（FR-006a）。設定錯誤即拋出例外，不讓應用帶病啟動。"""
        # 一次性檢查（FR-007）重用 auth_nonces，其保證只在「nonce 保存期 ≥ 憑證時效上限」時
        # 成立：否則 nonce 先被清掉、憑證仍在時效內，同一顆憑證可再用一次，且不留痕跡。
        # 此項與金鑰是否設定無關，一律檢查。
        if self.max_token_age_seconds > NONCE_RETENTION_SECONDS:
            raise RuntimeError(
                f"PORTAL_SSO_MAX_TOKEN_AGE_SECONDS（{self.max_token_age_seconds}）不得超過 "
                f"防重放 nonce 保存期（{NONCE_RETENTION_SECONDS} 秒，auth/nonce.py）——"
                "超過時憑證在 nonce 清除後仍在時效內，一次性保證會無聲失效"
            )

        if self.secret is None:
            logger.warning(
                "PORTAL_SSO_SECRET 未設定，智慧灌溉入口平台 SSO 整合尚未啟用；"
                "/TokenLogin、/Register、/QueryStatus 將一律拒絕請求"
            )
            return

        if not is_valid_secret_form(self.secret):
            raise RuntimeError(
                "PORTAL_SSO_SECRET 形式不正確：必須恰為 64 個十六進位字元（實際長度 "
                f"{len(self.secret)}）。內容解密需要 32 位元組的 AES 金鑰，而在「金鑰不做"
                "雜湊」的前提下（客戶 2026-09-08 確認），該金鑰只能由本設定值十六進位解碼"
                "取得。形式不符時 HMAC 簽章仍會通過、只有解密失敗，症狀會表現為「簽章對得上"
                "卻解不開內容」而極難歸因，因此在此直接拒絕啟動。"
            )

        # 形式已由正規表示式保證，這裡只是把「解碼確實得到 32 bytes」這個結論實際跑一次，
        # 避免日後有人放寬正規表示式卻沒發現長度不再成立
        key_length = len(self.encryption_key)
        if key_length != 32:
            raise RuntimeError(
                f"PORTAL_SSO_SECRET 十六進位解碼後為 {key_length} 位元組，AES-256 需要 32 位元組"
            )


portal_sso_settings = PortalSsoSettings()


class TokenLoginQueryRedactFilter(logging.Filter):
    """把 uvicorn 存取紀錄中含 authToken 的查詢字串遮蔽（FR-009）。

    GET /TokenLogin 把憑證放在查詢參數，uvicorn 預設的存取紀錄會原樣寫出整行網址。
    判準看**查詢字串是否含 authToken**，不看路徑——路由大小寫敏感，/tokenlogin 會 404，
    但那一行存取紀錄照樣帶著憑證，只比對路徑會漏掉。

    ⚠️ 只涵蓋應用程式本身的存取紀錄。反向代理（Caddy）的存取紀錄須在部署端另行設定，
    見 contracts/frontend-and-routing.md 3.3 第 3 項。
    """

    def filter(self, record: logging.LogRecord) -> bool:
        args = record.args
        # uvicorn.access 的 args 形狀：(client_addr, method, full_path, http_version, status_code)
        if not (isinstance(args, tuple) and len(args) == 5 and isinstance(args[2], str)):
            return True
        path, _, query = args[2].partition("?")
        if "authtoken" in query.lower():
            record.args = (args[0], args[1], f"{path}?[redacted]", args[3], args[4])
        return True


def verify_configuration() -> None:
    """供應用啟動流程呼叫。設定錯誤時拋出例外中斷啟動。"""
    portal_sso_settings.validate()
