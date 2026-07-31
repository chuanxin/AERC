/**
 * Qualification Store - 重複案件查詢狀態管理
 * 使用 Pinia 管理查詢狀態、結果快取和歷史記錄
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { wrapAsync, type ApiError } from '@/utils/asyncHelpers'
import { qualificationService } from '@/services/qualificationService'
import type {
  QualificationSearchRequest,
  QualificationResponse,
  AreaCheckResponse,
  GrantCaseItem,
  AreaStatistics,
  ResponseMetadata,
  QualificationSearchParams,
  IndigenousSearchParams,
  RecentSearch,
  QualificationError
} from '@/types/qualification'

/**
 * 重複案件查詢狀態管理
 * 遵循 Linus 簡潔原則：統一狀態管理，避免特殊情況
 */
export const useQualificationStore = defineStore('qualification', () => {
  // === 核心狀態 ===
  const isLoading = ref(false)
  const isIndigenousLoading = ref(false)
  const error = ref<string | null>(null)
  
  // === 查詢結果 ===
  const searchResults = ref<GrantCaseItem[]>([])
  const statistics = ref<AreaStatistics | undefined>()
  const metadata = ref<ResponseMetadata | undefined>()
  
  // === 原民鄉查詢狀態 ===
  const isIndigenousArea = ref(false)
  const isIndigenousAreaChecked = ref(false)
  
  // === UI 狀態 ===
  const showNoResultMessage = ref(false)
  const showAlert = ref(true)
  
  // === 歷史記錄 ===
  // 一律由使用者的實際查詢累積；不放預設示例資料——首次使用者看到自己從未查過的
  // 「最近查詢」並可點擊載入，等於把假條件當成真紀錄呈現
  const recentSearches = ref<RecentSearch[]>([])

  // === 共享的異步選項 ===
  const asyncOptions = {
    loadingRef: isLoading,
    errorRef: error
  }

  const indigenousAsyncOptions = {
    loadingRef: isIndigenousLoading,
    errorRef: error
  }

  // === 計算屬性 ===
  const hasResults = computed(() => searchResults.value.length > 0)
  const totalRecords = computed(() => metadata.value?.total_records || 0)
  const responseTime = computed(() => metadata.value?.response_time_ms || 0)
  const searchTime = computed(() => metadata.value?.search_time || '')
  
  // 面積統計的便利計算屬性
  const landTotalArea = computed(() => statistics.value?.land_total_area || '0')
  const usedArea = computed(() => statistics.value?.used_area || '0')
  const remainingArea = computed(() => statistics.value?.remaining_area || '0')
  const microIrrigationArea = computed(() => statistics.value?.micro_irrigation_area || '0')
  const remainingMicroArea = computed(() => statistics.value?.remaining_micro_area || '0')
  const sprinklerArea = computed(() => statistics.value?.sprinkler_area || '0')
  const remainingSprinklerArea = computed(() => statistics.value?.remaining_sprinkler_area || '0')

  // === 核心方法 ===

  /**
   * 搜尋重複案件 - 統一處理一般/原民/山坡地查詢
   * @param queryType 查詢類型
   * @param searchParams 查詢參數
   * @param years 查詢年度 (可選)
   * @returns 查詢結果
   */
  const search = wrapAsync(async (
    queryType: 'general' | 'indigenous' | 'slope',
    searchParams: QualificationSearchParams,
    years?: string[]
  ): Promise<QualificationResponse> => {
    // 清除前一次結果
    clearResults()

    const request: QualificationSearchRequest = qualificationService.buildSearchRequest(
      queryType,
      searchParams.landNumber || '', // 地號為必填
      searchParams.county, // 可選
      searchParams.town,   // 可選
      searchParams.section,
      true, // 包含面積統計
      true, // 包含水利工作站界限資訊
      years && years.length > 0 ? years : undefined // 空數組時傳 undefined 代表查詢所有年度
    )

    console.log('執行查詢:', request)

    const response = await qualificationService.search(request)

    // 更新狀態
    searchResults.value = response.results
    statistics.value = response.statistics
    metadata.value = response.metadata

    // 更新UI狀態
    showNoResultMessage.value = response.results.length === 0

    // 添加到歷史記錄
    addToRecentSearches({
      county: searchParams.county,
      town: searchParams.town,
      section: searchParams.section,
      landNumber: searchParams.landNumber,
      // 父/子地號與年度一併保存，否則「載入最近查詢」還原不出地號欄位與年度勾選
      parentLandNumber: searchParams.parentLandNumber,
      childLandNumber: searchParams.childLandNumber,
      years: years ? [...years] : [],
      searchTime: new Date(),
      queryType
    })

    console.log('查詢完成，找到', response.results.length, '筆記錄')
    return response
  }, {
    ...asyncOptions,
    errorFormatter: (err: unknown) => {
      const qualificationError = err as QualificationError
      return qualificationError.message || '查詢失敗'
    }
  })

  /**
   * 檢查原住民鄉
   * @param params 縣市鄉鎮參數
   * @returns 檢查結果
   */
  const checkIndigenousArea = wrapAsync(async (
    params: IndigenousSearchParams
  ): Promise<AreaCheckResponse> => {
    console.log('檢查原住民鄉:', params)

    const request = qualificationService.buildAreaCheckRequest(params.county, params.town)
    const response = await qualificationService.checkIndigenousArea(request)

    // 更新狀態
    isIndigenousArea.value = response.is_qualified
    isIndigenousAreaChecked.value = true

    // 添加到歷史記錄
    addToRecentSearches({
      county: params.county,
      town: params.town,
      searchTime: new Date(),
      queryType: 'indigenous'
    })

    console.log('原住民鄉檢查結果:', response.is_qualified ? '是' : '非', '原住民鄉')
    return response
  }, indigenousAsyncOptions)

  /**
   * 清除查詢結果
   */
  const clearResults = () => {
    searchResults.value = []
    statistics.value = undefined
    metadata.value = undefined
    showNoResultMessage.value = false
  }

  /**
   * 清除原民鄉檢查狀態
   */
  const clearIndigenousCheck = () => {
    isIndigenousArea.value = false
    isIndigenousAreaChecked.value = false
  }

  /**
   * 清除錯誤訊息
   */
  const clearErrors = () => {
    error.value = null
  }

  /**
   * 添加到最近查詢記錄
   * @param search 查詢記錄
   */
  // 年度比對鍵：排序後串接，使 ['113','114'] 與 ['114','113'] 視為同一組條件；
  // 空陣列與未定義同樣代表「未指定年度」，兩者比對鍵皆為空字串
  const yearsKey = (years?: string[]) => [...(years ?? [])].sort().join(',')

  const addToRecentSearches = (search: RecentSearch) => {
    // 檢查是否已存在相同查詢
    // 年度納入比對：同地號查 113 與查 114 是兩筆不同的查詢，後者不應覆蓋前者
    const existingIndex = recentSearches.value.findIndex(item =>
      item.county === search.county &&
      item.town === search.town &&
      (item.section === search.section || (!item.section && !search.section)) &&
      (item.landNumber === search.landNumber || (!item.landNumber && !search.landNumber)) &&
      yearsKey(item.years) === yearsKey(search.years) &&
      item.queryType === search.queryType
    )

    // 移除重複記錄
    if (existingIndex !== -1) {
      recentSearches.value.splice(existingIndex, 1)
    }

    // 添加到開頭
    recentSearches.value.unshift(search)

    // 限制最多保留 5 筆記錄
    if (recentSearches.value.length > 5) {
      recentSearches.value = recentSearches.value.slice(0, 5)
    }

    // 持久化到 localStorage
    try {
      localStorage.setItem('qualification_recent_searches', JSON.stringify(recentSearches.value))
    } catch (error) {
      console.warn('無法儲存查詢歷史:', error)
    }
  }

  /**
   * 從歷史記錄載入查詢
   * @param search 歷史查詢記錄
   */
  const loadFromHistory = (search: RecentSearch) => {
    console.log('載入歷史查詢:', search)
    return search
  }

  /**
   * 清除查詢歷史
   */
  const clearHistory = () => {
    recentSearches.value = []
    try {
      localStorage.removeItem('qualification_recent_searches')
    } catch (error) {
      console.warn('無法清除查詢歷史:', error)
    }
  }

  /**
   * 初始化 Store
   * 從 localStorage 載入歷史記錄
   */
  const init = () => {
    try {
      const saved = localStorage.getItem('qualification_recent_searches')
      if (saved) {
        const parsed = JSON.parse(saved)
        if (Array.isArray(parsed)) {
          // 轉換日期字串回 Date 物件
          recentSearches.value = parsed.map(item => ({
            ...item,
            searchTime: new Date(item.searchTime)
          }))
        }
      }
    } catch (error) {
      console.warn('載入查詢歷史失敗:', error)
    }
  }

  // 立即初始化
  init()

  // === 返回公開的狀態和方法 ===
  return {
    // 狀態
    isLoading: computed(() => isLoading.value),
    isIndigenousLoading: computed(() => isIndigenousLoading.value),
    error: computed(() => error.value),
    searchResults: computed(() => searchResults.value),
    statistics: computed(() => statistics.value),
    metadata: computed(() => metadata.value),
    isIndigenousArea: computed(() => isIndigenousArea.value),
    isIndigenousAreaChecked: computed(() => isIndigenousAreaChecked.value),
    showNoResultMessage: computed(() => showNoResultMessage.value),
    showAlert: computed(() => showAlert.value),
    recentSearches: computed(() => recentSearches.value),

    // 計算屬性
    hasResults,
    totalRecords,
    responseTime,
    searchTime,
    landTotalArea,
    usedArea,
    remainingArea,
    microIrrigationArea,
    remainingMicroArea,
    sprinklerArea,
    remainingSprinklerArea,

    // 方法
    search,
    checkIndigenousArea,
    clearResults,
    clearIndigenousCheck,
    clearErrors,
    addToRecentSearches,
    loadFromHistory,
    clearHistory,

    // 設置方法
    setShowAlert: (value: boolean) => { showAlert.value = value }
  }
})

export default useQualificationStore