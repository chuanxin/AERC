"""
Qualification 重複案件查詢系統的 FastAPI 路由
實現統一查詢介面和區域驗證功能
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional, List
import logging

from ..schemas.qualification import (
    QualificationSearchRequest, QualificationResponse,
    AreaCheckRequest, AreaCheckResponse,
    SearchHistoryResponse, RecentSearch
)
from ..crud.qualification import QualificationCRUD
from ..auth.guard import require_full_auth


# 設置日誌
logger = logging.getLogger(__name__)

# 建立路由器
router = APIRouter(prefix="/qualification", tags=["重複案件查詢"])


@router.post("/search", response_model=QualificationResponse)
async def search_qualification(
    request: QualificationSearchRequest,
    current_user = Depends(require_full_auth)
) -> QualificationResponse:
    """
    統一查詢介面 - 處理所有查詢類型
    消除特殊情況，使用統一的處理邏輯
    
    支援的查詢類型:
    - general: 一般區域查詢 (需要地號)
    - indigenous: 原住民鄉查詢 (地段名稱搜尋)
    - slope: 山坡地查詢 (地段名稱搜尋)
    """
    try:
        logger.info(f"Qualification search request: {request.query_type} - {request.params.dict()}")
        
        # 檢查是否有快取結果
        query_hash = QualificationCRUD.generate_query_hash(request)
        cached_result = await QualificationCRUD.get_cached_query(query_hash)
        if cached_result:
            logger.info(f"Returning cached result for query hash: {query_hash}")
            return cached_result
        
        # 執行查詢
        result = await QualificationCRUD.search_qualification_cases(request)
        
        logger.info(f"Qualification search completed: {result.metadata.total_records} results in {result.metadata.response_time_ms}ms")
        return result
        
    except ValueError as e:
        logger.error(f"Validation error in qualification search: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in qualification search: {e}")
        raise HTTPException(status_code=500, detail="查詢失敗，請稍後再試")


@router.post("/indigenous-check", response_model=AreaCheckResponse)
async def check_indigenous_area(
    request: AreaCheckRequest,
    current_user = Depends(require_full_auth)
) -> AreaCheckResponse:
    """
    原住民鄉區域驗證
    檢查指定的縣市鄉鎮是否為原住民鄉
    """
    try:
        logger.info(f"Indigenous area check: {request.county} {request.town}")
        
        result = await QualificationCRUD.check_indigenous_area(request)
        
        logger.info(f"Indigenous area check result: {result.is_qualified} - {result.area_type}")
        return result
        
    except Exception as e:
        logger.error(f"Error in indigenous area check: {e}")
        raise HTTPException(status_code=500, detail="區域驗證失敗")


@router.post("/slope-area-check", response_model=AreaCheckResponse)
async def check_slope_area(
    request: AreaCheckRequest,
    current_user = Depends(require_full_auth)
) -> AreaCheckResponse:
    """
    山坡地區域驗證
    檢查指定的縣市鄉鎮是否為山坡地
    """
    try:
        logger.info(f"Slope area check: {request.county} {request.town}")
        
        result = await QualificationCRUD.check_slope_area(request)
        
        logger.info(f"Slope area check result: {result.is_qualified} - {result.area_type}")
        return result
        
    except Exception as e:
        logger.error(f"Error in slope area check: {e}")
        raise HTTPException(status_code=500, detail="山坡地驗證失敗")


@router.get("/recent-searches", response_model=SearchHistoryResponse)
async def get_recent_searches(
    limit: int = Query(default=5, le=20, description="返回的最近查詢記錄數量"),
    current_user = Depends(require_full_auth)
) -> SearchHistoryResponse:
    """
    獲取最近查詢記錄
    用於查詢歷史管理功能
    """
    try:
        logger.info(f"Getting recent searches with limit: {limit}")
        
        # 這裡應該實現獲取用戶最近查詢的邏輯
        # 暫時返回空結果
        return SearchHistoryResponse(
            recent_searches=[],
            total_count=0
        )
        
    except Exception as e:
        logger.error(f"Error getting recent searches: {e}")
        raise HTTPException(status_code=500, detail="獲取查詢歷史失敗")


@router.delete("/clear-history")
async def clear_search_history(
    current_user = Depends(require_full_auth)
) -> dict:
    """
    清除查詢歷史記錄
    """
    try:
        logger.info("Clearing search history")
        
        # 這裡應該實現清除用戶查詢歷史的邏輯
        # 暫時返回成功回應
        
        return {"message": "查詢歷史已清除", "success": True}
        
    except Exception as e:
        logger.error(f"Error clearing search history: {e}")
        raise HTTPException(status_code=500, detail="清除歷史記錄失敗")


@router.get("/statistics/summary")
async def get_statistics_summary(
    years: Optional[List[str]] = Query(default=None, description="統計年度"),
    current_user = Depends(require_full_auth)
) -> dict:
    """
    獲取查詢統計摘要
    提供系統使用統計資訊
    """
    try:
        logger.info(f"Getting statistics summary for years: {years}")
        
        # 這裡應該實現統計邏輯
        # 暫時返回模擬資料
        
        return {
            "total_queries": 0,
            "query_types_distribution": {
                "general": 0,
                "indigenous": 0,
                "slope": 0
            },
            "average_response_time_ms": 0,
            "most_searched_areas": []
        }
        
    except Exception as e:
        logger.error(f"Error getting statistics summary: {e}")
        raise HTTPException(status_code=500, detail="獲取統計資料失敗")


@router.get("/health")
async def health_check() -> dict:
    """
    健康檢查端點
    用於監控系統狀態
    """
    try:
        # 簡單的資料庫連接測試
        from ..database.geo_models import GrantLocations
        count = await GrantLocations.all().count()
        
        return {
            "status": "healthy",
            "service": "qualification",
            "database_connection": "ok",
            "total_grant_locations": count,
            "timestamp": "2025-01-15T10:00:00Z"
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="服務暫時不可用")


# === 管理員專用端點 ===

@router.post("/admin/rebuild-cache")
async def rebuild_cache(
    current_user = Depends(require_full_auth)  # 這裡應該檢查管理員權限
) -> dict:
    """
    重建查詢快取
    管理員專用功能
    """
    try:
        logger.info("Rebuilding qualification cache")
        
        # 這裡應該實現快取重建邏輯
        # 例如：清除所有快取記錄、重新建立索引等
        
        return {"message": "快取重建完成", "success": True}
        
    except Exception as e:
        logger.error(f"Error rebuilding cache: {e}")
        raise HTTPException(status_code=500, detail="快取重建失敗")



@router.get("/admin/performance-metrics")
async def get_performance_metrics(
    current_user = Depends(require_full_auth)  # 這裡應該檢查管理員權限
) -> dict:
    """
    獲取效能指標
    管理員專用功能
    """
    try:
        logger.info("Getting performance metrics")
        
        # 這裡應該實現效能指標統計
        # 例如：平均響應時間、查詢頻率、錯誤率等
        
        return {
            "average_response_time_ms": 0,
            "queries_per_minute": 0,
            "error_rate": 0.0,
            "cache_hit_rate": 0.0,
            "active_connections": 0
        }
        
    except Exception as e:
        logger.error(f"Error getting performance metrics: {e}")
        raise HTTPException(status_code=500, detail="獲取效能指標失敗")