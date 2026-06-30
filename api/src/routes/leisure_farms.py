"""
休閒農場資料查詢系統的 FastAPI 路由
提供空間查詢和統計功能
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional
from decimal import Decimal
import logging

from ..schemas.leisure_farms import (
    LeisureFarmNearbyResponse,
    LeisureFarmCheckResponse,
    LeisureFarmByLocationResponse,
    LeisureFarmStatsResponse,
    NearbySearchRequest,
    LocationSearchRequest,
)
from ..crud.leisure_farms import LeisureFarmsCRUD
from ..auth.guard import require_full_auth
from ..auth.route_guards import require_permission
from ..schemas.permissions import ModuleName, PermissionAction


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/leisure-farms", tags=["休閒農場"])


@router.post(
    "/nearby",
    response_model=LeisureFarmNearbyResponse,
    dependencies=[Depends(require_permission(ModuleName.GIS, PermissionAction.VIEW))],
)
async def search_nearby_farms(
    request: NearbySearchRequest,
    current_user=Depends(require_full_auth)
) -> LeisureFarmNearbyResponse:
    """
    查詢指定座標附近的休閒農場
    
    使用 PostGIS 空間查詢，回傳指定半徑內的農場列表，依距離排序
    
    - **longitude**: 查詢點經度 (WGS84)
    - **latitude**: 查詢點緯度 (WGS84)  
    - **radius_meters**: 查詢半徑（公尺），預設 5000m，最大 50000m
    - **limit**: 最大回傳筆數，預設 10，最大 100
    """
    try:
        logger.info(
            f"Nearby farms search: ({request.longitude}, {request.latitude}), "
            f"radius={request.radius_meters}m, limit={request.limit}"
        )
        
        result = await LeisureFarmsCRUD.search_nearby(
            longitude=request.longitude,
            latitude=request.latitude,
            radius_meters=request.radius_meters,
            limit=request.limit
        )
        
        logger.info(f"Nearby farms search completed: {result.total_count} results")
        return result
        
    except Exception as e:
        logger.error(f"Error in nearby farms search: {e}")
        raise HTTPException(status_code=500, detail="查詢失敗，請稍後再試")


@router.get("/check", response_model=LeisureFarmCheckResponse)
async def check_nearby_farms(
    longitude: Decimal = Query(..., description="查詢點經度 (WGS84)"),
    latitude: Decimal = Query(..., description="查詢點緯度 (WGS84)"),
    radius_meters: float = Query(default=1000, ge=100, le=10000, description="查詢半徑（公尺）"),
    current_user=Depends(require_full_auth)
) -> LeisureFarmCheckResponse:
    """
    快速檢查指定座標附近是否有休閒農場
    
    用於在資格查詢頁面快速判斷是否需要提示使用者附近有休閒農場
    回傳最近的農場資訊和範圍內農場數量
    
    - **longitude**: 查詢點經度 (WGS84)
    - **latitude**: 查詢點緯度 (WGS84)
    - **radius_meters**: 查詢半徑（公尺），預設 1000m
    """
    try:
        logger.info(f"Check nearby farms: ({longitude}, {latitude}), radius={radius_meters}m")
        
        result = await LeisureFarmsCRUD.check_nearby_farms(
            longitude=longitude,
            latitude=latitude,
            radius_meters=radius_meters
        )
        
        logger.info(f"Check nearby farms completed: has_nearby={result.has_nearby_farms}")
        return result
        
    except Exception as e:
        logger.error(f"Error in check nearby farms: {e}")
        raise HTTPException(status_code=500, detail="檢查失敗，請稍後再試")


@router.get("/by-location", response_model=LeisureFarmByLocationResponse)
async def search_farms_by_location(
    county: Optional[str] = Query(None, description="縣市名稱"),
    township: Optional[str] = Query(None, description="鄉鎮市區名稱"),
    current_user=Depends(require_full_auth)
) -> LeisureFarmByLocationResponse:
    """
    依縣市鄉鎮查詢休閒農場
    
    可以只指定縣市，或同時指定縣市和鄉鎮
    
    - **county**: 縣市名稱（選填）
    - **township**: 鄉鎮市區名稱（選填）
    """
    try:
        logger.info(f"Search farms by location: county={county}, township={township}")
        
        result = await LeisureFarmsCRUD.search_by_location(
            county=county,
            township=township
        )
        
        logger.info(f"Search by location completed: {result.total_count} results")
        return result
        
    except Exception as e:
        logger.error(f"Error in search farms by location: {e}")
        raise HTTPException(status_code=500, detail="查詢失敗，請稍後再試")


@router.get("/stats", response_model=LeisureFarmStatsResponse)
async def get_farms_statistics(
    current_user=Depends(require_full_auth)
) -> LeisureFarmStatsResponse:
    """
    取得休閒農場統計資料
    
    回傳農場總數、依縣市分布統計、最後同步時間等資訊
    """
    try:
        logger.info("Getting leisure farms statistics")
        
        result = await LeisureFarmsCRUD.get_statistics()
        
        logger.info(f"Statistics: total={result.total_farms}, counties={len(result.by_county)}")
        return result
        
    except Exception as e:
        logger.error(f"Error getting farms statistics: {e}")
        raise HTTPException(status_code=500, detail="取得統計資料失敗")
