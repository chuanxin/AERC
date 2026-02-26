"""
Grant Statistics CRUD Operations
補助案件統計查詢的業務邏輯層 - 即時計算統計資料
"""

from typing import List, Optional
from decimal import Decimal

from ..database.models import Grants, GrantVersions, Offices, SubsidyAnnualBudget, Counties, Towns
from ..schemas.statistics import (
    ExecutionProgressResponse,
    OfficeExecutionStats,
    BudgetAnalysisResponse,
    OfficeBudgetStats,
    CountyTownStats,
    OfficeSummaryStats,
    CountyTownStatsResponse,
    OfficeSummaryStatsResponse,
    YearMetrics,
    CountyTownYearlyRow,
    CountyTownYearlyStatsResponse,
    OfficeSummaryYearlyRow,
    OfficeSummaryYearlyStatsResponse,
    CountyManagementAreaStats,
    OfficeManagementAreaStats,
    CountyManagementAreaStatsResponse,
    OfficeManagementAreaStatsResponse,
)

# 允許查詢的管理處 ID 清單（與前端 ALLOWED_OFFICE_IDS 保持一致）
ALLOWED_OFFICE_IDS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 23]

# 管理區類型常數
MANAGEMENT_AREA_INSIDE = "inside"
MANAGEMENT_AREA_OUTSIDE = "outside"


class GrantStatisticsCRUD:
    """補助案件統計的 CRUD 操作類"""

    @staticmethod
    def _calculate_grant_subsidy(grant) -> tuple:
        """
        計算單一案件的補助面積與補助金額

        從 grant.active_version.all_steps_data 提取面積和補助金額，
        與 step6.vue「農戶補助明細」邏輯一致。

        Returns:
            tuple[Decimal, Decimal]: (total_area, total_subsidy)
        """
        total_area = Decimal('0')
        total_subsidy = Decimal('0')

        if not grant.active_version:
            return total_area, total_subsidy

        all_steps_data = grant.active_version.all_steps_data or {}
        steps = all_steps_data.get('steps', {})

        # 提取施設面積資料（從 steps['2'].lands[].facilityAreaHa）
        step2_data = steps.get('2', {})
        lands = step2_data.get('lands', [])
        for land in lands:
            facility_area_ha = Decimal(str(land.get('facilityAreaHa', 0) or 0))
            total_area += facility_area_ha

        # 補助款 = A項補助（田間管路） + B項補助（調控設施） + 規劃設計費補助
        step4_data = steps.get('4', {})  # step3.vue → steps['4']
        step5_data = steps.get('5', {})  # step4.vue → steps['5']

        # 計算管路材料成本
        pipeline_material_cost = Decimal('0')

        # 主管1成本
        if step5_data.get('mainPipeQuantity') and step5_data.get('mainPipeUnitPrice'):
            pipeline_material_cost += (
                Decimal(str(step5_data.get('mainPipeQuantity', 0) or 0)) *
                Decimal(str(step5_data.get('mainPipeUnitPrice', 0) or 0))
            )

        # 主管2成本
        if step5_data.get('mainPipe2Quantity') and step5_data.get('mainPipe2UnitPrice'):
            pipeline_material_cost += (
                Decimal(str(step5_data.get('mainPipe2Quantity', 0) or 0)) *
                Decimal(str(step5_data.get('mainPipe2UnitPrice', 0) or 0))
            )

        # 灌溉系統成本
        pipes = step5_data.get('pipes', [])
        if isinstance(pipes, list):
            for pipe in pipes:
                group_id = pipe.get('groupId')
                module = pipe.get('module', '')
                if group_id in [2, 3, 4, 5, 6, 7, 8] or (group_id == 1 and module != '主管'):
                    total_price = pipe.get('totalPrice', 0)
                    if isinstance(total_price, (int, float)):
                        pipeline_material_cost += Decimal(str(total_price))
                    else:
                        pipeline_material_cost += Decimal(str(total_price or 0))

        # 工作費
        work_fee = step5_data.get('workFee', 0)
        if isinstance(work_fee, (int, float)):
            pipeline_material_cost += Decimal(str(work_fee))
        else:
            pipeline_material_cost += Decimal(str(int(work_fee or 0)))

        # 取得補助和設計費資料
        subsidy_amount = Decimal(str(step5_data.get('subsidyAmount', 0) or 0))
        design_fee_amount = Decimal(str(step5_data.get('designFee', 0) or 0))

        # 從 data_schema_version 欄位判斷是否為 legacy 資料
        data_schema_version = grant.active_version.data_schema_version if hasattr(grant.active_version, 'data_schema_version') else None
        is_legacy_data = data_schema_version == 'legacy'

        # A項補助：田間管路設施補助費
        if is_legacy_data:
            pipeline_subsidy = min(pipeline_material_cost, subsidy_amount)
        else:
            pipeline_subsidy = max(Decimal('0'), subsidy_amount - design_fee_amount)

        # B項補助：灌溉調控設施補助費
        facilities = step4_data.get('facilities', [])
        facility_subsidy = Decimal('0')
        if isinstance(facilities, list):
            for facility in facilities:
                facility_subsidy += Decimal(str(facility.get('subsidyAmount', 0) or 0))

        # 規劃設計費補助
        if is_legacy_data:
            design_fee_subsidy = design_fee_amount
        else:
            design_fee_subsidy = min(subsidy_amount, design_fee_amount)

        # 政府補助款總額 = A項 + B項 + 設計費補助
        total_subsidy = pipeline_subsidy + facility_subsidy + design_fee_subsidy

        return total_area, total_subsidy

    @staticmethod
    def _get_management_area_type(grant) -> str:
        """
        判斷案件歸屬管理區內或管理區外

        從 grant.active_version.all_steps_data.steps.2.lands[0].isIrrigationArea 判斷

        Args:
            grant: Grants model instance with active_version prefetched

        Returns:
            str: MANAGEMENT_AREA_INSIDE ("inside") 或 MANAGEMENT_AREA_OUTSIDE ("outside")
        """
        if not grant.active_version:
            return MANAGEMENT_AREA_OUTSIDE

        all_steps_data = grant.active_version.all_steps_data or {}
        steps = all_steps_data.get('steps', {})
        lands = steps.get('2', {}).get('lands', [])

        if not lands:
            # 無土地資料，預設為管理區外
            return MANAGEMENT_AREA_OUTSIDE

        first_land = lands[0]
        is_irrigation_area = first_land.get('isIrrigationArea', False)

        # null 或 False 都視為管理區外，僅 True 視為管理區內
        return MANAGEMENT_AREA_INSIDE if is_irrigation_area is True else MANAGEMENT_AREA_OUTSIDE

    @staticmethod
    async def get_execution_progress(
        year: int,
        office_id: Optional[int] = None,
    ) -> ExecutionProgressResponse:
        """
        取得即時執行進度統計

        純粹的資料查詢層 — 權限控制由 Route 層負責。

        Args:
            year: 統計年度（民國年）
            office_id: 辦公室 ID（None=查詢所有辦公室，有值=查詢指定辦公室）

        Returns:
            ExecutionProgressResponse: 執行進度統計資料
        """
        # 根據 office_id 決定查詢範圍
        if office_id is not None:
            offices = await Offices.filter(id=office_id).all()
        else:
            # 當 office_id 為 None 時，查詢 ALLOWED_OFFICE_IDS 中的所有辦公室
            # 注意：這裡包含 ID 為 1-19 和 23 的辦公室
            offices = await Offices.filter(id__in=ALLOWED_OFFICE_IDS).order_by('id').all()

        # 3. 建立縣市鄉鎮查詢表（一次查詢，傳入所有子方法）
        county_lookup, town_lookup = await GrantStatisticsCRUD._build_county_town_lookup()

        # 4. 為每個辦公室計算統計資料
        office_stats_list = []
        total_approved_budget = Decimal('0')
        total_completed_cases = 0
        total_area = Decimal('0')
        total_subsidy = Decimal('0')

        for office in offices:
            stats = await GrantStatisticsCRUD._calculate_office_execution_stats(
                year=year,
                office_id=office.id,
                office_name=office.name,
                county_lookup=county_lookup,
                town_lookup=town_lookup,
            )
            office_stats_list.append(stats)

            total_approved_budget += stats.approved_budget
            total_completed_cases += stats.completed_cases
            total_area += stats.total_area
            total_subsidy += stats.total_subsidy

        # 4. 計算整體執行率
        overall_execution_rate = Decimal('0')
        if total_approved_budget > 0:
            overall_execution_rate = (total_subsidy / total_approved_budget) * 100

        # 5. 建立回應
        return ExecutionProgressResponse(
            year=year,
            offices=office_stats_list,
            total_approved_budget=total_approved_budget,
            total_completed_cases=total_completed_cases,
            total_area=total_area,
            total_subsidy=total_subsidy,
            overall_execution_rate=overall_execution_rate
        )

    @staticmethod
    async def _calculate_office_execution_stats(
        year: int,
        office_id: int,
        office_name: str,
        county_lookup: dict,
        town_lookup: dict,
    ) -> OfficeExecutionStats:
        """
        計算單一辦公室的執行進度統計

        Args:
            year: 統計年度
            office_id: 辦公室 ID
            office_name: 辦公室名稱
            county_lookup: 縣市名稱查詢表（由父方法傳入）
            town_lookup: 鄉鎮區名稱查詢表（由父方法傳入）

        Returns:
            OfficeExecutionStats: 辦公室統計資料
        """
        # 1. 從 SubsidyAnnualBudget 取得核定預算
        annual_budget = await SubsidyAnnualBudget.filter(
            year=year,
            office_id=office_id
        ).first()

        approved_budget = annual_budget.approved_budget if annual_budget else Decimal('0')

        # 2. 查詢已結案案件（completed + submitted）
        # completed: 線上結案（含所有 legacy 歷史案件）
        # submitted: 已結案並完成文件上傳的完整封存狀態
        completed_grants = await Grants.filter(
            year=year,
            office_id=office_id,
            status__in=['completed', 'submitted']
        ).prefetch_related('active_version').all()

        completed_cases = 0
        total_area = Decimal('0')
        total_subsidy = Decimal('0')

        # 3. 從 all_steps_data 提取面積和補助金額（使用共用計算方法）
        for grant in completed_grants:
            if not grant.active_version:
                continue
            
            # 🔥 與 A02 系列保持一致：只統計有有效土地縣市資料的案件
            all_steps_data = grant.active_version.all_steps_data or {}
            steps = all_steps_data.get('steps', {})
            lands = steps.get('2', {}).get('lands', [])
            
            c_id, _, _, _ = GrantStatisticsCRUD._find_first_valid_county_town(
                lands, county_lookup, town_lookup
            )
            if c_id is None:  # 跳過沒有有效土地資料的案件
                continue
            
            grant_area, grant_subsidy = GrantStatisticsCRUD._calculate_grant_subsidy(grant)
            completed_cases += 1
            total_area += grant_area
            total_subsidy += grant_subsidy

        # 4. 計算執行率
        execution_rate = Decimal('0')
        if approved_budget > 0:
            execution_rate = (total_subsidy / approved_budget) * 100

        return OfficeExecutionStats(
            office_id=office_id,
            office_name=office_name,
            approved_budget=approved_budget,
            completed_cases=completed_cases,
            total_area=total_area,
            total_subsidy=total_subsidy,
            execution_rate=execution_rate
        )

    @staticmethod
    async def get_budget_analysis(
        year: int,
        office_id: Optional[int] = None,
    ) -> BudgetAnalysisResponse:
        """
        取得即時經費統計分析

        純粹的資料查詢層 — 權限控制由 Route 層負責。

        Args:
            year: 統計年度（民國年）
            office_id: 辦公室 ID（None=查詢所有辦公室，有值=查詢指定辦公室）

        Returns:
            BudgetAnalysisResponse: 經費統計分析資料
        """
        # 根據 office_id 決定查詢範圍
        if office_id is not None:
            offices = await Offices.filter(id=office_id).all()
        else:
            # 當 office_id 為 None 時，查詢 ALLOWED_OFFICE_IDS 中的所有辦公室
            offices = await Offices.filter(id__in=ALLOWED_OFFICE_IDS).order_by('id').all()

        # 3. 建立縣市鄉鎮查詢表（一次查詢，傳入所有子方法）
        county_lookup, town_lookup = await GrantStatisticsCRUD._build_county_town_lookup()

        # 4. 為每個辦公室計算統計資料
        office_stats_list = []
        total_planned_area = Decimal('0')
        total_planned_budget = Decimal('0')
        total_budgeted_subsidy = Decimal('0')
        total_unbudgeted_subsidy = Decimal('0')
        total_verified_amount = Decimal('0')
        total_verified_area = Decimal('0')

        for office in offices:
            stats = await GrantStatisticsCRUD._calculate_office_budget_stats(
                year=year,
                office_id=office.id,
                office_name=office.name,
                county_lookup=county_lookup,
                town_lookup=town_lookup,
            )
            office_stats_list.append(stats)

            total_planned_area += stats.planned_area
            total_planned_budget += stats.planned_budget
            total_budgeted_subsidy += stats.budgeted_subsidy
            total_unbudgeted_subsidy += stats.unbudgeted_subsidy
            total_verified_amount += stats.verified_amount
            total_verified_area += stats.verified_area

        # 4. 計算整體執行率
        overall_area_execution_rate = Decimal('0')
        overall_budget_execution_rate = Decimal('0')

        if total_planned_area > 0:
            # 已編預算面積 / 預定執行面積
            overall_area_execution_rate = (total_verified_area / total_planned_area) * 100

        if total_planned_budget > 0:
            # 已編列補助款 / 預定執行預算
            overall_budget_execution_rate = (total_budgeted_subsidy / total_planned_budget) * 100

        # 5. 建立回應
        return BudgetAnalysisResponse(
            year=year,
            offices=office_stats_list,
            total_planned_area=total_planned_area,
            total_planned_budget=total_planned_budget,
            total_budgeted_subsidy=total_budgeted_subsidy,
            total_unbudgeted_subsidy=total_unbudgeted_subsidy,
            total_verified_amount=total_verified_amount,
            overall_area_execution_rate=overall_area_execution_rate,
            overall_budget_execution_rate=overall_budget_execution_rate
        )

    @staticmethod
    async def _calculate_office_budget_stats(
        year: int,
        office_id: int,
        office_name: str,
        county_lookup: dict,
        town_lookup: dict,
    ) -> OfficeBudgetStats:
        """
        計算單一辦公室的經費統計分析

        Args:
            year: 統計年度
            office_id: 辦公室 ID
            office_name: 辦公室名稱
            county_lookup: 縣市名稱查詢表（由父方法傳入）
            town_lookup: 鄉鎮區名稱查詢表（由父方法傳入）

        Returns:
            OfficeBudgetStats: 辦公室經費統計資料
        """
        # 1. 從 SubsidyAnnualBudget 取得預定執行面積和預算
        # 🔥 容錯處理：如果表不存在，使用預設值（適用於尚未執行遷移的生產環境）
        try:
            annual_budget = await SubsidyAnnualBudget.filter(
                year=year,
                office_id=office_id
            ).first()

            planned_area = annual_budget.approved_area if annual_budget else Decimal('0')
            planned_budget = annual_budget.approved_budget if annual_budget else Decimal('0')
        except Exception as e:
            # 表不存在或查詢失敗時，使用預設值
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to query SubsidyAnnualBudget for year={year}, office_id={office_id}: {e}")
            planned_area = Decimal('0')
            planned_budget = Decimal('0')

        # 2. 查詢已編預算案件（狀態非 rejected, withdrawn, deleted）
        # 🔥 統一實作：排除無效狀態，計算有效案件的統計數據
        budgeted_grants = await Grants.filter(
            year=year,
            office_id=office_id
        ).exclude(
            status__in=['rejected', 'withdrawn', 'deleted']
        ).prefetch_related('active_version').all()

        budgeted_cases = 0
        budgeted_area = Decimal('0')
        budgeted_subsidy = Decimal('0')

        # 使用共用計算方法
        for grant in budgeted_grants:
            if not grant.active_version:
                continue
            
            # 🔥 與其他統計報表保持一致：只統計有有效土地縣市資料的案件
            all_steps_data = grant.active_version.all_steps_data or {}
            steps = all_steps_data.get('steps', {})
            lands = steps.get('2', {}).get('lands', [])
            
            c_id, _, _, _ = GrantStatisticsCRUD._find_first_valid_county_town(
                lands, county_lookup, town_lookup
            )
            if c_id is None:  # 跳過沒有有效土地資料的案件
                continue
            
            grant_area, grant_subsidy = GrantStatisticsCRUD._calculate_grant_subsidy(grant)
            budgeted_cases += 1
            budgeted_area += grant_area
            budgeted_subsidy += grant_subsidy

        # 3. 查詢已驗收案件（status in ['completed', 'submitted']）
        # completed: 線上結案，尚未完成文件上傳
        # submitted: 已結案，並完成文件上傳的完整封存狀態
        verified_grants = await Grants.filter(
            year=year,
            office_id=office_id,
            status__in=['completed', 'submitted']
        ).prefetch_related('active_version').all()

        verified_cases = 0
        verified_area = Decimal('0')
        verified_amount = Decimal('0')

        # 使用共用計算方法
        for grant in verified_grants:
            if not grant.active_version:
                continue
            
            # 🔥 與 A01, A02 系列保持一致：只統計有有效土地縣市資料的案件
            all_steps_data = grant.active_version.all_steps_data or {}
            steps = all_steps_data.get('steps', {})
            lands = steps.get('2', {}).get('lands', [])
            
            c_id, _, _, _ = GrantStatisticsCRUD._find_first_valid_county_town(
                lands, county_lookup, town_lookup
            )
            if c_id is None:  # 跳過沒有有效土地資料的案件
                continue
            
            grant_area, grant_subsidy = GrantStatisticsCRUD._calculate_grant_subsidy(grant)
            verified_cases += 1
            verified_area += grant_area
            verified_amount += grant_subsidy

        # 4. 計算未編列補助款（預定執行預算 - 已編列補助款）
        # 允許負值：當已編列補助款超過預定執行預算時，顯示超支金額
        unbudgeted_subsidy = planned_budget - budgeted_subsidy

        # 5. 計算執行率
        area_execution_rate = Decimal('0')
        budget_execution_rate = Decimal('0')

        if planned_area > 0:
            # 面積執行率 = 已編預算面積 / 預定執行面積
            area_execution_rate = (budgeted_area / planned_area) * 100

        if planned_budget > 0:
            # 計畫執行率 = 已編列補助款 / 預定執行預算
            budget_execution_rate = (budgeted_subsidy / planned_budget) * 100

        return OfficeBudgetStats(
            office_id=office_id,
            office_name=office_name,
            planned_area=planned_area,
            planned_budget=planned_budget,
            budgeted_cases=budgeted_cases,
            budgeted_area=budgeted_area,
            budgeted_subsidy=budgeted_subsidy,
            unbudgeted_subsidy=unbudgeted_subsidy,
            verified_cases=verified_cases,
            verified_area=verified_area,
            verified_amount=verified_amount,
            area_execution_rate=area_execution_rate,
            budget_execution_rate=budget_execution_rate
        )

    # ==================== A02 系列統計報表 ====================

    @staticmethod
    async def get_office_summary_stats(
        year: int,
        office_id: Optional[int] = None,
    ) -> OfficeSummaryStatsResponse:
        """
        A02-2: 取得各管理處統計資料（案件數 + 面積 + 金額）

        Args:
            year: 統計年度（民國年）
            office_id: 管理處 ID（None=全部）
        """
        # 查詢已結案案件
        query = Grants.filter(
            year=year,
            status__in=['completed', 'submitted']
        )
        if office_id is not None:
            query = query.filter(office_id=office_id)
        else:
            query = query.filter(office_id__in=ALLOWED_OFFICE_IDS)

        grants = await query.prefetch_related('active_version').all()

        # 取得管理處名稱
        office_ids = ALLOWED_OFFICE_IDS if office_id is None else [office_id]
        offices = await Offices.filter(id__in=office_ids).all()
        office_name_map = {o.id: o.name for o in offices}

        # 🔥 建立縣市鄉鎮查詢表（用於驗證土地資料完整性）
        county_lookup, town_lookup = await GrantStatisticsCRUD._build_county_town_lookup()

        # 按管理處彙總
        office_data: dict = {}
        for grant in grants:
            if not grant.active_version:
                continue
            
            # 🔥 與 A02-1, A02-3 保持一致：只統計有有效土地縣市資料的案件
            all_steps_data = grant.active_version.all_steps_data or {}
            steps = all_steps_data.get('steps', {})
            lands = steps.get('2', {}).get('lands', [])
            
            c_id, _, _, _ = GrantStatisticsCRUD._find_first_valid_county_town(
                lands, county_lookup, town_lookup
            )
            if c_id is None:  # 跳過沒有有效土地資料的案件
                continue
            
            oid = grant.office_id
            if oid not in office_data:
                office_data[oid] = {'cases': 0, 'area': Decimal('0'), 'subsidy': Decimal('0')}
            grant_area, grant_subsidy = GrantStatisticsCRUD._calculate_grant_subsidy(grant)
            office_data[oid]['cases'] += 1
            office_data[oid]['area'] += grant_area
            office_data[oid]['subsidy'] += grant_subsidy

        # 按 ALLOWED_OFFICE_IDS 順序建立統計列表
        stats = []
        total_cases = 0
        total_area = Decimal('0')
        total_subsidy = Decimal('0')

        for oid in ALLOWED_OFFICE_IDS:
            if office_id is not None and oid != office_id:
                continue
            if oid not in office_name_map:
                continue
            data = office_data.get(oid, {'cases': 0, 'area': Decimal('0'), 'subsidy': Decimal('0')})
            stats.append(OfficeSummaryStats(
                office_id=oid,
                office_name=office_name_map[oid],
                completed_cases=data['cases'],
                total_area=data['area'],
                total_subsidy=data['subsidy'],
            ))
            total_cases += data['cases']
            total_area += data['area']
            total_subsidy += data['subsidy']

        return OfficeSummaryStatsResponse(
            year=year,
            stats=stats,
            total_cases=total_cases,
            total_area=total_area,
            total_subsidy=total_subsidy,
        )

    @staticmethod
    async def _build_county_town_lookup() -> tuple:
        """
        建立縣市/鄉鎮區名稱查詢表

        Returns:
            tuple[dict, dict]: ({county_id: county_name}, {town_id: (town_name, county_id)})
        """
        counties = await Counties.all()
        towns = await Towns.all().prefetch_related('county')
        county_lookup = {c.id: c.name for c in counties}
        town_lookup = {t.id: (t.name, t.county_id) for t in towns}
        return county_lookup, town_lookup

    @staticmethod
    def _find_first_valid_county_town(
        lands: list, county_lookup: dict, town_lookup: dict
    ) -> tuple:
        """
        找到第一筆有效的縣市/鄉鎮區資料

        Returns:
            tuple: (county_id, county_name, town_id, town_name)
                   若全部無效則返回 (None, '', None, '')
        """
        for land in lands:
            land_county = land.get('landCounty')
            land_town = land.get('landTown')
            if land_county and land_town and land_county in county_lookup and land_town in town_lookup:
                return (
                    land_county,
                    county_lookup[land_county],
                    land_town,
                    town_lookup[land_town][0],
                )
        return (None, '', None, '')

    @staticmethod
    async def get_county_town_stats(
        year: int,
        office_id: Optional[int] = None,
    ) -> CountyTownStatsResponse:
        """
        A02-1: 取得各縣市鄉鎮區統計資料

        歸屬規則：
        - 案件數 + 補助面積 + 補助金額 → 全數歸屬至第一筆有效土地的縣市/鄉鎮區
        """
        county_lookup, town_lookup = await GrantStatisticsCRUD._build_county_town_lookup()

        # 查詢已結案案件
        query = Grants.filter(year=year, status__in=['completed', 'submitted'])
        if office_id is not None:
            query = query.filter(office_id=office_id)
        else:
            query = query.filter(office_id__in=ALLOWED_OFFICE_IDS)

        grants = await query.prefetch_related('active_version').all()

        # 按縣市鄉鎮區彙總
        # key = (county_id, town_id)
        ct_data: dict = {}

        for grant in grants:
            if not grant.active_version:
                continue
            all_steps_data = grant.active_version.all_steps_data or {}
            steps = all_steps_data.get('steps', {})
            lands = steps.get('2', {}).get('lands', [])

            grant_area, grant_subsidy = GrantStatisticsCRUD._calculate_grant_subsidy(grant)

            # 案件數 + 面積 + 補助金額 → 全數歸屬至第一筆有效土地
            c_id, c_name, t_id, t_name = GrantStatisticsCRUD._find_first_valid_county_town(
                lands, county_lookup, town_lookup
            )

            if c_id is not None:
                key = (c_id, t_id)
                if key not in ct_data:
                    ct_data[key] = {
                        'county_id': c_id, 'county_name': c_name,
                        'town_id': t_id, 'town_name': t_name,
                        'cases': 0, 'area': Decimal('0'), 'subsidy': Decimal('0'),
                    }
                ct_data[key]['cases'] += 1
                ct_data[key]['area'] += grant_area
                ct_data[key]['subsidy'] += grant_subsidy

        # 排序：county_id ASC, town_id ASC
        sorted_keys = sorted(ct_data.keys())
        stats = []
        total_cases = 0
        total_area = Decimal('0')
        total_subsidy = Decimal('0')

        for key in sorted_keys:
            d = ct_data[key]
            stats.append(CountyTownStats(
                county_id=d['county_id'],
                county_name=d['county_name'],
                town_id=d['town_id'],
                town_name=d['town_name'],
                completed_cases=d['cases'],
                total_area=d['area'],
                total_subsidy=d['subsidy'],
            ))
            total_cases += d['cases']
            total_area += d['area']
            total_subsidy += d['subsidy']

        return CountyTownStatsResponse(
            year=year,
            stats=stats,
            total_cases=total_cases,
            total_area=total_area,
            total_subsidy=total_subsidy,
        )

    @staticmethod
    async def get_county_town_stats_yearly(
        start_year: int,
        end_year: int,
        office_id: Optional[int] = None,
    ) -> CountyTownYearlyStatsResponse:
        """A02-3: 歷年各縣市鄉鎮區統計（橫向年度展開）"""
        county_lookup, town_lookup = await GrantStatisticsCRUD._build_county_town_lookup()

        # ct_data[(c_id, t_id)][year] = {cases, area, subsidy}
        ct_data: dict = {}
        ct_names: dict = {}   # {(c_id, t_id): (c_name, t_name)}
        years_with_data: set = set()

        # 🔥 分年度查詢以避免 SQL 參數超過 32767 限制
        for year in range(start_year, end_year + 1):
            query = Grants.filter(year=year, status__in=['completed', 'submitted'])
            if office_id is not None:
                query = query.filter(office_id=office_id)
            else:
                query = query.filter(office_id__in=ALLOWED_OFFICE_IDS)

            grants = await query.prefetch_related('active_version').all()

            for grant in grants:
                if not grant.active_version:
                    continue
                all_steps_data = grant.active_version.all_steps_data or {}
                steps = all_steps_data.get('steps', {})
                lands = steps.get('2', {}).get('lands', [])

                c_id, c_name, t_id, t_name = GrantStatisticsCRUD._find_first_valid_county_town(
                    lands, county_lookup, town_lookup
                )
                if c_id is None:
                    continue

                grant_area, grant_subsidy = GrantStatisticsCRUD._calculate_grant_subsidy(grant)

                key = (c_id, t_id)
                if key not in ct_data:
                    ct_data[key] = {}
                    ct_names[key] = (c_name, t_name)
                if year not in ct_data[key]:
                    ct_data[key][year] = {'cases': 0, 'area': Decimal('0'), 'subsidy': Decimal('0')}
                ct_data[key][year]['cases'] += 1
                ct_data[key][year]['area'] += grant_area
                ct_data[key][year]['subsidy'] += grant_subsidy
                years_with_data.add(year)

        years = sorted(years_with_data)
        rows = []
        for key in sorted(ct_data.keys()):
            c_name, t_name = ct_names[key]
            year_metrics = [
                YearMetrics(
                    year=y,
                    completed_cases=ct_data[key].get(y, {}).get('cases', 0),
                    total_area=ct_data[key].get(y, {}).get('area', Decimal('0')),
                    total_subsidy=ct_data[key].get(y, {}).get('subsidy', Decimal('0')),
                )
                for y in years
            ]
            rows.append(CountyTownYearlyRow(
                county_id=key[0],
                county_name=c_name,
                town_id=key[1],
                town_name=t_name,
                year_metrics=year_metrics,
            ))

        return CountyTownYearlyStatsResponse(
            start_year=start_year,
            end_year=end_year,
            years=years,
            rows=rows,
        )

    @staticmethod
    async def get_office_summary_stats_yearly(
        start_year: int,
        end_year: int,
        office_id: Optional[int] = None,
    ) -> OfficeSummaryYearlyStatsResponse:
        """A02-4: 歷年各管理處統計（橫向年度展開）"""
        office_ids = ALLOWED_OFFICE_IDS if office_id is None else [office_id]
        offices = await Offices.filter(id__in=office_ids).all()
        office_name_map = {o.id: o.name for o in offices}

        # 🔥 建立縣市鄉鎮查詢表（與 A02-3 保持一致：只統計有有效土地縣市資料的案件）
        county_lookup, town_lookup = await GrantStatisticsCRUD._build_county_town_lookup()

        # office_data[office_id][year] = {cases, area, subsidy}
        office_data: dict = {}
        years_with_data: set = set()

        # 🔥 分年度查詢以避免 SQL 參數超過 32767 限制
        for year in range(start_year, end_year + 1):
            query = Grants.filter(year=year, status__in=['completed', 'submitted'])
            if office_id is not None:
                query = query.filter(office_id=office_id)
            else:
                query = query.filter(office_id__in=ALLOWED_OFFICE_IDS)

            grants = await query.prefetch_related('active_version').all()

            for grant in grants:
                if not grant.active_version:
                    continue

                all_steps_data = grant.active_version.all_steps_data or {}
                steps = all_steps_data.get('steps', {})
                lands = steps.get('2', {}).get('lands', [])

                c_id, _, _, _ = GrantStatisticsCRUD._find_first_valid_county_town(
                    lands, county_lookup, town_lookup
                )
                if c_id is None:
                    continue

                oid = grant.office_id
                grant_area, grant_subsidy = GrantStatisticsCRUD._calculate_grant_subsidy(grant)

                if oid not in office_data:
                    office_data[oid] = {}
                if year not in office_data[oid]:
                    office_data[oid][year] = {'cases': 0, 'area': Decimal('0'), 'subsidy': Decimal('0')}
                office_data[oid][year]['cases'] += 1
                office_data[oid][year]['area'] += grant_area
                office_data[oid][year]['subsidy'] += grant_subsidy
                years_with_data.add(year)

        years = sorted(years_with_data)
        rows = []
        for oid in ALLOWED_OFFICE_IDS:
            if office_id is not None and oid != office_id:
                continue
            if oid not in office_name_map:
                continue
            yd = office_data.get(oid, {})
            year_metrics = [
                YearMetrics(
                    year=y,
                    completed_cases=yd.get(y, {}).get('cases', 0),
                    total_area=yd.get(y, {}).get('area', Decimal('0')),
                    total_subsidy=yd.get(y, {}).get('subsidy', Decimal('0')),
                )
                for y in years
            ]
            rows.append(OfficeSummaryYearlyRow(
                office_id=oid,
                office_name=office_name_map[oid],
                year_metrics=year_metrics,
            ))

        return OfficeSummaryYearlyStatsResponse(
            start_year=start_year,
            end_year=end_year,
            years=years,
            rows=rows,
        )

    # ==================== B01 系列推動成果統計報表（管理區內外分組） ====================

    @staticmethod
    async def get_b01_1_county_management_area_stats(
        year: int,
        office_id: Optional[int] = None,
    ) -> CountyManagementAreaStatsResponse:
        """
        B01-1: 取得各縣市管理區內外統計資料（單年度）

        統計維度：縣市 × 管理區內外（按 isIrrigationArea 欄位）

        Args:
            year: 統計年度（民國年）
            office_id: 管理處 ID（None=全部）

        Returns:
            CountyManagementAreaStatsResponse: 各縣市管理區內外統計
        """
        county_lookup, _ = await GrantStatisticsCRUD._build_county_town_lookup()

        # 查詢已結案案件
        query = Grants.filter(year=year, status__in=['completed', 'submitted'])
        if office_id is not None:
            query = query.filter(office_id=office_id)
        else:
            query = query.filter(office_id__in=ALLOWED_OFFICE_IDS)

        grants = await query.prefetch_related('active_version').all()

        # 按縣市 + 管理區類型彙總
        # key = county_id, value = {"inside": {...}, "outside": {...}}
        county_data: dict = {}

        for grant in grants:
            if not grant.active_version:
                continue

            grant_area, grant_subsidy = GrantStatisticsCRUD._calculate_grant_subsidy(grant)

            # 判斷管理區內/外
            area_type = GrantStatisticsCRUD._get_management_area_type(grant)

            # 取得縣市歸屬（使用第一筆有效土地的縣市）
            all_steps_data = grant.active_version.all_steps_data or {}
            steps = all_steps_data.get('steps', {})
            lands = steps.get('2', {}).get('lands', [])

            c_id, c_name, _, _ = GrantStatisticsCRUD._find_first_valid_county_town(
                lands, county_lookup, {}
            )

            if c_id is not None:
                if c_id not in county_data:
                    county_data[c_id] = {
                        'county_id': c_id,
                        'county_name': c_name,
                        'inside': {'cases': 0, 'area': Decimal('0'), 'subsidy': Decimal('0')},
                        'outside': {'cases': 0, 'area': Decimal('0'), 'subsidy': Decimal('0')},
                    }
                county_data[c_id][area_type]['cases'] += 1
                county_data[c_id][area_type]['area'] += grant_area
                county_data[c_id][area_type]['subsidy'] += grant_subsidy

        # 排序並組織結果
        sorted_county_ids = sorted(county_data.keys())
        stats = []
        total_cases = 0
        total_area = Decimal('0')
        total_subsidy = Decimal('0')

        for c_id in sorted_county_ids:
            d = county_data[c_id]
            stats.append(CountyManagementAreaStats(
                county_id=d['county_id'],
                county_name=d['county_name'],
                inside_cases=d['inside']['cases'],
                inside_area=d['inside']['area'],
                inside_subsidy=d['inside']['subsidy'],
                outside_cases=d['outside']['cases'],
                outside_area=d['outside']['area'],
                outside_subsidy=d['outside']['subsidy'],
            ))
            total_cases += d['inside']['cases'] + d['outside']['cases']
            total_area += d['inside']['area'] + d['outside']['area']
            total_subsidy += d['inside']['subsidy'] + d['outside']['subsidy']

        return CountyManagementAreaStatsResponse(
            year=year,
            stats=stats,
            total_cases=total_cases,
            total_area=total_area,
            total_subsidy=total_subsidy,
        )

    @staticmethod
    async def get_b01_2_office_management_area_stats(
        year: int,
        office_id: Optional[int] = None,
    ) -> OfficeManagementAreaStatsResponse:
        """
        B01-2: 取得各管理處管理區內外統計資料（單年度）

        統計維度：管理處 × 管理區內外（按 isIrrigationArea 欄位）

        Args:
            year: 統計年度（民國年）
            office_id: 管理處 ID（None=全部）

        Returns:
            OfficeManagementAreaStatsResponse: 各管理處管理區內外統計
        """
        # 查詢已結案案件
        query = Grants.filter(year=year, status__in=['completed', 'submitted'])
        if office_id is not None:
            query = query.filter(office_id=office_id)
        else:
            query = query.filter(office_id__in=ALLOWED_OFFICE_IDS)

        grants = await query.prefetch_related('active_version').all()

        # 取得管理處名稱
        office_ids = ALLOWED_OFFICE_IDS if office_id is None else [office_id]
        offices = await Offices.filter(id__in=office_ids).all()
        office_name_map = {o.id: o.name for o in offices}

        # 按管理處 + 管理區類型彙總
        # key = office_id, value = {"inside": {...}, "outside": {...}}
        office_data: dict = {}

        for grant in grants:
            if not grant.active_version:
                continue

            grant_area, grant_subsidy = GrantStatisticsCRUD._calculate_grant_subsidy(grant)

            # 判斷管理區內/外
            area_type = GrantStatisticsCRUD._get_management_area_type(grant)

            o_id = grant.office_id
            if o_id not in office_data:
                office_data[o_id] = {
                    'office_id': o_id,
                    'office_name': office_name_map.get(o_id, f'未知管理處({o_id})'),
                    'inside': {'cases': 0, 'area': Decimal('0'), 'subsidy': Decimal('0')},
                    'outside': {'cases': 0, 'area': Decimal('0'), 'subsidy': Decimal('0')},
                }
            office_data[o_id][area_type]['cases'] += 1
            office_data[o_id][area_type]['area'] += grant_area
            office_data[o_id][area_type]['subsidy'] += grant_subsidy

        # 排序並組織結果
        sorted_office_ids = sorted(office_data.keys())
        stats = []
        total_cases = 0
        total_area = Decimal('0')
        total_subsidy = Decimal('0')

        for o_id in sorted_office_ids:
            d = office_data[o_id]
            stats.append(OfficeManagementAreaStats(
                office_id=d['office_id'],
                office_name=d['office_name'],
                inside_cases=d['inside']['cases'],
                inside_area=d['inside']['area'],
                inside_subsidy=d['inside']['subsidy'],
                outside_cases=d['outside']['cases'],
                outside_area=d['outside']['area'],
                outside_subsidy=d['outside']['subsidy'],
            ))
            total_cases += d['inside']['cases'] + d['outside']['cases']
            total_area += d['inside']['area'] + d['outside']['area']
            total_subsidy += d['inside']['subsidy'] + d['outside']['subsidy']

        return OfficeManagementAreaStatsResponse(
            year=year,
            office_id=office_id,
            stats=stats,
            total_cases=total_cases,
            total_area=total_area,
            total_subsidy=total_subsidy,
        )

    @staticmethod
    async def get_b01_3_county_management_area_stats_yearly(
        start_year: int,
        end_year: int,
        office_id: Optional[int] = None,
    ) -> CountyManagementAreaStatsResponse:
        """
        B01-3: 取得歷年各縣市管理區內外統計資料

        統計維度：縣市 × 管理區內外，歷年累計（start_year ~ end_year）

        Args:
            start_year: 起始年度（民國年）
            end_year: 結束年度（民國年）
            office_id: 管理處 ID（None=全部）

        Returns:
            CountyManagementAreaStatsResponse: 歷年各縣市管理區內外統計
        """
        county_lookup, _ = await GrantStatisticsCRUD._build_county_town_lookup()

        # 按縣市 + 管理區類型彙總（歷年累計）
        county_data: dict = {}

        # 🔥 分年度查詢以避免 SQL 參數超過 32767 限制
        for year in range(start_year, end_year + 1):
            query = Grants.filter(
                year=year,
                status__in=['completed', 'submitted']
            )
            if office_id is not None:
                query = query.filter(office_id=office_id)
            else:
                query = query.filter(office_id__in=ALLOWED_OFFICE_IDS)

            grants = await query.prefetch_related('active_version').all()

            for grant in grants:
                if not grant.active_version:
                    continue

                grant_area, grant_subsidy = GrantStatisticsCRUD._calculate_grant_subsidy(grant)

                # 判斷管理區內/外
                area_type = GrantStatisticsCRUD._get_management_area_type(grant)

                # 取得縣市歸屬
                all_steps_data = grant.active_version.all_steps_data or {}
                steps = all_steps_data.get('steps', {})
                lands = steps.get('2', {}).get('lands', [])

                c_id, c_name, _, _ = GrantStatisticsCRUD._find_first_valid_county_town(
                    lands, county_lookup, {}
                )

                if c_id is not None:
                    if c_id not in county_data:
                        county_data[c_id] = {
                            'county_id': c_id,
                            'county_name': c_name,
                            'inside': {'cases': 0, 'area': Decimal('0'), 'subsidy': Decimal('0')},
                            'outside': {'cases': 0, 'area': Decimal('0'), 'subsidy': Decimal('0')},
                        }
                    county_data[c_id][area_type]['cases'] += 1
                    county_data[c_id][area_type]['area'] += grant_area
                    county_data[c_id][area_type]['subsidy'] += grant_subsidy

        # 排序並組織結果
        sorted_county_ids = sorted(county_data.keys())
        stats = []
        total_cases = 0
        total_area = Decimal('0')
        total_subsidy = Decimal('0')

        for c_id in sorted_county_ids:
            d = county_data[c_id]
            stats.append(CountyManagementAreaStats(
                county_id=d['county_id'],
                county_name=d['county_name'],
                inside_cases=d['inside']['cases'],
                inside_area=d['inside']['area'],
                inside_subsidy=d['inside']['subsidy'],
                outside_cases=d['outside']['cases'],
                outside_area=d['outside']['area'],
                outside_subsidy=d['outside']['subsidy'],
            ))
            total_cases += d['inside']['cases'] + d['outside']['cases']
            total_area += d['inside']['area'] + d['outside']['area']
            total_subsidy += d['inside']['subsidy'] + d['outside']['subsidy']

        return CountyManagementAreaStatsResponse(
            start_year=start_year,
            end_year=end_year,
            stats=stats,
            total_cases=total_cases,
            total_area=total_area,
            total_subsidy=total_subsidy,
        )

    @staticmethod
    async def get_b01_4_office_management_area_stats_yearly(
        start_year: int,
        end_year: int,
        office_id: Optional[int] = None,
    ) -> OfficeManagementAreaStatsResponse:
        """
        B01-4: 取得歷年各管理處管理區內外統計資料

        統計維度：管理處 × 管理區內外，歷年累計（start_year ~ end_year）

        Args:
            start_year: 起始年度（民國年）
            end_year: 結束年度（民國年）
            office_id: 管理處 ID（None=全部）

        Returns:
            OfficeManagementAreaStatsResponse: 歷年各管理處管理區內外統計
        """
        # 取得管理處名稱
        office_ids = ALLOWED_OFFICE_IDS if office_id is None else [office_id]
        offices = await Offices.filter(id__in=office_ids).all()
        office_name_map = {o.id: o.name for o in offices}

        # 按管理處 + 管理區類型彙總（歷年累計）
        office_data: dict = {}

        # 🔥 分年度查詢以避免 SQL 參數超過 32767 限制
        for year in range(start_year, end_year + 1):
            query = Grants.filter(
                year=year,
                status__in=['completed', 'submitted']
            )
            if office_id is not None:
                query = query.filter(office_id=office_id)
            else:
                query = query.filter(office_id__in=ALLOWED_OFFICE_IDS)

            grants = await query.prefetch_related('active_version').all()

            for grant in grants:
                if not grant.active_version:
                    continue

                grant_area, grant_subsidy = GrantStatisticsCRUD._calculate_grant_subsidy(grant)

                # 判斷管理區內/外
                area_type = GrantStatisticsCRUD._get_management_area_type(grant)

                o_id = grant.office_id
                if o_id not in office_data:
                    office_data[o_id] = {
                        'office_id': o_id,
                        'office_name': office_name_map.get(o_id, f'未知管理處({o_id})'),
                        'inside': {'cases': 0, 'area': Decimal('0'), 'subsidy': Decimal('0')},
                        'outside': {'cases': 0, 'area': Decimal('0'), 'subsidy': Decimal('0')},
                    }
                office_data[o_id][area_type]['cases'] += 1
                office_data[o_id][area_type]['area'] += grant_area
                office_data[o_id][area_type]['subsidy'] += grant_subsidy

        # 排序並組織結果
        sorted_office_ids = sorted(office_data.keys())
        stats = []
        total_cases = 0
        total_area = Decimal('0')
        total_subsidy = Decimal('0')

        for o_id in sorted_office_ids:
            d = office_data[o_id]
            stats.append(OfficeManagementAreaStats(
                office_id=d['office_id'],
                office_name=d['office_name'],
                inside_cases=d['inside']['cases'],
                inside_area=d['inside']['area'],
                inside_subsidy=d['inside']['subsidy'],
                outside_cases=d['outside']['cases'],
                outside_area=d['outside']['area'],
                outside_subsidy=d['outside']['subsidy'],
            ))
            total_cases += d['inside']['cases'] + d['outside']['cases']
            total_area += d['inside']['area'] + d['outside']['area']
            total_subsidy += d['inside']['subsidy'] + d['outside']['subsidy']

        return OfficeManagementAreaStatsResponse(
            start_year=start_year,
            end_year=end_year,
            office_id=office_id,
            stats=stats,
            total_cases=total_cases,
            total_area=total_area,
            total_subsidy=total_subsidy,
        )

    # ==================== A04 原民區域統計報表 ====================

    @staticmethod
    def _is_aboriginal_land(land: dict) -> bool:
        """判斷土地是否為原民區域（容錯處理 null/string）"""
        is_aboriginal = land.get('isAboriginalArea', False)
        if is_aboriginal is None:
            return False
        if isinstance(is_aboriginal, str):
            return is_aboriginal.lower() == 'true'
        return bool(is_aboriginal)

    @staticmethod
    def _find_first_valid_aboriginal_land(
        lands: list, county_lookup: dict, town_lookup: dict,
        strict_first_land: bool = False,
    ) -> tuple:
        """
        找到案件的原民區域有效土地

        Args:
            strict_first_land: 歸屬模式切換
                False (預設): 遍歷所有土地，回傳第一筆 isAboriginalArea=true 的有效土地
                True: 與 A02-1 一致，只看第一筆有效土地，若該土地非原民則排除整筆案件

        Returns:
            tuple: (county_name, town_name)
                   若無符合條件的土地則返回 (None, None)
        """
        is_aboriginal = GrantStatisticsCRUD._is_aboriginal_land

        if strict_first_land:
            # Mode B: 第一筆有效土地必須同時為原民區域，否則整筆案件排除
            for land in lands:
                land_county = land.get('landCounty')
                land_town = land.get('landTown')
                if land_county is None or land_town is None:
                    continue
                if land_county not in county_lookup or land_town not in town_lookup:
                    continue
                # 找到第一筆有效土地：判定原民與否即回傳
                if is_aboriginal(land):
                    return (county_lookup[land_county], town_lookup[land_town][0])
                return (None, None)
            return (None, None)

        # Mode A (預設): 找第一筆原民區域有效土地
        for land in lands:
            if not is_aboriginal(land):
                continue
            land_county = land.get('landCounty')
            land_town = land.get('landTown')
            if land_county is None or land_town is None:
                continue
            if land_county in county_lookup and land_town in town_lookup:
                return (county_lookup[land_county], town_lookup[land_town][0])

        return (None, None)

    @staticmethod
    async def get_aboriginal_statistics(
        year: int, strict_first_land: bool = False
    ) -> dict:
        """
        A04: 取得原民區域統計資料

        歸屬規則：
        - strict_first_land=False (預設): 找第一筆原民有效土地歸屬
        - strict_first_land=True: 與 A02-1 一致，第一筆有效土地必須為原民才計入
        """
        county_lookup, town_lookup = await GrantStatisticsCRUD._build_county_town_lookup()

        grants = await Grants.filter(
            year=year,
            status__in=['completed', 'submitted'],
            office_id__in=ALLOWED_OFFICE_IDS,
        ).prefetch_related('active_version').all()

        stats_dict: dict = {}

        for grant in grants:
            if not grant.active_version:
                continue
            all_steps_data = grant.active_version.all_steps_data or {}
            steps = all_steps_data.get('steps', {})
            lands = steps.get('2', {}).get('lands', [])

            county_name, town_name = GrantStatisticsCRUD._find_first_valid_aboriginal_land(
                lands, county_lookup, town_lookup,
                strict_first_land=strict_first_land,
            )
            if county_name is None:
                continue

            grant_area, grant_subsidy = GrantStatisticsCRUD._calculate_grant_subsidy(grant)

            key = (county_name, town_name)
            if key not in stats_dict:
                stats_dict[key] = {'count': 0, 'area': Decimal('0'), 'subsidy': Decimal('0')}
            stats_dict[key]['count'] += 1
            stats_dict[key]['area'] += grant_area
            stats_dict[key]['subsidy'] += grant_subsidy

        result = []
        total_count = 0
        total_area = Decimal('0')
        total_subsidy = Decimal('0')

        for (county, town), d in sorted(stats_dict.items()):
            result.append({
                'county': county,
                'town': town,
                'grant_count': d['count'],
                'subsidy_area': float(d['area']),
                'subsidy_amount': int(d['subsidy']),
            })
            total_count += d['count']
            total_area += d['area']
            total_subsidy += d['subsidy']

        return {
            'year': year,
            'stats': result,
            'total_count': total_count,
            'total_area': float(total_area),
            'total_subsidy': int(total_subsidy),
        }
