import { apiService } from './api/http'
import { ApplicationError } from '@/utils/asyncHelpers'
import { GIS } from './api/endpoints'
import type {
  GeoJsonFeatureCollection,
  GisStatsResponse,
  GisSearchResponse,
  GetPointsParams,
  SearchPointsParams,
  GeoJsonFeature,
  GisSearchResult
} from '@/types/gis'

/**
 * GIS Service - 處理所有 GIS 相關的 API 調用
 *
 * 提供統一的 GIS 資料存取接口，包含：
 * - 點位資料查詢
 * - 統計資訊
 * - 搜尋功能
 * - 資料轉換
 */

/**
 * 獲取當前地圖視窗範圍內的空間點位資料
 * @param bbox 必需的邊界框 'minLng,minLat,maxLng,maxLat'
 * @param params 其他篩選參數
 * @param mapZoomLevel 地圖縮放等級
 */
export const getGrantLocations = async (
  bbox: string,
  params: Omit<GetPointsParams, 'bbox'> = {},
  mapZoomLevel: number = 12
): Promise<GeoJsonFeatureCollection> => {
  try {
    // 驗證bbox格式
    if (!bbox || !bbox.includes(',')) {
      throw new Error('bbox is required and must be in format: minLng,minLat,maxLng,maxLat')
    }

    // 建立查詢參數（bbox始終包含）
    const searchParams = new URLSearchParams()
    searchParams.append('bbox', bbox)
    searchParams.append('zoom_level', Math.round(mapZoomLevel).toString())

    // 添加其他篩選參數
    if (params.source_system) searchParams.append('source_system', params.source_system)
    if (params.apply_year_min) searchParams.append('apply_year_min', params.apply_year_min.toString())
    if (params.apply_year_max) searchParams.append('apply_year_max', params.apply_year_max.toString())
    if (params.limit) searchParams.append('limit', params.limit.toString())
    if (params.no_clustering) searchParams.append('no_clustering', params.no_clustering.toString())

    // 添加詳細篩選參數
    if (params.case_number) searchParams.append('case_number', params.case_number)
    if (params.applicant_name) searchParams.append('applicant_name', params.applicant_name)
    if (params.land_section) searchParams.append('land_section', params.land_section)
    if (params.land_number) searchParams.append('land_number', params.land_number)

    const url = `${GIS.POINTS}?${searchParams.toString()}`
    console.log('[gisService] 載入視窗範圍資料:', { bbox, zoom: mapZoomLevel, 聚合: mapZoomLevel < 12 })

    const response = await apiService.get<GeoJsonFeatureCollection>(url)

    console.log(`[gisService] 成功載入 ${response.features.length} 筆資料 (${
      response.meta.clustering?.enabled ? '聚合模式' : '個別點位模式'
    })`)

    return response

  } catch (error: unknown) {
    console.error('[gisService.getGrantLocations] 載入失敗:', error)

    if (error instanceof Error) {
      const status = (error as any)?.response?.status || 500
      const message = (error as any)?.response?.data?.detail || error.message || '載入地圖資料失敗'

      throw new ApplicationError({
        message,
        status,
        source: 'gisService.getGrantLocations',
        originalError: error
      })
    }

    throw new ApplicationError({
      message: '未知錯誤',
      status: 500,
      source: 'gisService.getGrantLocations',
      originalError: error
    })
  }
}

/**
 * 獲取 GIS 統計資訊
 */
export const getGisStatistics = async (): Promise<GisStatsResponse> => {
  try {
    console.log('[gisService.getGisStatistics] 獲取統計資訊')

    const response = await apiService.get<GisStatsResponse>(GIS.STATS)

    console.log('[gisService.getGisStatistics] 統計資訊:', response)
    return response

  } catch (error: unknown) {
    console.error('[gisService.getGisStatistics] API 調用失敗:', error)

    if (error instanceof Error) {
      const status = (error as any)?.response?.status || 500
      const message = (error as any)?.response?.data?.detail || error.message || '載入統計資料失敗'

      throw new ApplicationError({
        message,
        status,
        source: 'gisService.getGisStatistics',
        originalError: error
      })
    }

    throw new ApplicationError({
      message: '未知錯誤',
      status: 500,
      source: 'gisService.getGisStatistics',
      originalError: error
    })
  }
}

/**
 * 搜尋當前視窗範圍內的補助案件
 * @param bbox 必需的邊界框
 * @param params 搜尋參數
 */
export const searchGrantCases = async (
  bbox: string,
  params: SearchPointsParams
): Promise<GisSearchResponse> => {
  try {
    // 驗證bbox格式
    if (!bbox || !bbox.includes(',')) {
      throw new Error('bbox is required for search within current map view')
    }

    console.log('[gisService.searchGrantCases] 在視窗範圍內搜尋:', { bbox, params })

    // 建立查詢參數（基於當前視窗範圍）
    const searchParams = new URLSearchParams()

    // 添加 bbox 參數以在視窗範圍內搜尋
    searchParams.append('bbox', bbox)

    if (params.applicant_name) searchParams.append('applicant_name', params.applicant_name)
    if (params.land_section) searchParams.append('land_section', params.land_section)
    if (params.case_number) searchParams.append('case_number', params.case_number)
    if (params.limit) searchParams.append('limit', params.limit.toString())

    const url = `${GIS.SEARCH}?${searchParams.toString()}`

    const response = await apiService.get<GisSearchResponse>(url)

    console.log(`[gisService.searchGrantCases] 搜尋結果: ${response.count} 筆`)
    return response

  } catch (error: unknown) {
    console.error('[gisService.searchGrantCases] 搜尋失敗:', error)

    if (error instanceof Error) {
      const status = (error as any)?.response?.status || 500
      const message = (error as any)?.response?.data?.detail || error.message || '搜尋案件失敗'

      throw new ApplicationError({
        message,
        status,
        source: 'gisService.searchGrantCases',
        originalError: error
      })
    }

    throw new ApplicationError({
      message: '未知錯誤',
      status: 500,
      source: 'gisService.searchGrantCases',
      originalError: error
    })
  }
}

/**
 * 將搜尋結果轉換為 GeoJSON 格式
 */
export const convertSearchResultsToGeoJson = (searchResponse: GisSearchResponse): GeoJsonFeatureCollection => {
  try {
    console.log('[gisService.convertSearchResultsToGeoJson] 轉換', searchResponse.results.length, '筆搜尋結果')

    const features: GeoJsonFeature[] = searchResponse.results.map((result: GisSearchResult) => {
      // 解析幾何資料
      let geometry
      try {
        geometry = typeof result.geometry === 'string'
          ? JSON.parse(result.geometry)
          : result.geometry
      } catch (e) {
        // 如果解析失敗，使用座標創建 Point 幾何
        console.warn('[gisService.convertSearchResultsToGeoJson] 幾何解析失敗，使用座標創建 Point:', e)
        geometry = {
          type: 'Point',
          coordinates: [result.longitude, result.latitude]
        }
      }

      return {
        type: 'Feature',
        geometry,
        properties: {
          cluster: false, // 搜尋結果總是個別點位
          id: result.id,
          source_system: result.source_system as 'new_aerc' | 'legacy_farmdata',
          source_id: result.source_id,
          applicant_name: result.applicant_name,
          land_section: result.land_section,
          land_number: result.land_number,
          apply_year: result.apply_year,
          case_status: result.case_status,
          land_type: '', // 搜尋結果中沒有此欄位
          meta_data: {}
        }
      }
    })

    return {
      type: 'FeatureCollection',
      features,
      meta: {
        count: searchResponse.count,
        clustering: {
          enabled: false,
          strategy: 'individual_points'
        },
        filters: {
          applicant_name: searchResponse.search_criteria.applicant_name,
          land_section: searchResponse.search_criteria.land_section,
          case_number: searchResponse.search_criteria.case_number
        },
        performance: {
          limit_applied: searchResponse.count,
          optimization: 'limit_only'
        }
      }
    }

  } catch (error) {
    console.error('[gisService.convertSearchResultsToGeoJson] 轉換失敗:', error)
    throw new ApplicationError({
      message: '資料轉換失敗',
      status: 500,
      source: 'gisService.convertSearchResultsToGeoJson',
      originalError: error
    })
  }
}

/**
 * 從OpenLayers地圖實例獲取當前視窗邊界框
 * @param map OpenLayers地圖實例
 * @returns bbox字符串格式 'minLng,minLat,maxLng,maxLat'
 */
export const getMapBoundingBox = (map: unknown): string => {
  if (!map) {
    throw new Error('Map instance is required')
  }

  try {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const olMap = map as any // OpenLayers map type not available in scope
    const view = olMap.getView()
    const extent = view.calculateExtent(olMap.getSize())

    // 轉換為經緯度坐標
    // 需要從外部導入toLonLat，這裡假設已在調用處處理
    const bottomLeft = [extent[0], extent[1]]
    const topRight = [extent[2], extent[3]]

    // 轉換投影座標為WGS84（需要在調用處處理投影轉換）
    return `${bottomLeft[0]},${bottomLeft[1]},${topRight[0]},${topRight[1]}`
  } catch (error) {
    console.error('[gisService.getMapBoundingBox] 獲取地圖範圍失敗:', error)
    throw new Error('Failed to get map bounding box')
  }
}

/**
 * 驗證bbox格式
 */
export const validateBbox = (bbox: string): boolean => {
  if (!bbox || typeof bbox !== 'string') return false

  const coords = bbox.split(',').map(Number)
  return coords.length === 4 && coords.every(coord => !isNaN(coord))
}

/**
 * 驗證並標準化篩選參數
 */
export const validateAndNormalizeFilters = (filters: Partial<Omit<GetPointsParams, 'bbox'>>): Omit<GetPointsParams, 'bbox'> => {
  const normalized: Omit<GetPointsParams, 'bbox'> = {}

  // 驗證 source_system
  if (filters.source_system && ['new_aerc', 'legacy_farmdata'].includes(filters.source_system)) {
    normalized.source_system = filters.source_system
  }

  // 驗證年度範圍
  if (typeof filters.apply_year_min === 'number' && filters.apply_year_min >= 90 && filters.apply_year_min <= 150) {
    normalized.apply_year_min = filters.apply_year_min
  }

  if (typeof filters.apply_year_max === 'number' && filters.apply_year_max >= 90 && filters.apply_year_max <= 150) {
    normalized.apply_year_max = filters.apply_year_max
  }

  // 驗證 limit
  if (typeof filters.limit === 'number' && filters.limit > 0 && filters.limit <= 100000) {
    normalized.limit = filters.limit
  }

  // 驗證 no_clustering
  if (typeof filters.no_clustering === 'boolean') {
    normalized.no_clustering = filters.no_clustering
  }

  // 驗證詳細篩選參數
  if (typeof filters.case_number === 'string' && filters.case_number.trim()) {
    normalized.case_number = filters.case_number.trim()
  }

  if (typeof filters.applicant_name === 'string' && filters.applicant_name.trim()) {
    normalized.applicant_name = filters.applicant_name.trim()
  }

  if (typeof filters.land_section === 'string' && filters.land_section.trim()) {
    normalized.land_section = filters.land_section.trim()
  }

  if (typeof filters.land_number === 'string' && filters.land_number.trim()) {
    normalized.land_number = filters.land_number.trim()
  }

  return normalized
}
