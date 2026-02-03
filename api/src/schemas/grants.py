from typing import Optional, List, Dict, Any, Union
from datetime import datetime, date
from pydantic import BaseModel, Field, field_validator
from tortoise.contrib.pydantic import pydantic_model_creator
from src.database.models import Grants
# 基本模型
class BaseSchema(BaseModel):
    class Config:
        from_attributes = True
        arbitrary_types_allowed = True

# Frontend request schema - matches GrantCreateRequest from frontend
class GrantCreateRequestSchema(BaseSchema):
    """前端申請表單資料模型 - 對應 frontend GrantCreateRequest interface"""
    name: str = Field(..., description="申請人姓名", min_length=1, max_length=50)
    id: str = Field(..., description="申請人身分證字號", min_length=10, max_length=10) 
    phone: str = Field(..., description="申請人電話", min_length=9)
    phone2: Optional[str] = Field(None, description="申請人備用電話", min_length=0)
    county: str = Field(..., description="縣市名稱", min_length=1, max_length=30)
    countyId: Optional[int] = Field(None, description="縣市ID")
    town: str = Field(..., description="鄉鎮市區名稱", min_length=1, max_length=30)
    townId: Optional[int] = Field(None, description="鄉鎮市區ID")
    village: Optional[str] = Field(None, description="村里名稱", max_length=30)
    villageId: Optional[int] = Field(None, description="村里ID")
    address: str = Field(..., description="詳細地址", min_length=1, max_length=255)
    undertracker: str = Field(..., description="承辦人姓名", min_length=1, max_length=50)
    office: str = Field(..., description="管理處名稱", min_length=1, max_length=50)
    officeId: Optional[int] = Field(None, description="管理處ID")
    valid: Optional[bool] = Field(default=False, description="前端驗證狀態")
    isDisasterCase: bool = Field(default=False, description="是否為災害案件")
    disasterCaseDescription: str = Field(default="", description="災害案件說明")
    
    @field_validator('valid')
    def validate_valid_field(cls, v):
        """處理 valid 欄位，null 值轉換為 False"""
        if v is None:
            return False
        return v
    
    @field_validator('id')
    def validate_id_number(cls, v):
        """驗證身分證字號格式"""
        if not v or len(v) != 10:
            raise ValueError('身分證字號必須為10碼')
        
        # 基本格式檢查: 第一碼為英文字母，第二碼為1或2，後面8碼為數字
        if not (v[0].isalpha() and v[1] in ['1', '2'] and v[2:].isdigit()):
            raise ValueError('身分證字號格式不正確')
        
        return v.upper()  # 確保英文字母為大寫
    
    @field_validator('phone1')
    def validate_phone(cls, v):
        """驗證電話號碼格式"""
        if not v:
            raise ValueError('電話號碼不能為空')
        
        # 去除空格和特殊符號，保留數字
        cleaned = ''.join(filter(lambda x: x.isdigit(), v))
        
        # 檢查長度，電話號碼通常為9-10碼
        if not (9 <= len(cleaned) <= 14):
            raise ValueError('電話號碼長度不正確')
        
        return cleaned
    @field_validator('phone2')
    def validate_phone(cls, v):
        """驗證電話號碼格式"""
        if not v:
            return None
        
        # 去除空格和特殊符號，保留數字
        cleaned = ''.join(filter(lambda x: x.isdigit(), v))
        
        # 檢查長度，電話號碼通常為9-10碼
        if not (9 <= len(cleaned) <= 14):
            raise ValueError('電話號碼長度不正確')
        
        return cleaned
    
    @field_validator('name', 'undertracker')
    def validate_name_fields(cls, v):
        """驗證姓名欄位不能為空白或只有空格"""
        if not v or not v.strip():
            raise ValueError('姓名欄位不能為空')
        return v.strip()
    
    @field_validator('county', 'town', 'office', 'address')
    def validate_text_fields(cls, v):
        """驗證文字欄位不能為空白或只有空格"""
        if not v or not v.strip():
            raise ValueError('此欄位不能為空')
        return v.strip()
    
    @field_validator('disasterCaseDescription')
    def validate_disaster_description(cls, v, values):
        """驗證災害案件說明"""
        # 從已驗證的值中獲取 isDisasterCase
        is_disaster = values.data.get('isDisasterCase', False) if hasattr(values, 'data') else False
        
        if is_disaster:
            if not v or not v.strip():
                raise ValueError('災害案件必須填寫說明內容')
            if len(v.strip()) < 10:
                raise ValueError('災害案件說明至少需要10個字')
            if len(v.strip()) > 500:
                raise ValueError('災害案件說明不可超過500個字')
        
        return v.strip() if v else ""

# 補助申請案件模型
class GrantInSchema(BaseSchema):
    """建立補助申請案件時使用的資料模型"""
    applicant_name: str = Field(..., description="申請人姓名")
    applicant_id: str = Field(..., description="申請人身分證字號")
    applicant_phone: str = Field(..., description="申請人電話")
    applicant_phone2: Optional[str] = Field(None, description="申請人備用電話")
    county: str = Field(..., description="縣市")
    town: str = Field(..., description="鄉鎮市區")
    village: Optional[str] = Field(None, description="村里")
    address: str = Field(..., description="詳細地址")
    
    office: str = Field(..., description="管理處ID")
    office_id: int = Field(..., description="管理處ID")
    undertracker: str = Field(..., description="承辦人姓名")
    
    @field_validator('applicant_id')
    def validate_id_number(cls, v):
        """驗證身分證字號格式"""
        if not v or len(v) != 10:
            raise ValueError('身分證字號必須為10碼')
        
        # 基本格式檢查: 第一碼為英文字母，第二碼為1或2，後面8碼為數字
        if not (v[0].isalpha() and v[1] in ['1', '2'] and v[2:].isdigit()):
            raise ValueError('身分證字號格式不正確')
        
        return v
    
    @field_validator('applicant_phone')
    def validate_phone(cls, v):
        """驗證電話號碼格式"""
        if not v:
            raise ValueError('電話號碼不能為空')
        
        # 去除空格和特殊符號
        v = ''.join(filter(lambda x: x.isdigit(), v))
        
        # 檢查長度，手機號碼通常為10碼
        if len(v) not in [9, 10]:
            raise ValueError('電話號碼長度不正確')
        
        return v
    
    @field_validator('applicant_phone2')
    def validate_phone(cls, v):
        """驗證電話號碼格式"""
        if not v:
            return None
        
        # 去除空格和特殊符號
        v = ''.join(filter(lambda x: x.isdigit(), v))
        
        # 檢查長度，手機號碼通常為10碼
        if len(v) not in [9, 10]:
            raise ValueError('電話號碼長度不正確')
        
        return v

GrantOutSchema = pydantic_model_creator(
    Grants, name="GrantOut", exclude=("created_by.password",)
)

class GrantUpdateSchema(BaseSchema):
    """更新補助申請案件時使用的資料模型"""
    applicant_name: Optional[str] = Field(None, description="申請人姓名")
    applicant_id: Optional[str] = Field(None, description="申請人身分證字號")
    applicant_phone: Optional[str] = Field(None, description="申請人電話")
    applicant_phone2: Optional[str] = Field(None, description="申請人備用電話")

    county_id: Optional[int] = Field(None, description="縣市ID")
    town_id: Optional[int] = Field(None, description="鄉鎮市區ID")
    village_id: Optional[int] = Field(None, description="村里ID")
    address: Optional[str] = Field(None, description="詳細地址")
    
    office_id: Optional[int] = Field(None, description="管理處ID")
    undertracker: Optional[str] = Field(None, description="承辦人姓名")
    
    status: Optional[str] = Field(None, description="案件狀態")
    status_detail: Optional[str] = Field(None, description="狀態詳情")
    current_step: Optional[int] = Field(None, description="目前步驟")
    
    @field_validator('applicant_id')
    def validate_id_number(cls, v):
        """驗證身分證字號格式"""
        if v is None:
            return v
            
        if len(v) != 10:
            raise ValueError('身分證字號必須為10碼')
        
        # 基本格式檢查: 第一碼為英文字母，第二碼為1或2，後面8碼為數字
        if not (v[0].isalpha() and v[1] in ['1', '2'] and v[2:].isdigit()):
            raise ValueError('身分證字號格式不正確')
        
        return v
    
    @field_validator('applicant_phone1')
    def validate_phone(cls, v):
        """驗證電話號碼格式"""
        if v is None:
            return v
            
        # 去除空格和特殊符號
        v = ''.join(filter(lambda x: x.isdigit(), v))
        
        # 檢查長度，手機號碼通常為10碼
        if len(v) not in [9, 10]:
            raise ValueError('電話號碼長度不正確')
        
        return v

    @field_validator('applicant_phone2')
    def validate_phone(cls, v):
        """驗證電話號碼格式"""
        if v is None:
            return v
            
        # 去除空格和特殊符號
        v = ''.join(filter(lambda x: x.isdigit(), v))
        
        # 檢查長度，手機號碼通常為10碼
        if len(v) not in [9, 10]:
            raise ValueError('電話號碼長度不正確')
        
        return v


class GrantStepSchema(BaseSchema):
    """更新補助申請案件特定步驟資料時使用的資料模型"""
    data: Dict[str, Any] = Field(..., description="步驟資料")


class GrantListSchema(BaseSchema):
    """補助申請案件列表資料模型"""
    id: int = Field(..., description="案件ID")
    case_number: str = Field(..., description="案件編號")
    year: int = Field(..., description="申請年度")
    applicant_name: str = Field(..., description="申請人姓名")
    status: str = Field(..., description="案件狀態")
    status_detail: Optional[str] = Field(None, description="狀態詳情")
    current_step: int = Field(..., description="目前步驟")
    
    # 關聯資料
    county_name: str = Field(..., description="縣市名稱")
    town_name: str = Field(..., description="鄉鎮市區名稱")
    office_name: str = Field(..., description="管理處名稱")
    
    # 補充資訊
    facility_type: Optional[str] = Field(None, description="設施型式")
    facility_area: Optional[float] = Field(None, description="設施面積(平方公尺)")
    created_at: datetime = Field(..., description="建立時間")


class CountySchema(BaseSchema):
    """縣市資料模型"""
    id: int = Field(..., description="縣市ID")
    name: str = Field(..., description="縣市名稱")
    code: str = Field(..., description="縣市代碼")


class TownSchema(BaseSchema):
    """鄉鎮市區資料模型"""
    id: int = Field(..., description="鄉鎮市區ID")
    name: str = Field(..., description="鄉鎮市區名稱")
    code: str = Field(..., description="鄉鎮市區代碼")
    is_indigenous: bool = Field(..., description="是否為原民區")
    indigenous_type: Optional[str] = Field(None, description="原民區類型(山地鄉/平地鄉)")


class VillageSchema(BaseSchema):
    """村里資料模型"""
    id: int = Field(..., description="村里ID")
    name: str = Field(..., description="村里名稱")
    code: str = Field(..., description="村里代碼")


class SectionSchema(BaseSchema):
    """地段資料模型"""
    id: int = Field(..., description="地段ID")
    name: str = Field(..., description="地段名稱")
    code: str = Field(..., description="地段代碼")


class OfficeSchema(BaseSchema):
    """管理處資料模型"""
    id: int = Field(..., description="管理處ID")
    name: str = Field(..., description="管理處名稱")
    short_name: str = Field(..., description="管理處縮寫")
    code: str = Field(..., description="管理處代碼")


# class GrantOutSchema(BaseSchema):
#     """補助申請案件詳細資料模型"""
#     id: int = Field(..., description="案件ID")
#     case_number: str = Field(..., description="案件編號")
#     year: int = Field(..., description="申請年度")
    
#     # 申請人資訊
#     applicant_name: str = Field(..., description="申請人姓名")
#     applicant_id: str = Field(..., description="申請人身分證字號")
#     applicant_phone: str = Field(..., description="申請人電話")
    
#     # 申請人地址
#     county: CountySchema = Field(..., description="縣市")
#     town: TownSchema = Field(..., description="鄉鎮市區")
#     village: Optional[VillageSchema] = Field(None, description="村里")
#     address: str = Field(..., description="詳細地址")
    
#     # 管理處與承辦人
#     office: OfficeSchema = Field(..., description="管理處")
#     manager: str = Field(..., description="承辦人姓名")
    
#     # 申請收件資訊
#     received_date: date = Field(..., description="收件日期")
#     received_time: str = Field(..., description="收件時間")
    
#     # 案件狀態
#     status: str = Field(..., description="案件狀態")
#     status_detail: Optional[str] = Field(None, description="狀態詳情")
#     current_step: int = Field(..., description="目前步驟")
    
#     # 時間戳記
#     created_at: datetime = Field(..., description="建立時間")
#     modified_at: datetime = Field(..., description="修改時間")
    
#     # 設施資訊 (如果有)
#     facility_type: Optional[str] = Field(None, description="設施型式")
#     facility_area: Optional[float] = Field(None, description="設施面積(平方公尺)")
#     facility_area_ha: Optional[float] = Field(None, description="設施面積(公頃)")
    
#     # 土地資訊 (如果有)
#     land_number: Optional[str] = Field(None, description="地號")
#     land_area: Optional[float] = Field(None, description="農地面積(平方公尺)")
#     land_area_ha: Optional[float] = Field(None, description="農地面積(公頃)")
    
#     # 補助金額資訊 (如果有)
#     pipe_line_subsidy: Optional[float] = Field(None, description="田間管路補助費")
#     facility_subsidy: Optional[float] = Field(None, description="灌溉調控設施補助費")
#     design_fee: Optional[float] = Field(None, description="規劃設計費")
#     total_budget: Optional[float] = Field(None, description="預算總計")


class GrantCreateResponseSchema(BaseSchema):
    """建立補助申請案件返回資料模型"""
    id: int = Field(..., description="案件ID")
    case_number: str = Field(..., description="案件編號")
    year: int = Field(..., description="申請年度")
    applicant_name: str = Field(..., description="申請人姓名")
    received_date: date = Field(..., description="建檔日期")
    received_time: str = Field(..., description="建檔時間")
    status: str = Field(..., description="案件狀態")
    is_disaster_case: bool = Field(..., description="是否為災害案件")
    disaster_case_description: Optional[str] = Field(None, description="災害案件說明")
    office_id: int = Field(..., description="管理處ID")
    undertracker: str = Field(..., description="收件人姓名")
    
    initial_version_id: Optional[int] = Field(None, description="初始版本ID")
    initial_version: Optional[int] = Field(None, description="初始版本號")


class GrantSearchSchema(BaseSchema):
    """補助申請案件搜尋條件資料模型"""
    year: Optional[int] = Field(None, description="申請年度")
    office_id: Optional[int] = Field(None, description="管理處ID")
    status: Optional[str] = Field(None, description="案件狀態")
    keywords: Optional[str] = Field(None, description="關鍵字搜尋")
    county_id: Optional[int] = Field(None, description="縣市ID")
    town_id: Optional[int] = Field(None, description="鄉鎮市區ID")
    applicant_id: Optional[str] = Field(None, description="申請人身分證字號")
    land_number: Optional[str] = Field(None, description="地號")
    is_aboriginal_area: Optional[bool] = Field(None, description="是否為原民區")
    date_from: Optional[date] = Field(None, description="建檔日期(起)")
    date_to: Optional[date] = Field(None, description="建檔日期(迄)")


# 土地相關模型
class CropDataSchema(BaseSchema):
    """作物資料模型"""
    category_id: int = Field(..., description="作物類別ID")
    name_id: int = Field(..., description="作物名稱ID")


class LandOwnerDataSchema(BaseSchema):
    """土地所有權人資料模型"""
    name: str = Field(..., description="所有權人姓名")
    id_number: str = Field(..., description="所有權人身分證字號")
    
    county_id: int = Field(..., description="縣市ID")
    town_id: int = Field(..., description="鄉鎮市區ID")
    village_id: Optional[int] = Field(None, description="村里ID")
    address: Optional[str] = Field(None, description="詳細地址")
    
    share_numerator: int = Field(..., description="持分分子")
    share_denominator: int = Field(..., description="持分分母")
    share_area: float = Field(..., description="持分面積(平方公尺)")


class GrantLandInSchema(BaseSchema):
    """補助申請案件土地資料模型"""
    # 設施地址
    county_id: int = Field(..., description="縣市ID")
    town_id: int = Field(..., description="鄉鎮市區ID")
    village_id: Optional[int] = Field(None, description="村里ID")
    section_id: Optional[int] = Field(None, description="地段ID")
    
    # 地號資訊
    land_number: str = Field(..., description="地號")
    is_aboriginal_area: bool = Field(False, description="是否為原民區")
    is_irrigation_area: bool = Field(False, description="是否位於灌區內")
    is_reapplied: bool = Field(False, description="是否再次申請")
    
    # 備註欄
    commented_remark: Optional[str] = Field(None, description="土地備註欄")

    # 坐標
    longitude: float = Field(..., description="經度")
    latitude: float = Field(..., description="緯度")
    
    # 面積
    land_area: float = Field(..., description="農地地籍面積(平方公尺)")
    land_area_ha: float = Field(..., description="農地地籍面積(公頃)")
    facility_area: float = Field(..., description="施設面積(平方公尺)")
    facility_area_ha: float = Field(..., description="施設面積(公頃)")
    
    # 作物資訊
    crops: List[CropDataSchema] = Field(..., description="作物資訊列表")
    
    # 土地所有權人資訊
    owners: List[LandOwnerDataSchema] = Field(..., description="土地所有權人列表")


# 年度補助額度相關模型
class ApplicantGrantSummaryItemSchema(BaseSchema):
    """申請人單筆補助案件摘要"""
    case_number: str = Field(..., description="案件編號")
    status: str = Field(..., description="案件狀態")
    subsidy_amount: float = Field(..., description="補助金額")
    created_at: datetime = Field(..., description="建立時間")


class ApplicantSubsidySummarySchema(BaseSchema):
    """申請人年度補助額度摘要"""
    applicant_id: str = Field(..., description="申請人身分證字號")
    applicant_name: str = Field(..., description="申請人姓名")
    year: int = Field(..., description="申請年度")
    total_subsidy_amount: float = Field(..., description="已用補助額度")
    remaining_amount: float = Field(..., description="剩餘可用額度")
    subsidy_limit: float = Field(default=500000, description="年度補助上限")
    grant_count: int = Field(..., description="案件數量")
    grants: List[ApplicantGrantSummaryItemSchema] = Field(..., description="案件列表")