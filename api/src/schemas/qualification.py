"""
Qualification 重複案件查詢系統的 Pydantic Schemas
基於現有的 GrantLocations 資料模型
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union
from enum import Enum
from decimal import Decimal
from datetime import datetime
from src.database.models import GrantStatus


class QualificationQueryType(str, Enum):
    """查詢類型枚舉 - 統一處理三種查詢模式"""
    GENERAL = "general"        # 一般區域查詢
    INDIGENOUS = "indigenous"  # 原住民鄉查詢
    SLOPE = "slope"           # 山坡地查詢


# 案件狀態直接使用 GrantStatus (單一來源原則)
# 不再維護重複的 CaseStatus 枚舉


class CaseType(str, Enum):
    """案件類型枚舉"""
    POWER_EQUIPMENT = "動力設備"    # 動力設備
    FIELD_PIPELINE = "田間管路"     # 田間管路
    STORAGE_FACILITY = "調蓄設施"   # 調蓄設施
    CONTROL_FACILITY = "調控設施"   # 調控設施


# === 請求 Schemas ===

class LocationParams(BaseModel):
    """地區查詢參數"""
    county: Optional[str] = Field(None, description="縣市名稱(可選)")
    town: Optional[str] = Field(None, description="鄉鎮名稱(可選)")
    section: Optional[str] = Field(None, description="地段名稱(可選)")
    land_number: Optional[str] = Field(None, description="地號")

    @validator('land_number')
    def validate_land_number_for_general(cls, v, values):
        """一般查詢類型必須提供地號"""
        # 這個驗證會在 QualificationSearchRequest 中處理
        return v


class QueryOptions(BaseModel):
    """查詢選項"""
    years: Optional[List[str]] = Field(default=None, description="查詢年度清單(空值代表查詢所有年度)")
    include_statistics: bool = Field(default=True, description="是否包含面積統計")
    include_office_boundaries: bool = Field(default=False, description="是否包含水利工作站界限交集資訊")
    max_results: int = Field(default=1000, le=1000, description="最大回傳結果數")

    @validator('years')
    def validate_years(cls, v):
        """驗證年度列表，過濾掉無效值"""
        if v is None:
            return v
        # 過濾掉 None 和空字串
        valid_years = [year for year in v if year is not None and isinstance(year, str) and year.strip()]
        return valid_years if valid_years else None


class QualificationSearchRequest(BaseModel):
    """統一查詢請求 - 消除三種查詢類型的特殊情況"""
    query_type: QualificationQueryType = Field(..., description="查詢類型")
    params: LocationParams = Field(..., description="地區查詢參數")
    options: Optional[QueryOptions] = Field(default_factory=QueryOptions, description="查詢選項")

    @validator('params')
    def validate_search_params(cls, v, values):
        """驗證查詢參數 - 至少需要地號或完整地址"""
        if not v.land_number and not (v.county and v.town):
            raise ValueError("必須提供地號，或者提供完整的縣市鄉鎮資訊")
        return v

    @validator('params')
    def validate_params_by_query_type(cls, v, values):
        """根據查詢類型驗證參數"""
        query_type = values.get('query_type')
        
        if query_type == QualificationQueryType.GENERAL:
            if not v.land_number:
                raise ValueError("一般區域查詢必須提供地號")
        
        return v


class AreaCheckRequest(BaseModel):
    """區域驗證請求"""
    county: str = Field(..., min_length=1, description="縣市名稱")
    town: str = Field(..., min_length=1, description="鄉鎮名稱")


# === 回應 Schemas ===

class AreaStatistics(BaseModel):
    """面積統計結果 - 7項核心指標"""
    land_total_area: Decimal = Field(..., description="設查詢地號總面積(㎡)")
    used_area: Decimal = Field(..., description="已經補助申請設施面積(㎡)")
    remaining_area: Decimal = Field(..., description="剩餘申請面積(㎡)")
    
    # 微灌設施統計
    micro_irrigation_area: Decimal = Field(..., description="已經補助微灌設施面積(㎡)")
    remaining_micro_area: Decimal = Field(..., description="剩餘申請面積-微灌(㎡)")
    
    # 噴水設施統計
    sprinkler_area: Decimal = Field(..., description="已經補助噴水設施面積(㎡)")
    remaining_sprinkler_area: Decimal = Field(..., description="剩餘申請面積-噴水(㎡)")

    class Config:
        json_encoders = {
            Decimal: lambda v: float(v)
        }


class GrantCaseItem(BaseModel):
    """補助案件項目"""
    id: int = Field(..., description="GrantLocations.id")
    source_system: str = Field(..., description="資料來源系統")
    grant_id: str = Field(..., description="對應的 grant ID")

    # 案件基本資訊
    case_number: Optional[str] = Field(None, description="案件編號")
    case_type: str = Field(..., description="案件類型")
    irrigation_type: Optional[str] = Field(None, description="灌溉型式")
    status: GrantStatus = Field(..., description="案件狀態")
    office: str = Field(..., description="管理處名稱 (來自 grants.office)")

    # 地籍資訊
    land_section: str = Field(..., description="地段")
    land_number: str = Field(..., description="地號")
    
    # 申請資訊
    application_year: int = Field(..., description="申請年度(民國年)")
    applicant: str = Field(..., description="申請人")
    department: Optional[str] = Field(None, description="承辦單位")
    
    
    # 面積資訊
    approved_area: Decimal = Field(..., description="核准面積(㎡)")
    land_registered_area: Optional[Decimal] = Field(None, description="地籍登記面積(㎡) - 來源於meta_data")
    
    # 額外資訊
    crops: Optional[List[Dict[str, str]]] = Field(None, description="作物資訊")
    is_aboriginal_area: Optional[bool] = Field(None, description="是否原民區域")
    office_boundaries: Optional[List[Dict[str, Any]]] = Field(None, description="水利工作站界限交集資訊")
    
    class Config:
        json_encoders = {
            Decimal: lambda v: float(v)
        }


class QueryInfo(BaseModel):
    """查詢資訊摘要"""
    query_type: QualificationQueryType = Field(..., description="查詢類型")
    location_description: str = Field(..., description="查詢地區描述")
    search_params: Dict[str, Any] = Field(..., description="搜尋參數")
    years_searched: List[str] = Field(..., description="已搜尋年度")


class ResponseMetadata(BaseModel):
    """回應元資料"""
    total_records: int = Field(..., description="總記錄數")
    search_time: str = Field(..., description="搜尋時間 ISO 格式")
    query_hash: Optional[str] = Field(None, description="查詢參數雜湊值")
    response_time_ms: Optional[int] = Field(None, description="查詢響應時間(毫秒)")


class QualificationResponse(BaseModel):
    """統一查詢回應"""
    query_info: QueryInfo = Field(..., description="查詢資訊")
    results: List[GrantCaseItem] = Field(..., description="查詢結果")
    statistics: Optional[AreaStatistics] = Field(None, description="面積統計")
    metadata: ResponseMetadata = Field(..., description="回應元資料")


class AreaCheckResponse(BaseModel):
    """區域驗證回應"""
    is_qualified: bool = Field(..., description="是否符合該區域類型")
    area_type: str = Field(..., description="區域類型: indigenous/slope/general")
    details: Optional[Dict[str, Any]] = Field(None, description="詳細資訊")


# === 查詢歷史相關 Schemas ===

class RecentSearch(BaseModel):
    """最近查詢記錄"""
    id: str = Field(..., description="查詢記錄ID")
    query_type: QualificationQueryType = Field(..., description="查詢類型")
    location: str = Field(..., description="地區描述")
    params: LocationParams = Field(..., description="查詢參數")
    search_time: datetime = Field(..., description="查詢時間")
    has_results: bool = Field(..., description="該次查詢是否有結果")


class SearchHistoryResponse(BaseModel):
    """查詢歷史回應"""
    recent_searches: List[RecentSearch] = Field(..., description="最近查詢記錄")
    total_count: int = Field(..., description="總查詢次數")


# === 資料轉換輔助 Schemas ===

class LegacyMetaData(BaseModel):
    """歷史資料 meta_data 格式"""
    farmarea: Optional[float] = Field(None, description="農地面積")
    buildarea: Optional[float] = Field(None, description="建設面積")
    finalarea: Optional[float] = Field(None, description="最終核准面積")


class NewAercMetaData(BaseModel):
    """新系統 meta_data 格式"""
    land_area: Optional[str] = Field(None, description="土地面積")
    facility_area: Optional[str] = Field(None, description="設施面積")
    land_county: Optional[int] = Field(None, description="縣市代碼")
    land_town: Optional[int] = Field(None, description="鄉鎮代碼")
    is_aboriginal_area: Optional[bool] = Field(None, description="是否原民區域")
    is_irrigation_area: Optional[bool] = Field(None, description="是否灌溉區域")
    crops: Optional[List[Dict[str, str]]] = Field(None, description="作物資訊")