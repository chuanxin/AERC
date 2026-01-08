import { apiService } from './api/http'
import { ApplicationError } from '@/utils/asyncHelpers'
import { GRANTS } from './api/endpoints'
import type { GrantCreateRequest } from '@/types/grantForms'
import { fieldMappingMiddleware, FieldMappingValidator, type DataRecord } from '@/types/fieldMappings'
import { GrantStorage, type GrantData } from '@/utils/grant-storage'

// 🔥 Linus式修復：與後端 GrantOutSchema (pydantic_model_creator) 完全對應
// 這是整個專案的**唯一資料來源** (Single Source of Truth)
export interface GrantCreateResponse {
  // 系統資訊
  id: number;
  case_number: string;
  year: number;
  sn: number; // 流水號
  status: string;
  current_step: number;

  // 申請人完整資訊 (Step1 所有欄位)
  applicant_name: string;
  applicant_id: string; // 🔥 新增：身分證字號
  applicant_phone: string; // 🔥 新增：電話

  // 地址完整資訊 (Step1 所有欄位)
  county: string; // 🔥 新增：縣市
  town: string; // 🔥 新增：鄉鎮
  village?: string; // 🔥 新增：村里
  address: string; // 🔥 新增：詳細地址

  // 承辦資訊
  office: string; // 🔥 新增：管理處名稱
  office_id?: number;
  undertracker?: string;

  // 災害案件資訊
  is_disaster_case: boolean;
  disaster_case_description?: string;

  // 建檔資訊
  received_date: string;
  received_time: string;

  // 時間戳記
  created_at: string; // 🔥 新增
  modified_at: string; // 🔥 新增

  // 建立人資訊
  created_by?: { // 🔥 新增
    id: number;
    username: string;
    full_name: string;
  };

  // 版本資訊
  active_version?: {
    id: number;
    version: string;
    comment?: string;
    created_at?: string;
  };

  // 歷史資料標記
  is_legacy?: boolean; // 🔥 新增
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
  land_locations?: string; // 土地位置摘要（僅縣市鄉鎮地段，不含面積）
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

// =============================================================================
// 年度補助額度限制相關介面
// =============================================================================

/**
 * 申請人單筆補助案件摘要
 */
export interface ApplicantGrantSummaryItem {
  case_number: string;
  status: string;
  subsidy_amount: number;
  created_at: string;
}

/**
 * 申請人年度補助額度摘要
 */
export interface ApplicantSubsidySummary {
  applicant_id: string;
  applicant_name: string;
  year: number;
  total_subsidy_amount: number;  // 已用補助額度
  remaining_amount: number;       // 剩餘可用額度
  subsidy_limit: number;          // 年度補助上限 (500,000)
  grant_count: number;            // 案件數量
  grants: ApplicantGrantSummaryItem[];
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

export const getGrantByCaseNumber = async (caseNumber: string, grantsId?: number): Promise<GrantCreateResponse> => {
  try {
    // 🔥 支援 grantsId 參數以區分重複的 case_number
    let url = GRANTS.BY_CASE_NUMBER(caseNumber)
    if (grantsId !== undefined) {
      url += `?grants_id=${grantsId}`
    }
    const response = await apiService.get(url)
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

    // 🔥 Linus式修復：Step1 後端期望前端格式（camelCase），不轉換
    // Step2-8 需要轉換為後端格式（snake_case）
    let requestData = data
    if (step !== 1) {
      requestData = fieldMappingMiddleware.beforeRequest(step, data as DataRecord, endpoint)
    }

    const response = await apiService.put(endpoint, requestData)

    // 使用字段映射中间件转換後端響應為前端格式
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
    const endpoint = GRANTS.STEP(caseNumber, step)

    // 🔥 Linus式修復：Step1 後端期望前端格式（camelCase），不轉換
    // Step2-8 需要轉換為後端格式（snake_case）
    if (step !== 1) {
      const transformedData = fieldMappingMiddleware.beforeRequest(step, updateRequest.data as DataRecord, endpoint)
      updateRequest = {
        ...updateRequest,
        data: transformedData
      }
    }

    const response = await apiService.put(endpoint, updateRequest as Record<string, unknown>)

    // 使用字段映射中间件转换后端响應為前端格式
    const transformedResponse = fieldMappingMiddleware.afterResponse(step, response as DataRecord, endpoint)

    return transformedResponse as GrantStepData
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

export const updateGrantStatus = async (caseNumber: string, status: string): Promise<{ success: boolean; status: string }> => {
  try {
    const response = await apiService.patch(GRANTS.UPDATE_STATUS(caseNumber), { status })
    return response as { success: boolean; status: string }
  } catch (error: unknown) {
    return handleApiError(error, 'grantsService.updateGrantStatus')
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
    // 🔥 Linus式修復：使用正確的 DELETE endpoint 函數
    await apiService.delete(GRANTS.DELETE(grantId))
    console.log(`📡 [deleteGrant] Successfully deleted grant ${grantId}`)
  } catch (error) {
    console.error(`📡 [deleteGrant] Failed to delete grant ${grantId}:`, error)
    throw handleApiError(error, 'grantsService.deleteGrant')
  }
}

/**
 * 查詢申請人年度補助額度摘要
 * @param applicantId 申請人身分證字號
 * @param year 申請年度（民國年）
 * @param currentGrantId 當前案件ID（用於排除自己，避免重複計算）
 */
export const getApplicantSubsidySummary = async (
  applicantId: string,
  year: number,
  currentGrantId?: number
): Promise<ApplicantSubsidySummary> => {
  try {
    let url = GRANTS.APPLICANT_SUBSIDY_SUMMARY(applicantId, year)

    // 如果有提供 currentGrantId，加入 query parameter
    if (currentGrantId !== undefined) {
      url += `?current_grant_id=${currentGrantId}`
    }

    console.log(`📡 [getApplicantSubsidySummary] API call to: ${url}`)
    const response = await apiService.get<ApplicantSubsidySummary>(url)
    console.log(`📡 [getApplicantSubsidySummary] Received subsidy summary:`, response)

    return response
  } catch (error) {
    console.error('📡 [getApplicantSubsidySummary] API error:', error)
    throw handleApiError(error, 'grantsService.getApplicantSubsidySummary')
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
    console.log('💾 [getGrantsFromLocalStorage] 從 localStorage 載入資料，參數:', params)
    const localGrants = GrantStorage.getAllGrants()

    let results = Object.entries(localGrants).map(([caseNumber, grantData]) =>
      this.transformLocalDataToListItem(caseNumber, grantData)
    )

    console.log('💾 [getGrantsFromLocalStorage] 原始資料筆數:', results.length)

    // 應用篩選條件
    if (params.year) {
      results = results.filter(item => item.year === params.year)
      console.log('💾 [getGrantsFromLocalStorage] 年度篩選後:', results.length, '筆 (年度:', params.year, ')')
    }

    if (params.office_id !== undefined && params.office_id !== null) {
      results = results.filter(item => item.office_id === params.office_id)
      console.log('💾 [getGrantsFromLocalStorage] 管理處篩選後:', results.length, '筆 (office_id:', params.office_id, ')')
    }

    if (params.search) {
      const searchTerm = params.search.toLowerCase()
      results = results.filter(item =>
        item.applicant_name.toLowerCase().includes(searchTerm) ||
        item.case_number.toLowerCase().includes(searchTerm) ||
        (item.applicant_id && item.applicant_id.toLowerCase().includes(searchTerm))
      )
      console.log('💾 [getGrantsFromLocalStorage] 搜尋篩選後:', results.length, '筆 (搜尋詞:', params.search, ')')
    }

    // 排序（最新的在前）
    results.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())

    // 分頁 - 只有在明確指定 limit 時才進行分頁
    if (params.limit !== undefined && params.limit > 0) {
      const skip = params.skip || 0
      console.log('💾 [getGrantsFromLocalStorage] 套用分頁: skip:', skip, 'limit:', params.limit)
      results = results.slice(skip, skip + params.limit)
    } else {
      console.log('💾 [getGrantsFromLocalStorage] 不限制數量，回傳所有', results.length, '筆資料')
    }

    return results
  }

  /**
   * 轉換本地資料為列表項目格式
   */
  private transformLocalDataToListItem(caseNumber: string, grantData: GrantData): GrantListItem {
    // 根據 officeName 對應到 office_id
    const officeNameToIdMap: Record<string, number> = {
      '農業部農田水利署': 0,
      '宜蘭管理處': 1,
      '北基管理處': 2,
      '桃園管理處': 3,
      '石門管理處': 4,
      '新竹管理處': 5,
      '苗栗管理處': 6,
      '臺中管理處': 7,
      '南投管理處': 8,
      '彰化管理處': 9,
      '雲林管理處': 10,
      '嘉南管理處': 11,
      '高雄管理處': 12,
      '屏東管理處': 13,
      '臺東管理處': 14,
      '花蓮管理處': 15,
      '七星管理處': 16,
      '瑠公管理處': 17,
      '金門縣農會': 18,
      '澎湖縣農會': 19,
      '農田水利人力發展中心': 20,
      '茶葉改良場': 21,
      '財團法人農業工程研究中心': 22,
      '高雄市政府農業局': 23,
      '農工中心': 99,
      '農業部': 100
    }

    const officeName = grantData.officeName || '未設定'
    const officeId = officeNameToIdMap[officeName] ?? null

    return {
      id: parseInt(caseNumber.replace(/\D/g, '')) || 0, // 臨時 ID
      case_number: caseNumber,
      year: parseInt(caseNumber.substring(0, 3)) || new Date().getFullYear() - 1911,
      applicant_name: grantData.applicantName || '未填寫',
      office: officeName,
      office_id: officeId,
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
   * 🔥 Good Taste: 直接使用 totalFacilityArea (m²)
   */
  private extractFacilityArea(grantData: GrantData): number {
    const step2Data = grantData.stepsData?.[2] || {}
    return Math.round(parseFloat(String(step2Data.totalFacilityArea || '0')))
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
  private cache = new Map<string, { data: unknown; timestamp: number }>()
  private readonly CACHE_DURATION = 5 * 60 * 1000 // 5分鐘

  /**
   * 取得快取資料
   */
  get<T>(key: string): T | null {
    const cached = this.cache.get(key)
    if (cached && Date.now() - cached.timestamp < this.CACHE_DURATION) {
      return cached.data as T
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

// =============================================================================
// 🆕 PDF生成相關函數
// =============================================================================

/**
 * 生成工程預算書封面PDF
 * @param grantData 補助案件資料
 */
export const generateKaiuPdf = async (grantData: GrantListItem): Promise<Blob> => {
  try {
    console.log('🖨️ [generateKaiuPdf] 準備生成PDF，案件資料:', grantData)

    // 構建PDF生成所需的資料格式
    const pdfData = {
      CASE_ID: grantData.case_number,
      APPLICANT: grantData.applicant_name,
      ADDRESS: '', // 這裡可能需要從其他地方取得地址資料
      LOCATION: '', // 土地位置資訊
      LAND_ID: '', // 地號資訊
      AREA_NUMBER: grantData.facility_area_m2 ? (grantData.facility_area_m2 / 10000).toFixed(4) : '0.0000', // 轉換為公頃
      FACILITY_TYPE: grantData.facility_type || '未設定',
      YEAR: grantData.year.toString()
    }

    console.log('🖨️ [generateKaiuPdf] PDF生成參數:', pdfData)

    // 調用後端PDF生成API - 直接使用axios實例以確保responseType生效
    const response = await apiService.post('/test/generate-kaiu-pdf-reportlab', pdfData, {
      responseType: 'blob',
      headers: {
        'Content-Type': 'application/json'
      }
    })

    console.log('🖨️ [generateKaiuPdf] PDF生成成功')

    // 檢查回應是否為Blob
    if (response instanceof Blob) {
      console.log('🖨️ [generateKaiuPdf] 檔案大小:', response.size, 'bytes')
      return response
    } else {
      // 如果不是Blob，可能是因為responseType沒有生效，需要手動轉換
      console.log('🖨️ [generateKaiuPdf] 轉換回應為Blob')
      return new Blob([response as any], { type: 'application/pdf' })
    }

  } catch (error: unknown) {
    console.error('🖨️ [generateKaiuPdf] PDF生成失敗:', error)
    throw new ApplicationError({
      message: 'PDF生成失敗，請稍後再試',
      status: (error as any)?.response?.status || 500,
      source: 'grantsService.generateKaiuPdf',
      originalError: error
    })
  }
}

/**
 * 生成結案申報書 PDF
 * @param caseNumber 案號
 * @returns Promise<Blob> PDF 檔案 Blob
 */
export const generateCompletionStatement = async (caseNumber: string): Promise<Blob> => {
  try {
    console.log('📋 [generateCompletionStatement] 準備生成結案申報書，案號:', caseNumber)

    // 調用後端結案申報書生成 API
    const response = await apiService.post(
      GRANTS.COMPLETION_STATEMENT(caseNumber),
      {},
      {
        responseType: 'blob'
      }
    )

    console.log('📋 [generateCompletionStatement] 結案申報書生成成功')

    // 檢查回應是否為 Blob
    if (response instanceof Blob) {
      console.log('📋 [generateCompletionStatement] 檔案大小:', response.size, 'bytes')
      return response
    } else {
      // 如果不是 Blob，手動轉換
      console.log('📋 [generateCompletionStatement] 轉換回應為 Blob')
      return new Blob([response as any], { type: 'application/pdf' })
    }

  } catch (error: unknown) {
    console.error('📋 [generateCompletionStatement] 結案申報書生成失敗:', error)
    throw new ApplicationError({
      message: '結案申報書生成失敗，請稍後再試',
      status: (error as any)?.response?.status || 500,
      source: 'grantsService.generateCompletionStatement',
      originalError: error
    })
  }
}

/**
 * 生成補助切結書 PDF
 * @param caseNumber 案號
 * @returns Promise<Blob> PDF 檔案 Blob
 */
export const generateDeclaration = async (caseNumber: string): Promise<Blob> => {
  try {
    console.log('📋 [generateDeclaration] 準備生成切結書，案號:', caseNumber)

    // 調用後端切結書生成 API
    const response = await apiService.post(
      GRANTS.DECLARATION(caseNumber),
      {},
      {
        responseType: 'blob'
      }
    )

    console.log('📋 [generateDeclaration] 切結書生成成功')

    // 檢查回應是否為 Blob
    if (response instanceof Blob) {
      console.log('📋 [generateDeclaration] 檔案大小:', response.size, 'bytes')
      return response
    } else {
      // 如果不是 Blob，手動轉換
      console.log('📋 [generateDeclaration] 轉換回應為 Blob')
      return new Blob([response as any], { type: 'application/pdf' })
    }

  } catch (error: unknown) {
    console.error('📋 [generateDeclaration] 切結書生成失敗:', error)
    throw new ApplicationError({
      message: '切結書生成失敗，請稍後再試',
      status: (error as any)?.response?.status || 500,
      source: 'grantsService.generateDeclaration',
      originalError: error
    })
  }
}

/**
 * 生成規劃委託書 PDF
 * @param caseNumber 案號
 * @returns Promise<Blob> PDF 檔案 Blob
 */
export const generateAuthorization = async (caseNumber: string): Promise<Blob> => {
  try {
    console.log('📋 [generateAuthorization] 準備生成規劃委託書，案號:', caseNumber)

    // 調用後端規劃委託書生成 API
    const response = await apiService.post(
      GRANTS.AUTHORIZATION(caseNumber),
      {},
      {
        responseType: 'blob'
      }
    )

    console.log('📋 [generateAuthorization] 規劃委託書生成成功')

    // 檢查回應是否為 Blob
    if (response instanceof Blob) {
      console.log('📋 [generateAuthorization] 檔案大小:', response.size, 'bytes')
      return response
    } else {
      // 如果不是 Blob，手動轉換
      console.log('📋 [generateAuthorization] 轉換回應為 Blob')
      return new Blob([response as any], { type: 'application/pdf' })
    }

  } catch (error: unknown) {
    console.error('📋 [generateAuthorization] 規劃委託書生成失敗:', error)
    throw new ApplicationError({
      message: '規劃委託書生成失敗，請稍後再試',
      status: (error as any)?.response?.status || 500,
      source: 'grantsService.generateAuthorization',
      originalError: error
    })
  }
}

/**
 * 生成工程預算書 PDF
 * @param caseNumber 案號
 * @param grantsId 案件ID（選填，用於區分重複案號的歷史案件）
 * @returns PDF檔案Blob
 */
export const generateBudgetStatement = async (caseNumber: string, grantsId?: number): Promise<Blob> => {
  try {
    console.log('📋 [generateBudgetStatement] 準備生成工程預算書，案號:', caseNumber, 'grants_id:', grantsId)

    // 構建 API URL，如果有 grantsId 則添加 query parameter
    let apiUrl = GRANTS.BUDGET_STATEMENT(caseNumber)
    if (grantsId !== undefined) {
      apiUrl += `?grants_id=${grantsId}`
    }

    // 調用後端工程預算書生成 API
    const response = await apiService.post(
      apiUrl,
      {},
      {
        responseType: 'blob'
      }
    )

    console.log('📋 [generateBudgetStatement] 工程預算書生成成功')

    // 檢查回應是否為 Blob
    if (response instanceof Blob) {
      console.log('📋 [generateBudgetStatement] 檔案大小:', response.size, 'bytes')
      return response
    } else {
      // 如果不是 Blob，手動轉換
      console.log('📋 [generateBudgetStatement] 轉換回應為 Blob')
      return new Blob([response as any], { type: 'application/pdf' })
    }

  } catch (error: unknown) {
    console.error('📋 [generateBudgetStatement] 工程預算書生成失敗:', error)
    throw new ApplicationError({
      message: '工程預算書生成失敗，請稍後再試',
      status: (error as any)?.response?.status || 500,
      source: 'grantsService.generateBudgetStatement',
      originalError: error
    })
  }
}

/**
 * 下載PDF檔案
 * @param blob PDF檔案Blob
 * @param filename 檔案名稱
 */
export const downloadPdfBlob = (blob: Blob, filename: string): void => {
  try {
    console.log('💾 [downloadPdfBlob] 開始下載PDF檔案:', filename)

    // 創建下載連結
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename

    // 觸發下載
    document.body.appendChild(link)
    link.click()

    // 清理
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)

    console.log('💾 [downloadPdfBlob] PDF下載完成')

  } catch (error) {
    console.error('💾 [downloadPdfBlob] PDF下載失敗:', error)
    throw new ApplicationError({
      message: 'PDF下載失敗',
      status: 500,
      source: 'grantsService.downloadPdfBlob',
      originalError: error
    })
  }
}

// =============================================================================
// 🆕 批次跨年度處理相關函數
// =============================================================================

/**
 * 批次跨年度處理結果介面
 */
export interface BatchCrossYearResult {
  originalCaseNumber: string
  newCaseNumber?: string
  success: boolean
  message: string
  error?: string
}

/**
 * 批次跨年度處理
 * @param selectedGrants 選取的案件列表
 */
export const batchCrossYearGrants = async (selectedGrants: GrantListItem[]): Promise<BatchCrossYearResult[]> => {
  try {
    console.log('🔄 [batchCrossYearGrants] 開始批次跨年度處理，案件數量:', selectedGrants.length)

    const requestData = {
      case_numbers: selectedGrants.map(grant => grant.case_number),
      grants_info: selectedGrants.map(grant => ({
        case_number: grant.case_number,
        applicant_name: grant.applicant_name,
        year: grant.year,
        office_id: grant.office_id
      }))
    }

    console.log('🔄 [batchCrossYearGrants] 發送請求資料:', requestData)

    const response = await apiService.post<BatchCrossYearResult[]>(
      '/grants/batch-cross-year',
      requestData
    )

    console.log('✅ [batchCrossYearGrants] 批次跨年度處理完成:', response)
    return response

  } catch (error: any) {
    console.error('❌ [batchCrossYearGrants] 批次跨年度處理失敗:', error)

    // 如果是網路錯誤或API錯誤，回傳錯誤訊息給每個案件
    const errorResults: BatchCrossYearResult[] = selectedGrants.map(grant => ({
      originalCaseNumber: grant.case_number,
      success: false,
      message: '批次跨年度處理失敗',
      error: error.response?.data?.detail || error.message || '未知錯誤'
    }))

    return errorResults
  }
}

// =============================================================================
// 🆕 版本管理相關函數
// =============================================================================

// 版本相關的類型定義
export interface GrantVersionResponse {
  id: number
  grant_id: number
  version: number
  comment?: string
  created_at: string
  case_number?: string
  is_duplicate?: boolean
  message: string
}

export interface GrantVersionDetail {
  id: number
  grant_id: number
  version: number
  all_steps_data: Record<string, any>
  all_steps_data_hash?: string
  comment?: string
  created_at: string
  modified_at: string
  created_by?: {
    id: number
    username: string
    full_name?: string
  }
}

/**
 * 建立新的補助案件版本
 * @param caseNumber 案件編號
 * @param allStepsData 所有步驟的完整資料
 * @param comment 版本說明
 */
export const createGrantVersion = async (
  caseNumber: string,
  allStepsData: Record<string, any>,
  comment?: string
): Promise<GrantVersionResponse> => {
  try {
    console.log(`🔄 Creating new version for case ${caseNumber}`)
    console.log(`📦 All steps data keys:`, Object.keys(allStepsData))
    console.log(`📝 Comment:`, comment)

    // 🔧 修正請求格式以匹配後端 API
    const requestBody = {
      all_steps_data: allStepsData,
      comment: comment || `變更設計 - ${new Date().toLocaleString('zh-TW')}`
    }

    const response = await apiService.post<GrantVersionResponse>(
      `/grants/case/${caseNumber}/create-version`,
      requestBody
    )

    console.log(`✅ Version created successfully:`, response)
    return response

  } catch (error: any) {
    console.error(`❌ Failed to create version for case ${caseNumber}:`, error)

    // 🔧 改善錯誤處理
    if (error.response?.status === 400) {
      const detail = error.response?.data?.detail || ''
      if (detail.includes('相同') || detail.includes('duplicate')) {
        throw new ApplicationError({
          message: '資料內容與現有版本相同，無需建立新版本',
          status: 400,
          source: 'grantsService.createGrantVersion',
          originalError: error
        })
      }
    }

    return handleApiError(error, 'grantsService.createGrantVersion')
  }
}

/**
 * 取得當前活躍版本的完整資料（用於變更設計繼承）
 * @param caseNumber 案件編號
 */
export const getCurrentVersionData = async (
  caseNumber: string
): Promise<Record<string, any>> => {
  try {
    console.log(`🔄 Loading current version data for case ${caseNumber}`)

    // 取得案件完整資料，包含當前版本
    const grantData = await apiService.get<any>(`/grants/case/${caseNumber}`)

    if (!grantData.active_version) {
      throw new Error('無法找到當前版本資料')
    }

    // 從當前版本中提取 all_steps_data
    const currentVersionData = grantData.active_version.all_steps_data || {}

    // 🔥 Linus式修復：清理資料結構，只保留 steps 格式，避免前後端格式混合
    // 檢查是否存在污染的資料結構（同時有數字鍵和 steps 鍵）
    const hasNumericKeys = Object.keys(currentVersionData).some(key => /^\d+$/.test(key))
    const hasStepsKey = 'steps' in currentVersionData

    if (hasNumericKeys && hasStepsKey) {
      console.warn('🚨 Detected mixed data structure, cleaning up...')
      console.log('Keys before cleanup:', Object.keys(currentVersionData))

      // 只返回正確的 steps 格式，移除污染的數字鍵
      const cleanedData = {
        steps: currentVersionData.steps || {}
      }
      console.log('✅ Cleaned data structure:', Object.keys(cleanedData))
      return cleanedData
    }

    console.log(`✅ Loaded current version data with steps:`, Object.keys(currentVersionData))
    return currentVersionData

  } catch (error: any) {
    console.error(`❌ Failed to load current version data for case ${caseNumber}:`, error)
    return handleApiError(error, 'grantsService.getCurrentVersionData')
  }
}

/**
 * 取得補助案件的版本列表
 * @param grantId 補助案件 ID
 * @param skip 跳過筆數
 * @param limit 限制筆數
 */
export const getGrantVersions = async (
  grantId: number,
  skip: number = 0,
  limit: number = 100
): Promise<GrantVersionDetail[]> => {
  try {
    console.log(`🔄 Loading versions for grant ${grantId}`)

    const response = await apiService.get<GrantVersionDetail[]>(
      `/grants/${grantId}/versions`,
      { params: { skip, limit } }
    )

    console.log(`✅ Loaded ${response.length} versions`)
    return response

  } catch (error: any) {
    console.error(`❌ Failed to load versions for grant ${grantId}:`, error)
    return handleApiError(error, 'grantsService.getGrantVersions')
  }
}

/**
 * 取得單一版本的詳細資料
 * @param versionId 版本 ID
 */
export const getGrantVersion = async (
  versionId: number
): Promise<GrantVersionDetail> => {
  try {
    console.log(`🔄 Loading version details for ${versionId}`)

    const response = await apiService.get<GrantVersionDetail>(
      `/grants/versions/${versionId}`
    )

    console.log(`✅ Loaded version details`)
    return response

  } catch (error: any) {
    console.error(`❌ Failed to load version ${versionId}:`, error)
    return handleApiError(error, 'grantsService.getGrantVersion')
  }
}

/**
 * 取得案件的 grant_papers 文件資料（根據 active_version_id 匹配）
 * @param caseNumber 案件編號
 * @param documentType 文件類型，預設為 'budget_statement'
 * @param grantsId 案件ID，用於區分重複案件編號（歷史案件）
 */
export const getGrantPapers = async (
  caseNumber: string,
  documentType: string = 'budget_statement',
  grantsId?: number
): Promise<any> => {
  try {
    console.log(`🔄 Loading grant papers for case ${caseNumber}, document type: ${documentType}${grantsId ? `, grants_id: ${grantsId}` : ''}`)

    const params = new URLSearchParams({
      document_type: documentType
    })

    if (grantsId) {
      params.append('grants_id', grantsId.toString())
    }

    const response = await apiService.get(
      `/grants/case/${caseNumber}/papers?${params.toString()}`
    )

    console.log(`✅ Loaded grant papers for case ${caseNumber}`)
    return response

  } catch (error: any) {
    console.error(`❌ Failed to load grant papers for case ${caseNumber}:`, error)
    return handleApiError(error, 'grantsService.getGrantPapers')
  }
}

// =============================================================================
// 🆕 版本比較相關函數
// =============================================================================

/**
 * 版本比較結果介面
 */
export interface VersionComparisonResult {
  case_number: string
  first_version: GrantVersionDetail
  latest_version: GrantVersionDetail
  facilities_comparison: FacilitiesComparison
}

/**
 * 設施比較結果介面
 */
export interface FacilitiesComparison {
  irrigation_control_facilities: FacilityComparisonItem[]
  pipeline_facilities: FacilityComparisonItem[]
  summary: {
    total_changes: number
    has_irrigation_changes: boolean
    has_pipeline_changes: boolean
  }
}

/**
 * 設施比較項目介面
 */
export interface FacilityComparisonItem {
  name: string
  specification?: string
  beforeQuantity: number
  afterQuantity: number
  quantityChange: number
  beforePrice?: string
  afterPrice?: string
  unit?: string
  changeType: 'added' | 'removed' | 'modified' | 'unchanged'
}

/**
 * 比較第一版本與最新版本的設施差異
 * @param caseNumber 案件編號
 */
export const compareGrantVersions = async (
  caseNumber: string
): Promise<VersionComparisonResult> => {
  try {
    console.log(`🔄 Comparing grant versions for case ${caseNumber}`)

    const response = await apiService.get<VersionComparisonResult>(
      `/grants/case/${caseNumber}/versions/compare`
    )

    console.log(`✅ Version comparison completed`)
    return response

  } catch (error: any) {
    console.error(`❌ Failed to compare versions for case ${caseNumber}:`, error)
    return handleApiError(error, 'grantsService.compareGrantVersions')
  }
}

/**
 * 取得案件的版本摘要（用於顯示版本資訊）
 * @param caseNumber 案件編號
 */
export const getGrantVersionSummary = async (
  case_number: string
): Promise<{
  total_versions: number
  first_version: { id: number; version: number; created_at: string }
  latest_version: { id: number; version: number; created_at: string }
  has_versions: boolean
}> => {
  try {
    console.log(`🔄 Loading version summary for case ${case_number}`)

    const response = await apiService.get<{
      total_versions: number
      first_version: { id: number; version: number; created_at: string }
      latest_version: { id: number; version: number; created_at: string }
      has_versions: boolean
    }>(
      `/grants/case/${case_number}/versions/summary`
    )

    console.log(`✅ Loaded version summary`)
    return response

  } catch (error: any) {
    console.error(`❌ Failed to load version summary for case ${case_number}:`, error)
    return handleApiError(error, 'grantsService.getGrantVersionSummary')
  }
}

/**
 * 本地版本比較函數（當API不可用時的備用方案）
 * @param firstVersionData 第一版本資料
 * @param latestVersionData 最新版本資料
 */
export const compareVersionsLocally = (
  firstVersionData: Record<string, any>,
  latestVersionData: Record<string, any>
): FacilitiesComparison => {
  console.log('🔄 Performing local version comparison')

  // 比較 step3 的灌溉調控設施
  const irrigationComparison = compareFacilities(
    firstVersionData[3]?.facilities || [],
    latestVersionData[3]?.facilities || [],
    'irrigation'
  )

  // 比較 step4 的田間管路設施
  const pipelineComparison = compareFacilities(
    [
      ...(firstVersionData[4]?.mainPipes || []),
      ...(firstVersionData[4]?.irrigationSystem || [])
    ],
    [
      ...(latestVersionData[4]?.mainPipes || []),
      ...(latestVersionData[4]?.irrigationSystem || [])
    ],
    'pipeline'
  )

  const result: FacilitiesComparison = {
    irrigation_control_facilities: irrigationComparison,
    pipeline_facilities: pipelineComparison,
    summary: {
      total_changes: irrigationComparison.filter(item => item.changeType !== 'unchanged').length +
                     pipelineComparison.filter(item => item.changeType !== 'unchanged').length,
      has_irrigation_changes: irrigationComparison.some(item => item.changeType !== 'unchanged'),
      has_pipeline_changes: pipelineComparison.some(item => item.changeType !== 'unchanged')
    }
  }

  console.log('✅ Local comparison completed:', result.summary)
  return result
}

/**
 * 比較兩個設施陣列的差異
 */
function compareFacilities(
  beforeFacilities: any[],
  afterFacilities: any[],
  type: 'irrigation' | 'pipeline'
): FacilityComparisonItem[] {
  const results: FacilityComparisonItem[] = []
  const processedNames = new Set<string>()

  // 處理 after 設施（包含新增和修改）
  afterFacilities.forEach(afterItem => {
    const name = afterItem.name || afterItem.typeLabel || `未命名${type}設施`
    processedNames.add(name)

    const beforeItem = beforeFacilities.find(item =>
      (item.name || item.typeLabel) === name
    )

    if (!beforeItem) {
      // 新增的設施
      results.push({
        name,
        specification: afterItem.specification || '',
        beforeQuantity: 0,
        afterQuantity: parseFloat(afterItem.quantity) || 0,
        quantityChange: parseFloat(afterItem.quantity) || 0,
        beforePrice: '0',
        afterPrice: afterItem.unitPrice || afterItem.totalPrice || '0',
        unit: afterItem.unit || '台',
        changeType: 'added'
      })
    } else {
      // 比較修改的設施
      const beforeQty = parseFloat(beforeItem.quantity) || 0
      const afterQty = parseFloat(afterItem.quantity) || 0
      const quantityChange = afterQty - beforeQty

      results.push({
        name,
        specification: afterItem.specification || beforeItem.specification || '',
        beforeQuantity: beforeQty,
        afterQuantity: afterQty,
        quantityChange,
        beforePrice: beforeItem.unitPrice || beforeItem.totalPrice || '0',
        afterPrice: afterItem.unitPrice || afterItem.totalPrice || '0',
        unit: afterItem.unit || beforeItem.unit || '台',
        changeType: quantityChange === 0 ? 'unchanged' : 'modified'
      })
    }
  })

  // 處理已移除的設施
  beforeFacilities.forEach(beforeItem => {
    const name = beforeItem.name || beforeItem.typeLabel || `未命名${type}設施`

    if (!processedNames.has(name)) {
      results.push({
        name,
        specification: beforeItem.specification || '',
        beforeQuantity: parseFloat(beforeItem.quantity) || 0,
        afterQuantity: 0,
        quantityChange: -(parseFloat(beforeItem.quantity) || 0),
        beforePrice: beforeItem.unitPrice || beforeItem.totalPrice || '0',
        afterPrice: '0',
        unit: beforeItem.unit || '台',
        changeType: 'removed'
      })
    }
  })

  return results.sort((a, b) => a.name.localeCompare(b.name))
}
