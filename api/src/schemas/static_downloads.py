from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime

# schema-max-length: skip（伺服器掃描檔案系統後組裝的回應資料，非使用者輸入路徑）
class StaticFileInfo(BaseModel):
    """靜態檔案資訊"""
    id: str = Field(description="檔案唯一識別碼")
    base_name: str = Field(description="基本檔名（不含副檔名）")
    filename: str = Field(description="完整檔名")
    format: str = Field(description="檔案格式")
    size: int = Field(description="檔案大小（bytes）")
    created_at: datetime = Field(description="建立時間")
    modified_at: datetime = Field(description="修改時間")
    category: Optional[str] = Field(default=None, description="檔案類型")
    description: Optional[str] = Field(default=None, description="檔案說明")
    download_url: str = Field(description="下載連結")

# schema-max-length: skip（伺服器組裝的檔案群組回應資料，非使用者輸入路徑）
class FileGroup(BaseModel):
    """相同檔名的多格式檔案群組"""
    base_name: str = Field(description="基本檔名")
    display_name: str = Field(description="顯示名稱")
    formats: List[StaticFileInfo] = Field(description="可用格式清單")
    category: Optional[str] = Field(default=None, description="檔案類型")
    description: Optional[str] = Field(default=None, description="檔案說明")
    total_files: int = Field(description="格式數量")
    latest_modified: datetime = Field(description="最新修改時間")

class StaticDownloadsListResponse(BaseModel):
    """靜態下載檔案清單回應"""
    file_groups: List[FileGroup] = Field(description="檔案群組清單")
    total_groups: int = Field(description="檔案群組總數")
    total_files: int = Field(description="檔案總數")
    categories: List[str] = Field(description="可用類型清單")

class StaticDownloadsFilterRequest(BaseModel):
    """靜態下載檔案篩選請求"""
    category: Optional[str] = Field(default=None, max_length=50, description="檔案類型篩選")
    format: Optional[str] = Field(default=None, max_length=20, description="檔案格式篩選")
    search_keyword: Optional[str] = Field(default=None, max_length=200, description="搜尋關鍵字")
    date_range: Optional[str] = Field(default=None, max_length=50, description="時間範圍篩選")

class BatchDownloadRequest(BaseModel):
    """批量下載請求"""
    file_ids: List[str] = Field(description="檔案ID清單")
    download_name: Optional[str] = Field(default=None, max_length=255, description="下載檔案名稱")