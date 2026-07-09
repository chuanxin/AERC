from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, HTTPException, Request
from tortoise.transactions import in_transaction

from src.auth.client_ip import get_client_ip
from src.auth.jwthandler import build_login_response
from src.auth.users import check_password_expired
from src.database.audit_models import AuditAction, AuditEventType, AuditResult
from src.database.models import AuthToken, AuthTokenStatus, AuthTokenType
from src.exceptions import AppError
from src.schemas.mfa import MfaSendRequest, MfaSendResponse, MfaVerifyRequest
from src.services.audit_service import audit_service
from src.services.email_service import EmailService, mask_email

router = APIRouter(prefix="/mfa", tags=["MFA"])

OTP_RESEND_COOLDOWN_SECONDS = 60
OTP_MAX_ATTEMPTS = 5


async def _get_pending_mfa_token(mfa_token: str, *, for_update: bool = False) -> AuthToken:
    """查詢有效（PENDING 且未逾期）的 MFA_VERIFICATION AuthToken，不存在/已逾期回 404/410

    for_update=True 時鎖定該筆記錄以防併發競態（見 VULN-004）；呼叫端必須在
    `async with in_transaction():` 內呼叫，且整個「讀取→判斷→寫入」的關鍵區段都要留在
    同一個 transaction 內，鎖才有意義——鎖定範圍由呼叫端決定，本函數只負責查詢本身。

    for_update=True 時不在此標記 EXPIRED：若寫入後緊接著 raise，會被外層交易一併
    rollback（savepoint 也救不了，因為底層只有一個真正的 transaction）。EXPIRED
    標記交給呼叫端在進入鎖定交易「之前」，先用 for_update=False 呼叫一次獨立檢查
    （該次呼叫在任何交易之外，是各自獨立的 auto-commit，寫入不會被後續動作牽連）。
    """
    query = AuthToken.filter(
        token=mfa_token,
        token_type=AuthTokenType.MFA_VERIFICATION,
        status=AuthTokenStatus.PENDING,
    )
    if for_update:
        query = query.select_for_update()
    auth_token = await query.prefetch_related("user").first()
    if auth_token is None:
        raise AppError(404, "驗證流程不存在或已失效，請重新登入")

    if auth_token.expires_at < datetime.now(timezone.utc):
        if not for_update:
            auth_token.status = AuthTokenStatus.EXPIRED
            await auth_token.save()
        raise AppError(410, "驗證已逾期，請重新登入")

    return auth_token


@router.post("/send", response_model=MfaSendResponse)
async def send_mfa_otp(payload: MfaSendRequest, request: Request):
    client_ip = get_client_ip(request)
    email_service = EmailService()
    cooldown_remaining: Optional[int] = None

    # phase 1：不鎖定的存在性/有效性檢查，404/410（含 EXPIRED 標記）在此獨立生效
    await _get_pending_mfa_token(payload.mfa_token)

    # phase 2：鎖定範圍只到「claim」（冷卻檢查 + 寫入新 otp）為止，寄信是慢速外部 I/O，
    # 刻意留在交易之外執行，避免持鎖等待 SMTP 造成其他請求排隊（VULN-004 修法的一部分）
    async with in_transaction():
        auth_token = await _get_pending_mfa_token(payload.mfa_token, for_update=True)
        user = auth_token.user

        now = datetime.now(timezone.utc)
        if auth_token.otp_sent_at is not None:
            elapsed_seconds = (now - auth_token.otp_sent_at).total_seconds()
            if elapsed_seconds < OTP_RESEND_COOLDOWN_SECONDS:
                cooldown_remaining = int(OTP_RESEND_COOLDOWN_SECONDS - elapsed_seconds)

        if cooldown_remaining is None:
            otp = await email_service.generate_and_store_otp(auth_token)

    # 交易已提交（鎖已釋放）才做稽核與寄信，稽核呼叫置於主業務邏輯完成之後（既有慣例）
    if cooldown_remaining is not None:
        await audit_service.log(
            event_type=AuditEventType.AUTH,
            action=AuditAction.LOGIN,
            result=AuditResult.FAILURE,
            actor_id=user.id,
            actor_username=user.username,
            actor_role=user.role,
            resource_type="mfa_otp_send",
            ip_address=client_ip,
            endpoint=str(request.url.path),
            failure_reason="冷卻中",
        )
        raise HTTPException(
            status_code=429,
            detail={"message": "請稍候再重新發送", "retry_after_seconds": cooldown_remaining},
        )

    sent = await email_service.send_mfa_otp_email(user.email, otp)

    await audit_service.log(
        event_type=AuditEventType.AUTH,
        action=AuditAction.LOGIN,
        result=AuditResult.SUCCESS if sent else AuditResult.FAILURE,
        actor_id=user.id,
        actor_username=user.username,
        actor_role=user.role,
        resource_type="mfa_otp_send",
        ip_address=client_ip,
        endpoint=str(request.url.path),
        failure_reason=None if sent else "Email 寄送失敗",
    )

    return MfaSendResponse(
        message="驗證碼已發送",
        masked_email=mask_email(user.email),
        retry_after_seconds=OTP_RESEND_COOLDOWN_SECONDS,
    )


@router.post("/verify")
async def verify_mfa_otp(payload: MfaVerifyRequest, request: Request):
    client_ip = get_client_ip(request)

    # phase 1：不鎖定的存在性/有效性檢查，404/410（含 EXPIRED 標記）在此獨立生效
    await _get_pending_mfa_token(payload.mfa_token)

    # phase 2：整段「讀取（鎖定）→ 比對 → 遞增/撤銷 → 存檔」都留在同一個 transaction 內，
    # 是純 DB 操作、無外部 I/O，鎖住整段沒有效能疑慮（VULN-004 修法）
    async with in_transaction():
        auth_token = await _get_pending_mfa_token(payload.mfa_token, for_update=True)
        user = auth_token.user
        otp_correct = auth_token.otp == payload.otp

        if otp_correct:
            auth_token.status = AuthTokenStatus.USED
            auth_token.used_at = datetime.now(timezone.utc)
            auth_token.otp_verified = True
        else:
            auth_token.otp_attempt_count += 1
            if auth_token.otp_attempt_count >= OTP_MAX_ATTEMPTS:
                auth_token.status = AuthTokenStatus.REVOKED
        await auth_token.save()

    # 交易已提交（鎖已釋放）才做稽核與後續回應，稽核呼叫置於主業務邏輯完成之後（既有慣例）
    if not otp_correct:
        if auth_token.status == AuthTokenStatus.REVOKED:
            await audit_service.log(
                event_type=AuditEventType.AUTH,
                action=AuditAction.LOGIN,
                result=AuditResult.FAILURE,
                actor_id=user.id,
                actor_username=user.username,
                actor_role=user.role,
                resource_type="mfa_otp_verify",
                ip_address=client_ip,
                endpoint=str(request.url.path),
                failure_reason="核對失敗次數達上限",
            )
            raise AppError(401, "驗證失敗次數過多，請重新登入")

        attempts_remaining = OTP_MAX_ATTEMPTS - auth_token.otp_attempt_count
        await audit_service.log(
            event_type=AuditEventType.AUTH,
            action=AuditAction.LOGIN,
            result=AuditResult.FAILURE,
            actor_id=user.id,
            actor_username=user.username,
            actor_role=user.role,
            resource_type="mfa_otp_verify",
            ip_address=client_ip,
            endpoint=str(request.url.path),
            failure_reason="驗證碼錯誤",
        )
        raise HTTPException(
            status_code=422,
            detail={"message": "驗證碼錯誤", "attempts_remaining": attempts_remaining},
        )

    await audit_service.log(
        event_type=AuditEventType.AUTH,
        action=AuditAction.LOGIN,
        result=AuditResult.SUCCESS,
        actor_id=user.id,
        actor_username=user.username,
        actor_role=user.role,
        resource_type="mfa_otp_verify",
        ip_address=client_ip,
        endpoint=str(request.url.path),
    )

    password_expired = check_password_expired(user)
    return await build_login_response(user, password_expired)
