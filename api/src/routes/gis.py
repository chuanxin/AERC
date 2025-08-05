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

from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional, Dict, Any
import json
from tortoise import connections

router = APIRouter(prefix="/gis", tags=["GIS"])

def _calculate_grid_size(zoom_level: int) -> float:
    """
    根據縮放等級計算聚合格網大小
    
    縮放等級越低（數字越小），格網越大，聚合程度越高
    格網大小以度（decimal degrees）為單位
    """
    # 基礎格網大小映射表
    grid_sizes = {
        1: 5.0,      # 國家級視圖 - 很大的格網
        2: 2.5,      # 大區域視圖
        3: 1.0,      # 省/州級視圖
        4: 0.5,      # 大城市級視圖
        5: 0.25,     # 城市級視圖
        6: 0.1,      # 區級視圖
        7: 0.05,     # 詳細城市視圖
        8: 0.025,    # 街道級視圖
        9: 0.01,     # 詳細街道視圖
        10: 0.005,   # 建築群級視圖
        11: 0.0025,  # 建築級視圖 
        12: 0.001,   # 高詳細級視圖 - 小格網
    }
    
    # 如果縮放等級超出範圍，使用邊界值
    if zoom_level <= 1:
        return grid_sizes[1]
    elif zoom_level >= 12:
        return grid_sizes[12]
    else:
        return grid_sizes.get(zoom_level, 0.01)  # 預設值

@router.get("/points")
async def get_spatial_points(
    bbox: str = Query(..., description="Required bounding box: 'minLng,minLat,maxLng,maxLat'"),
    source_system: Optional[str] = Query(None, description="Filter by source system"),
    apply_year_min: Optional[int] = Query(None, description="Minimum apply year"),
    apply_year_max: Optional[int] = Query(None, description="Maximum apply year"),
    zoom_level: Optional[int] = Query(12, description="Map zoom level for clustering decision"),
    limit: Optional[int] = Query(None, description="Maximum number of points to return (no limit if not specified)"),
    no_clustering: Optional[bool] = Query(False, description="Disable backend clustering to return raw points for frontend clustering")
) -> Dict[str, Any]:
    """
    獲取空間點位資料，始終以使用者視窗範圍(bbox)為準
    基於縮放等級自動決定聚合策略，確保最佳效能
    """
    try:
        # 解析必需的 bbox 參數
        try:
            coords = [float(x) for x in bbox.split(',')]
            if len(coords) != 4:
                raise ValueError("Invalid bbox format")
            min_lng, min_lat, max_lng, max_lat = coords
        except (ValueError, AttributeError):
            raise HTTPException(status_code=400, detail="bbox is required. Format: 'minLng,minLat,maxLng,maxLat'")
        
        # 建立基礎查詢條件（始終包含bbox篩選）
        where_conditions = [
            "geom IS NOT NULL",
            "ST_Within(geom, ST_MakeEnvelope($1, $2, $3, $4, 4326))"
        ]
        params = [min_lng, min_lat, max_lng, max_lat]
        
        # 添加其他篩選條件
        if source_system:
            where_conditions.append(f"source_system = ${len(params)+1}")
            params.append(source_system)
        
        if apply_year_min:
            where_conditions.append(f"apply_year >= ${len(params)+1}")
            params.append(apply_year_min)
            
        if apply_year_max:
            where_conditions.append(f"apply_year <= ${len(params)+1}")
            params.append(apply_year_max)
        
        # 決定聚合策略
        # 如果前端明確要求無聚合no_clustering=True），則強制不聚合
        # （否則根據縮放等級自動決定
        if no_clustering:
            use_clustering = False
            print(f"[API] 前端要求原始資料，禁用後端聚合")
        else:
            use_clustering = zoom_level < 12
            print(f"[API] 根據縮放等級 {zoom_level} 自動決定聚合: {use_clustering}")
        
        # 建立統一的SQL查詢（聚合或個別點位）
        if use_clustering:
            grid_size = _calculate_grid_size(zoom_level)
            limit_clause = f"LIMIT {limit}" if limit else ""
            sql = f"""
            WITH clustered_points AS (
                SELECT 
                    ST_SnapToGrid(geom, {grid_size}) as cluster_geom,
                    source_system,
                    COUNT(*) as point_count,
                    array_agg(COALESCE(applicant_name, '')) as cluster_applicants,
                    MIN(apply_year) as min_year,
                    MAX(apply_year) as max_year,
                    array_agg(DISTINCT COALESCE(land_section, '')) as cluster_sections
                FROM grant_locations 
                WHERE {' AND '.join(where_conditions)}
                GROUP BY ST_SnapToGrid(geom, {grid_size}), source_system
                HAVING COUNT(*) > 0
            )
            SELECT 
                json_build_object(
                    'type', 'Feature',
                    'geometry', ST_AsGeoJSON(cluster_geom)::json,
                    'properties', json_build_object(
                        'cluster', true,
                        'point_count', point_count,
                        'source_system', source_system,
                        'cluster_applicants', cluster_applicants,
                        'year_range', CASE 
                            WHEN min_year = max_year THEN min_year::text
                            ELSE min_year::text || '-' || max_year::text
                        END,
                        'land_sections', cluster_sections,
                        'zoom_level', {zoom_level},
                        'grid_size', {grid_size}
                    )
                ) as feature
            FROM clustered_points
            ORDER BY point_count DESC
            {limit_clause}
            """
        else:
            limit_clause = f"LIMIT {limit}" if limit else ""
            sql = f"""
            SELECT 
                json_build_object(
                    'type', 'Feature',
                    'geometry', ST_AsGeoJSON(geom)::json,
                    'properties', json_build_object(
                        'cluster', false,
                        'id', id,
                        'source_system', source_system,
                        'source_id', source_id,
                        'applicant_name', COALESCE(applicant_name, ''),
                        'land_section', COALESCE(land_section, ''),
                        'land_number', land_number,
                        'apply_year', apply_year,
                        'case_status', case_status,
                        'land_type', land_type,
                        'meta_data', meta_data
                    )
                ) as feature
            FROM grant_locations 
            WHERE {' AND '.join(where_conditions)}
            ORDER BY apply_year DESC
            {limit_clause}
            """
        
        # 執行查詢 - 使用 Tortoise 的連接
        conn = connections.get("default")
        results = await conn.execute_query_dict(sql, params)
        
        # 處理結果
        features = []
        for row in results:
            feature_data = row['feature']
            if isinstance(feature_data, str):
                features.append(json.loads(feature_data))
            else:
                features.append(feature_data)
        
        return {
            "type": "FeatureCollection",
            "features": features,
            "meta": {
                "count": len(features),
                "bbox": bbox,
                "clustering": {
                    "enabled": use_clustering,
                    "zoom_level": zoom_level,
                    "grid_size": _calculate_grid_size(zoom_level) if use_clustering else None
                },
                "filters": {
                    "source_system": source_system,
                    "apply_year_min": apply_year_min,
                    "apply_year_max": apply_year_max
                }
            }
        }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/stats")
async def get_spatial_stats() -> Dict[str, Any]:
    """
    獲取空間資料統計資訊
    """
    try:
        sql = """
        SELECT 
            source_system,
            COUNT(*) as total_points,
            MIN(apply_year) as earliest_year,
            MAX(apply_year) as latest_year,
            ST_AsText(ST_Envelope(ST_Collect(geom))) as bbox_polygon
        FROM grant_locations 
        WHERE geom IS NOT NULL
        GROUP BY source_system
        """
        
        # 使用 Tortoise 的連接
        conn = connections.get("default")
        results = await conn.execute_query_dict(sql, [])
        
        # 轉換結果為字典格式
        statistics = []
        total_points = 0
        for row in results:
            stat = {
                "source_system": row["source_system"],
                "total_points": row["total_points"],
                "earliest_year": row["earliest_year"],
                "latest_year": row["latest_year"],
                "bbox_polygon": row["bbox_polygon"]
            }
            statistics.append(stat)
            total_points += row["total_points"]
        
        return {
            "statistics": statistics,
            "total_points": total_points
        }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/search")
async def search_by_criteria(
    bbox: Optional[str] = Query(None, description="Optional bounding box: 'minLng,minLat,maxLng,maxLat'"),
    applicant_name: Optional[str] = Query(None, description="申請人姓名 (模糊搜尋)"),
    land_section: Optional[str] = Query(None, description="地段"),
    case_number: Optional[str] = Query(None, description="案件編號 (source_id)"),
    limit: Optional[int] = Query(None, description="最大回傳筆數 (no limit if not specified)")
) -> Dict[str, Any]:
    """
    依據條件搜尋案件位置，可選擇在指定的地理範圍內搜尋
    """
    if not any([applicant_name, land_section, case_number]):
        raise HTTPException(status_code=400, detail="至少需要提供一個搜尋條件")
    
    try:
        where_conditions = ["geom IS NOT NULL"]
        params = []
        
        # 添加 bbox 篩選（如果提供）
        if bbox:
            try:
                coords = [float(x) for x in bbox.split(',')]
                if len(coords) != 4:
                    raise ValueError("Invalid bbox format")
                min_lng, min_lat, max_lng, max_lat = coords
                where_conditions.append(f"ST_Within(geom, ST_MakeEnvelope(${len(params)+1}, ${len(params)+2}, ${len(params)+3}, ${len(params)+4}, 4326))")
                params.extend([min_lng, min_lat, max_lng, max_lat])
            except (ValueError, AttributeError):
                raise HTTPException(status_code=400, detail="Invalid bbox format. Expected: 'minLng,minLat,maxLng,maxLat'")
        
        if applicant_name:
            where_conditions.append(f"applicant_name ILIKE ${len(params)+1}")
            params.append(f"%{applicant_name}%")
        
        if land_section:
            where_conditions.append(f"land_section = ${len(params)+1}")
            params.append(land_section)
        
        if case_number:
            where_conditions.append(f"source_id = ${len(params)+1}")
            params.append(case_number)
        
        limit_clause = f"LIMIT {limit}" if limit else ""
        sql = f"""
        SELECT 
            id,
            source_system,
            source_id,
            applicant_name,
            land_section,
            land_number,
            apply_year,
            case_status,
            ST_X(geom) as longitude,
            ST_Y(geom) as latitude,
            ST_AsGeoJSON(geom) as geometry
        FROM grant_locations 
        WHERE {' AND '.join(where_conditions)}
        ORDER BY apply_year DESC
        {limit_clause}
        """
        
        # 使用 Tortoise 的連接
        conn = connections.get("default")
        results = await conn.execute_query_dict(sql, params)
        
        # 轉換結果為字典格式
        result_list = []
        for row in results:
            result_list.append({
                "id": row["id"],
                "source_system": row["source_system"],
                "source_id": row["source_id"],
                "applicant_name": row["applicant_name"],
                "land_section": row["land_section"],
                "land_number": row["land_number"],
                "apply_year": row["apply_year"],
                "case_status": row["case_status"],
                "longitude": row["longitude"],
                "latitude": row["latitude"],
                "geometry": row["geometry"]
            })
        
        return {
            "results": result_list,
            "count": len(result_list),
            "search_criteria": {
                "bbox": bbox,
                "applicant_name": applicant_name,
                "land_section": land_section,
                "case_number": case_number
            }
        }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
