import { defineStore } from 'pinia'
import {
  statisticsService,
  type ExecutionProgressResponse,
  type BudgetAnalysisResponse
} from '@/services/statisticsService'
import { wrapAsync } from '@/utils/asyncHelpers'

/**
 * Store for managing Statistics data
 * 管理統計資料的 Pinia Store
 */
export const useStatisticsStore = defineStore('statistics', () => {
  // State
  const executionProgress = ref<ExecutionProgressResponse | null>(null)
  const budgetAnalysis = ref<BudgetAnalysisResponse | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const currentYear = ref<number>(new Date().getFullYear() - 1911) // 預設為當前民國年

  // Computed properties
  const hasExecutionData = computed(() => executionProgress.value !== null)
  const hasBudgetData = computed(() => budgetAnalysis.value !== null)

  // 總辦公室數
  const totalOffices = computed(() => {
    return executionProgress.value?.offices.length || 0
  })

  // 執行進度摘要
  const executionSummary = computed(() => {
    if (!executionProgress.value) return null

    return {
      year: executionProgress.value.year,
      totalBudget: executionProgress.value.total_approved_budget,
      totalCases: executionProgress.value.total_completed_cases,
      totalArea: executionProgress.value.total_area,
      totalSubsidy: executionProgress.value.total_subsidy,
      executionRate: executionProgress.value.overall_execution_rate
    }
  })

  // 經費分析摘要
  const budgetSummary = computed(() => {
    if (!budgetAnalysis.value) return null

    return {
      year: budgetAnalysis.value.year,
      plannedArea: budgetAnalysis.value.total_planned_area,
      plannedBudget: budgetAnalysis.value.total_planned_budget,
      budgetedSubsidy: budgetAnalysis.value.total_budgeted_subsidy,
      unbudgetedSubsidy: budgetAnalysis.value.total_unbudgeted_subsidy,
      verifiedAmount: budgetAnalysis.value.total_verified_amount,
      areaExecutionRate: budgetAnalysis.value.overall_area_execution_rate,
      budgetExecutionRate: budgetAnalysis.value.overall_budget_execution_rate
    }
  })

  // Async options for wrapAsync
  const asyncOptions = {
    loadingRef: isLoading,
    errorRef: error
  }

  /**
   * 取得即時執行進度統計
   * @param year 統計年度（民國年），預設為當前年度
   */
  const fetchExecutionProgress = wrapAsync(async (year?: number) => {
    const queryYear = year || currentYear.value
    const response = await statisticsService.getExecutionProgress(queryYear)
    executionProgress.value = response
    return response
  }, asyncOptions)

  /**
   * 取得即時經費統計分析
   * @param year 統計年度（民國年），預設為當前年度
   */
  const fetchBudgetAnalysis = wrapAsync(async (year?: number) => {
    const queryYear = year || currentYear.value
    const response = await statisticsService.getBudgetAnalysis(queryYear)
    budgetAnalysis.value = response
    return response
  }, asyncOptions)

  /**
   * 同時取得執行進度和經費分析統計
   * @param year 統計年度（民國年），預設為當前年度
   */
  const fetchAllStatistics = wrapAsync(async (year?: number) => {
    const queryYear = year || currentYear.value
    await Promise.all([
      fetchExecutionProgress(queryYear),
      fetchBudgetAnalysis(queryYear)
    ])
  }, asyncOptions)

  /**
   * 設定當前統計年度
   * @param year 年度（民國年）
   */
  const setCurrentYear = (year: number) => {
    currentYear.value = year
  }

  /**
   * 重置 store 狀態
   */
  const resetState = () => {
    executionProgress.value = null
    budgetAnalysis.value = null
    isLoading.value = false
    error.value = null
    currentYear.value = new Date().getFullYear() - 1911
  }

  /**
   * 初始化 store - 載入當前年度的統計資料
   */
  const initializeStore = async () => {
    if (!hasExecutionData.value || !hasBudgetData.value) {
      await fetchAllStatistics()
    }
  }

  return {
    // State
    executionProgress,
    budgetAnalysis,
    isLoading,
    error,
    currentYear,

    // Computed
    hasExecutionData,
    hasBudgetData,
    totalOffices,
    executionSummary,
    budgetSummary,

    // Actions
    fetchExecutionProgress,
    fetchBudgetAnalysis,
    fetchAllStatistics,
    setCurrentYear,
    resetState,
    initializeStore
  }
})
