"""040 公告（最新消息）系統化管理的 Pydantic schema。

長度對齊規則（專案強制）：每個對應 ORM CharField 的輸入欄位皆設 max_length
且 ≤ ORM 值。content_markdown 對應 TextField（無 ORM 上限），設防禦性上限
50000——既有最長公告 436 字元，有充足餘裕，同時避免無上限輸入成為資源耗用面。

內容欄位只有 Markdown 一種：資料庫不儲存 HTML，呈現用的 content 由後端於
讀取時渲染產生，不接受前端傳入——欄位不存在就無法被填錯（N5 錯誤預防）。
"""

from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from src.database.models import AnnouncementStatus

# 內容長度上限：ORM 為 TextField 無上限可對齊，此為防禦性數值
CONTENT_MAX_LENGTH = 50000


# ── 公告類型 ──────────────────────────────────────────────────────────────

class AnnouncementTypeCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=20, description="類型名稱")
    color: str = Field(..., min_length=1, max_length=30, description="列表標示顏色")


class AnnouncementTypeUpdateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=20, description="類型名稱")
    color: str = Field(..., min_length=1, max_length=30, description="列表標示顏色")


# schema-max-length: skip
class AnnouncementTypeResponse(BaseModel):
    id: int
    name: str
    color: str


# ── 公告 ──────────────────────────────────────────────────────────────────

class AnnouncementCreateRequest(BaseModel):
    """必填僅 title 與 type_id（FR-006）。

    publish_date 選填——草稿階段不強迫決定發布日期，未提供時由後端填入建立當日。
    """

    title: str = Field(..., min_length=1, max_length=200, description="標題")
    type_id: int = Field(..., gt=0, description="公告類型 id")
    content_markdown: Optional[str] = Field(
        None, max_length=CONTENT_MAX_LENGTH, description="詳細內容（Markdown 原文）"
    )
    publish_date: Optional[date] = Field(None, description="發布日期；未填時預設建立當日")
    is_pinned: bool = Field(False, description="是否置頂")


class AnnouncementUpdateRequest(BaseModel):
    """不接受 status——狀態只能經 publish / unpublish 端點變更。

    這是把「發布」這個需要獨立稽核的動作，與「改內容」在介面上就分開，
    而不是靠呼叫端自律。
    """

    title: str = Field(..., min_length=1, max_length=200, description="標題")
    type_id: int = Field(..., gt=0, description="公告類型 id")
    content_markdown: Optional[str] = Field(
        None, max_length=CONTENT_MAX_LENGTH, description="詳細內容（Markdown 原文）"
    )
    publish_date: Optional[date] = Field(None, description="發布日期")
    is_pinned: bool = Field(False, description="是否置頂")


class PreviewRequest(BaseModel):
    content_markdown: Optional[str] = Field(
        None, max_length=CONTENT_MAX_LENGTH, description="待預覽的 Markdown 原文"
    )


# schema-max-length: skip
class PreviewResponse(BaseModel):
    content: str = Field(description="渲染 + 消毒後的 HTML，供前端直接呈現")
    changed: bool = Field(description="輸入中是否含被轉義或移除的形式")
    notices: List[str] = Field(description="被轉義或移除的項目（給人看的提示，不參與安全判定）")


# schema-max-length: skip
class AnnouncementListItem(BaseModel):
    """列表項目——不含內容，減少 payload 且列表不需要。"""

    id: int
    title: str
    type: AnnouncementTypeResponse
    publish_date: date
    is_pinned: bool


# schema-max-length: skip
class AnnouncementPublicDetail(AnnouncementListItem):
    """公開明細——content 為本次請求即時渲染的 HTML，不回傳作者原文。"""

    content: str
    status: AnnouncementStatus
    published_at: Optional[datetime]


# schema-max-length: skip
class AnnouncementManageListItem(AnnouncementListItem):
    status: AnnouncementStatus
    created_by_username: Optional[str]
    published_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime


# schema-max-length: skip
class AnnouncementManageDetail(AnnouncementManageListItem):
    """管理明細——唯一同時回傳作者原文與渲染結果的回應。

    content_markdown 供編輯器載入，content 供預覽；一次請求渲染一次，
    避免開啟編輯頁時多一趟往返。
    """

    content_markdown: Optional[str]
    content: str


# schema-max-length: skip
class PaginatedAnnouncements(BaseModel):
    items: List[AnnouncementListItem]
    total: int
    page: int
    page_size: int
    total_pages: int


# schema-max-length: skip
class PaginatedManageAnnouncements(BaseModel):
    items: List[AnnouncementManageListItem]
    total: int
    page: int
    page_size: int
    total_pages: int
