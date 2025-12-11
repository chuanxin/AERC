/**
 * Leisure Farms Service - 休閒農場資料查詢服務
 * 整合後端 leisure-farms API，提供統一的查詢介面
 */

import { apiService } from './api/http'
import { LEISURE_FARMS } from './api/endpoints'
import type {
  LeisureFarmNearbyResponse,
  LeisureFarmCheckResponse,
  LeisureFarmByLocationResponse,
  LeisureFarmStatsResponse,
  NearbySearchRequest,
  CheckNearbyRequest,
} from '@/types/leisureFarms'

/**
 * 休閒農場查詢服務
 */
export const leisureFarmsService = {
  /**
   * 查詢指定座標附近的休閒農場
   * @param request 鄰近查詢請求參數
   * @returns 鄰近農場列表
   */
  async searchNearby(request: NearbySearchRequest): Promise<LeisureFarmNearbyResponse> {
    try {
      console.log('查詢鄰近休閒農場:', request)

      const response = await apiService.post<LeisureFarmNearbyResponse>(
        LEISURE_FARMS.NEARBY,
        {
          longitude: request.longitude,
          latitude: request.latitude,
          radius_meters: request.radiusMeters ?? 5000,
          limit: request.limit ?? 10,
        }
      )

      console.log('鄰近休閒農場查詢結果:', response)
      return response
    } catch (error: unknown) {
      console.error('鄰近休閒農場查詢失敗:', error)
      throw error
    }
  },

  /**
   * 快速檢查指定座標附近是否有休閒農場
   * @param request 檢查請求參數
   * @returns 檢查結果
   */
  async checkNearby(request: CheckNearbyRequest): Promise<LeisureFarmCheckResponse> {
    try {
      console.log('檢查鄰近休閒農場:', request)

      const params = new URLSearchParams({
        longitude: request.longitude.toString(),
        latitude: request.latitude.toString(),
        radius_meters: (request.radiusMeters ?? 1000).toString(),
      })

      const response = await apiService.get<LeisureFarmCheckResponse>(
        `${LEISURE_FARMS.CHECK}?${params.toString()}`
      )

      console.log('鄰近休閒農場檢查結果:', response)
      return response
    } catch (error: unknown) {
      console.error('鄰近休閒農場檢查失敗:', error)
      throw error
    }
  },

  /**
   * 依縣市鄉鎮查詢休閒農場
   * @param county 縣市名稱
   * @param township 鄉鎮市區名稱
   * @returns 農場列表
   */
  async searchByLocation(
    county?: string,
    township?: string
  ): Promise<LeisureFarmByLocationResponse> {
    try {
      console.log('依地區查詢休閒農場:', { county, township })

      const params = new URLSearchParams()
      if (county) params.append('county', county)
      if (township) params.append('township', township)

      const url = params.toString()
        ? `${LEISURE_FARMS.BY_LOCATION}?${params.toString()}`
        : LEISURE_FARMS.BY_LOCATION

      const response = await apiService.get<LeisureFarmByLocationResponse>(url)

      console.log('依地區查詢結果:', response)
      return response
    } catch (error: unknown) {
      console.error('依地區查詢休閒農場失敗:', error)
      throw error
    }
  },

  /**
   * 取得休閒農場統計資料
   * @returns 統計資料
   */
  async getStatistics(): Promise<LeisureFarmStatsResponse> {
    try {
      console.log('取得休閒農場統計資料')

      const response = await apiService.get<LeisureFarmStatsResponse>(
        LEISURE_FARMS.STATS
      )

      console.log('休閒農場統計:', response)
      return response
    } catch (error: unknown) {
      console.error('取得休閒農場統計失敗:', error)
      throw error
    }
  },
}
