"""
Office Boundaries 水利工作站界限的 Pydantic 模式定義
用於空間查詢和資料交換
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date


# schema-max-length: skip（PostGIS 空間查詢的唯讀回應資料，非使用者輸入路徑）
class OfficeBoundaryInfo(BaseModel):
    """單一水利工作站界限資訊"""
    gid: int = Field(..., description="記錄ID")
    ia_code: Optional[str] = Field(None, description="灌區代碼")
    ia_name: Optional[str] = Field(None, description="灌區名稱")
    mng_code: Optional[str] = Field(None, description="管理處代碼")
    mng_name: Optional[str] = Field(None, description="管理處名稱")
    stn_code: Optional[str] = Field(None, description="工作站代碼")
    stn_name: Optional[str] = Field(None, description="工作站名稱")
    grp_code: Optional[str] = Field(None, description="小組代碼")
    grp_name: Optional[str] = Field(None, description="小組名稱")
    area: Optional[float] = Field(None, description="面積")
    record_date: Optional[date] = Field(None, description="記錄日期")
    sg: Optional[str] = Field(None, description="SG")
    stngrp: Optional[str] = Field(None, description="工作站小組")
    part: Optional[str] = Field(None, description="部分")

    class Config:
        from_attributes = True


class SpatialQueryRequest(BaseModel):
    """空間查詢請求參數"""
    coordinates: List[List[float]] = Field(
        ..., 
        description="查詢多邊形的坐標點陣列 [[lng1, lat1], [lng2, lat2], ...] (WGS84)"
    )
    srid: int = Field(default=4326, description="坐標系統 SRID，預設為 WGS84")
    
    class Config:
        json_schema_extra = {
            "example": {
                "coordinates": [[120.123, 23.456], [120.124, 23.456], [120.124, 23.457], [120.123, 23.457]],
                "srid": 4326
            }
        }


class SpatialQueryResponse(BaseModel):
    """空間查詢回應"""
    intersected_boundaries: List[OfficeBoundaryInfo] = Field(
        default=[], 
        description="與查詢區域相交的水利工作站界限"
    )
    total_count: int = Field(..., description="交集結果總數")
    query_summary: dict = Field(..., description="查詢摘要資訊")
    
    class Config:
        json_schema_extra = {
            "example": {
                "intersected_boundaries": [
                    {
                        "gid": 1,
                        "ia_code": "1701",
                        "ia_name": "桃園灌區",
                        "mng_code": "17",
                        "mng_name": "桃園管理處",
                        "stn_code": "1701",
                        "stn_name": "桃園工作站",
                        "grp_code": "170101",
                        "grp_name": "第一小組",
                        "area": 1000.5,
                        "record_date": "2023-01-01",
                        "sg": "SG001",
                        "stngrp": "桃園工作站第一小組",
                        "part": "A區"
                    }
                ],
                "total_count": 1,
                "query_summary": {
                    "management_offices": ["桃園管理處"],
                    "work_stations": ["桃園工作站"],
                    "irrigation_districts": ["桃園灌區"]
                }
            }
        }