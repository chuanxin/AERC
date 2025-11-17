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
    LoginWithCaptchaRequest,
)
from src.database.models import Users, AuthToken, AuthTokenType, AuthTokenStatus
from src.services.email_service import EmailService
from src.services.captcha_service import CaptchaService
from datetime import datetime, timezone

from src.auth.jwthandler import (
    create_access_token,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES,
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
        CaptchaResponse: 包含 captcha_id 和 captcha_code
    """
    captcha_id, captcha_code = await CaptchaService.generate()
    return CaptchaResponse(
        captcha_id=captcha_id,
        captcha_code=captcha_code
    )


@router.post("/register", response_model=UserOutSchema)
async def create_user(user: UserInSchema) -> UserOutSchema:
    return await crud.create_user(user)


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
    }
    response = JSONResponse(content=content)
    response.set_cookie(
        "Authorization",
        value=f"Bearer {token}",
        httponly=True,
        # max_age=1800,
        # expires=1800,
        samesite="Lax",
        secure=True,
    )

    return response


@router.post("/login-secure")
async def login_with_captcha(payload: LoginWithCaptchaRequest):
    """
    帶驗證碼的安全登入

    - 先驗證驗證碼
    - 再驗證帳號密碼
    - 返回 JWT Token
    """
    # 1. 驗證驗證碼
    if not await CaptchaService.verify(payload.captcha_id, payload.captcha_code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="驗證碼錯誤或已過期"
        )

    # 2. 驗證帳號密碼
    from src.auth.users import verify_password
    try:
        user = await Users.get(username=payload.username)
        if not verify_password(payload.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="使用者名稱或密碼不正確",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except DoesNotExist:
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

    # 3. 更新最後登入時間
    await crud.update_last_login(user.id)

    # 4. 生成 JWT Token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    token = jsonable_encoder(access_token)
    content = {
        "message": "You've successfully logged in. Welcome back!",
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
    "/users/whoami", response_model=UserInfoSchema, dependencies=[Depends(get_current_user)]
)
async def read_users_me(current_user: UserInfoSchema = Depends(get_current_user)):
    return current_user


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
        # 查找用戶
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
        # 查找用戶
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
            message="密碼重設信已發送至您的電子郵件",
            success=True
        )

    except DoesNotExist:
        # 安全考量：即使 Email 不存在也返回成功訊息（避免帳號探測）
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

        # 檢查是否過期
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
async def reset_password(payload: PasswordResetConfirm):
    """
    重設密碼

    - 驗證 Token 有效性和 OTP 已驗證
    - 更新用戶密碼
    - 返回重設結果
    """
    try:
        # 查找 AuthToken
        auth_token = await AuthToken.get(
            token=payload.token,
            token_type=AuthTokenType.PASSWORD_RESET,
            status=AuthTokenStatus.PENDING
        ).prefetch_related("user")

        # 檢查是否過期
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

        # 標記為已使用
        auth_token.status = AuthTokenStatus.USED
        auth_token.used_at = datetime.now(timezone.utc)
        await auth_token.save()

        # 更新密碼
        user = auth_token.user
        user.password = get_password_hash(payload.new_password)
        await user.save()

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