import { apiService } from './api/http'
import { NLSC } from './api/endpoints'
import { ApplicationError } from '@/utils/asyncHelpers'

// 地段資料介面
export interface LandSection {
  name: string
  code: string
  office: string
  office_name: string
  county_land_code: string
  town_land_code: string
}

// NLSC API 回應介面
export interface NlscLandSectionResponse {
  county_land_code: string
  town_land_code: string
  sections: LandSection[]
  count: number
  source: string
  api_url: string
}

// NLSC API 健康狀態介面
export interface NlscApiHealthResponse {
  nlsc_api_status: 'online' | 'offline' | 'timeout' | 'error'
  status_code?: number
  test_url?: string
  timestamp: string
  error?: string
}

/**
 * 透過地政代碼取得地段清單
 *
 * ✅ 端點更新（2025-12-12）：
 * - 舊路徑: /spatial/land-sections/{county}/{town} (@deprecated)
 * - 新路徑: /nlsc/sections/{county}/{town}
 *
 * @param countyLandCode 縣市地政代碼
 * @param townLandCode 鄉鎮地政代碼
 * @returns Promise<LandSection[]>
 */
export const fetchLandSectionsByLandCodes = async (
  countyLandCode: string,
  townLandCode: string
): Promise<LandSection[]> => {
  try {
    // ✅ 正確使用：NLSC.SECTIONS 是函數，需要調用並傳入參數
    const response = await apiService.get<NlscLandSectionResponse>(
      NLSC.SECTIONS(countyLandCode, townLandCode)
    )

    return response.sections || []
  } catch (error) {
    console.error('Failed to fetch land sections from NLSC API:', error)

    // 如果外部 API 失敗，返回空陣列，不拋出錯誤
    // 這樣可以讓系統繼續運作，只是地段選項會是空的
    return []
  }
}

/**
 * 檢查 NLSC API 健康狀態
 *
 * ✅ 端點更新（2025-12-12）：
 * - 舊路徑: /spatial/land-sections/health (@deprecated)
 * - 新路徑: /nlsc/health
 *
 * @returns Promise<NlscApiHealthResponse>
 */
export const checkNlscApiHealth = async (): Promise<NlscApiHealthResponse> => {
  try {
    // ✅ 使用端點常量而非硬編碼路徑
    const response = await apiService.get<NlscApiHealthResponse>(NLSC.HEALTH)
    return response
  } catch (error) {
    console.error('Failed to check NLSC API health:', error)

    return {
      nlsc_api_status: 'error',
      timestamp: new Date().toISOString(),
      error: error instanceof Error ? error.message : 'Unknown error'
    }
  }
}
