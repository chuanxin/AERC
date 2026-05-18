"""
NLSC (國土測繪中心) API 路由
提供所有 NLSC API 代理服務的統一端點

設計原則（Linus Style）：
- Simple proxy: 轉發請求到 NLSC API，不做複雜業務邏輯
- Consistent naming: RESTful 風格，消除動詞，使用名詞描述資源
- No special cases: 統一的錯誤處理機制，相同資源支援 GET/POST
- Clear separation: 所有 NLSC API 代理都在 /nlsc 下，與內部 PostGIS 查詢分離

架構更新（2025-12-12）：
- 重構端點命名為 RESTful 風格（移除 query-by- 前綴和 -get 後綴）
- 整併 land-sections 服務從 /spatial 遷移到 /nlsc
- 統一所有 NLSC API 代理服務在同一路由下
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Path
from fastapi.responses import Response
from typing import Optional, Dict, Any
from decimal import Decimal
import logging

from ..schemas.nlsc import (
    CadastralQueryByLandNumberRequest,
    CadastralQueryByPointRequest,
    CadastralQueryResponse,
    CadastralErrorResponse,
)
from ..services.nlsc_service import NLSCService
from ..auth.guard import require_full_auth

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/nlsc", tags=["NLSC 國土測繪中心"])


# ============================================================================
# 地籍圖查詢服務 - 統一資源端點
# ============================================================================

@router.get("/cadastral/map", response_model=CadastralQueryResponse)
async def query_cadastral_map(
    # 地號查詢參數（可選）
    county_code: Optional[str] = Query(None, description="縣市代碼（例如：'B' for 台中市）", min_length=1, max_length=2),
    section_code: Optional[str] = Query(None, description="地段代碼（例如：'0532'）", min_length=4, max_length=4),
    land_number_main: Optional[str] = Query(None, description="地號主號（例如：'1'）", min_length=1, max_length=4),
    land_number_sub: Optional[str] = Query(None, description="地號副號（例如：'0'），預設為 '0'", max_length=4),

    # 座標查詢參數（可選）
    longitude: Optional[Decimal] = Query(None, description="經度（WGS84 或 TWD97）", ge=-180, le=180),
    latitude: Optional[Decimal] = Query(None, description="緯度（WGS84 或 TWD97）", ge=-90, le=90),

    # 共用參數
    format: str = Query(default="gml", description="檔案格式（gml, kml, shp）"),
    srid: str = Query(default="4326", description="坐標系統（4326: WGS84, 3826: TWD97）"),
    current_user=Depends(require_full_auth)
) -> CadastralQueryResponse:
    """
    查詢地籍圖（統一資源端點）

    **RESTful 設計原則**：
    - Resource: `/cadastral/map` - 地籍圖資源（單一端點）
    - Query Parameters: 區分查詢方式（地號 vs 座標）
    - 消除特殊情況：兩種 NLSC API 都返回相同的資源類型

    **查詢方式 1 - 依地號查詢**：
    - 必填參數：county_code, section_code, land_number_main
    - 可選參數：land_number_sub（預設 '0'）
    - 對應 NLSC API: `CadasMapQuery/{county}/{section}/{land_number}/{format}/{srid}`

    **查詢方式 2 - 依座標查詢**：
    - 必填參數：longitude, latitude
    - 對應 NLSC API: `CadasMapPointQuery/{lon}/{lat}/{srid}/{format}`

    **共用參數**：
    - **format**: 檔案格式（gml, kml, shp），預設 'gml'
    - **srid**: 坐標系統（'4326': WGS84, '3826': TWD97），預設 '4326'

    **回應結構**：
    - **success**: 查詢是否成功
    - **features**: GeoJSON Feature 陣列（包含地籍圖幾何和屬性）
    - **total_count**: Feature 數量
    - **message**: 錯誤或警告訊息（如有）
    - **api_url**: 實際調用的 NLSC API URL（用於除錯）

    **範例**：
    - 地號查詢: `GET /nlsc/cadastral/map?county_code=B&section_code=0532&land_number_main=1`
    - 座標查詢: `GET /nlsc/cadastral/map?longitude=120.123&latitude=24.456`
    """
    try:
        # 判斷使用哪種查詢方式
        has_land_params = county_code and section_code and land_number_main
        has_point_params = longitude is not None and latitude is not None

        # 參數驗證：必須提供其中一種查詢方式
        if not has_land_params and not has_point_params:
            raise HTTPException(
                status_code=400,
                detail="請提供地號查詢參數（county_code, section_code, land_number_main）或座標查詢參數（longitude, latitude）"
            )

        # 參數驗證：不能同時提供兩種查詢方式
        if has_land_params and has_point_params:
            raise HTTPException(
                status_code=400,
                detail="請僅提供一種查詢方式（地號或座標），不可同時提供"
            )

        # 方式 1：依地號查詢
        if has_land_params:
            logger.info(
                f"Cadastral query by land number: {county_code}/{section_code}/"
                f"{land_number_main}-{land_number_sub or '0'}"
            )

            result = await NLSCService.query_cadastral_by_land_number(
                county_code=county_code,
                section_code=section_code,
                land_number_main=land_number_main,
                land_number_sub=land_number_sub or "0",
                format=format,
                srid=srid
            )

        # 方式 2：依座標查詢
        else:  # has_point_params
            logger.info(f"Cadastral query by point: ({longitude}, {latitude})")

            result = await NLSCService.query_cadastral_by_point(
                longitude=longitude,
                latitude=latitude,
                srid=srid,
                format=format
            )

        # 處理 NLSC API 回應
        if not result["success"]:
            logger.warning(f"NLSC API returned error: {result.get('message')}")
            return CadastralErrorResponse(**result)

        logger.info(f"Cadastral query completed: {result['total_count']} features")
        return CadastralQueryResponse(**result)

    except HTTPException:
        # 重新拋出 HTTP 異常（參數驗證錯誤）
        raise
    except Exception as e:
        logger.error(f"Error in cadastral map query: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="地籍圖查詢失敗，請稍後再試")


# ============================================================================
# 舊端點（向後相容，已標記 deprecated）- 地號/座標分開端點
# ============================================================================

@router.post("/cadastral/land", response_model=CadastralQueryResponse, deprecated=True)
@router.get("/cadastral/land", response_model=CadastralQueryResponse, deprecated=True)
async def query_cadastral_land(
    county_code: str = Query(..., description="縣市代碼（例如：'B' for 台中市）", min_length=1, max_length=2),
    section_code: str = Query(..., description="地段代碼（例如：'0532'）", min_length=4, max_length=4),
    land_number_main: str = Query(..., description="地號主號（例如：'1'）", min_length=1, max_length=4),
    land_number_sub: str = Query(default="0", description="地號副號（例如：'0'）", max_length=4),
    format: str = Query(default="gml", description="檔案格式（gml, kml, shp）"),
    srid: str = Query(default="4326", description="坐標系統（4326: WGS84, 3826: TWD97）"),
    current_user=Depends(require_full_auth)
) -> CadastralQueryResponse:
    """
    查詢地籍圖（依地號）- 已棄用

    **⚠️ 已棄用**: 此端點已棄用，請使用統一的 `GET /nlsc/cadastral/map`

    **遷移路徑**：
    - 舊路徑: `GET/POST /nlsc/cadastral/land` (deprecated)
    - 新路徑: `GET /nlsc/cadastral/map?county_code=...&section_code=...&land_number_main=...` (recommended)
    - 理由: 統一資源端點，用查詢參數區分查詢方式
    """
    logger.warning("Using deprecated endpoint: /cadastral/land, please migrate to /cadastral/map")

    # 轉發到新的統一端點
    return await query_cadastral_map(
        county_code=county_code,
        section_code=section_code,
        land_number_main=land_number_main,
        land_number_sub=land_number_sub,
        longitude=None,
        latitude=None,
        format=format,
        srid=srid,
        current_user=current_user
    )


@router.post("/cadastral/point", response_model=CadastralQueryResponse, deprecated=True)
@router.get("/cadastral/point", response_model=CadastralQueryResponse, deprecated=True)
async def query_cadastral_point(
    longitude: Decimal = Query(..., description="經度（WGS84 或 TWD97）", ge=-180, le=180),
    latitude: Decimal = Query(..., description="緯度（WGS84 或 TWD97）", ge=-90, le=90),
    srid: str = Query(default="4326", description="坐標系統（4326: WGS84, 3826: TWD97）"),
    format: str = Query(default="gml", description="檔案格式（gml, kml, shp）"),
    current_user=Depends(require_full_auth)
) -> CadastralQueryResponse:
    """
    查詢地籍圖（依座標點）- 已棄用

    **⚠️ 已棄用**: 此端點已棄用，請使用統一的 `GET /nlsc/cadastral/map`

    **遷移路徑**：
    - 舊路徑: `GET/POST /nlsc/cadastral/point` (deprecated)
    - 新路徑: `GET /nlsc/cadastral/map?longitude=...&latitude=...` (recommended)
    - 理由: 統一資源端點，用查詢參數區分查詢方式
    """
    logger.warning("Using deprecated endpoint: /cadastral/point, please migrate to /cadastral/map")

    # 轉發到新的統一端點
    return await query_cadastral_map(
        county_code=None,
        section_code=None,
        land_number_main=None,
        land_number_sub=None,
        longitude=longitude,
        latitude=latitude,
        format=format,
        srid=srid,
        current_user=current_user
    )


@router.get("/cadastral/tiles/{tile_matrix}/{tile_row}/{tile_col}")
async def proxy_cadastral_wmts_tile(
    tile_matrix: int = Path(..., description="TileMatrix 索引（zoom level, 0-19）"),
    tile_row: int = Path(..., description="TileRow 索引（Y 軸）"),
    tile_col: int = Path(..., description="TileCol 索引（X 軸）"),
    current_user=Depends(require_full_auth)
):
    """
    NLSC 地籍圖 WMTS 代理端點

    代理 NLSC 地籍圖 WMTS 服務，避免前端直接調用外部服務

    URL 格式：
    - NLSC 原始: `https://landmaps.nlsc.gov.tw/S_Maps/wmts/DMAPS/default/GoogleMapsCompatible/{TileMatrix}/{TileRow}/{TileCol}`
    - 本端點: `/api/nlsc/cadastral/tiles/{tile_matrix}/{tile_row}/{tile_col}`

    參數：
    - **tile_matrix**: TileMatrix 索引（zoom level, 0-19）
    - **tile_row**: TileRow 索引（Y 軸）
    - **tile_col**: TileCol 索引（X 軸）

    回應：
    - PNG 圖片（地籍圖磚塊）
    """
    try:
        logger.info(f"WMTS tile request: {tile_matrix}/{tile_row}/{tile_col}")

        # 調用 service 層代理請求
        tile_content = await NLSCService.proxy_cadastral_wmts_tile(
            tile_matrix=tile_matrix,
            tile_row=tile_row,
            tile_col=tile_col
        )

        # 返回圖片內容
        return Response(
            content=tile_content,
            media_type="image/png",
            headers={
                "Cache-Control": "public, max-age=86400",  # 快取 24 小時
                "Access-Control-Allow-Origin": "*"
            }
        )

    except Exception as e:
        logger.error(f"WMTS tile proxy error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="地籍圖磚塊代理失敗")


# ============================================================================
# 地段清單查詢服務（從 /spatial 遷移）
# ============================================================================

@router.get("/sections/{county_land_code}/{town_land_code}")
async def query_land_sections(
    county_land_code: str = Path(..., description="縣市地政代碼（例如：'A' for 台北市）"),
    town_land_code: str = Path(..., description="鄉鎮地政代碼（例如：'A01' for 中正區）"),
    current_user=Depends(require_full_auth)
) -> Dict[str, Any]:
    """
    查詢地段清單（依地政代碼）

    **架構遷移**：
    - 原路徑: `/spatial/land-sections/{county}/{town}` (已棄用)
    - 新路徑: `/nlsc/sections/{county}/{town}`
    - 理由: 統一所有 NLSC API 代理服務在 /nlsc 下

    對應 NLSC API:
    `https://api.nlsc.gov.tw/other/ListLandSection/{county_land_code}/{town_land_code}`

    Args:
        county_land_code: 縣市地政代碼（counties.land_code）
        town_land_code: 鄉鎮市區地政代碼（towns.land_code）

    Returns:
        地段清單資料（包含 sections, count, api_url）
    """
    try:
        logger.info(f"Land sections query: {county_land_code}/{town_land_code}")

        result = await NLSCService.query_land_sections(
            county_land_code=county_land_code,
            town_land_code=town_land_code
        )

        # 統一回應格式（無論成功或失敗都返回 200，由 success 欄位表示狀態）
        return result

    except Exception as e:
        logger.error(f"Error in land sections query: {e}", exc_info=True)
        # 返回結構化錯誤而非 HTTP 異常
        return {
            "success": False,
            "sections": [],
            "count": 0,
            "message": f"查詢失敗: {str(e)}",
            "error_type": "unknown_error"
        }


# ============================================================================
# NLSC API 健康檢查（從 /spatial 遷移）
# ============================================================================

@router.get("/health")
async def check_nlsc_api_health(
    current_user=Depends(require_full_auth)
) -> Dict[str, Any]:
    """
    檢查 NLSC API 服務健康狀態

    **架構遷移**：
    - 原路徑: `/spatial/land-sections/health` (已棄用)
    - 新路徑: `/nlsc/health`
    - 理由: 統一所有 NLSC API 相關端點在 /nlsc 下

    測試方式：
    - 使用台北市中正區的地段查詢作為健康檢查測試

    Returns:
        健康狀態資訊（包含 nlsc_api_status, status_code, timestamp）
    """
    try:
        logger.info("NLSC API health check requested")

        result = await NLSCService.check_health()

        return result

    except Exception as e:
        logger.error(f"Error in NLSC health check: {e}", exc_info=True)
        from datetime import datetime, timezone
        return {
            "nlsc_api_status": "error",
            "error": f"Health check failed: {str(e)}",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


# ============================================================================
# 舊端點（向後相容，已標記 deprecated）
# ============================================================================

@router.post("/cadastral/query-by-land-number", response_model=CadastralQueryResponse, deprecated=True)
async def query_cadastral_by_land_number_deprecated(
    request: CadastralQueryByLandNumberRequest,
    current_user=Depends(require_full_auth)
) -> CadastralQueryResponse:
    """
    查詢地籍圖（依地號）- 已棄用

    **⚠️ 已棄用**: 此端點已棄用，請使用 `GET/POST /nlsc/cadastral/land`

    **遷移路徑**：
    - 舊路徑: `POST /nlsc/cadastral/query-by-land-number` (deprecated)
    - 新路徑: `GET/POST /nlsc/cadastral/land` (recommended)
    """
    logger.warning("Using deprecated endpoint: /cadastral/query-by-land-number")

    # 轉發到新端點
    return await query_cadastral_land(
        county_code=request.county_code,
        section_code=request.section_code,
        land_number_main=request.land_number_main,
        land_number_sub=request.land_number_sub,
        format=request.format,
        srid=request.srid,
        current_user=current_user
    )


@router.post("/cadastral/query-by-point", response_model=CadastralQueryResponse, deprecated=True)
async def query_cadastral_by_point_deprecated(
    request: CadastralQueryByPointRequest,
    current_user=Depends(require_full_auth)
) -> CadastralQueryResponse:
    """
    查詢地籍圖（依座標點）- 已棄用

    **⚠️ 已棄用**: 此端點已棄用，請使用 `GET/POST /nlsc/cadastral/point`

    **遷移路徑**：
    - 舊路徑: `POST /nlsc/cadastral/query-by-point` (deprecated)
    - 新路徑: `GET/POST /nlsc/cadastral/point` (recommended)
    """
    logger.warning("Using deprecated endpoint: /cadastral/query-by-point")

    # 轉發到新端點
    return await query_cadastral_point(
        longitude=request.longitude,
        latitude=request.latitude,
        srid=request.srid,
        format=request.format,
        current_user=current_user
    )
