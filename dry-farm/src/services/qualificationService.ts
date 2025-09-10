/**
 * Qualification Service - 重複案件查詢服務
 * 整合後端 qualification API，提供統一的查詢介面
 */

import { apiService } from './api/http'
import { QUALIFICATION } from './api/endpoints'
import type {
  QualificationSearchRequest,
  QualificationResponse,
  AreaCheckRequest,
  AreaCheckResponse,
  HealthCheckResponse,
  QualificationError
} from '@/types/qualification'

/**
 * Qualification 查詢服務
 * 遵循現有服務架構模式，提供統一的 API 介面
 */
export const qualificationService = {
  /**
   * 搜尋重複案件
   * @param request 查詢請求參數
   * @returns 查詢結果，包含重複案件列表和面積統計
   */
  async search(request: QualificationSearchRequest): Promise<QualificationResponse> {
    try {
      console.log('發送重複案件查詢請求:', JSON.stringify(request, null, 2))

      const response = await apiService.post<QualificationResponse>(
        QUALIFICATION.SEARCH,
        request as unknown as Record<string, unknown>
      )

      if (!response) {
        throw new Error('查詢回應為空')
      }

      console.log('查詢成功，結果:', response)
      return response
    } catch (error: unknown) {
      console.error('重複案件查詢失敗:', error)
      
      // 處理 API 錯誤
      const apiError = error as { response?: { data?: { detail?: string; message?: string }; status?: number }; message?: string }
      const qualificationError: QualificationError = {
        message: apiError.response?.data?.detail || apiError.message || '查詢失敗',
        code: apiError.response?.status?.toString(),
        details: apiError.response?.data?.message
      }
      
      throw qualificationError
    }
  },

  /**
   * 檢查原住民鄉
   * @param request 縣市鄉鎮資料
   * @returns 是否為原住民鄉及詳細資訊
   */
  async checkIndigenousArea(request: AreaCheckRequest): Promise<AreaCheckResponse> {
    try {
      console.log('檢查原住民鄉:', request)

      const response = await apiService.post<AreaCheckResponse>(
        QUALIFICATION.INDIGENOUS_CHECK,
        request as unknown as Record<string, unknown>
      )

      console.log('原住民鄉檢查結果:', response)
      return response
    } catch (error: unknown) {
      console.error('原住民鄉檢查失敗:', error)
      
      const apiError = error as { response?: { data?: { detail?: string; message?: string }; status?: number }; message?: string }
      const qualificationError: QualificationError = {
        message: apiError.response?.data?.detail || apiError.message || '原住民鄉檢查失敗',
        code: apiError.response?.status?.toString(),
        details: apiError.response?.data?.message
      }
      
      throw qualificationError
    }
  },

  /**
   * 檢查山坡地
   * @param request 縣市鄉鎮資料  
   * @returns 是否為山坡地及詳細資訊
   */
  async checkSlopeArea(request: AreaCheckRequest): Promise<AreaCheckResponse> {
    try {
      console.log('檢查山坡地:', request)

      const response = await apiService.post<AreaCheckResponse>(
        QUALIFICATION.SLOPE_AREA_CHECK,
        request as unknown as Record<string, unknown>
      )

      console.log('山坡地檢查結果:', response)
      return response
    } catch (error: unknown) {
      console.error('山坡地檢查失敗:', error)
      
      const apiError = error as { response?: { data?: { detail?: string; message?: string }; status?: number }; message?: string }
      const qualificationError: QualificationError = {
        message: apiError.response?.data?.detail || apiError.message || '山坡地檢查失敗',
        code: apiError.response?.status?.toString(),
        details: apiError.response?.data?.message
      }
      
      throw qualificationError
    }
  },

  /**
   * 健康檢查 - 檢測服務狀態
   * @returns 系統健康狀態
   */
  async healthCheck(): Promise<HealthCheckResponse> {
    try {
      const response = await apiService.get<HealthCheckResponse>(
        QUALIFICATION.HEALTH
      )

      console.log('Qualification 服務健康狀態:', response)
      return response
    } catch (error: unknown) {
      console.error('健康檢查失敗:', error)
      
      const apiError = error as { response?: { data?: { detail?: string; message?: string }; status?: number }; message?: string }
      const qualificationError: QualificationError = {
        message: apiError.response?.data?.detail || apiError.message || '服務檢查失敗',
        code: apiError.response?.status?.toString(),
        details: apiError.response?.data?.message
      }
      
      throw qualificationError
    }
  },

  /**
   * 建構查詢請求物件
   * @param queryType 查詢類型
   * @param landNumber 地號 (必填)
   * @param county 縣市 (可選)
   * @param town 鄉鎮 (可選)
   * @param section 地段 (可選)
   * @param includeStatistics 是否包含面積統計
   * @param years 查詢年度範圍
   * @returns 查詢請求物件
   */
  buildSearchRequest(
    queryType: 'general' | 'indigenous' | 'slope',
    landNumber: string,
    county?: string,
    town?: string,
    section?: string,
    includeStatistics: boolean = true,
    years?: string[]
  ): QualificationSearchRequest {
    return {
      query_type: queryType,
      params: {
        county: county || undefined,
        town: town || undefined,
        section: section || undefined,
        land_number: landNumber
      },
      options: {
        include_statistics: includeStatistics,
        years: years && years.length > 0 ? years.filter(y => y && y.trim()) : undefined // 過濾空值和空字串
      }
    }
  },

  /**
   * 建構區域檢查請求物件
   * @param county 縣市
   * @param town 鄉鎮
   * @returns 區域檢查請求物件  
   */
  buildAreaCheckRequest(county: string, town: string): AreaCheckRequest {
    return { county, town }
  }
}

export default qualificationService

// 導出類型以供其他模組使用
export type {
  QualificationSearchRequest,
  QualificationResponse,
  AreaCheckRequest,
  AreaCheckResponse,
  HealthCheckResponse,
  QualificationError
}