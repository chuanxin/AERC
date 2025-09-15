import { apiService } from './api/http'

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
 * @param countyLandCode 縣市地政代碼
 * @param townLandCode 鄉鎮地政代碼
 * @returns Promise<LandSection[]>
 */
export const fetchLandSectionsByLandCodes = async (
  countyLandCode: string,
  townLandCode: string
): Promise<LandSection[]> => {
  try {
    const response = await apiService.get<NlscLandSectionResponse>(
      `/spatial/land-sections/${countyLandCode}/${townLandCode}`
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
 * @returns Promise<NlscApiHealthResponse>
 */
export const checkNlscApiHealth = async (): Promise<NlscApiHealthResponse> => {
  try {
    const response = await apiService.get<NlscApiHealthResponse>('/spatial/land-sections/health')
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