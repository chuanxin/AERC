"""
NLSC (國土測繪中心) API 服務層
負責調用 NLSC API 並解析 GML 回應

設計原則（Linus Style）：
- Keep it simple: 使用 Python 內建 xml.etree.ElementTree，不引入額外依賴
- Single responsibility: 專注於 NLSC API 調用和 GML 解析
- No special cases: 統一的錯誤處理機制

注意：NLSC API 的 SSL 憑證缺少 Subject Key Identifier，
即使匯入 TWCA 根憑證也無法通過 Python 的 SSL 驗證，
因此必須使用 verify=False 跳過驗證。
"""

import httpx
import xml.etree.ElementTree as ET
import logging
from typing import Dict, List, Optional, Tuple
from decimal import Decimal

logger = logging.getLogger(__name__)


class NLSCService:
    """​NLSC API 服務類別"""

    # NLSC API Base URLs
    CADASTRAL_QUERY_URL = "https://api.nlsc.gov.tw/dmaps/CadasMapQuery"
    CADASTRAL_POINT_QUERY_URL = "https://api.nlsc.gov.tw/dmaps/CadasMapPointQuery"
    CADASTRAL_WMTS_URL = "https://landmaps.nlsc.gov.tw/S_Maps/wmts/DMAPS/default/GoogleMapsCompatible"

    # GML 命名空間
    NAMESPACES = {
        'gml': 'http://www.opengis.net/gml',
        'wfs': 'http://www.opengis.net/wfs',
        'WFS': 'http://www.opengis.net/wfs'
    }

    @staticmethod
    def format_land_number(main: str, sub: str = "0") -> str:
        """
        格式化地號為 8 碼格式

        Args:
            main: 主號（例如：'1', '123'）
            sub: 副號（例如：'0', '5'）

        Returns:
            8 碼地號（例如：'00010000', '01230005'）
        """
        main_num = int(main or "0")
        sub_num = int(sub or "0")

        # 主號 4 碼 + 副號 4 碼
        main_part = str(main_num).zfill(4)
        sub_part = str(sub_num).zfill(4)

        return f"{main_part}{sub_part}"

    @staticmethod
    def parse_land_number(land_number_8: str) -> Tuple[str, str]:
        """
        解析 8 碼地號為主號和副號

        Args:
            land_number_8: 8 碼地號（例如：'00010000'）

        Returns:
            (main, sub): 主號和副號（例如：('1', '0')）
        """
        if len(land_number_8) != 8:
            logger.warning(f"Invalid land number format: {land_number_8}")
            return ("0", "0")

        main = str(int(land_number_8[:4]))  # 移除前導零
        sub = str(int(land_number_8[4:]))   # 移除前導零

        return (main, sub)

    @staticmethod
    def format_land_number_display(land_number_8: str) -> str:
        """
        格式化地號為顯示格式

        Args:
            land_number_8: 8 碼地號（例如：'00010000'）

        Returns:
            顯示格式（例如：'1' 或 '1-5'）
        """
        main, sub = NLSCService.parse_land_number(land_number_8)

        # 如果副號為 0，只顯示主號
        if sub == "0":
            return main
        else:
            return f"{main}-{sub}"

    @classmethod
    async def query_cadastral_by_land_number(
        cls,
        county_code: str,
        section_code: str,
        land_number_main: str,
        land_number_sub: str = "0",
        format: str = "gml",
        srid: str = "4326"
    ) -> Dict:
        """
        查詢地籍圖（依地號）

        Args:
            county_code: 縣市代碼
            section_code: 地段代碼
            land_number_main: 主號
            land_number_sub: 副號
            format: 檔案格式（gml, kml, shp）
            srid: 坐標系統（4326: WGS84, 3826: TWD97）

        Returns:
            解析後的 GeoJSON 格式資料
        """
        # 格式化地號為 8 碼
        land_number = cls.format_land_number(land_number_main, land_number_sub)

        # 建立 API URL
        api_url = f"{cls.CADASTRAL_QUERY_URL}/{county_code}/{section_code}/{land_number}/{format}/{srid}"
        logger.info(f"Querying NLSC Cadastral Map API: {api_url}")

        try:
            # 發送 HTTP 請求（跳過 SSL 驗證，因為 NLSC 憑證缺少 Subject Key Identifier）
            async with httpx.AsyncClient(timeout=30.0, verify=False) as client:
                response = await client.get(api_url)
                response.raise_for_status()

            # 解析 GML
            gml_text = response.text
            features = cls.parse_gml(gml_text, srid)

            return {
                "success": True,
                "features": features,
                "total_count": len(features),
                "api_url": api_url,
                "source": "nlsc_api"
            }

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error from NLSC API: {e}")
            return {
                "success": False,
                "features": [],
                "total_count": 0,
                "message": f"HTTP {e.response.status_code}: {e.response.reason_phrase}",
                "error_type": "http_error",
                "api_url": api_url
            }

        except Exception as e:
            logger.error(f"Failed to query NLSC API: {e}", exc_info=True)
            return {
                "success": False,
                "features": [],
                "total_count": 0,
                "message": f"查詢失敗: {str(e)}",
                "error_type": "unknown_error",
                "api_url": api_url
            }

    @classmethod
    async def query_cadastral_by_point(
        cls,
        longitude: Decimal,
        latitude: Decimal,
        srid: str = "4326",
        format: str = "gml"
    ) -> Dict:
        """
        查詢地籍圖（依座標點）

        Args:
            longitude: 經度
            latitude: 緯度
            srid: 坐標系統（4326: WGS84, 3826: TWD97）
            format: 檔案格式（gml, kml, shp）

        Returns:
            解析後的 GeoJSON 格式資料
        """
        # 建立 API URL
        api_url = f"{cls.CADASTRAL_POINT_QUERY_URL}/{longitude}/{latitude}/{srid}/{format}"
        logger.info(f"Querying NLSC Cadastral Map API (Point): {api_url}")

        try:
            # 發送 HTTP 請求（跳過 SSL 驗證，因為 NLSC 憑證缺少 Subject Key Identifier）
            async with httpx.AsyncClient(timeout=30.0, verify=False) as client:
                response = await client.get(api_url)
                response.raise_for_status()

            # 解析 GML
            gml_text = response.text
            features = cls.parse_gml(gml_text, srid)

            return {
                "success": True,
                "features": features,
                "total_count": len(features),
                "api_url": api_url,
                "source": "nlsc_api"
            }

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error from NLSC API: {e}")
            return {
                "success": False,
                "features": [],
                "total_count": 0,
                "message": f"HTTP {e.response.status_code}: {e.response.reason_phrase}",
                "error_type": "http_error",
                "api_url": api_url
            }

        except Exception as e:
            logger.error(f"Failed to query NLSC API (Point): {e}", exc_info=True)
            return {
                "success": False,
                "features": [],
                "total_count": 0,
                "message": f"查詢失敗: {str(e)}",
                "error_type": "unknown_error",
                "api_url": api_url
            }

    @classmethod
    def parse_gml(cls, gml_text: str, srid: str = "4326") -> List[Dict]:
        """
        解析 NLSC GML 2.1.2 格式為 GeoJSON Features

        Args:
            gml_text: GML 文字內容
            srid: 座標系統

        Returns:
            GeoJSON Features 列表
        """
        try:
            # 解析 XML
            root = ET.fromstring(gml_text)

            features = []

            # 查找所有 gml:featureMember 或 wfs:featureMember
            feature_members = root.findall('.//gml:featureMember', cls.NAMESPACES)
            if not feature_members:
                feature_members = root.findall('.//featureMember')  # 嘗試不帶命名空間

            logger.info(f"Found {len(feature_members)} feature members in GML")

            for member in feature_members:
                # 查找 CADASTRE feature
                cadastre = member.find('.//WFS:CADASTRE', cls.NAMESPACES)
                if cadastre is None:
                    cadastre = member.find('.//CADASTRE')  # 嘗試不帶命名空間

                if cadastre is None:
                    logger.warning("CADASTRE element not found in feature member")
                    continue

                # 提取屬性
                properties = cls._extract_properties(cadastre)

                # 提取幾何
                geometry = cls._extract_geometry(cadastre, srid)

                if geometry:
                    feature = {
                        "type": "Feature",
                        "properties": properties,
                        "geometry": geometry
                    }
                    features.append(feature)

            logger.info(f"Parsed {len(features)} features from GML")
            return features

        except ET.ParseError as e:
            logger.error(f"Failed to parse GML XML: {e}")
            logger.debug(f"GML content preview: {gml_text[:500]}")
            return []

        except Exception as e:
            logger.error(f"Unexpected error parsing GML: {e}", exc_info=True)
            return []

    @classmethod
    def _extract_properties(cls, cadastre_element: ET.Element) -> Dict:
        """從 CADASTRE 元素中提取屬性"""
        properties = {}

        # GML 標準欄位
        field_mapping = {
            'CITY': str,
            'TOWN': str,
            'OFFICE': str,
            'SECT': str,
            'LANDNO': str,
            'AREA': float,
            'LANDUSE': str,
            'LANDDETATIS': str,
            'VALUESSESSED': float,
            'VALUEANNOUNCE': float,
        }

        for field_name, field_type in field_mapping.items():
            # 嘗試帶命名空間查找
            element = cadastre_element.find(f'.//WFS:{field_name}', cls.NAMESPACES)
            if element is None:
                # 嘗試不帶命名空間
                element = cadastre_element.find(f'.//{field_name}')

            if element is not None and element.text:
                try:
                    if field_type == float:
                        properties[field_name] = float(element.text)
                    else:
                        properties[field_name] = element.text.strip()
                except ValueError:
                    logger.warning(f"Failed to convert {field_name}={element.text} to {field_type}")

        return properties

    @classmethod
    def _extract_geometry(cls, cadastre_element: ET.Element, srid: str) -> Optional[Dict]:
        """從 CADASTRE 元素中提取幾何資料"""
        try:
            # 查找 Shape/MultiPolygon
            multi_polygon = cadastre_element.find('.//gml:MultiPolygon', cls.NAMESPACES)
            if multi_polygon is None:
                multi_polygon = cadastre_element.find('.//MultiPolygon')

            if multi_polygon is None:
                logger.warning("MultiPolygon not found in CADASTRE element")
                return None

            # 查找所有 coordinates
            coordinates_elements = multi_polygon.findall('.//gml:coordinates', cls.NAMESPACES)
            if not coordinates_elements:
                coordinates_elements = multi_polygon.findall('.//coordinates')

            if not coordinates_elements:
                logger.warning("No coordinates found in MultiPolygon")
                return None

            # 解析座標（GML 2.1.2 使用 <gml:coordinates>）
            polygon_coordinates = []

            for coords_elem in coordinates_elements:
                coords_text = coords_elem.text.strip()
                # 分割座標對（格式：lon1,lat1 lon2,lat2 ...）
                coord_pairs = coords_text.split()

                ring = []
                for pair in coord_pairs:
                    lon, lat = pair.split(',')
                    ring.append([float(lon), float(lat)])

                polygon_coordinates.append(ring)

            # 構建 GeoJSON 幾何
            geometry = {
                "type": "MultiPolygon",
                "coordinates": [polygon_coordinates]  # MultiPolygon 格式：[[[ring1], [ring2]], ...]
            }

            return geometry

        except Exception as e:
            logger.error(f"Failed to extract geometry: {e}", exc_info=True)
            return None

    @classmethod
    async def proxy_cadastral_wmts_tile(
        cls,
        tile_matrix: int,
        tile_row: int,
        tile_col: int
    ) -> bytes:
        """
        代理 NLSC 地籍圖 WMTS 磚塊請求

        Args:
            tile_matrix: TileMatrix 索引（zoom level）
            tile_row: TileRow 索引（Y 軸）
            tile_col: TileCol 索引（X 軸）

        Returns:
            PNG 圖片內容（bytes）

        Raises:
            Exception: 當請求失敗時

        TODO: 添加快取機制以提升效能
        - 方案 A（簡單）：使用 @lru_cache 內存快取（5 行代碼，提升 70%）
        - 方案 B（推薦）：使用 Redis 快取（30 行代碼，提升 80%，持久化）
        - 方案 C（中等）：使用文件系統快取（25 行代碼，提升 70%，持久化）
        快取可使 70-90% 的請求從 200ms 降至 <1ms
        """
        # 構建 NLSC WMTS URL
        tile_url = f"{cls.CADASTRAL_WMTS_URL}/{tile_matrix}/{tile_row}/{tile_col}"
        logger.debug(f"Proxying WMTS tile: {tile_url}")

        try:
            # 發送 HTTP 請求（跳過 SSL 驗證）
            async with httpx.AsyncClient(timeout=10.0, verify=False) as client:
                response = await client.get(tile_url)
                response.raise_for_status()

            return response.content

        except httpx.HTTPStatusError as e:
            logger.error(f"NLSC WMTS HTTP error: {e}")
            raise

        except Exception as e:
            logger.error(f"Failed to proxy WMTS tile: {e}", exc_info=True)
            raise
