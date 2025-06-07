import { apiService } from './api/http'
import { ApplicationError } from '@/utils/asyncHelpers'
import { GRANT_VERSIONS } from './api/endpoints'

// Types
export interface GrantVersionCreateRequest {
  grant_id: number
  all_steps_data: Record<string, any>
  comment?: string
}

export interface GrantVersionResponse {
  id: number
  grant_id: number
  version: number
  comment?: string
  created_at: string
  case_number?: string
  is_duplicate?: boolean
  message?: string
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

export interface GrantVersionList {
  id: number
  grant_id: number
  version: number
  comment?: string
  created_at: string
  created_by_name?: string
}

export interface GrantVersionSummary {
  grant_id: number
  total_versions: number
  latest_version?: GrantVersionList
  active_version: {
    id?: number
    version?: number
    comment?: string
    created_at?: string
  }
  has_versions: boolean
  versions_list: GrantVersionList[]
}

export interface GrantVersionCompareRequest {
  version_a_id: number
  version_b_id: number
}

export interface GrantVersionCompareResult {
  version_a: GrantVersionDetail
  version_b: GrantVersionDetail
  differences: {
    added: Record<string, any>
    removed: Record<string, any>
    modified: Record<string, any>
    unchanged: Record<string, any>
  }
}

/**
 * 建立新的補助申請案件版本
 */
export const createGrantVersion = async (data: GrantVersionCreateRequest): Promise<GrantVersionResponse> => {
  try {
    console.log('建立版本請求，資料:', data)
    const response = await apiService.post<GrantVersionResponse>(GRANT_VERSIONS.CREATE, data)
    return response
  } catch (error: unknown) {
    return handleApiError(error, 'grantVersionsService.createGrantVersion')
  }
}

/**
 * 從目前的 localStorage 資料建立版本
 */
export const createVersionFromCurrentData = async (
  caseNumber: string, 
  allStepsData: Record<string, any>,
  comment?: string
): Promise<GrantVersionResponse> => {
  try {
    const response = await apiService.post<GrantVersionResponse>(
      GRANT_VERSIONS.FROM_CURRENT(caseNumber),
      { 
        all_steps_data: allStepsData,
        comment 
      }
    )
    return response
  } catch (error: unknown) {
    return handleApiError(error, 'grantVersionsService.createVersionFromCurrentData')
  }
}

/**
 * 取得補助申請案件的所有版本列表
 */
export const getGrantVersions = async (
  grantId: number,
  skip = 0,
  limit = 100
): Promise<GrantVersionList[]> => {
  try {
    const response = await apiService.get<GrantVersionList[]>(
      `${GRANT_VERSIONS.BY_GRANT(grantId)}?skip=${skip}&limit=${limit}`
    )
    return response
  } catch (error: unknown) {
    return handleApiError(error, 'grantVersionsService.getGrantVersions')
  }
}

/**
 * 取得單一版本的詳細資料
 */
export const getGrantVersionDetail = async (versionId: number): Promise<GrantVersionDetail> => {
  try {
    const response = await apiService.get<GrantVersionDetail>(GRANT_VERSIONS.DETAIL(versionId))
    return response
  } catch (error: unknown) {
    return handleApiError(error, 'grantVersionsService.getGrantVersionDetail')
  }
}

/**
 * 更新版本註解
 */
export const updateGrantVersionComment = async (
  versionId: number,
  comment: string
): Promise<GrantVersionDetail> => {
  try {
    const response = await apiService.put<GrantVersionDetail>(
      GRANT_VERSIONS.UPDATE(versionId),
      { comment }
    )
    return response
  } catch (error: unknown) {
    return handleApiError(error, 'grantVersionsService.updateGrantVersionComment')
  }
}

/**
 * 刪除版本
 */
export const deleteGrantVersion = async (versionId: number): Promise<{ message: string }> => {
  try {
    const response = await apiService.delete<{ message: string }>(GRANT_VERSIONS.DELETE(versionId))
    return response
  } catch (error: unknown) {
    return handleApiError(error, 'grantVersionsService.deleteGrantVersion')
  }
}

/**
 * 取得補助申請案件的現行版本
 */
export const getActiveVersion = async (grantId: number): Promise<GrantVersionDetail | null> => {
  try {
    const response = await apiService.get<GrantVersionDetail | null>(GRANT_VERSIONS.GET_ACTIVE(grantId))
    return response
  } catch (error: unknown) {
    // 如果沒有現行版本，返回 null 而不是拋出錯誤
    const status = (error as { response?: { status?: number } })?.response?.status
    if (status === 404) {
      return null
    }
    return handleApiError(error, 'grantVersionsService.getActiveVersion')
  }
}

/**
 * 設定現行版本
 */
export const setActiveVersion = async (
  grantId: number,
  versionId: number
): Promise<{ grant_id: number; active_version_id: number; version: number; message: string }> => {
  try {
    const response = await apiService.put(GRANT_VERSIONS.SET_ACTIVE(grantId, versionId), {})
    return response
  } catch (error: unknown) {
    return handleApiError(error, 'grantVersionsService.setActiveVersion')
  }
}

/**
 * 比較兩個版本的差異
 */
export const compareGrantVersions = async (
  versionAId: number,
  versionBId: number
): Promise<GrantVersionCompareResult> => {
  try {
    const response = await apiService.post<GrantVersionCompareResult>(
      GRANT_VERSIONS.COMPARE,
      { version_a_id: versionAId, version_b_id: versionBId }
    )
    return response
  } catch (error: unknown) {
    return handleApiError(error, 'grantVersionsService.compareGrantVersions')
  }
}

/**
 * 取得補助申請案件版本摘要資訊
 */
export const getGrantVersionsSummary = async (grantId: number): Promise<GrantVersionSummary> => {
  try {
    const response = await apiService.get<GrantVersionSummary>(GRANT_VERSIONS.SUMMARY(grantId))
    return response
  } catch (error: unknown) {
    return handleApiError(error, 'grantVersionsService.getGrantVersionsSummary')
  }
}

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
