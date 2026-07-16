"""
NLSC (國土測繪中心) 服務的 Pydantic Schemas
資料來源：National Land Surveying and Mapping Center
API 文件: https://api.nlsc.gov.tw/

支援服務：
- 地籍圖查詢 (CadasMapQuery, CadasMapPointQuery)
- 未來可擴充：地形圖、航照圖等
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Literal
from decimal import Decimal


# ========================================
# 地籍圖查詢 (Cadastral Map Query)
# ========================================

# === 請求 Schemas ===

class CadastralQueryByLandNumberRequest(BaseModel):
    """地籍圖查詢請求（依地號查詢）

    對應 NLSC API: https://api.nlsc.gov.tw/dmaps/CadasMapQuery/{county_code}/{section_code}/{land_number}/{format}/{srid}
    """
    county_code: str = Field(..., description="縣市代碼（例如：'B' for 台中市）", min_length=1, max_length=2)
    section_code: str = Field(..., description="地段代碼（例如：'0532'）", min_length=4, max_length=4)
    land_number_main: str = Field(..., description="地號主號（例如：'1'）", min_length=1, max_length=4)
    land_number_sub: str = Field(default="0", description="地號副號（例如：'0'）", max_length=4)
    format: Literal["gml", "kml", "shp"] = Field(default="gml", description="檔案格式")
    srid: Literal["4326", "3826"] = Field(default="4326", description="坐標系統（4326: WGS84, 3826: TWD97）")

    @validator("land_number_main", "land_number_sub")
    def validate_land_number(cls, v):
        """驗證地號格式（必須為數字）"""
        if v and not v.isdigit():
            raise ValueError("地號必須為數字")
        # 驗證範圍（0-9999）
        if v and (int(v) < 0 or int(v) > 9999):
            raise ValueError("地號必須在 0-9999 之間")
        return v


class CadastralQueryByPointRequest(BaseModel):
    """地籍圖查詢請求（依座標點查詢）

    對應 NLSC API: https://api.nlsc.gov.tw/dmaps/CadasMapPointQuery/{lon}/{lat}/{srid}/{format}
    """
    longitude: Decimal = Field(..., description="經度（WGS84 或 TWD97）", ge=-180, le=180)
    latitude: Decimal = Field(..., description="緯度（WGS84 或 TWD97）", ge=-90, le=90)
    srid: Literal["4326", "3826"] = Field(default="4326", description="坐標系統（4326: WGS84, 3826: TWD97）")
    format: Literal["gml", "kml", "shp"] = Field(default="gml", description="檔案格式")


# === 回應 Schemas ===

# schema-max-length: skip（外部 NLSC API GeoJSON 回應解析用，非使用者輸入路徑）
class CadastralFeatureProperties(BaseModel):
    """地籍圖 Feature 屬性

    GML 回傳欄位說明（NLSC API 標準格式）：
    - CITY: 縣市（例如：臺中市）
    - TOWN: 鄉鎮市區（例如：南區）
    - OFFICE: 地政事務所代碼（例如：BA）
    - SECT: 地段代碼（例如：0532）
    - LANDNO: 地號 8 碼（例如：00010000）
    - AREA: 面積（平方公尺）
    - LANDUSE: 使用分區（可能為空）
    - LANDDETATIS: 用地編定（可能為空）
    - VALUESSESSED: 公告地價（元/平方公尺）
    - VALUEANNOUNCE: 公告現值（元/平方公尺）
    """
    # NLSC GML 標準欄位
    CITY: Optional[str] = Field(None, description="縣市")
    TOWN: Optional[str] = Field(None, description="鄉鎮市區")
    OFFICE: Optional[str] = Field(None, description="地政事務所代碼")
    SECT: Optional[str] = Field(None, description="地段代碼")
    LANDNO: Optional[str] = Field(None, description="地號 8 碼")
    AREA: Optional[float] = Field(None, description="面積（平方公尺）")
    LANDUSE: Optional[str] = Field(None, description="使用分區")
    LANDDETATIS: Optional[str] = Field(None, description="用地編定")
    VALUESSESSED: Optional[float] = Field(None, description="公告地價（元/平方公尺）")
    VALUEANNOUNCE: Optional[float] = Field(None, description="公告現值（元/平方公尺）")

    # 前端相容欄位（格式化後的資料）
    # Land_no: Optional[str] = Field(None, description="格式化地號（例如：1-0 或 1）")
    # section: Optional[str] = Field(None, description="地段名稱")
    # area: Optional[float] = Field(None, description="面積（與 AREA 相同，提供給前端）")
    # Sec_cns: Optional[str] = Field(None, description="地段中文名稱")


# schema-max-length: skip（外部 NLSC API GeoJSON 回應解析用，非使用者輸入路徑）
class CadastralFeatureGeometry(BaseModel):
    """地籍圖 Feature 幾何資料（GeoJSON 格式）"""
    type: str = Field(..., description="幾何類型（例如：Polygon, MultiPolygon）")
    coordinates: List = Field(..., description="座標陣列（GeoJSON 格式）")


# schema-max-length: skip（外部 NLSC API GeoJSON 回應解析用，非使用者輸入路徑）
class CadastralFeature(BaseModel):
    """地籍圖 Feature（GeoJSON Feature 格式）"""
    type: Literal["Feature"] = Field(default="Feature", description="Feature 類型")
    properties: CadastralFeatureProperties = Field(..., description="屬性資料")
    geometry: CadastralFeatureGeometry = Field(..., description="幾何資料")
    id: Optional[str] = Field(None, description="Feature ID")


class CadastralQueryResponse(BaseModel):
    """地籍圖查詢回應（成功）"""
    success: bool = Field(default=True, description="查詢是否成功")
    features: List[CadastralFeature] = Field(default_factory=list, description="地籍圖 Features（GeoJSON 格式）")
    total_count: int = Field(default=0, description="Feature 總數")
    message: Optional[str] = Field(None, description="訊息（錯誤或警告）")
    api_url: Optional[str] = Field(None, description="NLSC API URL（用於除錯）")
    source: Literal["nlsc_api"] = Field(default="nlsc_api", description="資料來源")


class CadastralErrorResponse(BaseModel):
    """地籍圖查詢錯誤回應"""
    success: Literal[False] = Field(default=False, description="查詢失敗")
    features: List = Field(default_factory=list, description="空陣列")
    total_count: Literal[0] = Field(default=0, description="0 筆資料")
    message: str = Field(..., description="錯誤訊息")
    error_type: str = Field(..., description="錯誤類型（http_error, parse_error, validation_error, not_found）")
    api_url: Optional[str] = Field(None, description="NLSC API URL（用於除錯）")


# ========================================
# 未來擴充：地形圖、航照圖等服務
# ========================================

# TODO: 當需要添加其他 NLSC 服務時，在此處擴充
# 例如：
# - TopographicMapQueryRequest
# - AerialPhotoQueryRequest
# - etc.
