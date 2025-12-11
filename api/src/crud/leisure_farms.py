"""
休閒農場資料查詢系統的 CRUD 操作
使用 PostGIS 進行空間查詢
"""

from typing import List, Optional
from decimal import Decimal
import logging

from tortoise import connections

from ..database.geo_models import LeisureFarms
from ..schemas.leisure_farms import (
    LeisureFarmItem,
    LeisureFarmNearbyResponse,
    LeisureFarmCheckResponse,
    LeisureFarmByLocationResponse,
    LeisureFarmStatsResponse,
)

logger = logging.getLogger(__name__)


class LeisureFarmsCRUD:
    """休閒農場資料的 CRUD 操作類"""

    @staticmethod
    async def search_nearby(
        longitude: Decimal,
        latitude: Decimal,
        radius_meters: float = 5000,
        limit: int = 10
    ) -> LeisureFarmNearbyResponse:
        """
        查詢指定座標附近的休閒農場
        使用 PostGIS ST_DWithin 進行空間查詢
        
        Args:
            longitude: 查詢點經度 (WGS84)
            latitude: 查詢點緯度 (WGS84)
            radius_meters: 查詢半徑（公尺）
            limit: 最大回傳筆數
        """
        try:
            conn = connections.get("default")
            
            # 使用 PostGIS 進行空間查詢
            # ST_DWithin 使用 geography 類型進行公尺距離計算
            # ST_Distance 計算實際距離
            query = """
                SELECT 
                    id, farm_name, county, township, address, phone, web_url,
                    certify_start_date, certify_end_date, identify_item, photo_url,
                    longitude, latitude,
                    ST_Distance(
                        geom::geography, 
                        ST_SetSRID(ST_MakePoint($1, $2), 4326)::geography
                    ) as distance_meters
                FROM leisure_farms
                WHERE ST_DWithin(
                    geom::geography,
                    ST_SetSRID(ST_MakePoint($1, $2), 4326)::geography,
                    $3
                )
                ORDER BY distance_meters ASC
                LIMIT $4
            """
            
            results = await conn.execute_query_dict(
                query, 
                [float(longitude), float(latitude), radius_meters, limit]
            )
            
            farms = [
                LeisureFarmItem(
                    id=row["id"],
                    farm_name=row["farm_name"],
                    county=row["county"],
                    township=row["township"],
                    address=row["address"],
                    phone=row["phone"],
                    web_url=row["web_url"],
                    certify_start_date=row["certify_start_date"],
                    certify_end_date=row["certify_end_date"],
                    identify_item=row["identify_item"],
                    photo_url=row["photo_url"],
                    longitude=row["longitude"],
                    latitude=row["latitude"],
                    distance_meters=row["distance_meters"]
                )
                for row in results
            ]
            
            return LeisureFarmNearbyResponse(
                success=True,
                farms=farms,
                total_count=len(farms),
                query_point={"longitude": float(longitude), "latitude": float(latitude)},
                search_radius_meters=radius_meters,
                message=f"找到 {len(farms)} 間休閒農場"
            )
            
        except Exception as e:
            logger.error(f"Error searching nearby leisure farms: {e}")
            return LeisureFarmNearbyResponse(
                success=False,
                farms=[],
                total_count=0,
                search_radius_meters=radius_meters,
                message=f"查詢失敗: {str(e)}"
            )

    @staticmethod
    async def check_nearby_farms(
        longitude: Decimal,
        latitude: Decimal,
        radius_meters: float = 1000
    ) -> LeisureFarmCheckResponse:
        """
        檢查指定座標附近是否有休閒農場
        用於快速判斷是否需要提示使用者
        
        Args:
            longitude: 查詢點經度 (WGS84)
            latitude: 查詢點緯度 (WGS84)
            radius_meters: 查詢半徑（公尺），預設 1000m
        """
        try:
            conn = connections.get("default")
            
            # 先查詢最近的一間，並計算範圍內總數
            query = """
                WITH nearby AS (
                    SELECT 
                        id, farm_name, county, township, address, phone, web_url,
                        certify_start_date, certify_end_date, identify_item, photo_url,
                        longitude, latitude,
                        ST_Distance(
                            geom::geography, 
                            ST_SetSRID(ST_MakePoint($1, $2), 4326)::geography
                        ) as distance_meters
                    FROM leisure_farms
                    WHERE ST_DWithin(
                        geom::geography,
                        ST_SetSRID(ST_MakePoint($1, $2), 4326)::geography,
                        $3
                    )
                )
                SELECT 
                    (SELECT COUNT(*) FROM nearby) as total_count,
                    n.*
                FROM nearby n
                ORDER BY distance_meters ASC
                LIMIT 1
            """
            
            results = await conn.execute_query_dict(
                query,
                [float(longitude), float(latitude), radius_meters]
            )
            
            if not results:
                return LeisureFarmCheckResponse(
                    success=True,
                    has_nearby_farms=False,
                    nearest_farm=None,
                    farms_within_radius=0,
                    message="範圍內無休閒農場"
                )
            
            row = results[0]
            nearest_farm = LeisureFarmItem(
                id=row["id"],
                farm_name=row["farm_name"],
                county=row["county"],
                township=row["township"],
                address=row["address"],
                phone=row["phone"],
                web_url=row["web_url"],
                certify_start_date=row["certify_start_date"],
                certify_end_date=row["certify_end_date"],
                identify_item=row["identify_item"],
                photo_url=row["photo_url"],
                longitude=row["longitude"],
                latitude=row["latitude"],
                distance_meters=row["distance_meters"]
            )
            
            return LeisureFarmCheckResponse(
                success=True,
                has_nearby_farms=True,
                nearest_farm=nearest_farm,
                farms_within_radius=row["total_count"],
                message=f"範圍內有 {row['total_count']} 間休閒農場，最近距離 {row['distance_meters']:.0f} 公尺"
            )
            
        except Exception as e:
            logger.error(f"Error checking nearby leisure farms: {e}")
            return LeisureFarmCheckResponse(
                success=False,
                has_nearby_farms=False,
                message=f"檢查失敗: {str(e)}"
            )

    @staticmethod
    async def search_by_location(
        county: Optional[str] = None,
        township: Optional[str] = None
    ) -> LeisureFarmByLocationResponse:
        """
        依縣市鄉鎮查詢休閒農場
        
        Args:
            county: 縣市名稱
            township: 鄉鎮市區名稱
        """
        try:
            # 建構查詢條件
            filters = {}
            if county:
                filters["county"] = county
            if township:
                filters["township"] = township
            
            # 使用 ORM 查詢
            if filters:
                farms_db = await LeisureFarms.filter(**filters).all()
            else:
                farms_db = await LeisureFarms.all()
            
            farms = [
                LeisureFarmItem(
                    id=f.id,
                    farm_name=f.farm_name,
                    county=f.county,
                    township=f.township,
                    address=f.address,
                    phone=f.phone,
                    web_url=f.web_url,
                    certify_start_date=f.certify_start_date,
                    certify_end_date=f.certify_end_date,
                    identify_item=f.identify_item,
                    photo_url=f.photo_url,
                    longitude=f.longitude,
                    latitude=f.latitude,
                    distance_meters=None
                )
                for f in farms_db
            ]
            
            return LeisureFarmByLocationResponse(
                success=True,
                farms=farms,
                total_count=len(farms),
                county=county,
                township=township
            )
            
        except Exception as e:
            logger.error(f"Error searching leisure farms by location: {e}")
            return LeisureFarmByLocationResponse(
                success=False,
                farms=[],
                total_count=0,
                county=county,
                township=township
            )

    @staticmethod
    async def get_statistics() -> LeisureFarmStatsResponse:
        """
        取得休閒農場統計資料
        """
        try:
            conn = connections.get("default")
            
            # 總數和依縣市統計
            query = """
                SELECT 
                    county,
                    COUNT(*) as count,
                    MAX(last_synced) as last_synced
                FROM leisure_farms
                GROUP BY county
                ORDER BY count DESC
            """
            
            results = await conn.execute_query_dict(query)
            
            total_farms = sum(row["count"] for row in results)
            by_county = {row["county"]: row["count"] for row in results}
            last_synced = results[0]["last_synced"] if results else None
            
            return LeisureFarmStatsResponse(
                success=True,
                total_farms=total_farms,
                by_county=by_county,
                last_synced=last_synced
            )
            
        except Exception as e:
            logger.error(f"Error getting leisure farms statistics: {e}")
            return LeisureFarmStatsResponse(
                success=False,
                total_farms=0,
                by_county={}
            )
