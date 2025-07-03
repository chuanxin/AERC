import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import {
  getGrantLocations,
  getGisStatistics,
  searchGrantCases,
  convertSearchResultsToGeoJson,
  validateAndNormalizeFilters
} from '@/services/gisService'
import { ApplicationError } from '@/utils/asyncHelpers'
import type {
  GeoJsonFeature,
  GeoJsonFeatureCollection,
  GisStatsResponse,
  GisFilters,
  YearRange,
  DisplayMode,
  SearchPointsParams
} from '@/types/gis'

/**
 * GIS Store - 管理所有 GIS 相關的狀態和邏輯
 *
 * 功能包含：
 * - 點位資料管理
 * - 搜尋和篩選
 * - 統計資訊
 * - 顯示模式控制
 * - 載入狀態管理
 * - 錯誤處理
 */
export const useGisStore = defineStore('gis', () => {

  // ===== 響應式狀態 =====

  // 資料狀態
  const currentFeatures = ref<GeoJsonFeature[]>([])
  const statistics = ref<GisStatsResponse | null>(null)
  const lastLoadedData = ref<GeoJsonFeatureCollection | null>(null)

  // UI 狀態
  const loading = ref(false)
  const error = ref<string | null>(null)
  const displayMode = ref<DisplayMode>('heatmap')

  // 篩選狀態
  const filters = ref<GisFilters>({
  })

  // 年度範圍狀態
  const yearRange = ref<YearRange>({
    min: 97,
    max: 114,
    current: [97, 114]
  })

  // 地圖狀態
  const currentBounds = ref<string | null>(null)
  const selectedFeature = ref<GeoJsonFeature | null>(null)

  // ===== 計算屬性 =====

  const hasData = computed(() => currentFeatures.value.length > 0)

  const currentPointCount = computed(() => currentFeatures.value.length)

  const totalPointsInDatabase = computed(() =>
    statistics.value?.total_points || 0
  )

  const availableSourceSystems = computed(() =>
    statistics.value?.statistics.map(stat => ({
      title: stat.source_system === 'new_aerc' ? '新系統案件' : '歷史案件',
      value: stat.source_system
    })) || []
  )

  const isValidYearRange = computed(() => {
    const [min, max] = yearRange.value.current
    return min <= max && min >= yearRange.value.min && max <= yearRange.value.max
  })

  const currentFiltersForDisplay = computed(() => {
    const activeFilters: string[] = []

    if (filters.value.source_system) {
      activeFilters.push(filters.value.source_system === 'new_aerc' ? '新系統案件' : '歷史案件')
    }

    if (filters.value.apply_year_min || filters.value.apply_year_max) {
      const min = filters.value.apply_year_min || yearRange.value.min
      const max = filters.value.apply_year_max || yearRange.value.max
      activeFilters.push(`民國${min}-${max}年`)
    }

    if (filters.value.applicant_name) {
      activeFilters.push(`申請人: ${filters.value.applicant_name}`)
    }

    if (filters.value.land_section) {
      activeFilters.push(`地段: ${filters.value.land_section}`)
    }

    return activeFilters
  })

  // ===== Actions =====

  /**
   * 初始化 GIS Store（僅載入統計資料）
   */
  const initialize = async (): Promise<void> => {
    try {
      console.log('[gisStore.initialize] 初始化 GIS Store')
      await loadStatistics()
      console.log('[gisStore.initialize] 初始化完成，等待地圖載入後才載入資料')
    } catch (err) {
      console.error('[gisStore.initialize] 初始化失敗:', err)
      error.value = err instanceof ApplicationError ? err.message : '初始化失敗'
    }
  }

  /**
   * 載入統計資訊
   */
  const loadStatistics = async (): Promise<void> => {
    try {
      console.log('[gisStore.loadStatistics] 載入統計資訊')

      const stats = await getGisStatistics()
      statistics.value = stats

      // 更新年度範圍
      if (stats.statistics.length > 0) {
        const allStats = stats.statistics
        const earliestYear = Math.min(...allStats.map(s => s.earliest_year))
        const latestYear = Math.max(...allStats.map(s => s.latest_year))

        yearRange.value.min = earliestYear
        yearRange.value.max = latestYear

        // 如果當前範圍無效，重置為全範圍
        if (!isValidYearRange.value) {
          yearRange.value.current = [earliestYear, latestYear]
        }
      }

      console.log('[gisStore.loadStatistics] 統計資訊載入完成:', stats)

    } catch (err) {
      console.error('[gisStore.loadStatistics] 載入統計資訊失敗:', err)
      throw err
    }
  }

  /**
   * 載入當前地圖視窗範圍內的補助案件位置資料
   * @param bbox 必需的地圖邊界框
   * @param mapZoomLevel 地圖縮放等級
   * @param customFilters 額外篩選條件
   */
  const loadGrantLocations = async (
    bbox: string,
    mapZoomLevel: number = 12,
    customFilters?: Partial<Omit<GisFilters, 'bbox'>>
  ): Promise<void> => {
    loading.value = true
    error.value = null

    try {
      console.log('[gisStore.loadGrantLocations] 載入視窗範圍資料:', { bbox, zoom: mapZoomLevel })

      // 合併篩選條件
      const mergedFilters = { ...customFilters }

      // 添加年度篩選
      if (isValidYearRange.value) {
        mergedFilters.apply_year_min = yearRange.value.current[0]
        mergedFilters.apply_year_max = yearRange.value.current[1]
      }

      // 不設定 limit，讓 OpenLayers 前端聚合處理所有點位
      // 移除數量限制以評估效能表現
      // 請求原始點位資料，不進行後端聚合
      mergedFilters.no_clustering = true

      // 驗證和標準化篩選條件
      const normalizedFilters = validateAndNormalizeFilters(mergedFilters)

      // 調用 API（始終包含bbox）
      const response = await getGrantLocations(bbox, normalizedFilters, mapZoomLevel)

      // 更新狀態
      currentFeatures.value = response.features
      lastLoadedData.value = response
      currentBounds.value = bbox

      // 更新filters（不包含bbox，因為bbox是動態的）
      filters.value = { ...filters.value, ...normalizedFilters }

      console.log(`[gisStore.loadGrantLocations] 載入完成: ${response.features.length} 筆資料 (${
        response.meta.clustering?.enabled ? '聚合' : '個別'
      })`)

    } catch (err) {
      console.error('[gisStore.loadGrantLocations] 載入失敗:', err)
      error.value = err instanceof ApplicationError ? err.message : '載入地圖資料失敗'
      currentFeatures.value = []
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * 在當前地圖視窗範圍內搜尋補助案件
   * @param bbox 必需的地圖邊界框
   * @param searchParams 搜尋參數
   */
  const searchCases = async (bbox: string, searchParams: SearchPointsParams): Promise<void> => {
    loading.value = true
    error.value = null

    try {
      console.log('[gisStore.searchCases] 在視窗範圍內搜尋:', { bbox, searchParams })

      // 調用搜尋 API（基於當前視窗範圍）
      const searchResponse = await searchGrantCases(bbox, searchParams)

      // 轉換為 GeoJSON 格式
      const geoJsonData = convertSearchResultsToGeoJson(searchResponse)

      // 更新狀態
      currentFeatures.value = geoJsonData.features
      lastLoadedData.value = geoJsonData
      currentBounds.value = bbox

      // 更新篩選條件
      filters.value = {
        ...filters.value,
        applicant_name: searchParams.applicant_name,
        land_section: searchParams.land_section,
        case_number: searchParams.case_number
      }

      console.log(`[gisStore.searchCases] 搜尋完成: ${geoJsonData.features.length} 筆結果`)

    } catch (err) {
      console.error('[gisStore.searchCases] 搜尋失敗:', err)
      error.value = err instanceof ApplicationError ? err.message : '搜尋案件失敗'
      currentFeatures.value = []
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * 更新顯示模式（不自動重新載入，由呼叫者決定）
   */
  const updateDisplayMode = (mode: DisplayMode): void => {
    if (displayMode.value === mode) return
    console.log('[gisStore.updateDisplayMode] 切換顯示模式:', mode)
    displayMode.value = mode
  }

  /**
   * 更新年度範圍（不自動重新載入，由呼叫者決定）
   */
  const updateYearRange = (newRange: [number, number]): void => {
    console.log('[gisStore.updateYearRange] 更新年度範圍:', newRange)
    yearRange.value.current = newRange
  }

  /**
   * 更新篩選條件（不自動重新載入，由呼叫者決定）
   */
  const updateFilters = (newFilters: Partial<Omit<GisFilters, 'bbox'>>): void => {
    console.log('[gisStore.updateFilters] 更新篩選條件:', newFilters)
    filters.value = { ...filters.value, ...newFilters }
  }

  /**
   * 清除所有篩選條件
   */
  const clearFilters = (): void => {
    console.log('[gisStore.clearFilters] 清除篩選條件')
    filters.value = {} // 移除所有限制，包括 limit
    yearRange.value.current = [yearRange.value.min, yearRange.value.max]
  }

  /**
   * 選擇特定特徵
   */
  const selectFeature = (feature: GeoJsonFeature | null): void => {
    const featureId = feature && !feature.properties.cluster ? feature.properties.id : 'cluster'
    console.log('[gisStore.selectFeature] 選擇特徵:', featureId)
    selectedFeature.value = feature
  }

  /**
   * 更新地圖邊界
   */
  const updateBounds = (bounds: string): void => {
    currentBounds.value = bounds
  }

  /**
   * 清除錯誤狀態
   */
  const clearError = (): void => {
    error.value = null
  }

  // ===== 返回 Store 接口 =====

  return {
    // 狀態
    currentFeatures,
    statistics,
    loading,
    error,
    displayMode,
    filters,
    yearRange,
    currentBounds,
    selectedFeature,
    lastLoadedData,

    // 計算屬性
    hasData,
    currentPointCount,
    totalPointsInDatabase,
    availableSourceSystems,
    isValidYearRange,
    currentFiltersForDisplay,

    // Actions
    initialize,
    loadStatistics,
    loadGrantLocations,
    searchCases,
    updateDisplayMode,
    updateYearRange,
    updateFilters,
    clearFilters,
    selectFeature,
    updateBounds,
    clearError
  }
})
