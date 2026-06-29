import { apiService } from './api/http'
import { STATISTICS } from './api/endpoints'

/**
 * 管理處執行進度統計
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
 * 管理處經費統計分析
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
  },

  /**
   * 下載 A01 各管理處執行進度報表 Excel
   * @param year 統計年度（民國年）
   * @param officeId 管理處 ID（選填）
   */
  async downloadExecutionProgressExcel(year: number, officeId?: number | null): Promise<void> {
    const params: Record<string, unknown> = { year }
    if (officeId) {
      params.office_id = officeId
    }

    const filename = `A01_各管理處執行進度_${year}年度.xlsx`
    await apiService.download(STATISTICS.EXECUTION_PROGRESS_EXCEL, params, filename)
  },

  /**
   * 下載 A03 各管理處經費統計報表 Excel
   * @param year 統計年度（民國年）
   * @param officeId 管理處 ID（選填）
   */
  async downloadBudgetAnalysisExcel(year: number, officeId?: number | null): Promise<void> {
    const params: Record<string, unknown> = { year }
    if (officeId) {
      params.office_id = officeId
    }

    const filename = `A03_各管理處經費統計_${year}年度.xlsx`
    await apiService.download(STATISTICS.BUDGET_ANALYSIS_EXCEL, params, filename)
  },

  /**
   * 下載 A02-1 各縣市鄉鎮區統計報表 Excel
   */
  async downloadCountyTownExcel(year: number, officeId?: number | null): Promise<void> {
    const params: Record<string, unknown> = { year }
    if (officeId) params.office_id = officeId
    const filename = `A02-1_各縣市鄉鎮區統計_${year}年度.xlsx`
    await apiService.download(STATISTICS.COUNTY_TOWN_EXCEL, params, filename)
  },

  /**
   * 下載 A02-2 各管理處統計報表 Excel
   */
  async downloadOfficeSummaryExcel(year: number, officeId?: number | null): Promise<void> {
    const params: Record<string, unknown> = { year }
    if (officeId) params.office_id = officeId
    const filename = `A02-2_各管理處統計_${year}年度.xlsx`
    await apiService.download(STATISTICS.OFFICE_SUMMARY_EXCEL, params, filename)
  },

  /**
   * 下載 A02-3 歷年各縣市鄉鎮區統計報表 Excel
   */
  async downloadCountyTownYearlyExcel(startYear: number, endYear: number, officeId?: number | null): Promise<void> {
    const params: Record<string, unknown> = { start_year: startYear, end_year: endYear }
    if (officeId) params.office_id = officeId
    const filename = `A02-3_歷年各縣市鄉鎮區統計_${startYear}-${endYear}年度.xlsx`
    await apiService.download(STATISTICS.COUNTY_TOWN_YEARLY_EXCEL, params, filename)
  },

  /**
   * 下載 A02-4 歷年各管理處統計報表 Excel
   */
  async downloadOfficeSummaryYearlyExcel(startYear: number, endYear: number, officeId?: number | null): Promise<void> {
    const params: Record<string, unknown> = { start_year: startYear, end_year: endYear }
    if (officeId) params.office_id = officeId
    const filename = `A02-4_歷年各管理處統計_${startYear}-${endYear}年度.xlsx`
    await apiService.download(STATISTICS.OFFICE_SUMMARY_YEARLY_EXCEL, params, filename)
  },

  /**
   * 下載 A04 原民區域統計報表 Excel
   * @param year 統計年度（民國年）
   * @param strictFirstLand 嚴格第一筆土地模式（與A02-1一致的歸屬規則）
   */
  async downloadAboriginalStatsExcel(year: number, strictFirstLand: boolean = false): Promise<void> {
    const params: Record<string, unknown> = { year }
    if (strictFirstLand) {
      params.strict_first_land = true
    }
    const filename = `A04_原民區域統計_${year}年度.xlsx`
    await apiService.download(STATISTICS.ABORIGINAL_STATS_EXCEL, params, filename)
  },

  /**
   * 下載 A08 歷年原民區域統計報表 Excel
   * @param startYear 起始年度（民國年）
   * @param endYear 結束年度（民國年）
   */
  async downloadAboriginalYearlyExcel(startYear: number, endYear: number): Promise<void> {
    const params: Record<string, unknown> = { start_year: startYear, end_year: endYear }
    const filename = `A08_歷年原民區域統計_${startYear}-${endYear}年度.xlsx`
    await apiService.download(STATISTICS.ABORIGINAL_YEARLY_EXCEL, params, filename)
  },

  // ==================== A09/A10 事業區域內外推動成果統計報表 ====================

  /**
   * 下載 A09 各縣市事業區域內外統計報表 Excel
   * @param year 統計年度（民國年）
   */
  async downloadA09Excel(year: number): Promise<void> {
    const filename = `A09_${year}年度各縣市事業區域內外推動成果統計.xlsx`
    await apiService.download(STATISTICS.A09_EXCEL, { year }, filename)
  },

  /**
   * 下載 A10 各管理處事業區域內外統計報表 Excel
   * @param year 統計年度（民國年）
   */
  async downloadA10Excel(year: number): Promise<void> {
    const filename = `A10_${year}年度各管理處事業區域內外推動成果統計.xlsx`
    await apiService.download(STATISTICS.A10_EXCEL, { year }, filename)
  },

  // ==================== B01 系列推動成果統計報表（管理區內外分組） ====================

  /**
   * 下載 B01-1 各縣市管理區內外統計報表 Excel（單年度）
   * @param year 統計年度（民國年）
   * @param officeId 管理處 ID（選填）
   */
  async downloadB01_1Excel(year: number, officeId?: number | null): Promise<void> {
    const params: Record<string, unknown> = { year }
    if (officeId) params.office_id = officeId
    const filename = `B01-1_各縣市推動成果統計_${year}年度.xlsx`
    await apiService.download(STATISTICS.B01_1_EXCEL, params, filename)
  },

  /**
   * 下載 B01-2 各管理處管理區內外統計報表 Excel（單年度）
   * @param year 統計年度（民國年）
   * @param officeId 管理處 ID（選填）
   */
  async downloadB01_2Excel(year: number, officeId?: number | null): Promise<void> {
    const params: Record<string, unknown> = { year }
    if (officeId) params.office_id = officeId
    const filename = `B01-2_各管理處推動成果統計_${year}年度.xlsx`
    await apiService.download(STATISTICS.B01_2_EXCEL, params, filename)
  },

  /**
   * 下載 B01-3 歷年各縣市管理區內外統計報表 Excel
   * @param startYear 起始年度（民國年）
   * @param endYear 結束年度（民國年）
   * @param officeId 管理處 ID（選填）
   */
  async downloadB01_3Excel(startYear: number, endYear: number, officeId?: number | null): Promise<void> {
    const params: Record<string, unknown> = { start_year: startYear, end_year: endYear }
    if (officeId) params.office_id = officeId
    const filename = `B01-3_歷年各縣市推動成果統計_${startYear}-${endYear}年度.xlsx`
    await apiService.download(STATISTICS.B01_3_EXCEL, params, filename)
  },

  /**
   * 下載 B01-4 歷年各管理處管理區內外統計報表 Excel
   * @param startYear 起始年度（民國年）
   * @param endYear 結束年度（民國年）
   * @param officeId 管理處 ID（選填）
   */
  async downloadB01_4Excel(startYear: number, endYear: number, officeId?: number | null): Promise<void> {
    const params: Record<string, unknown> = { start_year: startYear, end_year: endYear }
    if (officeId) params.office_id = officeId
    const filename = `B01-4_歷年各管理處推動成果統計_${startYear}-${endYear}年度.xlsx`
    await apiService.download(STATISTICS.B01_4_EXCEL, params, filename)
  },

  // ==================== B03 各縣市鄉鎮區各類補助項目統計報表 ====================

  /**
   * 下載 B03 各縣市鄉鎮區各類補助項目統計報表 Excel
   * @param year 統計年度（民國年）
   * @param officeId 管理處 ID（選填）
   */
  async downloadB03Excel(year: number, officeId?: number | null): Promise<void> {
    const params: Record<string, unknown> = { year }
    if (officeId) params.office_id = officeId
    const filename = `B03_${year}年度各縣市鄉鎮區各類補助項目統計.xlsx`
    await apiService.download(STATISTICS.B03_EXCEL, params, filename)
  },
}
