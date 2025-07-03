// 前端篩選工具函數
import type { GeoJsonFeature, GrantLocationProperties } from '@/types/gis'

export interface FilterCriteria {
  applicantName: string
  landSection: string
  landNumber: string
  caseNumber: string
  sourceSystem: string | null
  yearStart: number
  yearEnd: number
}

// 統一的疊加圖層初始載入條件
export interface InitialOverlayLoadingParams {
  apply_year_min: number
  apply_year_max: number
  no_clustering: boolean
  source_system?: 'new_aerc' | 'legacy_farmdata'
  limit?: number
}

/**
 * 獲取當前年度（民國年）
 */
export function getCurrentYear(): number {
  return new Date().getFullYear() - 1911
}

/**
 * 獲取統一的疊加圖層初始載入條件參數
 * 目前設置為僅載入當年度資料
 */
export function getInitialOverlayLoadingParams(): InitialOverlayLoadingParams {
  const currentYear = getCurrentYear()
  return {
    apply_year_min: currentYear,
    apply_year_max: currentYear,
    no_clustering: true, // 使用原始資料，由前端處理聚合
    source_system: undefined,
    limit: undefined // 不設定數量限制，載入所有符合條件的資料
  }
}

/**
 * 對 GeoJSON 特徵進行前端篩選
 * @param features 原始特徵陣列
 * @param quickFilter 快速篩選關鍵字
 * @param detailedFilters 詳細篩選條件
 * @returns 篩選後的特徵陣列
 */
export function applyFrontendFilters(
  features: GeoJsonFeature[],
  quickFilter: string = '',
  detailedFilters: Partial<FilterCriteria> = {}
): GeoJsonFeature[] {
  if (!features || features.length === 0) {
    return features
  }

  let filteredFeatures = features

  // 1. 年度範圍篩選
  const yearMin = detailedFilters.yearStart
  const yearMax = detailedFilters.yearEnd
  if (yearMin || yearMax) {
    filteredFeatures = filteredFeatures.filter(feature => {
      const properties = feature.properties as GrantLocationProperties
      if (properties.cluster) return true // 聚合點位不篩選

      const applyYear = properties.apply_year
      if (!applyYear) return false

      if (yearMin && applyYear < yearMin) return false
      if (yearMax && applyYear > yearMax) return false

      return true
    })
  }

  // 2. 資料來源篩選
  if (detailedFilters.sourceSystem) {
    filteredFeatures = filteredFeatures.filter(feature => {
      const properties = feature.properties as GrantLocationProperties
      if (properties.cluster) return true // 聚合點位不篩選

      return properties.source_system === detailedFilters.sourceSystem
    })
  }

  // 3. 檢查是否有詳細篩選條件
  const hasDetailedFilters = !!(
    detailedFilters.applicantName ||
    detailedFilters.landSection ||
    detailedFilters.landNumber ||
    detailedFilters.caseNumber
  )

  // 4. 快速篩選（僅當沒有詳細篩選條件時使用）
  if (quickFilter && !hasDetailedFilters) {
    const searchTerm = quickFilter.toLowerCase()
    filteredFeatures = filteredFeatures.filter(feature => {
      const properties = feature.properties as GrantLocationProperties
      if (properties.cluster) return true // 聚合點位不篩選

      const applicantName = properties.applicant_name?.toLowerCase() || ''
      const landSection = properties.land_section?.toLowerCase() || ''
      const landNumber = properties.land_number?.toLowerCase() || ''
      const caseNumber = properties.source_id?.toLowerCase() || ''

      return applicantName.includes(searchTerm) ||
             landSection.includes(searchTerm) ||
             landNumber.includes(searchTerm) ||
             caseNumber.includes(searchTerm)
    })
  }

  // 5. 詳細篩選（AND 邏輯）
  if (hasDetailedFilters) {
    filteredFeatures = filteredFeatures.filter(feature => {
      const properties = feature.properties as GrantLocationProperties
      if (properties.cluster) return true // 聚合點位不篩選

      // 申請人姓名
      if (detailedFilters.applicantName) {
        const applicantName = properties.applicant_name?.toLowerCase() || ''
        const searchTerm = detailedFilters.applicantName.toLowerCase()
        if (!applicantName.includes(searchTerm)) return false
      }

      // 地段
      if (detailedFilters.landSection) {
        const landSection = properties.land_section?.toLowerCase() || ''
        const searchTerm = detailedFilters.landSection.toLowerCase()
        if (!landSection.includes(searchTerm)) return false
      }

      // 地號
      if (detailedFilters.landNumber) {
        const landNumber = properties.land_number?.toLowerCase() || ''
        const searchTerm = detailedFilters.landNumber.toLowerCase()
        if (!landNumber.includes(searchTerm)) return false
      }

      // 案件編號
      if (detailedFilters.caseNumber) {
        const caseNumber = properties.source_id?.toLowerCase() || ''
        const searchTerm = detailedFilters.caseNumber.toLowerCase()
        if (!caseNumber.includes(searchTerm)) return false
      }

      return true
    })
  }

  return filteredFeatures
}

/**
 * 創建測試資料用於驗證篩選功能
 */
export function createTestFeatures(): GeoJsonFeature[] {
  const currentYear = getCurrentYear()

  return [
    {
      type: 'Feature',
      geometry: { type: 'Point', coordinates: [120.5, 23.5] },
      properties: {
        cluster: false,
        id: 1,
        source_system: 'new_aerc',
        source_id: 'TEST001',
        applicant_name: '張三',
        land_section: '中正段',
        land_number: '123',
        apply_year: currentYear,
        case_status: '核准',
        land_type: '農地'
      }
    },
    {
      type: 'Feature',
      geometry: { type: 'Point', coordinates: [120.6, 23.6] },
      properties: {
        cluster: false,
        id: 2,
        source_system: 'legacy_farmdata',
        source_id: 'OLD002',
        applicant_name: '李四',
        land_section: '民權段',
        land_number: '456',
        apply_year: currentYear - 1,
        case_status: '審核中',
        land_type: '農地'
      }
    },
    {
      type: 'Feature',
      geometry: { type: 'Point', coordinates: [120.7, 23.7] },
      properties: {
        cluster: false,
        id: 3,
        source_system: 'new_aerc',
        source_id: 'TEST003',
        applicant_name: '王五',
        land_section: '中正段',
        land_number: '789',
        apply_year: currentYear,
        case_status: '核准',
        land_type: '農地'
      }
    }
  ]
}

/**
 * 測試前端篩選功能
 */
export function testFrontendFilters() {
  console.log('=== 測試前端篩選功能 ===')

  const testFeatures = createTestFeatures()
  const initialParams = getInitialOverlayLoadingParams()

  console.log('原始資料:', testFeatures.length, '筆')
  console.log('統一初始載入條件:', initialParams)

  // 測試年度篩選（使用統一初始載入條件）
  let filtered = applyFrontendFilters(testFeatures, '', {
    yearStart: initialParams.apply_year_min,
    yearEnd: initialParams.apply_year_max
  })
  console.log(`年度篩選 (${initialParams.apply_year_min}-${initialParams.apply_year_max}):`, filtered.length, '筆')

  // 測試申請人篩選
  filtered = applyFrontendFilters(testFeatures, '', { applicantName: '張' })
  console.log('申請人篩選 (張):', filtered.length, '筆')

  // 測試快速篩選
  filtered = applyFrontendFilters(testFeatures, '中正')
  console.log('快速篩選 (中正):', filtered.length, '筆')

  // 測試組合篩選
  filtered = applyFrontendFilters(testFeatures, '', {
    yearStart: initialParams.apply_year_min,
    yearEnd: initialParams.apply_year_max,
    landSection: '中正'
  })
  console.log(`組合篩選 (年度 ${initialParams.apply_year_min}-${initialParams.apply_year_max} + 地段 中正):`, filtered.length, '筆')

  console.log('=== 測試完成 ===')

  return {
    totalFeatures: testFeatures.length,
    initialParams,
    testResults: [
      {
        name: `年度篩選 (${initialParams.apply_year_min}-${initialParams.apply_year_max})`,
        count: applyFrontendFilters(testFeatures, '', {
          yearStart: initialParams.apply_year_min,
          yearEnd: initialParams.apply_year_max
        }).length
      },
      {
        name: '申請人篩選 (張)',
        count: applyFrontendFilters(testFeatures, '', { applicantName: '張' }).length
      },
      {
        name: '快速篩選 (中正)',
        count: applyFrontendFilters(testFeatures, '中正').length
      },
      {
        name: '組合篩選',
        count: applyFrontendFilters(testFeatures, '', {
          yearStart: initialParams.apply_year_min,
          yearEnd: initialParams.apply_year_max,
          landSection: '中正'
        }).length
      }
    ]
  }
}
