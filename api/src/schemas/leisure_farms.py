"""
休閒農場資料查詢系統的 Pydantic Schemas
資料來源：農業部開放資料平台
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal


# === 回應 Schemas ===

class LeisureFarmItem(BaseModel):
    """休閒農場單筆資料"""
    id: int = Field(..., description="主鍵 ID")
    farm_name: str = Field(..., description="農場名稱")
    county: str = Field(..., description="縣市名稱")
    township: str = Field(..., description="鄉鎮市區名稱")
    address: Optional[str] = Field(None, description="農場地址")
    phone: Optional[str] = Field(None, description="聯絡電話")
    web_url: Optional[str] = Field(None, description="農場網站")
    certify_start_date: Optional[date] = Field(None, description="認證起始日期")
    certify_end_date: Optional[date] = Field(None, description="認證結束日期")
    identify_item: Optional[str] = Field(None, description="認證項目")
    photo_url: Optional[str] = Field(None, description="農場照片 URL")
    longitude: Decimal = Field(..., description="經度 WGS84")
    latitude: Decimal = Field(..., description="緯度 WGS84")
    distance_meters: Optional[float] = Field(None, description="與查詢點的距離（公尺）")

    class Config:
        from_attributes = True


class LeisureFarmNearbyResponse(BaseModel):
    """鄰近休閒農場查詢回應"""
    success: bool = Field(default=True, description="查詢是否成功")
    farms: List[LeisureFarmItem] = Field(default_factory=list, description="鄰近農場列表")
    total_count: int = Field(default=0, description="總筆數")
    query_point: Optional[dict] = Field(None, description="查詢點座標")
    search_radius_meters: float = Field(..., description="查詢半徑（公尺）")
    message: Optional[str] = Field(None, description="訊息")


class LeisureFarmCheckResponse(BaseModel):
    """休閒農場重疊檢查回應"""
    success: bool = Field(default=True, description="查詢是否成功")
    has_nearby_farms: bool = Field(default=False, description="是否有鄰近農場")
    nearest_farm: Optional[LeisureFarmItem] = Field(None, description="最近的農場")
    farms_within_radius: int = Field(default=0, description="範圍內農場數量")
    message: Optional[str] = Field(None, description="訊息")


class LeisureFarmByLocationResponse(BaseModel):
    """依地區查詢休閒農場回應"""
    success: bool = Field(default=True, description="查詢是否成功")
    farms: List[LeisureFarmItem] = Field(default_factory=list, description="農場列表")
    total_count: int = Field(default=0, description="總筆數")
    county: Optional[str] = Field(None, description="查詢縣市")
    township: Optional[str] = Field(None, description="查詢鄉鎮")


class LeisureFarmStatsResponse(BaseModel):
    """休閒農場統計回應"""
    success: bool = Field(default=True, description="查詢是否成功")
    total_farms: int = Field(default=0, description="農場總數")
    by_county: dict = Field(default_factory=dict, description="依縣市統計")
    last_synced: Optional[datetime] = Field(None, description="最後同步時間")


# === 請求 Schemas ===

class NearbySearchRequest(BaseModel):
    """鄰近查詢請求"""
    longitude: Decimal = Field(..., description="查詢點經度 WGS84")
    latitude: Decimal = Field(..., description="查詢點緯度 WGS84")
    radius_meters: float = Field(default=5000, ge=100, le=50000, description="查詢半徑（公尺），預設 5000m")
    limit: int = Field(default=10, ge=1, le=100, description="最大回傳筆數")


class LocationSearchRequest(BaseModel):
    """依地區查詢請求"""
    county: Optional[str] = Field(None, description="縣市名稱")
    township: Optional[str] = Field(None, description="鄉鎮市區名稱")


# === 同步相關 Schemas ===

class MOALeisureFarmData(BaseModel):
    """MOA API 回傳的休閒農場資料格式"""
    FarmNm_CH: str = Field(..., description="農場名稱")
    County: str = Field(..., description="縣市")
    Township: str = Field(..., description="鄉鎮")
    Address_CH: Optional[str] = Field(None, description="地址")
    TEL: Optional[str] = Field(None, description="電話")
    WebURL: Optional[str] = Field(None, description="網站")
    CertifySDate: Optional[str] = Field(None, description="認證起始日期")
    CertifyEDate: Optional[str] = Field(None, description="認證結束日期")
    IdentifyItem: Optional[str] = Field(None, description="認證項目")
    Photo: Optional[str] = Field(None, description="照片")
    Longitude: str = Field(..., description="經度")
    Latitude: str = Field(..., description="緯度")

    class Config:
        extra = "ignore"  # 忽略 API 回傳的其他欄位


class SyncResultResponse(BaseModel):
    """同步結果回應"""
    success: bool = Field(default=True, description="同步是否成功")
    total_fetched: int = Field(default=0, description="從 API 取得的筆數")
    inserted: int = Field(default=0, description="新增筆數")
    updated: int = Field(default=0, description="更新筆數")
    errors: int = Field(default=0, description="錯誤筆數")
    sync_time: datetime = Field(..., description="同步時間")
    message: Optional[str] = Field(None, description="訊息")
