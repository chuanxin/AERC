import { apiService } from './api/http'
import { ApplicationError } from '@/utils/asyncHelpers'
import { GRANTS } from './api/endpoints'
import type { GrantCreateRequest } from '@/types/grantForms'
import { fieldMappingMiddleware, FieldMappingValidator, type DataRecord } from '@/types/fieldMappings'
import { GrantStorage, type GrantData } from '@/utils/grant-storage'

// Enhanced Types
export interface GrantCreateResponse {
  id: number;
  case_number: string;
  year: number;
  applicant_name: string;
  status: string;
  received_date: string;
  received_time: string;
  office_id?: number;
  is_disaster_case: boolean;
  disaster_case_description?: string;
  undertracker?: string;
  active_version?: {
    id: number;
    version: string;
    comment?: string;
    created_at?: string;
  };
}

export interface GrantStepData {
  id: number;
  case_number: string;
  current_step: number;
  status: string;
  [key: string]: unknown; // Allow for step-specific fields
}

// 新增列表查詢相關介面
export interface GrantListItem {
  id: number;
  case_number: string;
  year: number;
  applicant_name: string;
  applicant_id?: string;
  county?: string;
  town?: string;
  village?: string;
  office: string;
  office_id?: number;
  undertracker?: string;
  facility_type?: string;
  facility_area?: number;
  facility_area_m2?: number;
  status: string;
  current_step: number;
  is_disaster_case?: boolean;
  created_at: string;
  modified_at: string;
  created_by?: {
    id: number;
    username: string;
    full_name: string;
  };
  is_legacy?: boolean; // 是否為舊版案件
}

export interface GrantListParams {
  year?: number;
  office_id?: number;
  search?: string;
  skip?: number;
  limit?: number;
  status?: string;
}

// 服務狀態追蹤
export interface ServiceStatus {
  apiAvailable: boolean;
  lastApiCheck: Date;
  fallbackMode: boolean;
}

export const createGrant = async (data: GrantCreateRequest): Promise<GrantCreateResponse> => {
  try {
    console.log('發送建立專案請求，資料:', data)
    const response = await apiService.post<GrantCreateResponse>(GRANTS.CREATE, data as unknown as Record<string, unknown>)
    return response
  } catch (error: unknown) {
    if (error instanceof Error) {
      const status = (error as { response?: { status?: number } })?.response?.status || 500
      // const message = (error as { response?: { data?: { detail?: string } } })?.response?.data?.detail || error.message || '建立專案失敗'

      // throw new ApplicationError({
      //   message,
      //   status,
      //   source: 'grantsService.createGrant',
      //   originalError: error
      // })

      if (status === 422) {
        // Get validation errors from the response
        const validationErrors = (error as {
          response?: {
            data?: {
              detail?: Array<{loc: string[], msg: string, type: string}>
            }
          }
        })?.response?.data?.detail || []

        // Format validation errors into a readable message
        const errorMessages = validationErrors.map(err => {
          const field = err.loc.slice(1).join('.') // Remove 'body' prefix
          return `${field}: ${err.msg}`
        }).join('\n')

        throw new ApplicationError({
          message: `資料驗證失敗:\n${errorMessages}`,
          status,
          source: 'grantsService.createGrant',
          originalError: error
        })
      } else {
        // Handle other errors
        const message = (error as { response?: { data?: { detail?: string } } })?.response?.data?.detail || error.message || '建立專案失敗'
        throw new ApplicationError({
          message,
          status,
          source: 'grantsService.createGrant',
          originalError: error
        })
      }
    } else {
      throw new ApplicationError({
        message: '建立專案發生未知錯誤',
        status: 500,
        source: 'grantsService.createGrant',
        originalError: error
      })
    }
  }
}

export const getGrantByCaseNumber = async (caseNumber: string): Promise<GrantCreateResponse> => {
  try {
    // const url = mapApiPath(GRANTS.BY_CASE_NUMBER(caseNumber));
    // const response = await apiService.get(url);
    const response = await apiService.get(GRANTS.BY_CASE_NUMBER(caseNumber))
    return response as GrantCreateResponse
  } catch (error: unknown) {
    return handleApiError(error, 'grantsService.getGrantByCaseNumber')
  }
}

export const getGrantStepData = async (caseNumber: string, step: number): Promise<GrantStepData> => {
  try {
    const endpoint = GRANTS.STEP(caseNumber, step)
    console.log(`📡 [getGrantStepData] Calling API endpoint: ${endpoint}`)
    console.log(`📡 [getGrantStepData] Parameters: caseNumber=${caseNumber}, step=${step}`)

    const response = await apiService.get(endpoint)
    console.log(`📡 [getGrantStepData] API response:`, response)

    // 使用字段映射中间件转换后端数据为前端格式
    const transformedData = fieldMappingMiddleware.afterResponse(step, response as DataRecord, endpoint)

    // 在开发模式下验证数据完整性
    if (import.meta.env.DEV) {
      FieldMappingValidator.validateApiResponse(step, response as DataRecord, endpoint)
    }

    return transformedData as GrantStepData
  } catch (error: unknown) {
    console.error(`❌ [getGrantStepData] API error for step ${step}:`, error)
    return handleApiError(error, 'grantsService.getGrantStepData')
  }
}

// Enhanced interface for step data updates with tracking metadata
export interface GrantStepDataUpdateRequest extends Record<string, unknown> {
  data: Record<string, unknown>;
  action_type?: string;
  changed_fields?: string[];
  old_value?: Record<string, unknown>;
  session_id?: string;
  notes?: string;
}

export const updateGrantStepData = async (caseNumber: string, step: number, data: Record<string, unknown>): Promise<GrantStepData> => {
  try {
    const endpoint = GRANTS.STEP(caseNumber, step)

    // 使用字段映射中间件转换前端数据为后端格式
    const transformedData = fieldMappingMiddleware.beforeRequest(step, data as DataRecord, endpoint)

    const response = await apiService.put(endpoint, transformedData)

    // 使用字段映射中间件转换后端响应为前端格式
    const transformedResponse = fieldMappingMiddleware.afterResponse(step, response as DataRecord, endpoint)

    return transformedResponse as GrantStepData
  } catch (error: unknown) {
    return handleApiError(error, 'grantsService.updateGrantStepData')
  }
}

// Enhanced version with detailed tracking support
export const updateGrantStepDataWithTracking = async (
  caseNumber: string,
  step: number,
  updateRequest: GrantStepDataUpdateRequest
): Promise<GrantStepData> => {
  try {
    const response = await apiService.put(GRANTS.STEP(caseNumber, step), updateRequest as Record<string, unknown>)
    return response as GrantStepData
  } catch (error: unknown) {
    return handleApiError(error, 'grantsService.updateGrantStepDataWithTracking')
  }
}

export const updateCurrentStep = async (caseNumber: string, currentStep: number): Promise<{ success: boolean }> => {
  try {
    const response = await apiService.put(GRANTS.UPDATE_CURRENT_STEP(caseNumber), { current_step: currentStep })
    return response as { success: boolean }
  } catch (error: unknown) {
    return handleApiError(error, 'grantsService.updateCurrentStep')
  }
}

// =============================================================================
// 核心 API 服務層
// =============================================================================

/**
 * 取得案件列表
 */
export const getGrantsFromAPI = async (params: GrantListParams = {}): Promise<GrantListItem[]> => {
  try {
    const searchParams = new URLSearchParams()

    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        searchParams.append(key, String(value))
      }
    })

    const url = `${GRANTS.LIST}?${searchParams.toString()}`
    console.log(`📡 [getGrants] API call to: ${url}`)

    const response = await apiService.get<GrantListItem[]>(url)
    console.log(`📡 [getGrants] Received ${Array.isArray(response) ? response.length : 0} grants`)

    return response
  } catch (error) {
    console.error('📡 [getGrants] API error:', error)
    throw handleApiError(error, 'grantsService.getGrants')
  }
}

/**
 * 刪除案件
 */
export const deleteGrant = async (grantId: number): Promise<void> => {
  try {
    await apiService.delete(`${GRANTS.LIST}/${grantId}`)
    console.log(`📡 [deleteGrant] Successfully deleted grant ${grantId}`)
  } catch (error) {
    console.error(`📡 [deleteGrant] Failed to delete grant ${grantId}:`, error)
    throw handleApiError(error, 'grantsService.deleteGrant')
  }
}

// =============================================================================
// 混合模式服務（API + localStorage）
// =============================================================================

/**
 * 混合模式服務：優先使用 API，失敗時降級到 localStorage
 */
export class HybridGrantService {
  private useApi = true
  private serviceStatus: ServiceStatus = {
    apiAvailable: true,
    lastApiCheck: new Date(),
    fallbackMode: false
  }

  /**
   * 取得服務狀態
   */
  getServiceStatus(): ServiceStatus {
    return { ...this.serviceStatus }
  }

  /**
   * 取得案件列表（混合模式）
   */
  async getGrants(params: GrantListParams = {}): Promise<GrantListItem[]> {
    if (this.useApi) {
      try {
        const grants = await getGrantsFromAPI(params)
        this.serviceStatus.apiAvailable = true
        this.serviceStatus.fallbackMode = false
        this.serviceStatus.lastApiCheck = new Date()
        return grants
      } catch (error) {
        console.warn('📡 [HybridService] API failed, falling back to localStorage:', error)
        this.useApi = false
        this.serviceStatus.apiAvailable = false
        this.serviceStatus.fallbackMode = true
        this.serviceStatus.lastApiCheck = new Date()
        return this.getGrantsFromLocalStorage(params)
      }
    } else {
      return this.getGrantsFromLocalStorage(params)
    }
  }

  /**
   * 從 localStorage 獲取案件列表
   */
  private getGrantsFromLocalStorage(params: GrantListParams): GrantListItem[] {
    const localGrants = GrantStorage.getAllGrants()

    let results = Object.entries(localGrants).map(([caseNumber, grantData]) =>
      this.transformLocalDataToListItem(caseNumber, grantData)
    )

    // 應用篩選條件
    if (params.year) {
      results = results.filter(item => item.year === params.year)
    }

    if (params.search) {
      const searchTerm = params.search.toLowerCase()
      results = results.filter(item =>
        item.applicant_name.toLowerCase().includes(searchTerm) ||
        item.case_number.toLowerCase().includes(searchTerm) ||
        (item.applicant_id && item.applicant_id.toLowerCase().includes(searchTerm))
      )
    }

    // 排序（最新的在前）
    results.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())

    // 分頁
    if (params.skip || params.limit) {
      const skip = params.skip || 0
      const limit = params.limit || 100
      results = results.slice(skip, skip + limit)
    }

    return results
  }

  /**
   * 轉換本地資料為列表項目格式
   */
  private transformLocalDataToListItem(caseNumber: string, grantData: GrantData): GrantListItem {
    return {
      id: parseInt(caseNumber.replace(/\D/g, '')) || 0, // 臨時 ID
      case_number: caseNumber,
      year: parseInt(caseNumber.substring(0, 3)) || new Date().getFullYear() - 1911,
      applicant_name: grantData.applicantName || '未填寫',
      office: grantData.officeName || '未設定',
      office_id: 0, // 預設值，需要從 API 對應
      facility_type: this.extractFacilityType(grantData),
      facility_area_m2: this.extractFacilityArea(grantData),
      status: grantData.stepName || '處理中',
      current_step: grantData.currentStep || 1,
      is_disaster_case: grantData.isDisasterCase,
      undertracker: grantData.undertracker,
      created_at: grantData.createdAt || new Date().toISOString(),
      modified_at: grantData.updatedAt || new Date().toISOString()
    }
  }

  /**
   * 從步驟資料中提取設施類型
   */
  private extractFacilityType(grantData: GrantData): string {
    const step4Data = grantData.stepsData?.[4] || {}
    const typeMap: Record<string, string> = {
      '穿孔管系統': '穿孔管',
      '噴頭式系統': '噴灌',
      '微噴系統': '微噴',
      '滴灌系統': '滴灌',
      '其他': '其他'
    }
    return typeMap[step4Data.irrigationType as string] || '未設定'
  }

  /**
   * 從步驟資料中提取設施面積
   */
  private extractFacilityArea(grantData: GrantData): number {
    const step2Data = grantData.stepsData?.[2] || {}
    const areaHa = parseFloat(String(step2Data.facilityAreaHa || step2Data.landAreaHa || '0'))
    return Math.round(areaHa * 10000) // 轉換為平方公尺
  }

  /**
   * 嘗試重新連接 API
   */
  async tryReconnectApi(): Promise<boolean> {
    try {
      // 嘗試一個簡單的 API 呼叫
      await getGrantsFromAPI({ limit: 1 })
      this.useApi = true
      this.serviceStatus.apiAvailable = true
      this.serviceStatus.fallbackMode = false
      this.serviceStatus.lastApiCheck = new Date()
      console.log('📡 [HybridService] API reconnected successfully')
      return true
    } catch (error) {
      console.warn('📡 [HybridService] API still unavailable:', error)
      return false
    }
  }

  /**
   * 刪除案件（混合模式）
   */
  async deleteGrant(item: GrantListItem): Promise<void> {
    if (this.useApi && this.serviceStatus.apiAvailable) {
      try {
        await deleteGrant(item.id)
        console.log(`📡 [HybridService] Successfully deleted grant ${item.case_number} via API`)
      } catch (error) {
        console.warn(`📡 [HybridService] API delete failed, falling back to localStorage:`, error)
        GrantStorage.deleteGrant(item.case_number)
      }
    } else {
      GrantStorage.deleteGrant(item.case_number)
      console.log(`📡 [HybridService] Deleted grant ${item.case_number} from localStorage`)
    }
  }
}

// =============================================================================
// 快取服務
// =============================================================================

export class GrantCacheService {
  private cache = new Map<string, { data: any; timestamp: number }>()
  private readonly CACHE_DURATION = 5 * 60 * 1000 // 5分鐘

  /**
   * 取得快取資料
   */
  get<T>(key: string): T | null {
    const cached = this.cache.get(key)
    if (cached && Date.now() - cached.timestamp < this.CACHE_DURATION) {
      return cached.data
    }
    return null
  }

  /**
   * 設定快取資料
   */
  set<T>(key: string, data: T): void {
    this.cache.set(key, { data, timestamp: Date.now() })
  }

  /**
   * 清除快取
   */
  clear(pattern?: string): void {
    if (pattern) {
      const regex = new RegExp(pattern)
      for (const key of this.cache.keys()) {
        if (regex.test(key)) {
          this.cache.delete(key)
        }
      }
    } else {
      this.cache.clear()
    }
  }

  /**
   * 取得快取統計
   */
  getStats() {
    return {
      size: this.cache.size,
      keys: Array.from(this.cache.keys())
    }
  }
}

// =============================================================================
// 單例服務實例
// =============================================================================

export const hybridGrantService = new HybridGrantService()
export const grantCacheService = new GrantCacheService()

// Helper function for error handling
const handleApiError = (error: unknown, source: string): never => {
  if (error instanceof Error) {
    const status = (error as { response?: { status?: number } })?.response?.status || 500

    if (status === 422) {
      // Handle validation errors
      const validationErrors = (error as {
        response?: {
          data?: {
            detail?: Array<{loc: string[], msg: string, type: string}>
          }
        }
      })?.response?.data?.detail || []

      const errorMessages = validationErrors.map(err => {
        const field = err.loc.slice(1).join('.')
        return `${field}: ${err.msg}`
      }).join('\n')

      throw new ApplicationError({
        message: `資料驗證失敗:\n${errorMessages}`,
        status,
        source,
        originalError: error
      })
    } else {
      // Handle other errors
      const message = (error as { response?: { data?: { detail?: string } } })?.response?.data?.detail || error.message || '操作失敗'
      throw new ApplicationError({
        message,
        status,
        source,
        originalError: error
      })
    }
  } else {
    throw new ApplicationError({
      message: '發生未知錯誤',
      status: 500,
      source,
      originalError: error
    })
  }
}
