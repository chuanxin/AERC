from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from tortoise.exceptions import DoesNotExist

import src.crud.users as crud
from src.auth.users import validate_user, get_password_hash
from src.schemas.token import Status
from src.schemas.users import (
    UserInSchema,
    UserOutSchema,
    UserInfoSchema,
    EmailVerificationRequest,
    EmailVerificationConfirm,
    EmailVerificationResponse,
    PasswordResetRequest,
    PasswordResetConfirm,
    PasswordResetResponse,
    OTPVerificationRequest,
    OTPVerificationResponse,
    CaptchaResponse,
    RegistrationOTPResponse,
    RegistrationOTPVerificationResponse,
    LoginWithCaptchaRequest,
    UserRegistrationRequest,
    UserRegistrationResponse,
)
from src.database.models import Users, AuthToken, AuthTokenType, AuthTokenStatus
from src.services.email_service import EmailService
from src.services.captcha_service import CaptchaService
from src.services.password_policy import PasswordPolicyService
from datetime import datetime, timezone

from src.auth.jwthandler import (
    create_access_token,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)

from src.schemas.users import (
    AccountMigrationOTPVerifyRequest,
    AccountMigrationOTPVerifyResponse,
    AccountMigrationCompleteRequest,
    AccountMigrationCompleteResponse,
    ChangePasswordRequest,
)


router = APIRouter()


@router.get(
    "/captcha",
    response_model=CaptchaResponse,
    status_code=status.HTTP_200_OK,
    summary="生成登入驗證碼",
    description="生成 4 位數字驗證碼供登入使用"
)
async def generate_captcha():
    """
    生成登入驗證碼

    Returns:
        CaptchaResponse: 包含 captcha_token 和 captcha_code
    """
    captcha_token, captcha_code = CaptchaService.generate()
    return CaptchaResponse(
        captcha_token=captcha_token,
        captcha_code=captcha_code
    )


# ============================================
# 帳號註冊相關端點
# ============================================

@router.get("/check-username/{username}")
async def check_username_availability(username: str):
    """
    即時檢查帳號是否可用

    Returns:
        available: bool - 是否可用
        message: str - 說明訊息
    """
    import re

    # 驗證帳號格式
    if len(username) < 3:
        return {"available": False, "message": "帳號長度至少需要 3 個字元"}

    if len(username) > 20:
        return {"available": False, "message": "帳號長度不得超過 20 個字元"}

    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return {"available": False, "message": "帳號只能包含英文字母、數字和底線"}

    # 檢查是否已存在
    existing_user = await Users.filter(username=username).first()
    if existing_user:
        return {"available": False, "message": "此帳號已被使用"}

    return {"available": True, "message": "帳號可用"}


@router.get("/check-email/{email}")
async def check_email_availability(email: str):
    """
    即時檢查 Email 是否可用

    Returns:
        available: bool - 是否可用
        message: str - 說明訊息
    """
    import re

    # 驗證 Email 格式
    email_pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
    if not re.match(email_pattern, email):
        return {"available": False, "message": "請輸入有效的電子郵件格式"}

    # 檢查是否已存在
    existing_user = await Users.filter(email=email).first()
    if existing_user:
        return {"available": False, "message": "此電子郵件已被使用"}

    return {"available": True, "message": "電子郵件可用"}


@router.post("/send-registration-otp", response_model=RegistrationOTPResponse)
async def send_registration_otp(payload: EmailVerificationRequest):
    """
    發送註冊驗證碼到指定 Email

    - 驗證 Email 是否已被使用
    - 發送 6 位數 OTP 到 Email
    - 返回 Token 供後續驗證使用
    """
    import secrets
    from datetime import datetime, timezone, timedelta

    try:
        print(f"[send_registration_otp] 開始處理: email={payload.email}")

        # 檢查 Email 是否已存在
        existing_email = await Users.filter(email=payload.email).first()
        if existing_email:
            print(f"[send_registration_otp] Email 已存在: {payload.email}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="此電子郵件已被使用"
            )

        # 生成 6 位數 OTP
        otp = ''.join([str(secrets.randbelow(10)) for _ in range(6)])
        print(f"[send_registration_otp] OTP 已生成: {otp}")

        # 發送 OTP Email（使用 EmailService 的標準模板）
        email_service = EmailService()
        print(f"[send_registration_otp] 開始發送郵件")
        success = await email_service.send_registration_otp_email(
            email=payload.email,
            otp=otp
        )
        print(f"[send_registration_otp] 郵件發送結果: success={success}, type={type(success)}")

        if not success:
            print(f"[send_registration_otp] 郵件發送失敗")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="驗證碼郵件發送失敗"
            )

        # 將 OTP 和 Email 暫存（使用 token 作為 key）
        # 這裡我們將資訊編碼到 token 中，使用 HMAC 方式
        import hmac
        import hashlib
        import base64
        import time

        print(f"[send_registration_otp] 開始生成 token")

        # 建立包含 email, otp, timestamp 的 token
        timestamp = int(time.time())
        expires_at = timestamp + (15 * 60)  # 15 分鐘後過期
        data = f"{payload.email}:{otp}:{expires_at}"

        # 使用 HMAC 簽名（使用 CaptchaService 的 secret key）
        secret_key = CaptchaService._secret_key
        signature = hmac.new(secret_key, data.encode(), hashlib.sha256).hexdigest()
        token = base64.urlsafe_b64encode(f"{data}:{signature}".encode()).decode()

        print(f"[send_registration_otp] Token 已生成")

        response_data = {
            "message": "驗證碼已發送至您的電子郵件",
            "token": token,
            "expires_in": 900  # 15 分鐘
        }
        print(f"[send_registration_otp] 準備返回響應: {response_data}")
        print(f"[send_registration_otp] 響應類型檢查 - message: {type(response_data['message'])}, token: {type(response_data['token'])}, expires_in: {type(response_data['expires_in'])}")

        return response_data

    except HTTPException:
        raise
    except Exception as e:
        print(f"[send_registration_otp] 發生異常: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"發送驗證碼失敗：{str(e)}"
        )


@router.post("/verify-registration-otp", response_model=RegistrationOTPVerificationResponse)
async def verify_registration_otp(token: str, otp: str):
    """
    驗證註冊 OTP

    Args:
        token: 包含 email 資訊的加密 token
        otp: 使用者輸入的 6 位數 OTP

    Returns:
        success: bool
        email: str - 已驗證的 email
    """
    from src.services.captcha_service import CaptchaService
    import hmac
    import hashlib
    import base64
    import time

    try:
        # 解碼 token
        decoded = base64.urlsafe_b64decode(token.encode()).decode()
        parts = decoded.rsplit(':', 1)
        if len(parts) != 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="無效的驗證 Token"
            )

        data, signature = parts
        data_parts = data.split(':')
        if len(data_parts) != 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="無效的驗證 Token"
            )

        email, stored_otp, expires_at = data_parts

        # 驗證簽名
        secret_key = CaptchaService._secret_key
        expected_signature = hmac.new(secret_key, data.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected_signature):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="無效的驗證 Token"
            )

        # 檢查是否過期
        if int(time.time()) > int(expires_at):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="驗證碼已過期，請重新發送"
            )

        # 驗證 OTP
        if otp != stored_otp:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="驗證碼錯誤"
            )

        # 驗證成功，建立已驗證的 token（用於最終註冊）
        timestamp = int(time.time())
        expires_at = timestamp + (30 * 60)  # 30 分鐘內完成註冊
        verified_data = f"{email}:verified:{expires_at}"
        verified_signature = hmac.new(secret_key, verified_data.encode(), hashlib.sha256).hexdigest()
        verified_token = base64.urlsafe_b64encode(f"{verified_data}:{verified_signature}".encode()).decode()

        return {
            "success": True,
            "message": "Email 驗證成功",
            "email": email,
            "verified_token": verified_token
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="驗證失敗"
        )


@router.post("/register", response_model=UserRegistrationResponse)
async def create_user(payload: UserRegistrationRequest) -> UserRegistrationResponse:
    """
    帳號申請

    - 驗證 Email 已通過 OTP 驗證
    - 檢查帳號/Email 是否重複
    - 建立待審核帳號（is_active=False）
    - 建立申請記錄（含申請原因）
    """
    from src.database.models import Offices, UserRegistration
    import hmac
    import hashlib
    import base64
    import time

    try:
        # 驗證 Email Token
        try:
            decoded = base64.urlsafe_b64decode(payload.verified_token.encode()).decode()
            parts = decoded.rsplit(':', 1)
            if len(parts) != 2:
                raise ValueError("Invalid token format")

            data, signature = parts
            data_parts = data.split(':')
            if len(data_parts) != 3:
                raise ValueError("Invalid token data")

            token_email, status_flag, expires_at = data_parts

            # 驗證簽名
            secret_key = CaptchaService._secret_key
            expected_signature = hmac.new(secret_key, data.encode(), hashlib.sha256).hexdigest()
            if not hmac.compare_digest(signature, expected_signature):
                raise ValueError("Invalid signature")

            # 檢查是否過期
            if int(time.time()) > int(expires_at):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email 驗證已過期，請重新驗證"
                )

            # 確認 Email 匹配
            if token_email != payload.email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email 與驗證的 Email 不符"
                )

            # 確認是已驗證狀態
            if status_flag != "verified":
                raise ValueError("Token not verified")

        except HTTPException:
            raise
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email 驗證無效，請重新驗證"
            )

        # 檢查帳號是否已存在
        existing_user = await Users.filter(username=payload.username).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="此帳號已被使用"
            )

        # 檢查 Email 是否已存在
        existing_email = await Users.filter(email=payload.email).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="此電子郵件已被使用"
            )

        # 驗證所屬單位是否存在
        office = await Offices.filter(id=payload.office_id).first()
        if not office:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="所選單位不存在"
            )

        # 建立使用者帳號（停用狀態，需管理員審核）
        new_user = await Users.create(
            username=payload.username,
            email=payload.email,
            full_name=payload.full_name,
            office_id=payload.office_id,
            department=payload.department,
            job_title=payload.job_title,
            phone=payload.phone,
            phone_ext=payload.phone_ext,
            mobile=payload.mobile,
            password=get_password_hash(payload.password),
            is_active=False,  # 預設停用，需管理員審核
            role="user"
        )

        # 建立申請記錄（儲存申請原因）
        await UserRegistration.create(
            user_id=new_user.id,
            application_reason=payload.application_reason
        )

        return UserRegistrationResponse(
            message="帳號申請已送出，請等待管理員審核。審核通過後將會寄送通知至您的電子郵件。",
            success=True,
            user_id=new_user.id
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"系統錯誤：{str(e)}"
        )


@router.post("/login")
async def login(user: OAuth2PasswordRequestForm = Depends()):
    user = await validate_user(user)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="使用者名稱或密碼不正確",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="使用者名稱或密碼不正確",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 使用 crud 函數更新最後登入時間
    await crud.update_last_login(user.id)

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    token = jsonable_encoder(access_token)
    content = {
        "message": "You've successfully logged in. Welcome back!",
        "access_token": token,
        "password_expired": user.password_expired,  # 密碼是否已過期
    }
    response = JSONResponse(content=content)
    response.set_cookie(
        "Authorization",
        value=f"Bearer {token}",
        httponly=True,
        samesite="Lax",
        secure=True,
    )

    return response


@router.post("/login-secure")
async def login_with_captcha(payload: LoginWithCaptchaRequest):
    """
    帶驗證碼的安全登入

    - 先驗證驗證碼
    - 再驗證帳號密碼（含鎖定檢查）
    - 返回 JWT Token
    """
    # 1. 驗證驗證碼
    if not CaptchaService.verify(payload.captcha_token, payload.captcha_code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="驗證碼錯誤或已過期"
        )

    # 2. 驗證帳號密碼（含鎖定檢查）
    from src.auth.users import (
        verify_password,
        check_account_locked,
        record_failed_login,
        reset_failed_login,
        check_password_expired,
    )

    try:
        user = await Users.get(username=payload.username)
    except DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="使用者名稱或密碼不正確",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 檢查帳號是否啟用
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="使用者名稱或密碼不正確",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 檢查帳號是否被鎖定
    await check_account_locked(user)

    # 驗證密碼
    if not verify_password(payload.password, user.password):
        await record_failed_login(user)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="使用者名稱或密碼不正確",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 登入成功，重置失敗計數
    await reset_failed_login(user)

    # 3. 更新最後登入時間
    await crud.update_last_login(user.id)

    # 4. 檢查密碼是否過期
    password_expired = check_password_expired(user)

    # 5. 生成 JWT Token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    token = jsonable_encoder(access_token)
    content = {
        "message": "You've successfully logged in. Welcome back!",
        "access_token": token,
        "password_expired": password_expired,  # 密碼是否已過期
    }
    response = JSONResponse(content=content)
    response.set_cookie(
        "Authorization",
        value=f"Bearer {token}",
        httponly=True,
        samesite="Lax",
        secure=True,
    )

    return response


@router.post("/refresh")
async def refresh_token(current_user: UserInfoSchema = Depends(get_current_user)):
    """
    刷新用戶的 access token
    """
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await create_access_token(
        data={"sub": current_user.username}, expires_delta=access_token_expires
    )
    token = jsonable_encoder(access_token)
    content = {
        "message": "Token refreshed successfully",
        "access_token": token,
    }
    response = JSONResponse(content=content)
    response.set_cookie(
        "Authorization",
        value=f"Bearer {token}",
        httponly=True,
        samesite="Lax",
        secure=True,
    )
    return response


@router.get(
    "/users/whoami", dependencies=[Depends(get_current_user)]
)
async def read_users_me(current_user: UserInfoSchema = Depends(get_current_user)):
    from src.auth.users import check_password_expired
    user = await Users.get(username=current_user.username)
    result = current_user.model_dump()
    result['password_expired'] = check_password_expired(user)
    return result


@router.post("/change-password", status_code=200)
async def change_password(
    payload: ChangePasswordRequest,
    request: Request,
    current_user: UserInfoSchema = Depends(get_current_user)
):
    """
    密碼過期強制更換

    JWT 已驗證使用者身份（登入時已輸入正確密碼），此端點不再重複驗證舊密碼。
    執行 PasswordPolicyService 進行：最短效期、三代不重複、歷史記錄。
    成功回傳 200；政策違規回傳 400 含說明訊息。
    """
    success, error_msg = await PasswordPolicyService.change_password(
        user_id=current_user.id,
        new_password=payload.new_password,
        change_method="user_change",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )

    return {"message": "密碼已成功更換"}


@router.delete(
    "/user/{user_id}",
    response_model=Status,
    responses={404: {"model": dict}},
    dependencies=[Depends(get_current_user)],
)
async def delete_user(
    user_id: int, current_user: UserOutSchema = Depends(get_current_user)
) -> Status:
    return await crud.delete_user(user_id, current_user)


# ============================================
# Email 驗證相關端點
# ============================================

@router.post(
    "/send-verification-email",
    response_model=EmailVerificationResponse,
    status_code=status.HTTP_200_OK,
    summary="發送 Email 驗證信",
    description="向指定的電子郵件地址發送驗證信"
)
async def send_verification_email(
    request: Request,
    payload: EmailVerificationRequest
):
    """
    發送 Email 驗證信

    - 檢查 Email 是否已註冊
    - 如果已驗證，返回提示
    - 如果未驗證，發送驗證信
    - 統一響應時間（防止 Timing Attack）
    """
    import asyncio
    import time

    # 記錄開始時間
    start_time = time.time()

    # 設定最小響應時間（秒）- 模擬真實發信延遲
    MIN_RESPONSE_TIME = 1.5

    try:
        # 查找用戶（如有重複將由 ORM 拋出異常）
        user = await Users.get(email=payload.email)

        # 檢查是否已驗證
        if user.email_verified:
            # 統一響應時間
            elapsed = time.time() - start_time
            if elapsed < MIN_RESPONSE_TIME:
                await asyncio.sleep(MIN_RESPONSE_TIME - elapsed)

            return EmailVerificationResponse(
                message="此電子郵件已完成驗證",
                success=True,
                email=user.email
            )

        # 發送驗證信
        email_service = EmailService()
        success = await email_service.send_verification_email(
            user=user,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent")
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="驗證信發送失敗，請稍後再試"
            )

        # 統一響應時間
        elapsed = time.time() - start_time
        if elapsed < MIN_RESPONSE_TIME:
            await asyncio.sleep(MIN_RESPONSE_TIME - elapsed)

        return EmailVerificationResponse(
            message="驗證信已發送至您的電子郵件",
            success=True,
            email=user.email
        )

    except DoesNotExist:
        # 安全考量：即使 Email 不存在也返回成功訊息（避免帳號探測）
        # 並且延遲到最小響應時間，防止 Timing Attack
        elapsed = time.time() - start_time
        if elapsed < MIN_RESPONSE_TIME:
            await asyncio.sleep(MIN_RESPONSE_TIME - elapsed)

        return EmailVerificationResponse(
            message="如果該電子郵件已註冊，您將收到驗證信",
            success=True
        )
    except Exception as e:
        # 統一錯誤響應時間
        elapsed = time.time() - start_time
        if elapsed < MIN_RESPONSE_TIME:
            await asyncio.sleep(MIN_RESPONSE_TIME - elapsed)

        # 特別處理資料完整性問題
        if "multiple" in str(e).lower() or "MultipleObjectsReturned" in str(type(e).__name__):
            # 錯誤代碼供管理員追查（通用代碼，不揭露具體問題）
            error_code = "ERR_SYSTEM_001"
            # 記錄詳細資訊供管理員查詢（包含 email、IP、時間戳）
            import logging
            logger = logging.getLogger(__name__)
            logger.error(
                f"[{error_code}] Data integrity issue detected during email verification. "
                f"Email: {payload.email}, IP: {request.client.host}, Timestamp: {datetime.now(timezone.utc).isoformat()}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"系統發生錯誤，請聯絡系統管理員並提供錯誤代碼：{error_code}"
            )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"系統錯誤：{str(e)}"
        )


@router.post(
    "/verify-email",
    response_model=EmailVerificationResponse,
    status_code=status.HTTP_200_OK,
    summary="驗證 Email",
    description="使用 Token 驗證電子郵件地址"
)
async def verify_email(payload: EmailVerificationConfirm):
    """
    驗證 Email

    - 驗證 Token 有效性
    - 標記用戶 Email 為已驗證
    - 返回驗證結果
    """
    try:
        email_service = EmailService()

        # 驗證 Token
        user = await email_service.verify_token(
            token=payload.token,
            token_type=AuthTokenType.EMAIL_VERIFICATION
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="驗證連結無效或已過期，請重新申請驗證信"
            )

        # 標記 Email 為已驗證
        user.email_verified = True
        await user.save()

        return EmailVerificationResponse(
            message="電子郵件驗證成功",
            success=True,
            email=user.email
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"系統錯誤：{str(e)}"
        )


# ============================================
# 密碼重設相關端點
# ============================================

@router.post(
    "/request-password-reset",
    response_model=PasswordResetResponse,
    status_code=status.HTTP_200_OK,
    summary="請求密碼重設",
    description="發送密碼重設信到指定的電子郵件"
)
async def request_password_reset(
    request: Request,
    payload: PasswordResetRequest
):
    """
    請求密碼重設

    - 檢查 Email 是否已註冊
    - 如果已註冊，發送密碼重設信
    - 統一響應時間（防止 Timing Attack）
    """
    import asyncio
    import time

    # 記錄開始時間
    start_time = time.time()

    # 設定最小響應時間（秒）- 模擬真實發信延遲
    MIN_RESPONSE_TIME = 1.5

    try:
        # 查找用戶（如有重複將由 ORM 拋出異常）
        user = await Users.get(email=payload.email, is_active=True)

        # 發送密碼重設信
        email_service = EmailService()
        success = await email_service.send_password_reset_email(
            user=user,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent")
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="密碼重設信發送失敗，請稍後再試"
            )

        # 計算剩餘時間並延遲（確保總時間至少為 MIN_RESPONSE_TIME）
        elapsed = time.time() - start_time
        if elapsed < MIN_RESPONSE_TIME:
            await asyncio.sleep(MIN_RESPONSE_TIME - elapsed)

        return PasswordResetResponse(
            message="如果該電子郵件已註冊，您將收到密碼重設信",
            success=True
        )

    except DoesNotExist:
        # 安全考量：即使 Email 不存在也返回相同訊息（避免帳號探測）
        # 並且延遲到最小響應時間，防止 Timing Attack
        elapsed = time.time() - start_time
        if elapsed < MIN_RESPONSE_TIME:
            await asyncio.sleep(MIN_RESPONSE_TIME - elapsed)

        return PasswordResetResponse(
            message="如果該電子郵件已註冊，您將收到密碼重設信",
            success=True
        )
    except Exception as e:
        # 統一錯誤響應時間
        elapsed = time.time() - start_time
        if elapsed < MIN_RESPONSE_TIME:
            await asyncio.sleep(MIN_RESPONSE_TIME - elapsed)

        # 特別處理資料完整性問題（使用與驗證端點相同的錯誤處理）
        if "multiple" in str(e).lower() or "MultipleObjectsReturned" in str(type(e).__name__):
            # 錯誤代碼供管理員追查（通用代碼，不揭露具體問題）
            error_code = "ERR_SYSTEM_001"
            # 記錄詳細資訊供管理員查詢（包含 email、IP、時間戳）
            import logging
            logger = logging.getLogger(__name__)
            logger.error(
                f"[{error_code}] Data integrity issue detected during password reset. "
                f"Email: {payload.email}, IP: {request.client.host}, Timestamp: {datetime.now(timezone.utc).isoformat()}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"系統發生錯誤，請聯絡系統管理員並提供錯誤代碼：{error_code}"
            )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"系統錯誤：{str(e)}"
        )


@router.post(
    "/verify-otp",
    response_model=OTPVerificationResponse,
    status_code=status.HTTP_200_OK,
    summary="驗證 OTP",
    description="驗證密碼重設的 OTP 驗證碼"
)
async def verify_otp(payload: OTPVerificationRequest):
    """
    驗證 OTP

    - 驗證 Token 和 OTP 有效性
    - 標記 OTP 為已驗證
    - 返回驗證結果
    """
    try:
        # 查找 AuthToken
        auth_token = await AuthToken.get(
            token=payload.token,
            token_type=AuthTokenType.PASSWORD_RESET,
            status=AuthTokenStatus.PENDING
        ).prefetch_related("user")

        # 檢查是否過期（使用 timezone-aware datetime）
        if auth_token.expires_at < datetime.now(timezone.utc):
            auth_token.status = AuthTokenStatus.EXPIRED
            await auth_token.save()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="驗證碼已過期，請重新申請密碼重設"
            )

        # 驗證 OTP
        if auth_token.otp != payload.otp:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="驗證碼錯誤，請檢查您的電子郵件"
            )

        # 標記 OTP 為已驗證
        auth_token.otp_verified = True
        await auth_token.save()

        return OTPVerificationResponse(
            message="驗證碼驗證成功",
            success=True
        )

    except HTTPException:
        raise
    except DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="重設連結無效或已過期，請重新申請密碼重設"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"系統錯誤：{str(e)}"
        )


@router.post(
    "/reset-password",
    response_model=PasswordResetResponse,
    status_code=status.HTTP_200_OK,
    summary="重設密碼",
    description="使用 Token 重設密碼"
)
async def reset_password(payload: PasswordResetConfirm, request: Request):
    """
    重設密碼

    - 驗證 Token 有效性和 OTP 已驗證
    - 更新用戶密碼
    - 寄送密碼變更通知信
    - 返回重設結果
    """
    try:
        # 查找 AuthToken
        auth_token = await AuthToken.get(
            token=payload.token,
            token_type=AuthTokenType.PASSWORD_RESET,
            status=AuthTokenStatus.PENDING
        ).prefetch_related("user")

        # 檢查是否過期（使用 timezone-aware datetime）
        if auth_token.expires_at < datetime.now(timezone.utc):
            auth_token.status = AuthTokenStatus.EXPIRED
            await auth_token.save()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="重設連結無效或已過期，請重新申請密碼重設"
            )

        # 檢查 OTP 是否已驗證
        if not auth_token.otp_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="請先完成驗證碼驗證"
            )

        # 更新密碼（包含三代不重複檢查）
        user = auth_token.user
        success, error_msg = await PasswordPolicyService.change_password(
            user_id=user.id,
            new_password=payload.new_password,
            change_method="password_reset",
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent")
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )

        # 密碼變更成功後，才標記 Token 為已使用
        auth_token.status = AuthTokenStatus.USED
        auth_token.used_at = datetime.now(timezone.utc)
        await auth_token.save()

        # 寄送密碼變更成功通知信
        try:
            email_service = EmailService()
            await email_service.send_password_changed_notification(
                user=user,
                ip_address=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent")
            )
        except Exception as email_error:
            # 記錄但不阻止密碼重設成功
            print(f"Warning: Failed to send password change notification email: {email_error}")

        return PasswordResetResponse(
            message="密碼重設成功，請使用新密碼登入",
            success=True
        )

    except HTTPException:
        raise
    except DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="重設連結無效或已過期，請重新申請密碼重設"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"系統錯誤：{str(e)}"
        )
    
# ============================================
# 帳號轉移相關端點（舊系統使用者啟用）
# ============================================

@router.post(
    "/login/migrate/verify-otp",
    response_model=AccountMigrationOTPVerifyResponse,
    status_code=status.HTTP_200_OK,
    summary="驗證帳號轉移 OTP",
    description="驗證帳號轉移的 Token 和 OTP，返回使用者資訊"
)
async def verify_migration_otp(payload: AccountMigrationOTPVerifyRequest):
    """
    驗證帳號轉移 OTP

    步驟:
    1. 驗證 Token 是否有效（未過期、未使用）
    2. 驗證 OTP 是否正確
    3. 標記 OTP 為已驗證（otp_verified=True）
    4. 返回使用者資訊供前端顯示和編輯
    """
    try:
        # 查找 AuthToken
        auth_token = await AuthToken.filter(
            token=payload.token,
            token_type=AuthTokenType.ACCOUNT_MIGRATION,
            status=AuthTokenStatus.PENDING
        ).prefetch_related("user", "user__office").first()

        if not auth_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="無效的轉移連結或連結已失效"
            )

        # 檢查是否過期
        if auth_token.expires_at < datetime.now(timezone.utc):
            auth_token.status = AuthTokenStatus.EXPIRED
            await auth_token.save()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="轉移連結已過期，請重新申請"
            )

        # 驗證 OTP
        if auth_token.otp != payload.otp:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="驗證碼錯誤，請檢查您的郵件"
            )

        # 標記 OTP 為已驗證
        auth_token.otp_verified = True
        await auth_token.save()

        # 準備使用者資訊
        user = auth_token.user
        user_info = {
            "username": user.username,
            "full_name": user.full_name,
            "email": user.email,
            "office_id": user.office_id,
            "office_name": user.office.short_name if user.office else None,
            "department": user.department,
            "job_title": user.job_title,
            "phone": user.phone,
            "phone_ext": user.phone_ext,
            "mobile": user.mobile
        }

        return AccountMigrationOTPVerifyResponse(
            message="驗證成功，請設定您的帳號資訊",
            success=True,
            user_info=user_info
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"系統錯誤：{str(e)}"
        )


@router.post(
    "/login/migrate/complete",
    response_model=AccountMigrationCompleteResponse,
    status_code=status.HTTP_200_OK,
    summary="完成帳號轉移",
    description="完成帳號轉移：更新使用者資訊、設定密碼、啟用帳號"
)
async def complete_account_migration(payload: AccountMigrationCompleteRequest):
    """
    完成帳號轉移

    步驟:
    1. 再次驗證 Token + OTP + otp_verified
    2. 更新使用者資訊（full_name, phone, mobile等）
    3. 設定新密碼並 hash
    4. 啟用帳號：email_verified=True, is_active=True
    5. 設定 password_changed_at=NOW()
    6. 標記 Token 為 USED
    7. 返回成功訊息
    """
    try:
        # 查找 AuthToken
        auth_token = await AuthToken.filter(
            token=payload.token,
            token_type=AuthTokenType.ACCOUNT_MIGRATION,
            status=AuthTokenStatus.PENDING,
            otp_verified=True  # 必須已驗證 OTP
        ).prefetch_related("user").first()

        if not auth_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="無效的請求或 OTP 尚未驗證"
            )

        # 再次驗證 OTP
        if auth_token.otp != payload.otp:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="驗證碼錯誤"
            )

        # 檢查是否過期
        if auth_token.expires_at < datetime.now(timezone.utc):
            auth_token.status = AuthTokenStatus.EXPIRED
            await auth_token.save()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="轉移連結已過期"
            )

        # 獲取使用者
        user = auth_token.user

        # 更新使用者資訊（僅更新有提供的欄位）
        if payload.full_name:
            user.full_name = payload.full_name
        if payload.job_title:
            user.job_title = payload.job_title
        if payload.office_id is not None:
            user.office_id = payload.office_id
        if payload.department:
            import json
            try:
                # 解析 JSON 字串並儲存為 JSONB
                department_data = json.loads(payload.department)

                # 驗證 JSON 結構（應該是 dict）
                if not isinstance(department_data, dict):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="department 欄位必須是有效的 JSON 物件"
                    )

                user.department = department_data
            except json.JSONDecodeError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"department 欄位包含無效的 JSON 格式: {str(e)}"
                )
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"處理 department 欄位時發生錯誤: {str(e)}"
                )
        if payload.phone:
            user.phone = payload.phone
        if payload.phone_ext:
            user.phone_ext = payload.phone_ext
        if payload.mobile:
            user.mobile = payload.mobile

        # 設定新密碼
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        user.password = pwd_context.hash(payload.new_password)

        # 啟用帳號
        user.email_verified = True
        user.is_active = True
        user.password_changed_at = datetime.now(timezone.utc)

        # 儲存使用者
        await user.save()

        # 標記 Token 為已使用
        auth_token.status = AuthTokenStatus.USED
        auth_token.used_at = datetime.now(timezone.utc)
        await auth_token.save()

        return AccountMigrationCompleteResponse(
            message="帳號啟用成功！請使用您的帳號和新密碼登入",
            success=True,
            username=user.username
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"系統錯誤：{str(e)}"
        )