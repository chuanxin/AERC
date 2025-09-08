"""
Qualification 重複案件查詢系統的 CRUD 操作
基於現有的 GrantLocations 實現查詢邏輯
"""

from typing import List, Optional, Dict
from decimal import Decimal
import hashlib
from datetime import datetime

from tortoise.exceptions import DoesNotExist
from tortoise import timezone
from tortoise.expressions import Q

from ..database.geo_models import GrantLocations
from ..database.models import QualificationQuery, QualificationQueryType, Towns, Counties
from ..schemas.qualification import (
    QualificationSearchRequest, GrantCaseItem, AreaStatistics,
    QueryInfo, ResponseMetadata, QualificationResponse,
    AreaCheckRequest, AreaCheckResponse
)


class QualificationCRUD:
    """重複案件查詢的 CRUD 操作類 - 遵循 Linus 簡潔原則"""

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
        
        # 3. 轉換為統一格式
        case_items = []
        for location in grant_locations:
            case_item = await QualificationCRUD._convert_to_case_item(location)
            case_items.append(case_item)
        
        # 4. 計算面積統計
        statistics = None
        if request.options and request.options.include_statistics:
            statistics = QualificationCRUD._calculate_area_statistics(case_items)
        
        # 5. 建立回應
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
        
        # 6. 儲存查詢記錄 (可選的快取機制)
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
            # 一般查詢: 優先使用地號查詢，縣市鄉鎮為輔助篩選
            if request.params.land_number:
                conditions &= Q(land_number__iexact=request.params.land_number)
            
            # 可選的地區篩選條件 (當用戶有提供時才使用)
            if request.params.county:
                # 這裡需要與地址欄位比對，或者建立縣市對應關係
                pass  # 暫時跳過，因為 GrantLocations 中沒有直接的縣市欄位
            
            if request.params.section:
                conditions &= Q(land_section__icontains=request.params.section)
                
        elif request.query_type in [QualificationQueryType.INDIGENOUS, QualificationQueryType.SLOPE]:
            # 原民鄉/山坡地查詢: 地段名稱模糊搜尋
            if request.params.land_number:
                conditions &= Q(land_number__iexact=request.params.land_number)
            if request.params.section:
                conditions &= Q(land_section__icontains=request.params.section)
        
        # 排除草稿狀態(可能不完整) - 所有查詢共通邏輯
        conditions &= ~Q(case_status="draft")
        
        return conditions

    @staticmethod
    async def _convert_to_case_item(location: GrantLocations) -> GrantCaseItem:
        """將 GrantLocations 轉換為統一的 GrantCaseItem 格式"""
        # 解析 meta_data 獲取面積資訊
        approved_area = Decimal('0.00')
        crops = None
        is_aboriginal_area = None
        case_type = "一般設施"  # 預設值
        
        if location.meta_data:
            if location.source_system == "legacy_farmdata":
                # 歷史資料格式
                approved_area = Decimal(str(location.meta_data.get('finalarea', 0)))
                case_type = "歷史案件"
                
            elif location.source_system == "new_aerc":
                # 新系統資料格式
                facility_area = location.meta_data.get('facility_area', '0')
                approved_area = Decimal(str(facility_area))
                crops = location.meta_data.get('crops', [])
                is_aboriginal_area = location.meta_data.get('is_aboriginal_area')
                case_type = QualificationCRUD._infer_case_type_from_crops(crops)
        
        return GrantCaseItem(
            id=location.id,
            source_system=location.source_system,
            grant_id=str(location.source_id),
            case_number=location.case_number,
            case_type=case_type,
            status=location.case_status,
            land_section=location.land_section or "",
            land_number=location.land_number or "",
            application_year=location.apply_year or 0,
            applicant=location.applicant_name or "",
            department=None,  # GrantLocations 中沒有此欄位
            approved_area=approved_area,
            crops=crops,
            is_aboriginal_area=is_aboriginal_area
        )

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
                search_results=[item.model_dump() for item in results[:10]],  # 只儲存前10筆避免資料過大
                area_statistics=statistics.model_dump() if statistics else None,
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
            county = await Counties.get(name=request.county)
            
            # 查找原住民鄉鎮
            town = await Towns.get(
                county=county,
                name=request.town,
                is_indigenous=True
            )
            
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
            cached_query = await QualificationQuery.get(query_hash=query_hash)
            
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