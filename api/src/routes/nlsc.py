"""
NLSC (國土測繪中心) API 路由
提供地籍圖查詢等服務的代理端點

設計原則（Linus Style）：
- Simple proxy: 轉發請求到 NLSC API，不做複雜業務邏輯
- Consistent error handling: 統一的錯誤回應格式
- No database: 純代理服務，不涉及資料庫操作（未來可選添加快取）
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import Response
from typing import Optional
from decimal import Decimal
import logging
import httpx

from ..schemas.nlsc import (
    CadastralQueryByLandNumberRequest,
    CadastralQueryByPointRequest,
    CadastralQueryResponse,
    CadastralErrorResponse,
)
from ..services.nlsc_service import NLSCService
from ..auth.jwthandler import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/nlsc", tags=["NLSC 國土測繪中心"])


@router.post("/cadastral/query-by-land-number", response_model=CadastralQueryResponse)
async def query_cadastral_by_land_number(
    request: CadastralQueryByLandNumberRequest,
    current_user=Depends(get_current_user)
) -> CadastralQueryResponse:
    """
    查詢地籍圖（依地號）

    對應 NLSC API: `https://api.nlsc.gov.tw/dmaps/CadasMapQuery/{county}/{section}/{land_number}/{format}/{srid}`

    請求參數：
    - **county_code**: 縣市代碼（例如：'B' for 台中市）
    - **section_code**: 地段代碼（例如：'0532'）
    - **land_number_main**: 地號主號（例如：'1'）
    - **land_number_sub**: 地號副號（例如：'0'），預設為 '0'
    - **format**: 檔案格式（gml, kml, shp），預設為 'gml'
    - **srid**: 坐標系統（'4326': WGS84, '3826': TWD97），預設為 '4326'

    回應：
    - **features**: GeoJSON Feature 陣列（包含地籍圖幾何和屬性）
    - **total_count**: Feature 數量
    - **message**: 錯誤或警告訊息（如有）
    - **api_url**: NLSC API URL（用於除錯）
    """
    try:
        logger.info(
            f"Cadastral query by land number: {request.county_code}/{request.section_code}/"
            f"{request.land_number_main}-{request.land_number_sub}"
        )

        result = await NLSCService.query_cadastral_by_land_number(
            county_code=request.county_code,
            section_code=request.section_code,
            land_number_main=request.land_number_main,
            land_number_sub=request.land_number_sub,
            format=request.format,
            srid=request.srid
        )

        if not result["success"]:
            # NLSC API 調用失敗，但不拋出 HTTP 錯誤
            # 返回結構化的錯誤回應（success: false）
            logger.warning(f"NLSC API returned error: {result.get('message')}")
            return CadastralErrorResponse(**result)

        logger.info(f"Cadastral query completed: {result['total_count']} features")
        return CadastralQueryResponse(**result)

    except Exception as e:
        logger.error(f"Error in cadastral query by land number: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="地籍圖查詢失敗，請稍後再試")


@router.post("/cadastral/query-by-point", response_model=CadastralQueryResponse)
async def query_cadastral_by_point(
    request: CadastralQueryByPointRequest,
    current_user=Depends(get_current_user)
) -> CadastralQueryResponse:
    """
    查詢地籍圖（依座標點）

    對應 NLSC API: `https://api.nlsc.gov.tw/dmaps/CadasMapPointQuery/{lon}/{lat}/{srid}/{format}`

    請求參數：
    - **longitude**: 經度（WGS84 或 TWD97）
    - **latitude**: 緯度（WGS84 或 TWD97）
    - **srid**: 坐標系統（'4326': WGS84, '3826': TWD97），預設為 '4326'
    - **format**: 檔案格式（gml, kml, shp），預設為 'gml'

    回應：
    - **features**: GeoJSON Feature 陣列（包含地籍圖幾何和屬性）
    - **total_count**: Feature 數量
    - **message**: 錯誤或警告訊息（如有）
    - **api_url**: NLSC API URL（用於除錯）
    """
    try:
        logger.info(f"Cadastral query by point: ({request.longitude}, {request.latitude})")

        result = await NLSCService.query_cadastral_by_point(
            longitude=request.longitude,
            latitude=request.latitude,
            srid=request.srid,
            format=request.format
        )

        if not result["success"]:
            # NLSC API 調用失敗，但不拋出 HTTP 錯誤
            # 返回結構化的錯誤回應（success: false）
            logger.warning(f"NLSC API returned error: {result.get('message')}")
            return CadastralErrorResponse(**result)

        logger.info(f"Cadastral point query completed: {result['total_count']} features")
        return CadastralQueryResponse(**result)

    except Exception as e:
        logger.error(f"Error in cadastral query by point: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="地籍圖查詢失敗，請稍後再試")


@router.get("/cadastral/query-by-land-number-get", response_model=CadastralQueryResponse)
async def query_cadastral_by_land_number_get(
    county_code: str = Query(..., description="縣市代碼（例如：'B'）", min_length=1, max_length=2),
    section_code: str = Query(..., description="地段代碼（例如：'0532'）", min_length=4, max_length=4),
    land_number_main: str = Query(..., description="地號主號（例如：'1'）", min_length=1, max_length=4),
    land_number_sub: str = Query(default="0", description="地號副號（例如：'0'）", max_length=4),
    format: str = Query(default="gml", description="檔案格式（gml, kml, shp）"),
    srid: str = Query(default="4326", description="坐標系統（4326: WGS84, 3826: TWD97）"),
    current_user=Depends(get_current_user)
) -> CadastralQueryResponse:
    """
    查詢地籍圖（依地號，GET 方法）

    提供 GET 方法作為替代端點，方便瀏覽器直接調用和測試

    查詢參數：
    - **county_code**: 縣市代碼
    - **section_code**: 地段代碼
    - **land_number_main**: 地號主號
    - **land_number_sub**: 地號副號（可選）
    - **format**: 檔案格式（可選）
    - **srid**: 坐標系統（可選）
    """
    # 建立 request 物件並調用 POST 處理函數
    request = CadastralQueryByLandNumberRequest(
        county_code=county_code,
        section_code=section_code,
        land_number_main=land_number_main,
        land_number_sub=land_number_sub,
        format=format,  # type: ignore
        srid=srid  # type: ignore
    )

    return await query_cadastral_by_land_number(request, current_user)


@router.get("/cadastral/query-by-point-get", response_model=CadastralQueryResponse)
async def query_cadastral_by_point_get(
    longitude: Decimal = Query(..., description="經度（WGS84 或 TWD97）", ge=-180, le=180),
    latitude: Decimal = Query(..., description="緯度（WGS84 或 TWD97）", ge=-90, le=90),
    srid: str = Query(default="4326", description="坐標系統（4326: WGS84, 3826: TWD97）"),
    format: str = Query(default="gml", description="檔案格式（gml, kml, shp）"),
    current_user=Depends(get_current_user)
) -> CadastralQueryResponse:
    """
    查詢地籍圖（依座標點，GET 方法）

    提供 GET 方法作為替代端點，方便瀏覽器直接調用和測試

    查詢參數：
    - **longitude**: 經度
    - **latitude**: 緯度
    - **srid**: 坐標系統（可選）
    - **format**: 檔案格式（可選）
    """
    # 建立 request 物件並調用 POST 處理函數
    request = CadastralQueryByPointRequest(
        longitude=longitude,
        latitude=latitude,
        srid=srid,  # type: ignore
        format=format  # type: ignore
    )

    return await query_cadastral_by_point(request, current_user)


@router.get("/wmts/cadastral/{tile_matrix}/{tile_row}/{tile_col}")
async def proxy_cadastral_wmts_tile(
    tile_matrix: int,
    tile_row: int,
    tile_col: int,
    current_user=Depends(get_current_user)
):
    """
    NLSC 地籍圖 WMTS 代理端點

    代理 NLSC 地籍圖 WMTS 服務，避免前端直接調用外部服務

    URL 格式：
    - NLSC 原始: https://landmaps.nlsc.gov.tw/S_Maps/wmts/DMAPS/default/GoogleMapsCompatible/{TileMatrix}/{TileRow}/{TileCol}
    - 本端點: /api/v1/nlsc/wmts/cadastral/{tile_matrix}/{tile_row}/{tile_col}

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

    except httpx.HTTPStatusError as e:
        logger.error(f"WMTS tile HTTP error: {e}")
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"地籍圖磚塊載入失敗: HTTP {e.response.status_code}"
        )

    except Exception as e:
        logger.error(f"WMTS tile proxy error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="地籍圖磚塊代理失敗")
