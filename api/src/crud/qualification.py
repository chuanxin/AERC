"""
Qualification 重複案件查詢系統的 CRUD 操作
基於現有的 GrantLocations 實現查詢邏輯
"""

from typing import List, Optional, Dict, Any
from decimal import Decimal
import hashlib
import logging
from datetime import datetime

from tortoise.exceptions import DoesNotExist
from tortoise import timezone
from tortoise.expressions import Q

from ..database.geo_models import GrantLocations
from ..database.models import QualificationQuery, QualificationQueryType, Towns, Counties, GrantVersions, GrantStatusGroup
from ..schemas.qualification import (
    QualificationSearchRequest, GrantCaseItem, AreaStatistics,
    QueryInfo, ResponseMetadata, QualificationResponse,
    AreaCheckRequest, AreaCheckResponse
)

logger = logging.getLogger(__name__)

# 逐案件「資料格式錯誤」警告的固定訊息（最終值，非範例）——缺縣市/鄉鎮名稱時使用
DATA_FORMAT_WARNING_MSG = "此案件缺少縣市／鄉鎮資料，資料格式可能有誤"


class QualificationCRUD:
    """重複案件查詢的 CRUD 操作類 - 遵循 Linus 簡潔原則"""

    @staticmethod
    def _has_incomplete_county_town(location: GrantLocations) -> bool:
        """判定案件的 meta_data 是否缺少縣市/鄉鎮名稱（source-agnostic，對三來源一律適用）。

        缺名稱代表資料結構可能受損或非正規進入系統，屬應讓操作者可見的異常。
        此述詞為單一 SSOT，同時驅動逐案件警告旗標與後端診斷 log。
        """
        return (
            not location.meta_data
            or not location.meta_data.get('county')
            or not location.meta_data.get('town')
        )

    @staticmethod
    def generate_query_hash(request: QualificationSearchRequest) -> str:
        """生成查詢參數雜湊值用於快取"""
        query_str = f"{request.query_type}_{request.params.model_dump()}_{request.options.model_dump() if request.options else ''}"
        return hashlib.sha256(query_str.encode()).hexdigest()[:16]

    @staticmethod
    async def search_qualification_cases(
        request: QualificationSearchRequest
    ) -> QualificationResponse:
        """
        統一查詢介面 - 消除三種查詢類型的特殊情況處理
        這是核心查詢邏輯，使用統一的處理方式
        """
        start_time = datetime.now()
        
        # 1. 建構查詢條件 - 統一邏輯，無特殊情況
        query_conditions = await QualificationCRUD._build_query_conditions(request)

        # 2. 執行資料庫查詢
        grant_locations = await GrantLocations.filter(query_conditions).all()

        # 3. 根據縣市和鄉鎮資訊過濾 meta_data - 在有搜尋結果的情況下
        if grant_locations and (request.params.county or request.params.town):
            grant_locations = QualificationCRUD._filter_by_county_town(grant_locations, request.params.county, request.params.town)

        # 4. 轉換為統一格式並合併重複記錄
        # 先按 source_id + land_section + land_number 分組
        grouped_locations = {}
        for location in grant_locations:
            # 建立唯一鍵：source_id + land_section + land_number
            group_key = f"{location.source_id}_{location.land_section or ''}_{location.land_number or ''}"
            
            if group_key not in grouped_locations:
                grouped_locations[group_key] = []
            grouped_locations[group_key].append(location)
        
        # 為每個分組選擇代表記錄並轉換
        case_items = []
        for group_key, locations_group in grouped_locations.items():
            # 選擇代表記錄（取最新的或者有最多資料的）
            representative_location = QualificationCRUD._select_representative_location(locations_group)
            case_item = await QualificationCRUD._convert_to_case_item(
                representative_location, 
                include_office_boundaries=(request.options and request.options.include_office_boundaries)
            )
            case_items.append(case_item)
        
        # 5. 計算面積統計
        statistics = None
        if request.options and request.options.include_statistics:
            statistics = QualificationCRUD._calculate_area_statistics(case_items)

        # 6. office_boundaries 已經在 _convert_to_case_item 中處理

        # 7. 建立回應
        end_time = datetime.now()
        response_time_ms = int((end_time - start_time).total_seconds() * 1000)
        
        # 建立已搜尋年度列表
        if request.options and request.options.years:
            # 過濾有效年度
            years_searched = [
                year for year in request.options.years 
                if year is not None and isinstance(year, str) and year.strip()
            ]
            if not years_searched:  # 如果過濾後為空，代表查詢所有年度
                years_searched = await QualificationCRUD._get_available_years()
        else:
            # 未指定年度時查詢所有年度
            years_searched = await QualificationCRUD._get_available_years()
            
        query_info = QueryInfo(
            query_type=request.query_type,
            location_description=QualificationCRUD._build_location_description(request),
            search_params=request.params.model_dump(),
            years_searched=years_searched
        )
        
        metadata = ResponseMetadata(
            total_records=len(case_items),
            search_time=start_time.isoformat(),
            query_hash=QualificationCRUD.generate_query_hash(request),
            response_time_ms=response_time_ms
        )
        
        # 8. 儲存查詢記錄 (可選的快取機制)
        await QualificationCRUD._save_query_record(request, case_items, statistics, metadata)
        
        return QualificationResponse(
            query_info=query_info,
            results=case_items,
            statistics=statistics,
            metadata=metadata
        )

    @staticmethod
    async def _build_query_conditions(request: QualificationSearchRequest) -> Q:
        """建構查詢條件 - 統一處理邏輯"""
        conditions = Q()

        # 年度過濾 - 所有查詢類型共通 (只有指定年度時才過濾)
        if request.options and request.options.years and len(request.options.years) > 0:
            # 過濾掉 None 值和空字串，只處理有效的年度字串
            valid_years = [
                year for year in request.options.years
                if year is not None and isinstance(year, str) and year.strip()
            ]
            if valid_years:
                year_list = [int(year) for year in valid_years]
                conditions &= Q(apply_year__in=year_list)
        # 未指定年度或年度列表為空時查詢所有年度 (97-114年)

        # 地區過濾 - 根據查詢類型統一處理
        if request.query_type == QualificationQueryType.GENERAL:
            # 一般查詢: 優先使用地號查詢，地段為輔助篩選
            if request.params.land_number:
                conditions &= Q(land_number__iexact=request.params.land_number)

            if request.params.section:
                section_normalized = request.params.section.replace('台', '臺')
                conditions &= (
                    Q(land_section__icontains=request.params.section) |
                    Q(land_section_name__icontains=section_normalized) |
                    Q(land_section_name__icontains=section_normalized.replace('臺', '台'))
                )

        elif request.query_type in [QualificationQueryType.INDIGENOUS, QualificationQueryType.SLOPE]:
            # 原民鄉/山坡地查詢: 地段名稱模糊搜尋
            if request.params.land_number:
                conditions &= Q(land_number__iexact=request.params.land_number)
            if request.params.section:
                section_normalized = request.params.section.replace('台', '臺')
                conditions &= (
                    Q(land_section__icontains=request.params.section) |
                    Q(land_section_name__icontains=section_normalized) |
                    Q(land_section_name__icontains=section_normalized.replace('臺', '台'))
                )

        # 排除無效案件（EXCLUDED：rejected/withdrawn/deleted） - 所有查詢共通邏輯
        conditions &= ~Q(case_status__in=list(GrantStatusGroup.EXCLUDED))

        return conditions

    @staticmethod
    async def _convert_to_case_item(location: GrantLocations, include_office_boundaries: bool = False) -> GrantCaseItem:
        """將 GrantLocations 轉換為統一的 GrantCaseItem 格式"""
        # 解析 meta_data 獲取面積資訊
        approved_area = Decimal('0.00')
        land_registered_area = None
        crops = None
        is_aboriginal_area = None
        case_type = "一般設施"  # 預設值
        
        if location.meta_data:
            # 統一處理所有舊系統資料來源 (消除特殊情況)
            if location.source_system in ("legacy_farmdata", "mssql_legacy"):
                # 歷史資料格式
                approved_area = Decimal(str(location.meta_data.get('finalarea', 0)))
                # 地籍登記面積來源：farmarea
                farmarea = location.meta_data.get('farmarea')
                if farmarea is not None:
                    land_registered_area = Decimal(str(farmarea))
                # 從 grant_versions.all_steps_data.pay_detail 判斷設施類型
                case_type = await QualificationCRUD._infer_legacy_case_type(location.source_id)

            elif location.source_system == "new_aerc":
                # 新系統資料格式
                facility_area = location.meta_data.get('facility_area', '0')
                approved_area = Decimal(str(facility_area))
                # 地籍登記面積來源：land_area
                land_area = location.meta_data.get('land_area')
                if land_area is not None:
                    land_registered_area = Decimal(str(land_area))
                crops = location.meta_data.get('crops', [])
                is_aboriginal_area = location.meta_data.get('is_aboriginal_area')
                case_type = QualificationCRUD._infer_case_type_from_crops(crops)
        
        # 根據 source_system 決定 grant_id 的取得方式
        grant_id = ""
        if location.source_system == "new_aerc":
            # 新系統：直接使用 source_id
            grant_id = str(location.source_id)
        elif location.source_system in ("legacy_farmdata", "mssql_legacy"):
            # 歷史資料：通過 source_id 查找 grant_versions，取得 grant_id
            try:
                grant_version = await GrantVersions.filter(version=location.source_id).prefetch_related('grant').first()
                if grant_version:
                    grant_id = str(grant_version.grant.id)
                else:
                    grant_id = str(location.source_id)
            except Exception as e:
                # 查詢 grant_version 發生非預期例外，記錄診斷後降級使用 source_id 作為後備
                logger.warning(
                    "[_convert_to_case_item] 查詢 grant_version 失敗（source_id=%s）：%s",
                    location.source_id, str(e),
                )
                grant_id = str(location.source_id)

        # 查詢 office_boundaries (如果需要)
        office_boundaries_data = None
        if include_office_boundaries:
            office_boundaries_data = await QualificationCRUD._query_office_boundaries_for_location(location)

        # 缺縣市/鄉鎮名稱時：設逐案件警告旗標 + 留後端診斷 log（不靜默放行）
        data_format_warning = None
        if QualificationCRUD._has_incomplete_county_town(location):
            data_format_warning = DATA_FORMAT_WARNING_MSG
            logger.warning(
                "[_convert_to_case_item] 案件缺縣市/鄉鎮名稱，標記資料格式警告：id=%s, source_system=%s",
                location.id, location.source_system,
            )

        return GrantCaseItem(
            id=location.id,
            source_system=location.source_system,
            grant_id=grant_id,
            case_number=location.case_number,
            case_type=case_type,
            status=location.case_status,
            land_section=location.land_section or "",
            land_number=location.land_number or "",
            application_year=location.apply_year or 0,
            applicant=location.applicant_name or "",
            department=None,  # GrantLocations 中沒有此欄位
            approved_area=approved_area,
            land_registered_area=land_registered_area,
            crops=crops,
            is_aboriginal_area=is_aboriginal_area,
            office_boundaries=office_boundaries_data,
            data_format_warning=data_format_warning,
        )

    @staticmethod
    def _select_representative_location(locations: List[GrantLocations]) -> GrantLocations:
        """從同一組 (source_id + land_section + land_number) 的記錄中選擇代表記錄"""
        if len(locations) == 1:
            return locations[0]
        
        # 選擇策略：優先選擇有更多 meta_data 資訊的記錄
        best_location = locations[0]
        best_score = 0
        
        for location in locations:
            score = 0
            
            # meta_data 資訊完整性評分
            if location.meta_data:
                score += len(location.meta_data) * 2  # meta_data 鍵值數量
                
                # 特別重要的欄位給予額外分數
                if location.meta_data.get('finalarea'):
                    score += 10
                if location.meta_data.get('farmarea'):
                    score += 10
                if location.meta_data.get('facility_area'):
                    score += 10
                if location.meta_data.get('land_area'):
                    score += 10
            
            # 其他欄位完整性評分
            if location.case_number:
                score += 5
            if location.applicant_name:
                score += 5
            if location.case_status:
                score += 3
            if location.comment:
                score += 2
            
            # 更新時間越新得分越高（以秒為單位的微調）
            if location.updated_at:
                score += location.updated_at.timestamp() / 1000000  # 微調分數
            
            if score > best_score:
                best_score = score
                best_location = location
        
        return best_location

    @staticmethod
    async def _infer_legacy_case_type(source_id: str) -> str:
        """從 grant_versions.all_steps_data.pay_detail 推斷歷史案件類型（包含所有有金額的項目）"""
        try:
            grant_version = await GrantVersions.filter(version=source_id).first()
            if grant_version and grant_version.all_steps_data and isinstance(grant_version.all_steps_data, dict):
                pay_detail = grant_version.all_steps_data.get('pay_detail', {})
                
                # 收集所有有金額的設施類型
                facility_types = []
                
                if pay_detail.get('pipe_facility') and pay_detail['pipe_facility'] > 0:
                    facility_types.append("田間管路")
                if pay_detail.get('power_facility') and pay_detail['power_facility'] > 0:
                    facility_types.append("動力設備")
                if pay_detail.get('control_facility') and pay_detail['control_facility'] > 0:
                    facility_types.append("調控設施")
                if pay_detail.get('storage_facility') and pay_detail['storage_facility'] > 0:
                    facility_types.append("調蓄設施")
                
                # 如果有找到設施類型，用逗號連接返回
                if facility_types:
                    return ", ".join(facility_types)
                
        except Exception as e:
            # 非預期例外，記錄診斷後降級回傳預設值（"歷史案件"）
            logger.warning(
                "[_infer_legacy_case_type] 推斷案件類型失敗（source_id=%s）：%s",
                source_id, str(e),
            )

        # 如果無法判斷或發生錯誤，回傳歷史案件作為預設值
        return "歷史案件"

    @staticmethod
    def _infer_case_type_from_crops(crops: Optional[List[Dict[str, str]]]) -> str:
        """從作物資訊推斷案件類型"""
        if not crops:
            return "一般設施"
        
        # 根據作物類型推斷設施類型
        crop_categories = [crop.get('category', '') for crop in crops]
        
        if any('果樹' in category for category in crop_categories):
            return "田間管路"  # 果樹通常需要田間管路
        elif any('糧食' in category for category in crop_categories):
            return "調控設施"  # 糧食作物通常需要調控設施
        else:
            return "一般設施"

    @staticmethod
    def _calculate_area_statistics(case_items: List[GrantCaseItem]) -> AreaStatistics:
        """
        計算面積統計 - 7項核心指標
        使用 Decimal 確保精度
        """
        if not case_items:
            return AreaStatistics(
                land_total_area=Decimal('0.00'),
                used_area=Decimal('0.00'),
                remaining_area=Decimal('0.00'),
                micro_irrigation_area=Decimal('0.00'),
                remaining_micro_area=Decimal('0.00'),
                sprinkler_area=Decimal('0.00'),
                remaining_sprinkler_area=Decimal('0.00')
            )
        
        # 統計各類面積
        total_used_area = sum(item.approved_area for item in case_items)
        
        # 按案件類型分類統計
        micro_irrigation_area = sum(
            item.approved_area for item in case_items 
            if item.case_type in ["田間管路", "微灌設施"]
        )
        
        sprinkler_area = sum(
            item.approved_area for item in case_items
            if item.case_type in ["調控設施", "噴水設施"]
        )
        
        # 假設土地總面積 (實際應該從地籍資料獲取)
        # 這裡使用最大單筆面積的3倍作為估算
        max_area = max((item.approved_area for item in case_items), default=Decimal('0'))
        estimated_total_area = max_area * Decimal('3')
        
        return AreaStatistics(
            land_total_area=estimated_total_area,
            used_area=total_used_area,
            remaining_area=max(estimated_total_area - total_used_area, Decimal('0')),
            micro_irrigation_area=micro_irrigation_area,
            remaining_micro_area=max(estimated_total_area * Decimal('0.6') - micro_irrigation_area, Decimal('0')),
            sprinkler_area=sprinkler_area,
            remaining_sprinkler_area=max(estimated_total_area * Decimal('0.8') - sprinkler_area, Decimal('0'))
        )

    @staticmethod
    def _build_location_description(request: QualificationSearchRequest) -> str:
        """建立地區描述文字"""
        params = request.params
        parts = []
        
        # 只添加非 None 的值到描述中
        if params.county:
            parts.append(params.county)
        if params.town:
            parts.append(params.town)
        if params.section:
            parts.append(params.section)
        if params.land_number:
            parts.append(params.land_number)
            
        return " ".join(parts) if parts else "未指定地區"

    @staticmethod
    async def _query_office_boundaries_for_location(location: GrantLocations) -> Optional[List[Dict[str, Any]]]:
        """
        根據單一地號資訊查詢 office_boundaries 交集
        使用 PostGIS 空間查詢功能
        """
        try:
            from tortoise import connections
            
            # 使用原生 SQL 直接查詢 grant_locations.geom 欄位進行空間交集
            connection = connections.get("default")
            
            # PostGIS 空間交集查詢：grant_locations.geom 與 office_boundaries.geom
            # 需要坐標系統轉換：4326 (WGS84) -> 3824 (TWD97 TM2)
            sql_query = """
            SELECT ob.gid, ob.ia_code, ob.ia_name, ob.mng_code, ob.mng_name, 
                   ob.stn_code, ob.stn_name, ob.grp_code, ob.grp_name, 
                   ob.area, ob.record_date, ob.sg, ob.stngrp, ob.part
            FROM office_boundaries ob, grant_locations gl
            WHERE gl.id = $1 
              AND gl.geom IS NOT NULL
              AND ST_Intersects(ST_Transform(gl.geom, 3824), ob.geom)
            ORDER BY ob.ia_code, ob.stn_code, ob.grp_code
            """
            
            results = await connection.execute_query(sql_query, [location.id])
            
            # 轉換查詢結果
            boundaries = []
            for row in results[1]:  # results[1] 是資料行
                boundary_data = {
                    'gid': row[0],
                    'ia_code': row[1],
                    'ia_name': row[2],
                    'mng_code': row[3],
                    'mng_name': row[4],
                    'stn_code': row[5],
                    'stn_name': row[6],
                    'grp_code': row[7],
                    'grp_name': row[8],
                    'area': row[9],
                    'record_date': row[10].isoformat() if row[10] else None,
                    'sg': row[11],
                    'stngrp': row[12],
                    'part': row[13]
                }
                boundaries.append(boundary_data)
            
            return boundaries if boundaries else None
            
        except Exception as e:
            # 記錄錯誤但不中斷主要查詢流程
            print(f"Office boundaries query failed for location {location.id}: {e}")
            return None

    @staticmethod
    async def _save_query_record(
        request: QualificationSearchRequest,
        results: List[GrantCaseItem],
        statistics: Optional[AreaStatistics],
        metadata: ResponseMetadata
    ) -> None:
        """儲存查詢記錄用於快取和分析"""
        try:
            await QualificationQuery.create(
                query_type=request.query_type,
                location_data=request.params.model_dump(),
                query_options=request.options.model_dump() if request.options else {},
                search_results=[
                    {**item.model_dump(), 
                     'approved_area': float(item.approved_area),
                     'land_registered_area': float(item.land_registered_area) if item.land_registered_area else None}
                    for item in results[:10]
                ],  # 只儲存前10筆避免資料過大，並轉換 Decimal 為 float
                area_statistics={
                    **statistics.model_dump(),
                    'land_total_area': float(statistics.land_total_area),
                    'used_area': float(statistics.used_area),
                    'remaining_area': float(statistics.remaining_area),
                    'micro_irrigation_area': float(statistics.micro_irrigation_area),
                    'remaining_micro_area': float(statistics.remaining_micro_area),
                    'sprinkler_area': float(statistics.sprinkler_area),
                    'remaining_sprinkler_area': float(statistics.remaining_sprinkler_area)
                } if statistics else None,
                result_count=metadata.total_records,
                query_hash=metadata.query_hash,
                response_time_ms=metadata.response_time_ms
            )
        except Exception as e:
            # 查詢記錄儲存失敗不應影響主要功能
            print(f"Failed to save query record: {e}")

    # === 區域驗證相關方法 ===
    
    @staticmethod
    async def check_indigenous_area(request: AreaCheckRequest) -> AreaCheckResponse:
        """檢查是否為原住民鄉 - 使用現有的 Towns 模型"""
        try:
            # 先查找縣市
            county = await Counties.filter(name=request.county).first()
            if not county:
                return AreaCheckResponse(is_qualified=False, area_type='general')
            
            # 查找原住民鄉鎮
            town = await Towns.filter(
                county=county,
                name=request.town,
                is_indigenous=True
            ).first()
            
            if not town:
                return AreaCheckResponse(is_qualified=False, area_type='general')
            
            # 判斷原民鄉類型
            indigenous_type = "mountain" if town.indigenous_type == "1" else "plain"
            
            return AreaCheckResponse(
                is_qualified=True,
                area_type="indigenous",
                details={
                    "category": indigenous_type,
                    "town_name": town.name,
                    "indigenous_type": town.indigenous_type
                }
            )
            
        except DoesNotExist:
            return AreaCheckResponse(
                is_qualified=False,
                area_type="general",
                details=None
            )

    @staticmethod
    async def check_slope_area(request: AreaCheckRequest) -> AreaCheckResponse:
        """檢查是否為山坡地 - 暫時實現，可後續擴展"""
        # 暫時實現：基於鄉鎮名稱的簡單判斷
        # 實際應該要有專門的山坡地資料庫或與地理資訊系統整合
        slope_keywords = ["山地", "山區", "高山", "山坡", "梨山", "阿里山"]
        
        is_slope = any(keyword in request.town for keyword in slope_keywords)
        
        return AreaCheckResponse(
            is_qualified=is_slope,
            area_type="slope" if is_slope else "general",
            details={
                "detection_method": "keyword_based",
                "note": "基於地名關鍵字判斷，實際應整合專門的山坡地資料庫"
            } if is_slope else None
        )

    # === 輔助方法 ===
    
    @staticmethod
    async def _get_available_years() -> List[str]:
        """動態獲取資料庫中實際存在的年度範圍"""
        try:
            # 查詢資料庫中實際存在的年度範圍
            years_data = await GrantLocations.all().distinct().values_list('apply_year', flat=True)
            
            # 過濾掉 None 值並轉換為字串，然後排序
            available_years = sorted([
                str(year) for year in years_data 
                if year is not None and isinstance(year, int)
            ], reverse=True)  # 降序排列，最新年度在前
            
            # 如果資料庫沒有資料，回退到預設範圍
            if not available_years:
                # 動態計算：從97年到當前民國年
                from datetime import datetime
                current_roc_year = datetime.now().year - 1911
                available_years = [str(i) for i in range(current_roc_year, 96, -1)]  # 倒序
                
            return available_years
            
        except Exception as e:
            # 查詢失敗時的回退策略：使用動態計算的預設範圍
            print(f"Failed to get available years from database: {e}")
            from datetime import datetime
            current_roc_year = datetime.now().year - 1911
            return [str(i) for i in range(current_roc_year, 96, -1)]  # 97年到當前年度，倒序
    
    # === 查詢優化相關方法 ===
    
    @staticmethod
    async def get_cached_query(query_hash: str) -> Optional[QualificationResponse]:
        """獲取快取的查詢結果"""
        try:
            cached_query = await QualificationQuery.filter(query_hash=query_hash).order_by('-created_at').first()
            
            if not cached_query:
                return None
            
            # 檢查快取是否過期 (例如: 10分鐘)
            cache_age = (timezone.now() - cached_query.created_at).total_seconds()
            if cache_age > 600:  # 10分鐘快取
                return None
            
            # 重建回應物件
            # 這裡需要從快取資料重建 QualificationResponse
            # 簡化實現，實際使用時需要完整重建
            return None  # 暫時不實現快取機制
            
        except DoesNotExist:
            return None

    @staticmethod
    def _filter_by_county_town(locations: List[GrantLocations], county: Optional[str], town: Optional[str]) -> List[GrantLocations]:
        """
        根據縣市和鄉鎮資訊過濾查詢結果
        檢查 meta_data 中的縣市和鄉鎮資訊
        """
        if not locations or (not county and not town):
            return locations

        filtered_locations = []

        for location in locations:
            if not location.meta_data:
                # 沒有 meta_data，容錯保留此記錄（向後相容）。
                # 缺名稱的診斷 log 與逐案件警告旗標由 _convert_to_case_item 統一評估（見 _has_incomplete_county_town），
                # 本函式僅負責過濾時的容錯保留，兩處判斷獨立但一致、互不干擾。
                filtered_locations.append(location)
                continue

            # 檢查 meta_data 中的縣市和鄉鎮資訊
            meta_county = location.meta_data.get('county')
            meta_town = location.meta_data.get('town')

            # 縣市比對
            county_match = True
            if county:
                if meta_county:
                    # 支援部分匹配，例如 "台中市" 可以匹配 "臺中市"
                    county_normalized = county.replace('台', '臺')
                    meta_county_normalized = str(meta_county).replace('台', '臺')
                    county_match = (county_normalized in meta_county_normalized or
                                  meta_county_normalized in county_normalized)
                else:
                    # meta_data 無縣市名稱，容錯保留此記錄（診斷與警告旗標於 _convert_to_case_item 統一處理）
                    county_match = True

            # 鄉鎮比對
            town_match = True
            if town:
                if meta_town:
                    # 正規化鄉鎮名稱：處理台/臺的字元差異
                    town_normalized = town.replace('台', '臺')
                    meta_town_normalized = str(meta_town).replace('台', '臺')
                    town_match = (town_normalized in meta_town_normalized or
                                meta_town_normalized in town_normalized)
                else:
                    # meta_data 無鄉鎮名稱，容錯保留此記錄（診斷與警告旗標於 _convert_to_case_item 統一處理）
                    town_match = True

            # 同時滿足縣市和鄉鎮條件才保留
            if county_match and town_match:
                filtered_locations.append(location)

        return filtered_locations