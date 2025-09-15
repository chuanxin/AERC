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


@router.get("/land-sections/{county_land_code}/{town_land_code}")
async def get_land_sections_by_codes(county_land_code: str, town_land_code: str) -> Dict[str, Any]:
    """
    使用地政代碼取得地段清單

    透過 NLSC API 服務呼叫外部地段資料
    URL format: https://api.nlsc.gov.tw/other/ListLandSection/{county_land_code}/{town_land_code}

    Args:
        county_land_code: 縣市地政代碼 (counties.land_code)
        town_land_code: 鄉鎮市區地政代碼 (towns.land_code)

    Returns:
        Dict containing land sections list from NLSC API
    """
    try:
        # 建構 NLSC API URL
        nlsc_url = f"https://api.nlsc.gov.tw/other/ListLandSection/{county_land_code}/{town_land_code}"

        # 呼叫外部 NLSC API (忽略 SSL 憑證驗證)
        async with httpx.AsyncClient(timeout=30.0, verify=False) as client:
            try:
                response = await client.get(nlsc_url)
                response.raise_for_status()

                # 檢查回應內容類型並解析 XML
                content_type = response.headers.get('content-type', '')
                response_text = response.text

                # 解析 XML 回應
                try:
                    root = ET.fromstring(response_text)
                    nlsc_data = []

                    # 根據 NLSC API 的實際 XML 結構解析地段資料
                    # 結構: <sectItems><sectItem><sectcode>0001</sectcode><sectstr>東門段一小段</sectstr></sectItem>...</sectItems>
                    for sect_item in root.findall('.//sectItem'):
                        sect_code = sect_item.find('sectcode')
                        sect_str = sect_item.find('sectstr')
                        office = sect_item.find('office')
                        office_str = sect_item.find('officestr')

                        if sect_str is not None and sect_str.text:
                            section_data = {
                                "name": sect_str.text.strip(),
                                "code": sect_code.text.strip() if sect_code is not None and sect_code.text else "",
                                "office": office.text.strip() if office is not None and office.text else "",
                                "office_name": office_str.text.strip() if office_str is not None and office_str.text else ""
                            }
                            nlsc_data.append(section_data)

                except ET.ParseError as e:
                    # 如果 XML 解析失敗，嘗試作為純文字處理
                    if response_text.strip():
                        lines = [line.strip() for line in response_text.strip().split('\n') if line.strip()]
                        nlsc_data = [line for line in lines if not line.startswith('<?') and not line.startswith('<')]
                    else:
                        nlsc_data = []
                except Exception as e:
                    raise HTTPException(
                        status_code=502,
                        detail=f"Failed to parse NLSC API response. Content-Type: {content_type}, Error: {str(e)}"
                    )

                # 轉換為統一格式
                sections_list = []
                for item in nlsc_data:
                    if isinstance(item, dict):
                        sections_list.append({
                            "name": item["name"],
                            "code": item["code"],
                            "office": item.get("office", ""),
                            "office_name": item.get("office_name", ""),
                            "county_land_code": county_land_code,
                            "town_land_code": town_land_code
                        })
                    elif isinstance(item, str) and item.strip():
                        # 兼容舊格式
                        sections_list.append({
                            "name": item.strip(),
                            "code": "",
                            "office": "",
                            "office_name": "",
                            "county_land_code": county_land_code,
                            "town_land_code": town_land_code
                        })

                return {
                    "county_land_code": county_land_code,
                    "town_land_code": town_land_code,
                    "sections": sections_list,
                    "count": len(sections_list),
                    "source": "NLSC_API",
                    "api_url": nlsc_url
                }

            except httpx.TimeoutException:
                raise HTTPException(
                    status_code=504,
                    detail="NLSC API request timeout"
                )
            except httpx.HTTPStatusError as e:
                raise HTTPException(
                    status_code=502,
                    detail=f"NLSC API returned error: {e.response.status_code}"
                )
            except Exception as e:
                raise HTTPException(
                    status_code=502,
                    detail=f"Failed to fetch data from NLSC API: {str(e)}"
                )

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Land sections query error: {str(e)}")


@router.get("/land-sections/health")
async def check_nlsc_api_health() -> Dict[str, Any]:
    """
    檢查 NLSC API 服務健康狀態

    測試 NLSC API 是否可用
    """
    try:
        # 使用一個已知的地政代碼進行測試 (例如：台北市中正區)
        test_url = "https://api.nlsc.gov.tw/other/ListLandSection/A/A01"

        async with httpx.AsyncClient(timeout=10.0, verify=False) as client:
            try:
                response = await client.get(test_url)
                is_online = response.status_code == 200

                return {
                    "nlsc_api_status": "online" if is_online else "offline",
                    "status_code": response.status_code,
                    "test_url": test_url,
                    "timestamp": "2024-09-15T10:00:00Z"
                }

            except httpx.TimeoutException:
                return {
                    "nlsc_api_status": "timeout",
                    "test_url": test_url,
                    "timestamp": "2024-09-15T10:00:00Z",
                    "error": "Request timeout"
                }
            except Exception as e:
                return {
                    "nlsc_api_status": "error",
                    "test_url": test_url,
                    "timestamp": "2024-09-15T10:00:00Z",
                    "error": str(e)
                }

    except Exception as e:
        return {
            "nlsc_api_status": "error",
            "error": f"Health check failed: {str(e)}",
            "timestamp": "2024-09-15T10:00:00Z"
        }