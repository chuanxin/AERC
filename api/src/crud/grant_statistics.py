"""
Grant Statistics CRUD Operations
補助案件統計查詢的業務邏輯層 - 即時計算統計資料
"""

from typing import List, Optional
from decimal import Decimal
from tortoise.expressions import Q

from ..database.models import Grants, GrantVersions, Offices, SubsidyAnnualBudget
from ..schemas.statistics import (
    ExecutionProgressResponse,
    OfficeExecutionStats,
    BudgetAnalysisResponse,
    OfficeBudgetStats
)


class GrantStatisticsCRUD:
    """補助案件統計的 CRUD 操作類"""

    @staticmethod
    async def get_execution_progress(
        year: int,
        office_id: Optional[int] = None,
        user_role: str = "user"
    ) -> ExecutionProgressResponse:
        """
        取得即時執行進度統計

        Args:
            year: 統計年度（民國年）
            office_id: 辦公室 ID（若為 None 則查詢所有辦公室）
            user_role: 使用者角色（admin/manager/user）

        Returns:
            ExecutionProgressResponse: 執行進度統計資料
        """
        # 1. 建構查詢條件
        query = Grants.filter(year=year)

        # 權限控制：非 admin 只能查看自己辦公室的資料
        if user_role != "admin" and office_id is not None:
            query = query.filter(office_id=office_id)

        # 2. 取得所有符合條件的辦公室
        if office_id is not None and user_role != "admin":
            # 單一辦公室查詢
            offices = await Offices.filter(id=office_id).all()
        else:
            # 查詢所有辦公室（admin 權限）
            # 只查詢有案件的辦公室
            office_ids = await query.distinct().values_list("office_id", flat=True)
            offices = await Offices.filter(id__in=office_ids).all()

        # 3. 為每個辦公室計算統計資料
        office_stats_list = []
        total_approved_budget = Decimal('0')
        total_completed_cases = 0
        total_area = Decimal('0')
        total_subsidy = Decimal('0')

        for office in offices:
            stats = await GrantStatisticsCRUD._calculate_office_execution_stats(
                year=year,
                office_id=office.id,
                office_name=office.name
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
        office_name: str
    ) -> OfficeExecutionStats:
        """
        計算單一辦公室的執行進度統計

        Args:
            year: 統計年度
            office_id: 辦公室 ID
            office_name: 辦公室名稱

        Returns:
            OfficeExecutionStats: 辦公室統計資料
        """
        # 1. 從 SubsidyAnnualBudget 取得核定預算
        annual_budget = await SubsidyAnnualBudget.filter(
            year=year,
            office_id=office_id
        ).first()

        approved_budget = annual_budget.approved_budget if annual_budget else Decimal('0')

        # 2. 查詢已結案案件（status in ['completed', 'submitted']）
        completed_grants = await Grants.filter(
            year=year,
            office_id=office_id,
            status__in=['completed', 'submitted']
        ).prefetch_related('active_version').all()

        completed_cases = len(completed_grants)
        total_area = Decimal('0')
        total_subsidy = Decimal('0')

        # 3. 從 all_steps_data 提取面積和補助金額
        for grant in completed_grants:
            if grant.active_version:
                all_steps_data = grant.active_version.all_steps_data or {}

                # 提取施設面積資料（從 step2.lands[].facilityAreaHa）
                step2_data = all_steps_data.get('step2', {})
                lands = step2_data.get('lands', [])
                for land in lands:
                    # 使用施設面積（公頃）
                    facility_area_ha = Decimal(str(land.get('facilityAreaHa', 0) or 0))
                    total_area += facility_area_ha

                # 提取補助金額（從 budget_items.total_subsidy）
                budget_items = all_steps_data.get('budget_items', {})
                subsidy_amount = Decimal(str(budget_items.get('total_subsidy', 0) or 0))
                total_subsidy += subsidy_amount

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
        user_role: str = "user"
    ) -> BudgetAnalysisResponse:
        """
        取得即時經費統計分析

        Args:
            year: 統計年度（民國年）
            office_id: 辦公室 ID（若為 None 則查詢所有辦公室）
            user_role: 使用者角色（admin/manager/user）

        Returns:
            BudgetAnalysisResponse: 經費統計分析資料
        """
        # 1. 建構查詢條件
        query = Grants.filter(year=year)

        # 權限控制：非 admin 只能查看自己辦公室的資料
        if user_role != "admin" and office_id is not None:
            query = query.filter(office_id=office_id)

        # 2. 取得所有符合條件的辦公室
        if office_id is not None and user_role != "admin":
            offices = await Offices.filter(id=office_id).all()
        else:
            office_ids = await query.distinct().values_list("office_id", flat=True)
            offices = await Offices.filter(id__in=office_ids).all()

        # 3. 為每個辦公室計算統計資料
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
                office_name=office.name
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
        office_name: str
    ) -> OfficeBudgetStats:
        """
        計算單一辦公室的經費統計分析

        Args:
            year: 統計年度
            office_id: 辦公室 ID
            office_name: 辦公室名稱

        Returns:
            OfficeBudgetStats: 辦公室經費統計資料
        """
        # 1. 從 SubsidyAnnualBudget 取得預定執行面積和預算
        annual_budget = await SubsidyAnnualBudget.filter(
            year=year,
            office_id=office_id
        ).first()

        planned_area = annual_budget.approved_area if annual_budget else Decimal('0')
        planned_budget = annual_budget.approved_budget if annual_budget else Decimal('0')

        # 2. 查詢已編預算案件（status='under_review'）
        budgeted_grants = await Grants.filter(
            year=year,
            office_id=office_id,
            status='under_review'
        ).prefetch_related('active_version').all()

        budgeted_cases = len(budgeted_grants)
        budgeted_area = Decimal('0')
        budgeted_subsidy = Decimal('0')

        for grant in budgeted_grants:
            if grant.active_version:
                all_steps_data = grant.active_version.all_steps_data or {}

                # 提取施設面積
                step2_data = all_steps_data.get('step2', {})
                lands = step2_data.get('lands', [])
                for land in lands:
                    facility_area_ha = Decimal(str(land.get('facilityAreaHa', 0) or 0))
                    budgeted_area += facility_area_ha

                # 提取補助金額
                budget_items = all_steps_data.get('budget_items', {})
                subsidy_amount = Decimal(str(budget_items.get('total_subsidy', 0) or 0))
                budgeted_subsidy += subsidy_amount

        # 3. 查詢已驗收案件（status='completed'）
        verified_grants = await Grants.filter(
            year=year,
            office_id=office_id,
            status='completed'
        ).prefetch_related('active_version').all()

        verified_cases = len(verified_grants)
        verified_area = Decimal('0')
        verified_amount = Decimal('0')

        for grant in verified_grants:
            if grant.active_version:
                all_steps_data = grant.active_version.all_steps_data or {}

                # 提取施設面積
                step2_data = all_steps_data.get('step2', {})
                lands = step2_data.get('lands', [])
                for land in lands:
                    facility_area_ha = Decimal(str(land.get('facilityAreaHa', 0) or 0))
                    verified_area += facility_area_ha

                # 提取補助金額
                budget_items = all_steps_data.get('budget_items', {})
                subsidy_amount = Decimal(str(budget_items.get('total_subsidy', 0) or 0))
                verified_amount += subsidy_amount

        # 4. 計算未編列補助款（預定執行預算 - 已編列補助款）
        unbudgeted_subsidy = planned_budget - budgeted_subsidy
        if unbudgeted_subsidy < 0:
            unbudgeted_subsidy = Decimal('0')

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
