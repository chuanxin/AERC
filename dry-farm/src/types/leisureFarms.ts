/**
 * 休閒農場資料類型定義
 * 對應後端 api/src/schemas/leisure_farms.py
 */

/** 休閒農場單筆資料 */
export interface LeisureFarmItem {
  /** 主鍵 ID */
  id: number
  /** 農場名稱 */
  farmName: string
  /** 縣市名稱 */
  county: string
  /** 鄉鎮市區名稱 */
  township: string
  /** 農場地址 */
  address: string | null
  /** 聯絡電話 */
  phone: string | null
  /** 農場網站 */
  webUrl: string | null
  /** 認證起始日期 */
  certifyStartDate: string | null
  /** 認證結束日期 */
  certifyEndDate: string | null
  /** 認證項目 */
  identifyItem: string | null
  /** 農場照片 URL */
  photoUrl: string | null
  /** 經度 WGS84 */
  longitude: number
  /** 緯度 WGS84 */
  latitude: number
  /** 與查詢點的距離（公尺） */
  distanceMeters: number | null
}

/** 鄰近休閒農場查詢回應 */
export interface LeisureFarmNearbyResponse {
  /** 查詢是否成功 */
  success: boolean
  /** 鄰近農場列表 */
  farms: LeisureFarmItem[]
  /** 總筆數 */
  totalCount: number
  /** 查詢點座標 */
  queryPoint: { longitude: number; latitude: number } | null
  /** 查詢半徑（公尺） */
  searchRadiusMeters: number
  /** 訊息 */
  message: string | null
}

/** 休閒農場重疊檢查回應 */
export interface LeisureFarmCheckResponse {
  /** 查詢是否成功 */
  success: boolean
  /** 是否有鄰近農場 */
  hasNearbyFarms: boolean
  /** 最近的農場 */
  nearestFarm: LeisureFarmItem | null
  /** 範圍內農場數量 */
  farmsWithinRadius: number
  /** 訊息 */
  message: string | null
}

/** 依地區查詢休閒農場回應 */
export interface LeisureFarmByLocationResponse {
  /** 查詢是否成功 */
  success: boolean
  /** 農場列表 */
  farms: LeisureFarmItem[]
  /** 總筆數 */
  totalCount: number
  /** 查詢縣市 */
  county: string | null
  /** 查詢鄉鎮 */
  township: string | null
}

/** 休閒農場統計回應 */
export interface LeisureFarmStatsResponse {
  /** 查詢是否成功 */
  success: boolean
  /** 農場總數 */
  totalFarms: number
  /** 依縣市統計 */
  byCounty: Record<string, number>
  /** 最後同步時間 */
  lastSynced: string | null
}

/** 鄰近查詢請求參數 */
export interface NearbySearchRequest {
  /** 查詢點經度 WGS84 */
  longitude: number
  /** 查詢點緯度 WGS84 */
  latitude: number
  /** 查詢半徑（公尺），預設 5000m */
  radiusMeters?: number
  /** 最大回傳筆數，預設 10 */
  limit?: number
}

/** 依地區查詢請求參數 */
export interface LocationSearchRequest {
  /** 縣市名稱 */
  county?: string
  /** 鄉鎮市區名稱 */
  township?: string
}

/** 快速檢查請求參數 */
export interface CheckNearbyRequest {
  /** 查詢點經度 WGS84 */
  longitude: number
  /** 查詢點緯度 WGS84 */
  latitude: number
  /** 查詢半徑（公尺），預設 1000m */
  radiusMeters?: number
}
