# -*- coding: utf-8 -*-
import os
import sys
import locale
import codecs

# 強制設定 UTF-8 編碼 - 解決 Windows charmap 編碼問題
os.environ['PYTHONIOENCODING'] = 'utf-8'

# 設定標準輸出和錯誤輸出為 UTF-8
if sys.platform.startswith('win'):
    # Windows 特定的 UTF-8 設定
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

if hasattr(locale, 'setlocale'):
    try:
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    except:
        try:
            locale.setlocale(locale.LC_ALL, 'C.UTF-8')
        except:
            pass

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
import json
import httpx
import xml.etree.ElementTree as ET
from tortoise import connections
from tortoise.exceptions import DoesNotExist
from src.database.models import Counties, Towns

router = APIRouter(prefix="/spatial", tags=["Spatial Services"])


@router.post("/office")
async def query_office_boundaries(geometry_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    查詢農田水利事業區域空間相交
    
    接收 GeoJSON 幾何物件，與 office_boundaries.geom 進行空間交集查詢
    
    Args:
        geometry_data: GeoJSON 格式的幾何物件
        {
            "type": "Polygon",
            "coordinates": [[[lng, lat], [lng, lat], ...]]
        }
    
    Returns:
        Dict containing matched office boundaries info
    """
    try:
        # 驗證輸入的幾何資料
        if not geometry_data or "type" not in geometry_data or "coordinates" not in geometry_data:
            raise HTTPException(status_code=400, detail="Invalid geometry data format")
        
        # 將 GeoJSON 轉換為字串供 PostGIS 使用
        geojson_str = json.dumps(geometry_data)
        
        connection = connections.get("default")
        
        # PostGIS 空間交集查詢：輸入的幾何物件與 office_boundaries.geom
        # 輸入幾何假設為 WGS84 (4326)，需轉換到 TWD97 TM2 (3824) 與 office_boundaries 匹配
        sql_query = """
        SELECT ob.gid, ob.ia_code, ob.ia_name, ob.mng_code, ob.mng_name, 
               ob.stn_code, ob.stn_name, ob.grp_code, ob.grp_name,
               ob.area, ob.record_date, ob.sg, ob.stngrp, ob.part
        FROM office_boundaries ob
        WHERE ST_Intersects(
            ob.geom, 
            ST_Transform(ST_GeomFromGeoJSON($1), 3824)
        )
        ORDER BY ob.ia_code, ob.stn_code, ob.grp_code
        """
        
        result = await connection.execute_query(sql_query, [geojson_str])
        
        boundaries_list = []
        for row in result[1]:  # result[1] contains the rows
            boundaries_list.append({
                "gid": row[0],
                "ia_code": row[1],
                "ia_name": row[2],
                "mng_code": row[3],
                "mng_name": row[4],
                "stn_code": row[5],
                "stn_name": row[6], 
                "grp_code": row[7],
                "grp_name": row[8],
                "area": row[9],
                "record_date": row[10].isoformat() if row[10] else None,
                "sg": row[11],
                "stngrp": row[12],
                "part": row[13]
            })
        
        return {
            "office_boundaries": boundaries_list,
            "count": len(boundaries_list),
            "query_geometry": geometry_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Office boundaries spatial query error: {str(e)}")


@router.post("/county") 
async def query_county_boundaries(geometry_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    查詢縣市界線空間相交
    
    接收 GeoJSON 幾何物件，與 county_moi_1090820.geom 進行空間交集查詢
    
    Args:
        geometry_data: GeoJSON 格式的幾何物件
        {
            "type": "Polygon", 
            "coordinates": [[[lng, lat], [lng, lat], ...]]
        }
    
    Returns:
        Dict containing matched county boundaries info
    """
    try:
        # 驗證輸入的幾何資料
        if not geometry_data or "type" not in geometry_data or "coordinates" not in geometry_data:
            raise HTTPException(status_code=400, detail="Invalid geometry data format")
        
        # 將 GeoJSON 轉換為字串供 PostGIS 使用
        geojson_str = json.dumps(geometry_data)
        
        connection = connections.get("default")
        
        # PostGIS 空間交集查詢：輸入的幾何物件與 county_moi_1090820.geom
        # 輸入幾何假設為 WGS84 (4326)，需轉換到 TWD97 TM2 (3824) 與縣市界線匹配
        sql_query = """
        SELECT cm.gid, cm.countyid, cm.countycode, cm.countyname, cm.countyeng
        FROM county_moi_1090820 cm
        WHERE ST_Intersects(
            cm.geom,
            ST_Transform(ST_GeomFromGeoJSON($1), 3824)
        )
        ORDER BY cm.countyname
        """
        
        result = await connection.execute_query(sql_query, [geojson_str])
        
        counties_list = []
        for row in result[1]:  # result[1] contains the rows
            counties_list.append({
                "gid": row[0],
                "countyid": row[1], 
                "countycode": row[2],
                "countyname": row[3],
                "countyeng": row[4]
            })
        
        return {
            "county_boundaries": counties_list,
            "count": len(counties_list),
            "query_geometry": geometry_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"County boundaries spatial query error: {str(e)}")


@router.get("/land-sections/{county_land_code}/{town_land_code}", deprecated=True)
async def get_land_sections_by_codes(county_land_code: str, town_land_code: str) -> Dict[str, Any]:
    """
    使用地政代碼取得地段清單 - 已棄用

    **⚠️ 已棄用**: 此端點已遷移到 NLSC 路由下，請使用 `GET /nlsc/sections/{county}/{town}`

    **遷移路徑**：
    - 舊路徑: `GET /spatial/land-sections/{county}/{town}` (deprecated)
    - 新路徑: `GET /nlsc/sections/{county}/{town}` (recommended)
    - 理由: 統一所有 NLSC API 代理服務在 /nlsc 下，spatial 專注於內部 PostGIS 空間查詢

    透過 NLSC API 服務呼叫外部地段資料
    URL format: https://api.nlsc.gov.tw/other/ListLandSection/{county_land_code}/{town_land_code}

    Args:
        county_land_code: 縣市地政代碼 (counties.land_code)
        town_land_code: 鄉鎮市區地政代碼 (towns.land_code)

    Returns:
        Dict containing land sections list from NLSC API
    """
    logger.warning(f"Using deprecated endpoint: /spatial/land-sections/{county_land_code}/{town_land_code}, please migrate to /nlsc/sections")

    # 轉發到 NLSC Service（統一邏輯，避免重複代碼）
    from src.services.nlsc_service import NLSCService

    result = await NLSCService.query_land_sections(
        county_land_code=county_land_code,
        town_land_code=town_land_code
    )

    # 返回統一格式（保持向後相容）
    return result


@router.get("/land-sections/health", deprecated=True)
async def check_nlsc_api_health() -> Dict[str, Any]:
    """
    檢查 NLSC API 服務健康狀態 - 已棄用

    **⚠️ 已棄用**: 此端點已遷移到 NLSC 路由下，請使用 `GET /nlsc/health`

    **遷移路徑**：
    - 舊路徑: `GET /spatial/land-sections/health` (deprecated)
    - 新路徑: `GET /nlsc/health` (recommended)
    - 理由: 統一所有 NLSC API 相關端點在 /nlsc 下

    測試 NLSC API 是否可用
    """
    logger.warning("Using deprecated endpoint: /spatial/land-sections/health, please migrate to /nlsc/health")

    # 轉發到 NLSC Service（統一邏輯）
    from src.services.nlsc_service import NLSCService

    result = await NLSCService.check_health()
    return result