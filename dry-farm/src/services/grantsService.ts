import { apiService } from './api/http'
import { ApplicationError } from '@/utils/asyncHelpers'
import { GRANTS } from './api/endpoints'

// Types
export interface GrantCreateRequest {
  name: string
  id: string
  phone: string
  county: string
  countyId: number
  town: string
  townId: number
  village?: string
  villageId?: number
  address: string
  undertracker: string
  department: string
  departmentId: number
}

export interface GrantCreateResponse {
  id: number;
  case_number: string;
  year: number;
  applicant_name: string;
  status: string;
  received_date: string;
  received_time: string;
}

// Add these interfaces
export interface GrantStepData {
  id: number;
  case_number: string;
  current_step: number;
  status: string;
  [key: string]: any; // Allow for step-specific fields
}

export interface Step1Data {
  name: string;
  id: string;
  phone: string;
  county: string;
  town: string;
  village?: string;
  address: string;
  manager: string;
  department: string;
  departmentId: number;
  caseNumber: string;
  receivedDate: string;
  receivedTime: string;
}

export const createGrant = async (data: GrantCreateRequest): Promise<GrantCreateResponse> => {
  try {
    console.log('發送建立專案請求，資料:', data)
    const response = await apiService.post<GrantCreateResponse>(GRANTS.CREATE, data)
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

export const getGrantByCaseNumber = async (caseNumber: string): Promise<any> => {
  try {
    // const url = mapApiPath(GRANTS.BY_CASE_NUMBER(caseNumber));
    // const response = await apiService.get(url);
    const response = await apiService.get(GRANTS.BY_CASE_NUMBER(caseNumber))
    return response
  } catch (error: unknown) {
    handleApiError(error, 'grantsService.getGrantByCaseNumber')
  }
}

export const getGrantStepData = async (caseNumber: string, step: number): Promise<GrantStepData> => {
  try {
    const response = await apiService.get(GRANTS.STEP(caseNumber, step))
    return response
  } catch (error: unknown) {
    return handleApiError(error, 'grantsService.getGrantStepData')
  }
}

export const updateGrantStepData = async (caseNumber: string, step: number, data: any): Promise<GrantStepData> => {
  try {
    const response = await apiService.put(GRANTS.STEP(caseNumber, step), data)
    return response
  } catch (error: unknown) {
    return handleApiError(error, 'grantsService.updateGrantStepData')
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
