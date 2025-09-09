/**
 * Qualification 重複案件查詢系統的 TypeScript 類型定義
 * 對應後端 api/src/schemas/qualification.py
 */

export type QualificationQueryType = 'general' | 'indigenous' | 'slope'

export interface LocationParams {
  county?: string
  town?: string
  section?: string
  land_number?: string
}

export interface QueryOptions {
  include_statistics?: boolean
  years?: string[]
}

export interface QualificationSearchRequest {
  query_type: QualificationQueryType
  params: LocationParams
  options?: QueryOptions
}

export interface GrantCaseItem {
  id: number
  source_system: string
  source_id?: number
  grant_id: string
  case_number?: string
  case_type: string
  status: string
  land_section: string
  land_number: string
  application_year: number
  applicant: string
  department?: string
  approved_area: string // Decimal as string
  land_registered_area?: string // Decimal as string - 地籍登記面積
  crops?: Array<{
    category?: string
    name?: string
    area?: string
  }>
  is_aboriginal_area?: boolean
}

export interface AreaStatistics {
  land_total_area: string      // Decimal as string
  used_area: string           // Decimal as string
  remaining_area: string      // Decimal as string
  micro_irrigation_area: string     // Decimal as string
  remaining_micro_area: string      // Decimal as string
  sprinkler_area: string           // Decimal as string
  remaining_sprinkler_area: string  // Decimal as string
}

export interface QueryInfo {
  query_type: QualificationQueryType
  location_description: string
  search_params: Record<string, unknown>
  years_searched: string[]
}

export interface ResponseMetadata {
  total_records: number
  search_time: string
  query_hash: string
  response_time_ms: number
}

export interface QualificationResponse {
  query_info: QueryInfo
  results: GrantCaseItem[]
  statistics?: AreaStatistics
  metadata: ResponseMetadata
}

export interface AreaCheckRequest {
  county: string
  town: string
}

export interface AreaCheckResponse {
  is_qualified: boolean
  area_type: 'indigenous' | 'slope' | 'general'
  details?: Record<string, unknown>
}

export interface HealthCheckResponse {
  status: string
  timestamp: string
  database_connection: boolean
  models_registered: number
}

// 前端特有的類型定義
export interface QualificationSearchParams {
  county: string
  town: string
  section?: string
  landNumber?: string
  parentLandNumber?: string
  childLandNumber?: string
}

export interface IndigenousSearchParams {
  county: string
  town: string
}

export interface RecentSearch {
  county: string
  town: string
  section?: string
  landNumber?: string
  searchTime: Date
  queryType: QualificationQueryType
}

// API 錯誤類型
export interface QualificationError {
  message: string
  code?: string
  details?: string
}

// 查詢狀態類型
export interface QualificationState {
  isLoading: boolean
  isIndigenousLoading: boolean
  error: string | null
  results: GrantCaseItem[]
  statistics?: AreaStatistics
  metadata?: ResponseMetadata
  recentSearches: RecentSearch[]
  isIndigenousArea: boolean
  isIndigenousAreaChecked: boolean
  showNoResultMessage: boolean
}
