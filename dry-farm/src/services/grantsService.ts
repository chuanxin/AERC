import { apiService } from './api/http'
import { ApplicationError } from '@/utils/asyncHelpers'
import { GRANTS } from './api/endpoints'
import type { GrantCreateRequest } from '@/types/grantForms'
import { fieldMappingMiddleware, FieldMappingValidator, type DataRecord } from '@/types/fieldMappings'

// Types
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
}

// Add these interfaces
export interface GrantStepData {
  id: number;
  case_number: string;
  current_step: number;
  status: string;
  [key: string]: unknown; // Allow for step-specific fields
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
