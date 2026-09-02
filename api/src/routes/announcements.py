"""040 公告（最新消息）系統化管理。

架構：二層（schemas + routes，路由內直接操作 ORM），比照 routes/security.py。
公告是單一實體的直接 CRUD 加三態切換，無跨實體驗證、無多步驟業務流程、
無版本控制——說不出為何需要獨立 CRUD 層，就不需要（憲法「架構模式決策閘門」）。

⚠️ 路由宣告順序是契約的一部分：`/manage` 與 `/types` 系列必須全部宣告在
`/{id}` 之前，且 `{id}` 標註為 int。兩道防線同時採用，不依賴單一機制。
"""

import math
from datetime import date, datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, Query, Request, status
from tortoise.exceptions import IntegrityError

from src.auth.jwthandler import get_current_user
from src.database.audit_models import AuditAction, AuditEventType, AuditResult
from src.database.models import Announcement, AnnouncementStatus, AnnouncementType
from src.exceptions import AppError
from src.schemas.announcements import (
    AnnouncementCreateRequest,
    AnnouncementManageDetail,
    AnnouncementManageListItem,
    AnnouncementPublicDetail,
    AnnouncementListItem,
    AnnouncementTypeCreateRequest,
    AnnouncementTypeResponse,
    AnnouncementTypeUpdateRequest,
    AnnouncementUpdateRequest,
    PaginatedAnnouncements,
    PaginatedManageAnnouncements,
    PreviewRequest,
    PreviewResponse,
)
from src.schemas.permissions import ModuleName, PermissionAction
from src.schemas.users import UserInfoSchema
from src.services.audit_service import audit_service
from src.services.content_renderer import preview as render_preview
from src.services.content_renderer import render
from src.services.permission_service import permission_service

router = APIRouter(prefix="/announcements", tags=["Announcements"])

# 排序：置頂優先 → 發布日期新到舊 → id 新到舊
#
# 第三鍵 id 不是裝飾：少了它，同日期多則的順序由 PostgreSQL 自行決定，
# 使用者會看到重新整理就換順序；分頁時更嚴重——不穩定排序會讓同一則公告
# 在第 1 頁與第 2 頁重複出現或整則消失（FR-014）。
_ORDER = ("-is_pinned", "-publish_date", "-id")


# ── 共用小工具 ────────────────────────────────────────────────────────────

def _require(current_user: UserInfoSchema, action: PermissionAction) -> None:
    """公告管理權限守衛。守衛不可延後——沒有守衛的管理 API 是安全漏洞。"""
    allowed, _reason = permission_service.check_permission(
        user_role=current_user.role,
        user_permissions=current_user.permissions,
        module=ModuleName.ANNOUNCEMENTS,
        action=action,
    )
    if not allowed:
        raise AppError(403, "無此操作權限")


def _can_manage(current_user: UserInfoSchema) -> bool:
    allowed, _ = permission_service.check_permission(
        user_role=current_user.role,
        user_permissions=current_user.permissions,
        module=ModuleName.ANNOUNCEMENTS,
        action=PermissionAction.VIEW,
    )
    return allowed


def _type_out(t: AnnouncementType) -> AnnouncementTypeResponse:
    return AnnouncementTypeResponse(id=t.id, name=t.name, color=t.color)


def _list_item(a: Announcement) -> AnnouncementListItem:
    return AnnouncementListItem(
        id=a.id, title=a.title, type=_type_out(a.type),
        publish_date=a.publish_date, is_pinned=a.is_pinned,
    )


def _public_detail(a: Announcement) -> AnnouncementPublicDetail:
    """公開明細：content 為本次請求即時渲染的 HTML，不回傳作者原文。"""
    return AnnouncementPublicDetail(
        id=a.id, title=a.title, type=_type_out(a.type),
        publish_date=a.publish_date, is_pinned=a.is_pinned,
        content=render(a.content_markdown),
        status=a.status, published_at=a.published_at,
    )


def _manage_list_item(a: Announcement) -> AnnouncementManageListItem:
    return AnnouncementManageListItem(
        id=a.id, title=a.title, type=_type_out(a.type),
        publish_date=a.publish_date, is_pinned=a.is_pinned,
        status=a.status,
        created_by_username=a.created_by.username if a.created_by else None,
        published_at=a.published_at,
        created_at=a.created_at, updated_at=a.updated_at,
    )


def _manage_detail(a: Announcement) -> AnnouncementManageDetail:
    """管理明細：同時回傳作者原文（供編輯器）與渲染結果（供預覽）。"""
    return AnnouncementManageDetail(
        **_manage_list_item(a).model_dump(),
        content_markdown=a.content_markdown,
        content=render(a.content_markdown),
    )


def _client_ip(request: Request) -> str:
    """生產環境反向代理是 Caddy，真實來源 IP 在 X-Real-IP。"""
    return request.headers.get("X-Real-IP", "") or (
        request.client.host if request.client else ""
    )


async def _audit(
    request: Request,
    current_user: UserInfoSchema,
    action: AuditAction,
    resource_type: str,
    resource_id: int | str,
    changed_fields: dict,
) -> None:
    """稽核紀錄。

    `changed_fields` 一律含 title（公告）或 name（類型）——security_audit_logs
    沒有獨立的標題欄位、resource_id 只是數字、公告為硬刪除，事後僅憑數字
    查不回任何東西（FR-042）。
    """
    await audit_service.log(
        event_type=AuditEventType.CONFIG,
        action=action,
        result=AuditResult.SUCCESS,
        actor_id=current_user.id,
        actor_username=current_user.username,
        actor_role=current_user.role,
        resource_type=resource_type,
        resource_id=str(resource_id),
        ip_address=_client_ip(request),
        user_agent=request.headers.get("User-Agent", ""),
        endpoint=str(request.url.path),
        changed_fields=changed_fields,
    )


async def _get_type_or_404(type_id: int) -> AnnouncementType:
    t = await AnnouncementType.filter(id=type_id).first()
    if t is None:
        raise AppError(404, "找不到此公告類型")
    return t


# ═════════════════════════════════════════════════════════════════════════
# 管理端點——公告類型
#
# ⚠️ 必須宣告在 /{id} 之前（見檔頭）。
# ═════════════════════════════════════════════════════════════════════════

@router.get("/types", response_model=list[AnnouncementTypeResponse])
async def list_types(current_user: UserInfoSchema = Depends(get_current_user)):
    """公告類型清單。

    權限為 ANNOUNCEMENTS:VIEW 而非「僅需登入」——公開列表與明細的回應已內嵌
    type{id,name,color}，公開端從來不需要這支端點；其真實消費者只有管理後台
    的類型維護介面與類型篩選下拉。
    """
    _require(current_user, PermissionAction.VIEW)
    types = await AnnouncementType.all().order_by("id")
    return [_type_out(t) for t in types]


@router.post("/types", response_model=AnnouncementTypeResponse, status_code=status.HTTP_201_CREATED)
async def create_type(
    payload: AnnouncementTypeCreateRequest,
    request: Request,
    current_user: UserInfoSchema = Depends(get_current_user),
):
    _require(current_user, PermissionAction.CREATE)

    # 預檢提供友善訊息
    if await AnnouncementType.filter(name=payload.name).exists():
        raise AppError(409, "此類型名稱已存在")
    try:
        created = await AnnouncementType.create(name=payload.name, color=payload.color)
    except IntegrityError as e:
        # 安全網（防預檢與寫入之間的並發競態）：實際查詢驗證衝突欄位，
        # 不用刪除法猜測。name 是本表唯一的唯一約束候選；驗不出來就誠實回報
        # 並記錄診斷，不對使用者宣稱一個未經驗證的原因（AERC-0417 教訓）。
        if await AnnouncementType.filter(name=payload.name).exists():
            raise AppError(409, "此類型名稱已存在")
        raise AppError(500, "系統錯誤，請稍後再試", diagnostic=str(e))

    await _audit(request, current_user, AuditAction.CREATE, "announcement_type",
                 created.id, {"name": created.name, "color": created.color})
    return _type_out(created)


@router.put("/types/{type_id}", response_model=AnnouncementTypeResponse)
async def update_type(
    type_id: int,
    payload: AnnouncementTypeUpdateRequest,
    request: Request,
    current_user: UserInfoSchema = Depends(get_current_user),
):
    _require(current_user, PermissionAction.EDIT)
    target = await _get_type_or_404(type_id)

    if await AnnouncementType.filter(name=payload.name).exclude(id=type_id).exists():
        raise AppError(409, "此類型名稱已存在")

    before = {"name": target.name, "color": target.color}
    target.name = payload.name
    target.color = payload.color
    try:
        await target.save()
    except IntegrityError as e:
        if await AnnouncementType.filter(name=payload.name).exclude(id=type_id).exists():
            raise AppError(409, "此類型名稱已存在")
        raise AppError(500, "系統錯誤，請稍後再試", diagnostic=str(e))

    await _audit(request, current_user, AuditAction.UPDATE, "announcement_type", type_id,
                 {"name": target.name, "before": before})
    return _type_out(target)


@router.delete("/types/{type_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_type(
    type_id: int,
    request: Request,
    current_user: UserInfoSchema = Depends(get_current_user),
):
    """刪除公告類型。

    兩道檢查皆先於刪除；FK RESTRICT 為並發競態的資料庫層最終保證，
    觸發時回同一個 409 與同一句訊息。
    """
    _require(current_user, PermissionAction.DELETE)
    target = await _get_type_or_404(type_id)

    in_use = await Announcement.filter(type_id=type_id).count()
    if in_use > 0:
        raise AppError(409, f"此類型已被 {in_use} 則公告使用，無法刪除")

    if await AnnouncementType.all().count() <= 1:
        raise AppError(409, "系統必須至少保留一種公告類型")

    name = target.name
    try:
        await target.delete()
    except IntegrityError as e:
        # RESTRICT 觸發：預檢與刪除之間有人建了公告
        still_in_use = await Announcement.filter(type_id=type_id).count()
        if still_in_use > 0:
            raise AppError(409, f"此類型已被 {still_in_use} 則公告使用，無法刪除")
        raise AppError(500, "系統錯誤，請稍後再試", diagnostic=str(e))

    await _audit(request, current_user, AuditAction.DELETE, "announcement_type",
                 type_id, {"name": name})


# ═════════════════════════════════════════════════════════════════════════
# 管理端點——公告
# ═════════════════════════════════════════════════════════════════════════

@router.get("/manage", response_model=PaginatedManageAnnouncements)
async def list_manage(
    page: int = Query(1, ge=1, description="頁碼"),
    page_size: int = Query(20, ge=1, le=100, description="每頁筆數"),
    status_filter: Optional[AnnouncementStatus] = Query(None, alias="status"),
    type_id: Optional[int] = Query(None, gt=0),
    keyword: Optional[str] = Query(None, max_length=200, description="標題關鍵字"),
    current_user: UserInfoSchema = Depends(get_current_user),
):
    _require(current_user, PermissionAction.VIEW)

    query = Announcement.all()
    if status_filter is not None:
        query = query.filter(status=status_filter)
    if type_id is not None:
        query = query.filter(type_id=type_id)
    if keyword:
        query = query.filter(title__icontains=keyword)

    total = await query.count()
    rows = await (
        query.prefetch_related("type", "created_by")
        .order_by(*_ORDER)
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    return PaginatedManageAnnouncements(
        items=[_manage_list_item(a) for a in rows],
        total=total, page=page, page_size=page_size,
        total_pages=max(1, math.ceil(total / page_size)),
    )


@router.post("", response_model=AnnouncementManageDetail, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=AnnouncementManageDetail, status_code=status.HTTP_201_CREATED,
             include_in_schema=False)
async def create_announcement(
    payload: AnnouncementCreateRequest,
    request: Request,
    current_user: UserInfoSchema = Depends(get_current_user),
):
    """新增公告。

    只收 content_markdown 並**原樣儲存**——作者打什麼就存什麼，包含他貼進來的
    任何原始碼，那在資料庫裡只是文字（FR-006a）。渲染與消毒發生在輸出端。
    publish_date 未提供時填入建立當日（FR-006）。
    """
    _require(current_user, PermissionAction.CREATE)
    await _get_type_or_404(payload.type_id)

    created = await Announcement.create(
        title=payload.title,
        type_id=payload.type_id,
        content_markdown=payload.content_markdown,
        publish_date=payload.publish_date or date.today(),
        status=AnnouncementStatus.DRAFT,
        is_pinned=payload.is_pinned,
        created_by_id=current_user.id,
    )
    await created.fetch_related("type", "created_by")
    await _audit(request, current_user, AuditAction.CREATE, "announcement",
                 created.id, {"title": created.title})
    return _manage_detail(created)


@router.get("/manage/{announcement_id}", response_model=AnnouncementManageDetail)
async def get_manage_detail(
    announcement_id: int,
    current_user: UserInfoSchema = Depends(get_current_user),
):
    """管理明細——唯一同時回傳作者原文與渲染結果的端點。"""
    _require(current_user, PermissionAction.VIEW)
    target = await (
        Announcement.filter(id=announcement_id)
        .prefetch_related("type", "created_by").first()
    )
    if target is None:
        raise AppError(404, "找不到此公告")
    return _manage_detail(target)


@router.put("/manage/{announcement_id}", response_model=AnnouncementManageDetail)
async def update_announcement(
    announcement_id: int,
    payload: AnnouncementUpdateRequest,
    request: Request,
    current_user: UserInfoSchema = Depends(get_current_user),
):
    """編輯公告。

    request schema **不含 status**——狀態只能經 publish / unpublish 端點變更。
    這是把「發布」這個需要獨立稽核的動作，與「改內容」在介面上就分開。
    """
    _require(current_user, PermissionAction.EDIT)
    target = await (
        Announcement.filter(id=announcement_id).prefetch_related("type", "created_by").first()
    )
    if target is None:
        raise AppError(404, "找不到此公告")
    await _get_type_or_404(payload.type_id)

    changed: dict = {}
    if target.title != payload.title:
        changed["title_before"] = target.title
    if target.type_id != payload.type_id:
        changed["type_id"] = {"before": target.type_id, "after": payload.type_id}
    if (target.content_markdown or "") != (payload.content_markdown or ""):
        # content 只記「已變更」布林，不把整段內容塞進稽核紀錄
        changed["content_changed"] = True
    if payload.publish_date and target.publish_date != payload.publish_date:
        changed["publish_date"] = {
            "before": target.publish_date.isoformat(), "after": payload.publish_date.isoformat()
        }
    if target.is_pinned != payload.is_pinned:
        changed["is_pinned"] = {"before": target.is_pinned, "after": payload.is_pinned}

    target.title = payload.title
    target.type_id = payload.type_id
    target.content_markdown = payload.content_markdown
    if payload.publish_date:
        target.publish_date = payload.publish_date
    target.is_pinned = payload.is_pinned
    await target.save()
    await target.fetch_related("type", "created_by")

    # title 無論是否變更皆記錄——只改內容的那次修改，事後同樣要查得出
    # 動的是哪一則公告（FR-042）
    await _audit(request, current_user, AuditAction.UPDATE, "announcement",
                 announcement_id, {"title": target.title, **changed})
    return _manage_detail(target)


@router.patch("/manage/{announcement_id}/publish", response_model=AnnouncementManageDetail)
async def publish_announcement(
    announcement_id: int,
    request: Request,
    current_user: UserInfoSchema = Depends(get_current_user),
):
    """發布。合法起始狀態為 draft / archived。"""
    _require(current_user, PermissionAction.EDIT)
    target = await (
        Announcement.filter(id=announcement_id).prefetch_related("type", "created_by").first()
    )
    if target is None:
        raise AppError(404, "找不到此公告")
    if target.status == AnnouncementStatus.PUBLISHED:
        raise AppError(400, "公告狀態不允許此操作")

    before = target.status.value if hasattr(target.status, "value") else str(target.status)
    target.status = AnnouncementStatus.PUBLISHED
    target.published_at = datetime.now(timezone.utc)
    await target.save()
    await target.fetch_related("type", "created_by")

    await _audit(request, current_user, AuditAction.PUBLISH, "announcement", announcement_id,
                 {"title": target.title, "status": {"before": before, "after": "published"}})
    return _manage_detail(target)


@router.patch("/manage/{announcement_id}/unpublish", response_model=AnnouncementManageDetail)
async def unpublish_announcement(
    announcement_id: int,
    request: Request,
    current_user: UserInfoSchema = Depends(get_current_user),
):
    """下架。合法起始狀態僅 published；published_at **保留不清空**。

    清空會讓稽核紀錄與資料本身矛盾——稽核說某人某時發布過，資料卻顯示從未發布。
    """
    _require(current_user, PermissionAction.EDIT)
    target = await (
        Announcement.filter(id=announcement_id).prefetch_related("type", "created_by").first()
    )
    if target is None:
        raise AppError(404, "找不到此公告")
    if target.status != AnnouncementStatus.PUBLISHED:
        raise AppError(400, "公告狀態不允許此操作")

    target.status = AnnouncementStatus.ARCHIVED
    await target.save()
    await target.fetch_related("type", "created_by")

    await _audit(request, current_user, AuditAction.UNPUBLISH, "announcement", announcement_id,
                 {"title": target.title, "status": {"before": "published", "after": "archived"}})
    return _manage_detail(target)


@router.delete("/manage/{announcement_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_announcement(
    announcement_id: int,
    request: Request,
    current_user: UserInfoSchema = Depends(get_current_user),
):
    """硬刪除。二次確認是前端職責，後端不增設確認參數——把它做成 API 參數
    只會讓非 UI 呼叫端繞過。"""
    _require(current_user, PermissionAction.DELETE)
    target = await Announcement.filter(id=announcement_id).first()
    if target is None:
        raise AppError(404, "找不到此公告")

    title = target.title
    await target.delete()
    # 硬刪除後僅憑 resource_id 查不回任何東西，title 必須進 changed_fields
    await _audit(request, current_user, AuditAction.DELETE, "announcement",
                 announcement_id, {"title": title})


@router.post("/manage/preview", response_model=PreviewResponse)
async def preview_content(
    payload: PreviewRequest,
    current_user: UserInfoSchema = Depends(get_current_user),
):
    """編輯期即時預覽與回饋。不寫入任何資料。

    端點名稱不叫 sanitize-preview——Markdown 化後這支端點的主要職責是
    渲染預覽，消毒只是其中一段。
    """
    if not _can_manage(current_user):
        raise AppError(403, "無此操作權限")
    return PreviewResponse(**render_preview(payload.content_markdown))


# ═════════════════════════════════════════════════════════════════════════
# 公開讀取端點（僅需登入）
#
# ⚠️ 必須宣告在最後：/{announcement_id} 會吃掉任何字面路徑。
#    兩道防線——(1) 宣告順序讓 /manage、/types 先匹配；
#              (2) announcement_id 標註為 int，字串本就無法匹配。
# ═════════════════════════════════════════════════════════════════════════

@router.get("", response_model=PaginatedAnnouncements)
@router.get("/", response_model=PaginatedAnnouncements, include_in_schema=False)
async def list_public(
    limit: Optional[int] = Query(None, ge=1, le=50, description="首頁用；與分頁參數互斥"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: UserInfoSchema = Depends(get_current_user),
):
    """公開列表：首頁與列表頁共用。僅回傳 published，**不含內容**。

    列表不回傳內容，因此完全沒有渲染成本。
    """
    query = Announcement.filter(status=AnnouncementStatus.PUBLISHED)
    total = await query.count()

    rows_q = query.prefetch_related("type").order_by(*_ORDER)
    if limit is not None:
        rows = await rows_q.limit(limit)
        eff_page, eff_size = 1, limit
    else:
        rows = await rows_q.offset((page - 1) * page_size).limit(page_size)
        eff_page, eff_size = page, page_size

    return PaginatedAnnouncements(
        items=[_list_item(a) for a in rows],
        total=total, page=eff_page, page_size=eff_size,
        total_pages=max(1, math.ceil(total / eff_size)),
    )


@router.get("/{announcement_id}", response_model=AnnouncementPublicDetail)
async def get_public_detail(
    announcement_id: int,
    current_user: UserInfoSchema = Depends(get_current_user),
):
    """公開明細。content 為本次請求即時渲染並消毒的 HTML。

    具 ANNOUNCEMENTS:VIEW 權限者可讀任何狀態（發布前預覽，FR-032）；
    否則僅 published。

    「不存在」與「一般使用者存取非 published」兩種情況的回應**完全相同**
    ——若前者 404、後者 403，等於洩漏「這個 id 存在但你不能看」，而兩種
    訊息也沒有帶來任何好處。
    """
    query = Announcement.filter(id=announcement_id)
    if not _can_manage(current_user):
        query = query.filter(status=AnnouncementStatus.PUBLISHED)

    target = await query.prefetch_related("type").first()
    if target is None:
        raise AppError(404, "找不到此公告")
    return _public_detail(target)
