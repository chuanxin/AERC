"""
Statistics 統計功能的 Pydantic Schemas
包含 Dashboard 統計和 Statistics 功能頁的所有統計資料結構
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from decimal import Decimal


# ==================== Dashboard 即時執行進度統計 ====================

class OfficeExecutionStats(BaseModel):
    """單一辦公室的即時執行進度統計"""
    office_id: int = Field(..., description="辦公室 ID")
    office_name: str = Field(..., description="辦公室名稱")
    approved_budget: Decimal = Field(default=Decimal('0'), description="年度核定預算總額")
    completed_cases: int = Field(default=0, description="已結案案件總數")
    total_area: Decimal = Field(default=Decimal('0'), description="總補助案件面積（公頃）")
    total_subsidy: Decimal = Field(default=Decimal('0'), description="總補助金額")
    execution_rate: Decimal = Field(default=Decimal('0'), description="補助款執行率（%）")

    class Config:
        json_encoders = {
            Decimal: lambda v: float(v)
        }


class ExecutionProgressResponse(BaseModel):
    """即時執行進度統計回應"""
    year: int = Field(..., description="統計年度（民國年）")
    offices: List[OfficeExecutionStats] = Field(default_factory=list, description="各辦公室統計資料")
    total_approved_budget: Decimal = Field(default=Decimal('0'), description="總核定預算")
    total_completed_cases: int = Field(default=0, description="總已結案案件數")
    total_area: Decimal = Field(default=Decimal('0'), description="總補助面積（公頃）")
    total_subsidy: Decimal = Field(default=Decimal('0'), description="總補助金額")
    overall_execution_rate: Decimal = Field(default=Decimal('0'), description="整體執行率（%）")

    class Config:
        json_encoders = {
            Decimal: lambda v: float(v)
        }


# ==================== Statistics 功能頁經費分析統計 ====================

class OfficeBudgetStats(BaseModel):
    """單一辦公室的經費統計分析"""
    office_id: int = Field(..., description="辦公室 ID")
    office_name: str = Field(..., description="辦公室名稱")

    # 預定執行
    planned_area: Decimal = Field(default=Decimal('0'), description="預定執行面積（公頃）")
    planned_budget: Decimal = Field(default=Decimal('0'), description="預定執行預算")

    # 已編預算
    budgeted_cases: int = Field(default=0, description="已編預算案件數")
    budgeted_area: Decimal = Field(default=Decimal('0'), description="已編預算面積（公頃）")
    budgeted_subsidy: Decimal = Field(default=Decimal('0'), description="已編列補助款")
    unbudgeted_subsidy: Decimal = Field(default=Decimal('0'), description="未編列補助款")

    # 已驗收
    verified_cases: int = Field(default=0, description="已驗收案件數")
    verified_area: Decimal = Field(default=Decimal('0'), description="總已驗收面積（公頃）")
    verified_amount: Decimal = Field(default=Decimal('0'), description="總已驗收金額")

    # 執行率
    area_execution_rate: Decimal = Field(default=Decimal('0'), description="面積執行率（%）")
    budget_execution_rate: Decimal = Field(default=Decimal('0'), description="計畫執行率（%）")

    class Config:
        json_encoders = {
            Decimal: lambda v: float(v)
        }


class BudgetAnalysisResponse(BaseModel):
    """即時經費統計分析回應"""
    year: int = Field(..., description="統計年度（民國年）")
    offices: List[OfficeBudgetStats] = Field(default_factory=list, description="各辦公室經費統計")

    # 總計
    total_planned_area: Decimal = Field(default=Decimal('0'), description="總預定執行面積（公頃）")
    total_planned_budget: Decimal = Field(default=Decimal('0'), description="總預定執行預算")
    total_budgeted_subsidy: Decimal = Field(default=Decimal('0'), description="總已編列補助款")
    total_unbudgeted_subsidy: Decimal = Field(default=Decimal('0'), description="總未編列補助款")
    total_verified_amount: Decimal = Field(default=Decimal('0'), description="總已驗收金額")

    # 整體執行率
    overall_area_execution_rate: Decimal = Field(default=Decimal('0'), description="整體面積執行率（%）")
    overall_budget_execution_rate: Decimal = Field(default=Decimal('0'), description="整體計畫執行率（%）")

    class Config:
        json_encoders = {
            Decimal: lambda v: float(v)
        }


# ==================== A02 系列統計報表 ====================

class CountyTownStats(BaseModel):
    """單一縣市鄉鎮區的統計資料"""
    county_id: int = Field(..., description="縣市 ID")
    county_name: str = Field(..., description="縣市名稱")
    town_id: int = Field(..., description="鄉鎮區 ID")
    town_name: str = Field(..., description="鄉鎮區名稱")
    completed_cases: int = Field(default=0, description="補助案件數")
    total_area: Decimal = Field(default=Decimal('0'), description="補助面積（公頃）")
    total_subsidy: Decimal = Field(default=Decimal('0'), description="補助金額（元）")

    class Config:
        json_encoders = {Decimal: lambda v: float(v)}


class OfficeSummaryStats(BaseModel):
    """單一管理處的 A02 統計資料（案件數 + 面積 + 金額）"""
    office_id: int = Field(..., description="管理處 ID")
    office_name: str = Field(..., description="管理處名稱")
    completed_cases: int = Field(default=0, description="補助案件數")
    total_area: Decimal = Field(default=Decimal('0'), description="補助面積（公頃）")
    total_subsidy: Decimal = Field(default=Decimal('0'), description="補助金額（元）")

    class Config:
        json_encoders = {Decimal: lambda v: float(v)}


class CountyTownStatsResponse(BaseModel):
    """A02-1/A02-3 各縣市鄉鎮區統計回應"""
    year: Optional[int] = Field(None, description="統計年度（A02-1 單年度）")
    start_year: Optional[int] = Field(None, description="起始年度（A02-3 歷年）")
    end_year: Optional[int] = Field(None, description="結束年度（A02-3 歷年）")
    stats: List[CountyTownStats] = Field(default_factory=list)
    total_cases: int = Field(default=0)
    total_area: Decimal = Field(default=Decimal('0'))
    total_subsidy: Decimal = Field(default=Decimal('0'))

    class Config:
        json_encoders = {Decimal: lambda v: float(v)}


class OfficeSummaryStatsResponse(BaseModel):
    """A02-2/A02-4 各管理處統計回應"""
    year: Optional[int] = Field(None, description="統計年度（A02-2 單年度）")
    start_year: Optional[int] = Field(None, description="起始年度（A02-4 歷年）")
    end_year: Optional[int] = Field(None, description="結束年度（A02-4 歷年）")
    stats: List[OfficeSummaryStats] = Field(default_factory=list)
    total_cases: int = Field(default=0)
    total_area: Decimal = Field(default=Decimal('0'))
    total_subsidy: Decimal = Field(default=Decimal('0'))

    class Config:
        json_encoders = {Decimal: lambda v: float(v)}


# ==================== A04 原民區域統計報表 ====================

class AboriginalAreaStats(BaseModel):
    """原民區域統計記錄（按縣市鄉鎮區彙總）"""
    county: str = Field(..., description="縣市名稱")
    town: str = Field(..., description="鄉鎮區名稱")
    grant_count: int = Field(default=0, ge=0, description="補助案件數")
    subsidy_area: Decimal = Field(default=Decimal('0'), ge=0, description="補助面積（公頃）")
    subsidy_amount: int = Field(default=0, ge=0, description="補助金額（元）")

    class Config:
        json_encoders = {Decimal: lambda v: float(v)}
