"""
Email 服務模組 - 處理所有系統郵件發送

Two-Layer Architecture (Simple Service):
- 直接使用 fastapi-mail
- 統一的 Email 發送介面
- Token 生成和管理邏輯
"""

import os
import uuid
import random
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from jinja2 import Template

from src.database.models import Users, AuthToken, AuthTokenType, AuthTokenStatus


class EmailConfig:
    """Email 配置 - 從環境變數讀取 SMTP 設定"""

    MAIL_USERNAME: str = os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD: str = os.getenv("MAIL_PASSWORD", "")
    MAIL_FROM: str = os.getenv("MAIL_FROM", "noreply@aerc.gov.tw")
    MAIL_PORT: int = int(os.getenv("MAIL_PORT", "587"))
    MAIL_SERVER: str = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_FROM_NAME: str = os.getenv("MAIL_FROM_NAME", "AERC 系統")
    MAIL_STARTTLS: bool = os.getenv("MAIL_STARTTLS", "True").lower() == "true"
    MAIL_SSL_TLS: bool = os.getenv("MAIL_SSL_TLS", "False").lower() == "true"
    USE_CREDENTIALS: bool = os.getenv("USE_CREDENTIALS", "True").lower() == "true"
    VALIDATE_CERTS: bool = os.getenv("VALIDATE_CERTS", "True").lower() == "true"

    # 前端 URL（用於生成驗證連結）
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3001")

    # Token 過期時間（小時）
    EMAIL_VERIFICATION_EXPIRE_HOURS: int = int(os.getenv("EMAIL_VERIFICATION_EXPIRE_HOURS", "24"))
    PASSWORD_RESET_EXPIRE_HOURS: int = int(os.getenv("PASSWORD_RESET_EXPIRE_HOURS", "1"))
    ACCOUNT_MIGRATION_EXPIRE_HOURS: int = int(os.getenv("ACCOUNT_MIGRATION_EXPIRE_HOURS", "168"))  # 7天

    @classmethod
    def get_connection_config(cls) -> ConnectionConfig:
        """取得 FastMail 連線配置"""
        return ConnectionConfig(
            MAIL_USERNAME=cls.MAIL_USERNAME,
            MAIL_PASSWORD=cls.MAIL_PASSWORD,
            MAIL_FROM=cls.MAIL_FROM,
            MAIL_PORT=cls.MAIL_PORT,
            MAIL_SERVER=cls.MAIL_SERVER,
            MAIL_FROM_NAME=cls.MAIL_FROM_NAME,
            MAIL_STARTTLS=cls.MAIL_STARTTLS,
            MAIL_SSL_TLS=cls.MAIL_SSL_TLS,
            USE_CREDENTIALS=cls.USE_CREDENTIALS,
            VALIDATE_CERTS=cls.VALIDATE_CERTS,
        )


class EmailService:
    """Email 服務 - 統一的郵件發送介面"""

    def __init__(self):
        self.config = EmailConfig.get_connection_config()
        self.fast_mail = FastMail(self.config)

    @staticmethod
    def mask_name(name: str) -> str:
        """
        遮罩姓名，保留頭尾各一個字元，中間用 * 替代

        Args:
            name: 原始姓名

        Returns:
            str: 遮罩後的姓名

        Examples:
            "張三" -> "張*"
            "王小明" -> "王*明"
            "李大華" -> "李*華"
            "陳明德華" -> "陳**華"
        """
        if not name or len(name) <= 1:
            return name
        elif len(name) == 2:
            return f"{name[0]}*"
        else:
            # 3個字以上：首字 + n個* + 尾字
            masked_middle = "*" * (len(name) - 2)
            return f"{name[0]}{masked_middle}{name[-1]}"

    async def send_email(
        self,
        recipients: List[str],
        subject: str,
        body_html: str,
        body_text: Optional[str] = None
    ) -> bool:
        """
        發送 Email

        Args:
            recipients: 收件人列表
            subject: 郵件主旨
            body_html: HTML 郵件內容
            body_text: 純文字郵件內容（可選）

        Returns:
            bool: 是否發送成功
        """
        try:
            # 檢查必要配置
            if not EmailConfig.MAIL_USERNAME or not EmailConfig.MAIL_PASSWORD:
                print(f"Email 發送失敗: SMTP 認證資訊未設定 (MAIL_USERNAME={EmailConfig.MAIL_USERNAME!r}, MAIL_PASSWORD={'***' if EmailConfig.MAIL_PASSWORD else 'empty'})")
                return False

            if not EmailConfig.MAIL_SERVER:
                print(f"Email 發送失敗: SMTP 伺服器未設定 (MAIL_SERVER={EmailConfig.MAIL_SERVER!r})")
                return False

            message = MessageSchema(
                subject=subject,
                recipients=recipients,
                body=body_html,
                subtype=MessageType.html
            )

            print(f"正在發送郵件至 {recipients} via {EmailConfig.MAIL_SERVER}:{EmailConfig.MAIL_PORT}")
            await self.fast_mail.send_message(message)
            print(f"郵件發送成功: {subject}")
            return True
        except Exception as e:
            # 詳細記錄錯誤資訊
            import traceback
            error_details = traceback.format_exc()
            print(f"Email 發送失敗: {type(e).__name__}: {e}")
            print(f"錯誤詳情:\n{error_details}")
            print(f"SMTP 配置: SERVER={EmailConfig.MAIL_SERVER}, PORT={EmailConfig.MAIL_PORT}, "
                  f"USERNAME={EmailConfig.MAIL_USERNAME!r}, STARTTLS={EmailConfig.MAIL_STARTTLS}, "
                  f"SSL_TLS={EmailConfig.MAIL_SSL_TLS}")
            return False

    async def create_auth_token(
        self,
        user: Users,
        token_type: AuthTokenType,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuthToken:
        """
        建立認證 Token

        Args:
            user: 使用者物件
            token_type: Token 類型
            ip_address: 請求 IP
            user_agent: 請求 User-Agent

        Returns:
            AuthToken: 建立的 Token 物件
        """
        # 撤銷該用戶同類型的所有待處理 Token
        await AuthToken.filter(
            user=user,
            token_type=token_type,
            status=AuthTokenStatus.PENDING
        ).update(status=AuthTokenStatus.REVOKED)

        # 計算過期時間
        if token_type == AuthTokenType.EMAIL_VERIFICATION:
            expire_hours = EmailConfig.EMAIL_VERIFICATION_EXPIRE_HOURS
        elif token_type == AuthTokenType.ACCOUNT_MIGRATION:
            expire_hours = EmailConfig.ACCOUNT_MIGRATION_EXPIRE_HOURS
        else:  # PASSWORD_RESET
            expire_hours = EmailConfig.PASSWORD_RESET_EXPIRE_HOURS

        # 使用 timezone-aware datetime (UTC)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=expire_hours)

        # 生成 OTP（密碼重設和帳號轉移都需要 OTP）
        otp_code = None
        if token_type in [AuthTokenType.PASSWORD_RESET, AuthTokenType.ACCOUNT_MIGRATION]:
            otp_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])

        # 建立新 Token
        auth_token = await AuthToken.create(
            user=user,
            token_type=token_type,
            token=str(uuid.uuid4()),
            otp=otp_code,
            otp_verified=False,
            status=AuthTokenStatus.PENDING,
            expires_at=expires_at,
            ip_address=ip_address,
            user_agent=user_agent
        )

        return auth_token

    async def verify_token(self, token: str, token_type: AuthTokenType) -> Optional[Users]:
        """
        驗證 Token

        Args:
            token: Token 字串
            token_type: Token 類型

        Returns:
            Optional[Users]: 驗證成功返回使用者物件，失敗返回 None
        """
        try:
            auth_token = await AuthToken.get(
                token=token,
                token_type=token_type,
                status=AuthTokenStatus.PENDING
            ).prefetch_related("user")

            # 檢查是否過期（使用 timezone-aware datetime）
            if auth_token.expires_at < datetime.now(timezone.utc):
                auth_token.status = AuthTokenStatus.EXPIRED
                await auth_token.save()
                return None

            # 標記為已使用
            auth_token.status = AuthTokenStatus.USED
            auth_token.used_at = datetime.now(timezone.utc)
            await auth_token.save()

            return auth_token.user
        except:
            return None

    async def send_verification_email(
        self,
        user: Users,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> bool:
        """
        發送 Email 驗證信

        Args:
            user: 使用者物件
            ip_address: 請求 IP
            user_agent: 請求 User-Agent

        Returns:
            bool: 是否發送成功
        """
        # 建立 Token
        auth_token = await self.create_auth_token(
            user=user,
            token_type=AuthTokenType.EMAIL_VERIFICATION,
            ip_address=ip_address,
            user_agent=user_agent
        )

        # 生成驗證連結
        verification_url = f"{EmailConfig.FRONTEND_URL}/verify-email?token={auth_token.token}"

        # 遮罩姓名（隱私保護）
        display_name = user.full_name or user.username
        masked_name = self.mask_name(display_name)

        # 渲染 HTML 模板
        html_template = Template(EMAIL_VERIFICATION_HTML_TEMPLATE)
        body_html = html_template.render(
            username=user.username,
            full_name=masked_name,
            verification_url=verification_url,
            expire_hours=EmailConfig.EMAIL_VERIFICATION_EXPIRE_HOURS,
            frontend_url=EmailConfig.FRONTEND_URL,
            current_year=datetime.now().year  # [新增] 傳入當前年份
        )

        # 發送郵件
        return await self.send_email(
            recipients=[user.email],
            subject="請驗證您的電子郵件地址",
            body_html=body_html
        )

    async def send_password_reset_email(
        self,
        user: Users,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> bool:
        """
        發送密碼重設信

        Args:
            user: 使用者物件
            ip_address: 請求 IP
            user_agent: 請求 User-Agent

        Returns:
            bool: 是否發送成功
        """
        # 建立 Token（包含 OTP）
        auth_token = await self.create_auth_token(
            user=user,
            token_type=AuthTokenType.PASSWORD_RESET,
            ip_address=ip_address,
            user_agent=user_agent
        )

        # 生成重設連結
        reset_url = f"{EmailConfig.FRONTEND_URL}/login/reset?token={auth_token.token}"

        # 遮罩姓名（隱私保護）
        display_name = user.full_name or user.username
        masked_name = self.mask_name(display_name)

        # 渲染 HTML 模板
        html_template = Template(PASSWORD_RESET_HTML_TEMPLATE)
        body_html = html_template.render(
            username=user.username,
            full_name=masked_name,
            reset_url=reset_url,
            otp=auth_token.otp,
            expire_hours=EmailConfig.PASSWORD_RESET_EXPIRE_HOURS,
            frontend_url=EmailConfig.FRONTEND_URL,
            current_year=datetime.now().year  # [新增] 傳入當前年份
        )

        # 發送郵件
        return await self.send_email(
            recipients=[user.email],
            subject="重設您的密碼",
            body_html=body_html
        )

    async def send_password_changed_notification(
        self,
        user: Users,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> bool:
        """
        發送密碼變更成功通知信

        Args:
            user: 使用者物件
            ip_address: 變更密碼時的請求 IP
            user_agent: 變更密碼時的請求 User-Agent

        Returns:
            bool: 是否發送成功
        """
        from datetime import datetime, timezone, timedelta

        # 遮罩姓名（隱私保護）
        display_name = user.full_name or user.username
        masked_name = self.mask_name(display_name)

        # 格式化變更時間（UTC+8 台灣時區）
        utc_now = datetime.now(timezone.utc)
        utc_plus_8 = utc_now + timedelta(hours=8)
        change_time = utc_plus_8.strftime("%Y-%m-%d %H:%M:%S") + " (UTC+8)"

        # 渲染 HTML 模板
        html_template = Template(PASSWORD_CHANGED_HTML_TEMPLATE)
        body_html = html_template.render(
            username=user.username,
            full_name=masked_name,
            change_time=change_time,
            ip_address=ip_address or "未知",
            user_agent=user_agent or "未知",
            frontend_url=EmailConfig.FRONTEND_URL,
            current_year=datetime.now().year  # [新增] 傳入當前年份
        )

        # 發送郵件
        return await self.send_email(
            recipients=[user.email],
            subject="您的密碼已成功變更",
            body_html=body_html
        )

    async def send_registration_otp_email(
        self,
        email: str,
        otp: str
    ) -> bool:
        """
        發送註冊驗證碼 Email（無需使用者物件）

        Args:
            email: 收件人 Email
            otp: 6 位數 OTP 驗證碼

        Returns:
            bool: 是否發送成功
        """
        # 渲染 HTML 模板
        html_template = Template(REGISTRATION_OTP_HTML_TEMPLATE)
        body_html = html_template.render(
            otp=otp,
            frontend_url=EmailConfig.FRONTEND_URL,
            current_year=datetime.now().year  # [新增] 傳入當前年份
        )

        # 發送郵件
        return await self.send_email(
            recipients=[email],
            subject="帳號申請驗證碼",
            body_html=body_html
        )

    async def send_account_migration_email(
        self,
        user: Users,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> bool:
        """
        發送帳號轉移驗證信（舊系統使用者啟用）

        Args:
            user: 使用者物件
            ip_address: 請求 IP
            user_agent: 請求 User-Agent

        Returns:
            bool: 是否發送成功
        """
        # 建立 Token（包含 OTP）
        auth_token = await self.create_auth_token(
            user=user,
            token_type=AuthTokenType.ACCOUNT_MIGRATION,
            ip_address=ip_address,
            user_agent=user_agent
        )

        # 生成轉移連結
        migration_url = f"{EmailConfig.FRONTEND_URL}/login/migrate?token={auth_token.token}"

        # 遮罩姓名（隱私保護）
        display_name = user.full_name or user.username
        masked_name = self.mask_name(display_name)

        # 渲染 HTML 模板
        html_template = Template(ACCOUNT_MIGRATION_HTML_TEMPLATE)
        body_html = html_template.render(
            username=user.username,
            full_name=masked_name,
            migration_url=migration_url,
            otp=auth_token.otp,
            expire_hours=EmailConfig.ACCOUNT_MIGRATION_EXPIRE_HOURS // 24,  # 轉換為天數
            frontend_url=EmailConfig.FRONTEND_URL,
            current_year=datetime.now().year  # [新增] 傳入當前年份
        )

        # 發送郵件
        return await self.send_email(
            recipients=[user.email],
            subject="帳號轉移通知",
            body_html=body_html
        )


# ============================================
# Email 模板定義
# ============================================

EMAIL_VERIFICATION_HTML_TEMPLATE = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="zh-TW">
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    <title>驗證您的電子郵件</title>
</head>
<body style="margin: 0; padding: 0; background-color: #f5f5f5;">
    <table border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #f5f5f5;">
        <tr>
            <td align="center" style="padding: 40px 15px;">
                <!-- 主容器 -->
                <table border="0" cellpadding="0" cellspacing="0" width="600" style="background-color: #ffffff; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">

                    <!-- Header -->
                    <tr>
                        <td align="center" style="padding: 40px 30px 20px 30px;">
                            <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                <tr>
                                    <td align="center" style="font-family: 'Microsoft JhengHei', 'PingFang TC', 'Helvetica Neue', Arial, sans-serif; font-size: 24px; font-weight: bold; color: #3ea0a3; padding-bottom: 8px;">
                                        推廣管路灌溉設施管理資料庫
                                    </td>
                                </tr>
                                <tr>
                                    <td align="center" style="font-family: 'Microsoft JhengHei', 'PingFang TC', 'Helvetica Neue', Arial, sans-serif; font-size: 14px; color: #6c757d;">
                                        農業部農田水利署便民服務
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding-top: 20px;">
                                        <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                            <tr>
                                                <td style="border-top: 2px solid #3ea0a3;"></td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>

                    <!-- Content -->
                    <tr>
                        <td style="padding: 40px 40px 30px 40px;">
                            <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                <!-- Greeting -->
                                <tr>
                                    <td style="font-family: 'Microsoft JhengHei', 'PingFang TC', 'Helvetica Neue', Arial, sans-serif; font-size: 20px; font-weight: 500; color: #1a1a1a; padding-bottom: 20px;">
                                        親愛的 {{ full_name }} 先生/小姐 您好：
                                    </td>
                                </tr>

                                <!-- Message -->
                                <tr>
                                    <td style="font-family: 'Microsoft JhengHei', 'PingFang TC', 'Helvetica Neue', Arial, sans-serif; font-size: 15px; line-height: 1.7; color: #4a4a4a; padding-bottom: 30px;">
                                        感謝註冊使用「推廣管路灌溉設施管理資料庫」。為了確保您的帳戶安全，請點擊下方按鈕完成電子郵件驗證。
                                    </td>
                                </tr>

                                <!-- CTA Button -->
                                <tr>
                                    <td align="center" style="padding: 20px 0 30px 0;">
                                        <table border="0" cellpadding="0" cellspacing="0">
                                            <tr>
                                                <td align="center" style="background-color: #3ea0a3; border-radius: 6px;">
                                                    <a href="{{ verification_url }}" target="_blank" style="font-family: 'Microsoft JhengHei', 'PingFang TC', 'Helvetica Neue', Arial, sans-serif; font-size: 16px; font-weight: 600; color: #ffffff; text-decoration: none; padding: 16px 48px; display: inline-block;">
                                                        驗證電子郵件
                                                    </a>
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>

                                <!-- Link Section -->
                                <tr>
                                    <td style="background-color: #f8f9fa; border: 1px solid #e9ecef; border-radius: 6px; padding: 16px;">
                                        <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                            <tr>
                                                <td style="font-family: 'Microsoft JhengHei', 'PingFang TC', 'Helvetica Neue', Arial, sans-serif; font-size: 13px; color: #6c757d; padding-bottom: 8px; font-weight: 500;">
                                                    若按鈕無法使用，請複製以下連結至瀏覽器：
                                                </td>
                                            </tr>
                                            <tr>
                                                <td style="font-family: 'Microsoft JhengHei', 'PingFang TC', 'Helvetica Neue', Arial, sans-serif; font-size: 13px; color: #3ea0a3; word-break: break-all; line-height: 1.5;">
                                                    {{ verification_url }}
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>

                                <!-- Divider -->
                                <tr>
                                    <td align="center" style="padding: 30px 0;">
                                        <table border="0" cellpadding="0" cellspacing="0" width="100">
                                            <tr>
                                                <td style="border-top: 1px solid #e0e0e0;"></td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>

                                <!-- Info Box -->
                                <tr>
                                    <td style="background-color: #fff3e0; border-left: 4px solid #ff9800; border-radius: 6px; padding: 16px;">
                                        <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                            <tr>
                                                <td style="font-family: 'Microsoft JhengHei', 'PingFang TC', 'Helvetica Neue', Arial, sans-serif; font-size: 14px; font-weight: 600; color: #e65100; padding-bottom: 12px;">
                                                    注意事項
                                                </td>
                                            </tr>
                                            <tr>
                                                <td style="font-family: 'Microsoft JhengHei', 'PingFang TC', 'Helvetica Neue', Arial, sans-serif; font-size: 13px; color: #5d4037; line-height: 1.7;">
                                                    • 此驗證連結將於 <strong>{{ expire_hours }} 小時</strong> 後失效<br/>
                                                    • 如果您未曾於「推廣管路灌溉設施管理資料庫」註冊帳號，請忽略此郵件<br/>
                                                    • 為保障帳戶安全，請勿將此郵件轉發給他人
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>

                            </table>
                        </td>
                    </tr>

                    <!-- Footer -->
                    <tr>
                        <td align="center" style="background-color: #3ea0a3; padding: 9px 12px; border-radius: 0 0 8px 8px;">
                            <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                <tr>
                                    <td align="center" style="padding-bottom: 12px;">
                                        <a href="{{ frontend_url }}" target="_blank" style="font-family: 'Microsoft JhengHei', 'PingFang TC', 'Helvetica Neue', Arial, sans-serif; font-size: 16px; font-weight: 600; color: #ffffff; text-decoration: none;">
                                            農業部農田水利署-推廣管路灌溉設施管理資料庫
                                        </a>
                                    </td>
                                </tr>
                                <tr>
                                    <td align="center" style="font-family: 'Microsoft JhengHei', 'PingFang TC', 'Helvetica Neue', Arial, sans-serif; font-size: 13px; color: #ffffff; opacity: 0.9; line-height: 1.6;">
                                        本郵件由系統自動發送，請勿直接回覆<br/>
                                        &copy; {{ current_year }} 農田水利署 版權所有
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>

                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""

PASSWORD_RESET_HTML_TEMPLATE = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="zh-TW">
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    <title>重設您的密碼</title>
</head>
<body style="margin: 0; padding: 0; background-color: #f5f5f5;">
    <table border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #f5f5f5;">
        <tr>
            <td align="center" style="padding: 40px 15px;">
                <!-- 主容器 -->
                <table border="0" cellpadding="0" cellspacing="0" width="600" style="background-color: #ffffff; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">

                    <!-- Header -->
                    <tr>
                        <td align="center" style="padding: 40px 30px 20px 30px;">
                            <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                <tr>
                                    <td align="center" style="font-family: 'Microsoft JhengHei', 'PingFang TC', 'Helvetica Neue', Arial, sans-serif; font-size: 24px; font-weight: bold; color: #3ea0a3; padding-bottom: 8px;">
                                        您的驗證碼是： {{ otp }}
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding-top: 20px;">
                                        <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                            <tr>
                                                <td style="border-top: 2px solid #3ea0a3;"></td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>

                    <!-- Content -->
                    <tr>
                        <td style="padding: 40px 40px 30px 40px;">
                            <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                <!-- Greeting -->
                                <tr>
                                    <td style="font-family: 'Microsoft JhengHei', 'PingFang TC', 'Helvetica Neue', Arial, sans-serif; font-size: 20px; font-weight: 500; color: #1a1a1a; padding-bottom: 20px;">
                                        親愛的 {{ full_name }} 先生/小姐 您好：
                                    </td>
                                </tr>

                                <!-- Message -->
                                <tr>
                                    <td style="font-family: 'Microsoft JhengHei', 'PingFang TC', 'Helvetica Neue', Arial, sans-serif; font-size: 15px; line-height: 1.7; color: #4a4a4a; padding-bottom: 30px;">
                                        我們收到了您的密碼重設請求。為了確保帳戶安全，請點擊下方按鈕並使用驗證碼完成密碼重設。
                                    </td>
                                </tr>

                                <!-- CTA Button -->
                                <tr>
                                    <td align="center" style="padding: 30px 0;">
                                        <table border="0" cellpadding="0" cellspacing="0">
                                            <tr>
                                                <td align="center" style="background-color: #3ea0a3; border-radius: 6px;">
                                                    <a href="{{ reset_url }}" target="_blank" style="font-family: 'Microsoft JhengHei', 'PingFang TC', 'Helvetica Neue', Arial, sans-serif; font-size: 16px; font-weight: 600; color: #ffffff; text-decoration: none; padding: 16px 48px; display: inline-block;">
                                                        前往重設密碼
                                                    </a>
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>

                                <!-- Link Section -->
                                <tr>
                                    <td style="background-color: #f8f9fa; border: 1px solid #e9ecef; border-radius: 6px; padding: 16px;">
                                        <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                            <tr>
                                                <td style="font-family: 'Microsoft JhengHei', 'PingFang TC', 'Helvetica Neue', Arial, sans-serif; font-size: 13px; color: #6c757d; padding-bottom: 8px; font-weight: 500;">
                                                    若按鈕無法使用，請複製以下連結至瀏覽器：
                                                </td>
                                            </tr>
                                            <tr>
                                                <td style="font-family: 'Microsoft JhengHei', 'PingFang TC', 'Helvetica Neue', Arial, sans-serif; font-size: 13px; color: #E74C3C; word-break: break-all; line-height: 1.5;">
                                                    {{ reset_url }}
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>

                                <!-- Divider -->
                                <tr>
                                    <td align="center" style="padding: 30px 0;">
                                        <table border="0" cellpadding="0" cellspacing="0" width="100">
                                            <tr>
                                                <td style="border-top: 1px solid #e0e0e0;"></td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>

                                <!-- Warning Box -->
                                <tr>
                                    <td style="background-color: #fff3e0; border-left: 4px solid #ff9800; border-radius: 6px; padding: 16px;">
                                        <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                            <tr>
                                                <td style="font-family: 'Microsoft JhengHei', 'PingFang TC', 'Helvetica Neue', Arial, sans-serif; font-size: 14px; font-weight: 600; color: #c62828; padding-bottom: 12px;">
                                                    注意事項
                                                </td>
                                            </tr>
                                            <tr>
                                                <td style="font-family: 'Microsoft JhengHei', 'PingFang TC', 'Helvetica Neue', Arial, sans-serif; font-size: 13px; color: #b71c1c; line-height: 1.7;">
                                                    • 此重設連結將於 <strong>{{ expire_hours }} 小時</strong> 後失效<br/>
                                                    • 如果您未提出密碼重設請求，請立即聯繫管理員<br/>
                                                    • 請勿將此連結或驗證碼分享給任何人
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>

                            </table>
                        </td>
                    </tr>

                    <!-- Footer -->
                    <tr>
                        <td align="center" style="background-color: #3ea0a3; padding: 9px 12px; border-radius: 0 0 8px 8px;">
                            <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                <tr>
                                    <td align="center" style="padding-bottom: 12px;">
                                        <a href="{{ frontend_url }}" target="_blank" style="font-family: 'Microsoft JhengHei', 'PingFang TC', 'Helvetica Neue', Arial, sans-serif; font-size: 16px; font-weight: 600; color: #ffffff; text-decoration: none;">
                                            農業部農田水利署-推廣管路灌溉設施管理資料庫
                                        </a>
                                    </td>
                                </tr>
                                <tr>
                                    <td align="center" style="font-family: 'Microsoft JhengHei', 'PingFang TC', 'Helvetica Neue', Arial, sans-serif; font-size: 13px; color: #ffffff; opacity: 0.9; line-height: 1.6;">
                                        本郵件由系統自動發送，請勿直接回覆<br/>
                                        &copy; {{ current_year }}  農田水利署 版權所有
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>

                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""

PASSWORD_CHANGED_HTML_TEMPLATE = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="zh-TW">
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    <title>密碼變更成功通知</title>
</head>
<body style="margin: 0; padding: 0; background-color: #f5f5f5;">
    <table border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #f5f5f5;">
        <tr>
            <td align="center" style="padding: 40px 15px;">
                <!-- 主容器 -->
                <table border="0" cellpadding="0" cellspacing="0" width="600" style="background-color: #ffffff; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">

                    <!-- Header -->
                    <tr>
                        <td align="center" style="padding: 40px 30px 20px 30px;">
                            <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                <tr>
                                    <td align="center" style="font-family: 'Microsoft JhengHei', 'PingFang TC', 'Helvetica Neue', Arial, sans-serif; font-size: 24px; font-weight: bold; color: #4CAF50; padding-bottom: 8px;">
                                        ✓ 密碼已成功變更
                                    </td>
                                </tr>
                                <tr>
                                    <td align="center" style="font-family: 'Microsoft JhengHei', 'PingFang TC', 'Helvetica Neue', Arial, sans-serif; font-size: 14px; color: #6c757d;">
                                        推廣管路灌溉設施管理資料庫
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding-top: 20px;">
                                        <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                            <tr>
                                                <td style="border-top: 2px solid #4CAF50;"></td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>

                    <!-- Content -->
                    <tr>
                        <td style="padding: 40px 40px 30px 40px;">
                            <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                <!-- Greeting -->
                                <tr>
                                    <td style="font-family: 'Microsoft JhengHei', 'PingFang TC', 'Helvetica Neue', Arial, sans-serif; font-size: 20px; font-weight: 500; color: #1a1a1a; padding-bottom: 20px;">
                                        親愛的 {{ full_name }} 先生/小姐 您好：
                                    </td>
                                </tr>

                                <!-- Message -->
                                <tr>
                                    <td style="font-family: 'Microsoft JhengHei', 'PingFang TC', 'Helvetica Neue', Arial, sans-serif; font-size: 15px; line-height: 1.7; color: #4a4a4a; padding-bottom: 30px;">
                                        您的帳戶密碼已於 <strong>{{ change_time }}</strong> 成功變更。如果這是您本人的操作，您可以忽略此郵件。
                                    </td>
                                </tr>

                                <!-- Info Box -->
                                <tr>
                                    <td style="background-color: #e8f5e9; border-left: 4px solid #4CAF50; border-radius: 6px; padding: 16px; margin-bottom: 20px;">
                                        <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                            <tr>
                                                <td style="font-family: 'Microsoft JhengHei', 'PingFang TC', 'Helvetica Neue', Arial, sans-serif; font-size: 14px; font-weight: 600; color: #2E7D32; padding-bottom: 12px;">
                                                    變更資訊
                                                </td>
                                            </tr>
                                            <tr>
                                                <td style="font-family: 'Microsoft JhengHei', 'PingFang TC', 'Helvetica Neue', Arial, sans-serif; font-size: 13px; color: #1B5E20; line-height: 1.7;">
                                                    • 帳號：{{ username }}<br/>
                                                    • 變更時間：{{ change_time }}<br/>
                                                    • IP 位址：{{ ip_address }}<br/>
                                                    • 裝置資訊：{{ user_agent }}
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>

                                <!-- Divider -->
                                <tr>
                                    <td align="center" style="padding: 30px 0;">
                                        <table border="0" cellpadding="0" cellspacing="0" width="100">
                                            <tr>
                                                <td style="border-top: 1px solid #e0e0e0;"></td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>

                                <!-- Warning Box -->
                                <tr>
                                    <td style="background-color: #ffebee; border-left: 4px solid #F44336; border-radius: 6px; padding: 16px;">
                                        <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                            <tr>
                                                <td style="font-family: 'Microsoft JhengHei', 'PingFang TC', 'Helvetica Neue', Arial, sans-serif; font-size: 14px; font-weight: 600; color: #c62828; padding-bottom: 12px;">
                                                    重要安全提醒
                                                </td>
                                            </tr>
                                            <tr>
                                                <td style="font-family: 'Microsoft JhengHei', 'PingFang TC', 'Helvetica Neue', Arial, sans-serif; font-size: 13px; color: #b71c1c; line-height: 1.7;">
                                                    如果您<strong>未曾</strong>進行此密碼變更操作，您的帳戶可能已被他人存取。請立即：<br/>
                                                    • 使用「忘記密碼」功能重設您的密碼<br/>
                                                    • 檢查您的帳戶活動記錄<br/>
                                                    • 聯繫系統管理員尋求協助
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>

                            </table>
                        </td>
                    </tr>

                    <!-- Footer -->
                    <tr>
                        <td align="center" style="background-color: #3ea0a3; padding: 9px 12px; border-radius: 0 0 8px 8px;">
                            <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                <tr>
                                    <td align="center" style="padding-bottom: 12px;">
                                        <a href="{{ frontend_url }}" target="_blank" style="font-family: 'Microsoft JhengHei', 'PingFang TC', 'Helvetica Neue', Arial, sans-serif; font-size: 16px; font-weight: 600; color: #ffffff; text-decoration: none;">
                                            農業部農田水利署-推廣管路灌溉設施管理資料庫
                                        </a>
                                    </td>
                                </tr>
                                <tr>
                                    <td align="center" style="font-family: 'Microsoft JhengHei', 'PingFang TC', 'Helvetica Neue', Arial, sans-serif; font-size: 13px; color: #ffffff; opacity: 0.9; line-height: 1.6;">
                                        本郵件由系統自動發送，請勿直接回覆<br/>
                                        &copy; {{ current_year }}  農田水利署 版權所有
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>

                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""

REGISTRATION_OTP_HTML_TEMPLATE = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="zh-TW">
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    <title>帳號申請驗證碼</title>
</head>
<body style="margin: 0; padding: 0; background-color: #f5f5f5;">
    <table border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #f5f5f5;">
        <tr>
            <td align="center" style="padding: 40px 15px;">
                <!-- 主容器 -->
                <table border="0" cellpadding="0" cellspacing="0" width="600" style="background-color: #ffffff; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">

                    <!-- Header -->
                    <tr>
                        <td align="center" style="padding: 40px 30px 20px 30px;">
                            <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                <tr>
                                    <td align="center" style="font-family: 'Microsoft JhengHei', 'PingFang TC', 'Helvetica Neue', Arial, sans-serif; font-size: 24px; font-weight: bold; color: #3ea0a3; padding-bottom: 8px;">
                                        您的驗證碼是： {{ otp }}
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding-top: 20px;">
                                        <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                            <tr>
                                                <td style="border-top: 2px solid #3ea0a3;"></td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>

                    <!-- Content -->
                    <tr>
                        <td style="padding: 40px 40px 30px 40px;">
                            <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                <!-- Greeting -->
                                <tr>
                                    <td style="font-family: 'Microsoft JhengHei', 'PingFang TC', 'Helvetica Neue', Arial, sans-serif; font-size: 20px; font-weight: 500; color: #1a1a1a; padding-bottom: 20px;">
                                        您好：
                                    </td>
                                </tr>

                                <!-- Message -->
                                <tr>
                                    <td style="font-family: 'Microsoft JhengHei', 'PingFang TC', 'Helvetica Neue', Arial, sans-serif; font-size: 15px; line-height: 1.7; color: #4a4a4a; padding-bottom: 30px;">
                                        您正在申請「推廣管路灌溉設施管理資料庫」帳號。請在申請頁面輸入以上驗證碼以完成 Email 驗證。
                                    </td>
                                </tr>

                                <!-- Divider -->
                                <tr>
                                    <td align="center" style="padding: 30px 0;">
                                        <table border="0" cellpadding="0" cellspacing="0" width="100">
                                            <tr>
                                                <td style="border-top: 1px solid #e0e0e0;"></td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>

                                <!-- Warning Box -->
                                <tr>
                                    <td style="background-color: #fff3e0; border-left: 4px solid #ff9800; border-radius: 6px; padding: 16px;">
                                        <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                            <tr>
                                                <td style="font-family: 'Microsoft JhengHei', 'PingFang TC', 'Helvetica Neue', Arial, sans-serif; font-size: 14px; font-weight: 600; color: #e65100; padding-bottom: 12px;">
                                                    注意事項
                                                </td>
                                            </tr>
                                            <tr>
                                                <td style="font-family: 'Microsoft JhengHei', 'PingFang TC', 'Helvetica Neue', Arial, sans-serif; font-size: 13px; color: #5d4037; line-height: 1.7;">
                                                    • 此驗證碼將於 <strong>15 分鐘</strong> 後失效<br/>
                                                    • 如果您未曾於「推廣管路灌溉設施管理資料庫」申請帳號，請忽略此郵件<br/>
                                                    • 為保障帳戶安全，請勿將驗證碼分享給任何人
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>

                            </table>
                        </td>
                    </tr>

                    <!-- Footer -->
                    <tr>
                        <td align="center" style="background-color: #3ea0a3; padding: 9px 12px; border-radius: 0 0 8px 8px;">
                            <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                <tr>
                                    <td align="center" style="padding-bottom: 12px;">
                                        <a href="{{ frontend_url }}" target="_blank" style="font-family: 'Microsoft JhengHei', 'PingFang TC', 'Helvetica Neue', Arial, sans-serif; font-size: 16px; font-weight: 600; color: #ffffff; text-decoration: none;">
                                            農業部農田水利署-推廣管路灌溉設施管理資料庫
                                        </a>
                                    </td>
                                </tr>
                                <tr>
                                    <td align="center" style="font-family: 'Microsoft JhengHei', 'PingFang TC', 'Helvetica Neue', Arial, sans-serif; font-size: 13px; color: #ffffff; opacity: 0.9; line-height: 1.6;">
                                        本郵件由系統自動發送，請勿直接回覆<br/>
                                        &copy; {{ current_year }}  農田水利署 版權所有
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>

                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""


ACCOUNT_MIGRATION_HTML_TEMPLATE = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="zh-TW">
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    <title>帳號轉移通知</title>
</head>
<body style="margin: 0; padding: 0; background-color: #f5f5f5;">
    <table border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #f5f5f5;">
        <tr>
            <td align="center" style="padding: 40px 15px;">
                <!-- 主容器 -->
                <table border="0" cellpadding="0" cellspacing="0" width="600" style="background-color: #ffffff; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                    <!-- Header -->
                    <tr>
                        <td align="center" style="padding: 40px 30px 20px 30px;">
                            <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                <tr>
                                    <td align="center" style="font-family: 'Microsoft JhengHei', 'PingFang TC', 'Helvetica Neue', Arial, sans-serif; font-size: 24px; font-weight: bold; color: #3ea0a3; padding-bottom: 8px;">
                                        您的驗證碼是： {{ otp }}
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding-top: 20px;">
                                        <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                            <tr>
                                                <td style="border-top: 2px solid #3ea0a3;"></td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    <!-- Content -->
                    <tr>
                        <td style="padding: 40px 40px 30px 40px;">
                            <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                <tr>
                                    <td style="font-family: 'Microsoft JhengHei', 'PingFang TC', 'Helvetica Neue', Arial, sans-serif; font-size: 20px; font-weight: 500; color: #1a1a1a; padding-bottom: 20px;">
                                        親愛的 {{ full_name }} 先生/小姐 您好：
                                    </td>
                                </tr>
                                <tr>
                                    <td style="font-family: 'Microsoft JhengHei', 'PingFang TC', 'Helvetica Neue', Arial, sans-serif; font-size: 15px; line-height: 1.7; color: #4a4a4a; padding-bottom: 20px;">
                                        推廣管路灌溉設施管理資料庫已完成升級，為了確保您的帳戶安全，請完成帳號轉移程序。
                                    </td>
                                </tr>
                                <tr>
                                    <td style="font-family: 'Microsoft JhengHei', 'PingFang TC', 'Helvetica Neue', Arial, sans-serif; font-size: 15px; line-height: 1.7; color: #4a4a4a; padding-bottom: 10px;">
                                        請點擊下方按鈕並使用驗證碼完成帳號轉移。轉移過程中您需要：
                                        <ul style="margin: 10px 0; padding-left: 20px;">
                                            <li style="margin: 8px 0;">確認您的個人資訊</li>
                                            <li style="margin: 8px 0;">設定新的登入密碼</li>
                                        </ul>
                                    </td>
                                </tr>
                                <!-- CTA Button -->
                                <tr>
                                    <td align="center" style="padding: 30px 0;">
                                        <table border="0" cellpadding="0" cellspacing="0">
                                            <tr>
                                                <td align="center" style="background-color: #3ea0a3; border-radius: 6px;">
                                                    <a href="{{ migration_url }}" target="_blank" style="font-family: 'Microsoft JhengHei', 'PingFang TC', 'Helvetica Neue', Arial, sans-serif; font-size: 16px; font-weight: 600; color: #ffffff; text-decoration: none; padding: 16px 48px; display: inline-block;">
                                                        立即轉移帳號
                                                    </a>
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>

                                <!-- Link Section -->
                                <tr>
                                    <td style="background-color: #f8f9fa; border: 1px solid #e9ecef; border-radius: 6px; padding: 16px;">
                                        <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                            <tr>
                                                <td style="font-family: 'Microsoft JhengHei', 'PingFang TC', 'Helvetica Neue', Arial, sans-serif; font-size: 13px; color: #6c757d; padding-bottom: 8px; font-weight: 500;">
                                                    若按鈕無法使用，請複製以下連結至瀏覽器：
                                                </td>
                                            </tr>
                                            <tr>
                                                <td style="font-family: 'Microsoft JhengHei', 'PingFang TC', 'Helvetica Neue', Arial, sans-serif; font-size: 13px; color: #3ea0a3; word-break: break-all; line-height: 1.5;">
                                                    {{ migration_url }}
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>

                                <!-- Divider -->
                                <tr>
                                    <td align="center" style="padding: 30px 0;">
                                        <table border="0" cellpadding="0" cellspacing="0" width="100">
                                            <tr>
                                                <td style="border-top: 1px solid #e0e0e0;"></td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>

                                <!-- Warning -->
                                <tr>
                                    <td style="background-color: #fff8e1; border-left: 4px solid #ffc107; padding: 16px; border-radius: 6px;">
                                        <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                            <tr>
                                                <td style="font-family: 'Microsoft JhengHei', 'PingFang TC', 'Helvetica Neue', Arial, sans-serif; font-size: 14px; font-weight: 600; color: #f57c00; padding-bottom: 12px;">
                                                    注意事項
                                                </td>
                                            </tr>
                                            <tr>
                                                <td style="font-family: 'Microsoft JhengHei', 'PingFang TC', 'Helvetica Neue', Arial, sans-serif; font-size: 13px; color: #666666; line-height: 1.7;">
                                                    • 此連結將在 <strong>{{ expire_hours }} 天</strong> 後失效<br/>
                                                    • 驗證碼僅供本次使用，請勿轉發他人<br/>
                                                    • 若您未申請帳號轉移，請忽略此郵件
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    <!-- Footer -->
                    <tr>
                        <td align="center" style="background-color: #3ea0a3; padding: 9px 12px; border-radius: 0 0 8px 8px;">
                            <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                <tr>
                                    <td align="center" style="padding-bottom: 12px;">
                                        <a href="{{ frontend_url }}" target="_blank" style="font-family: 'Microsoft JhengHei', 'PingFang TC', 'Helvetica Neue', Arial, sans-serif; font-size: 16px; font-weight: 600; color: #ffffff; text-decoration: none;">
                                            農業部農田水利署-推廣管路灌溉設施管理資料庫
                                        </a>
                                    </td>
                                </tr>
                                <tr>
                                    <td align="center" style="font-family: 'Microsoft JhengHei', 'PingFang TC', 'Helvetica Neue', Arial, sans-serif; font-size: 13px; color: #ffffff; opacity: 0.9; line-height: 1.6;">
                                        本郵件由系統自動發送，請勿直接回覆<br/>
                                        &copy; {{ current_year }}  農田水利署 版權所有
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""

