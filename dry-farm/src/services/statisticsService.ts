import { apiService } from './api/http'
import { STATISTICS } from './api/endpoints'

/**
 * 辦公室執行進度統計
 */
export interface OfficeExecutionStats {
  office_id: number
  office_name: string
  approved_budget: number
  completed_cases: number
  total_area: number
  total_subsidy: number
  execution_rate: number
}

/**
 * 即時執行進度統計回應
 */
export interface ExecutionProgressResponse {
  year: number
  offices: OfficeExecutionStats[]
  total_approved_budget: number
  total_completed_cases: number
  total_area: number
  total_subsidy: number
  overall_execution_rate: number
}

/**
 * 辦公室經費統計分析
 */
export interface OfficeBudgetStats {
  office_id: number
  office_name: string
  planned_area: number
  planned_budget: number
  budgeted_cases: number
  budgeted_area: number
  budgeted_subsidy: number
  unbudgeted_subsidy: number
  verified_cases: number
  verified_area: number
  verified_amount: number
  area_execution_rate: number
  budget_execution_rate: number
}

/**
 * 即時經費統計分析回應
 */
export interface BudgetAnalysisResponse {
  year: number
  offices: OfficeBudgetStats[]
  total_planned_area: number
  total_planned_budget: number
  total_budgeted_subsidy: number
  total_unbudgeted_subsidy: number
  total_verified_amount: number
  overall_area_execution_rate: number
  overall_budget_execution_rate: number
}

/**
 * Service for handling Statistics-related API calls
 */
export const statisticsService = {
  /**
   * 取得即時執行進度統計
   * @param year 統計年度（民國年）
   * @returns 執行進度統計資料
   */
  async getExecutionProgress(year: number): Promise<ExecutionProgressResponse> {
    return await apiService.get<ExecutionProgressResponse>(
      `${STATISTICS.EXECUTION_PROGRESS}?year=${year}`
    )
  },

  /**
   * 取得即時經費統計分析
   * @param year 統計年度（民國年）
   * @returns 經費統計分析資料
   */
  async getBudgetAnalysis(year: number): Promise<BudgetAnalysisResponse> {
    return await apiService.get<BudgetAnalysisResponse>(
      `${STATISTICS.BUDGET_ANALYSIS}?year=${year}`
    )
  }
}
