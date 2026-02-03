/**
 * 前後端字段映射配置
 * 確保前後端字段名稱一致性，避免數據同步問題
 */

import type { Step1Data } from './grantForms'

// 定義通用數據類型
export type DataRecord = Record<string, unknown>

// 字段映射配置接口
interface FieldMappingConfig {
  [step: number]: {
    // 前端字段名 -> 後端字段名的映射
    frontendToBackend: Record<string, string>
    // 後端字段名 -> 前端字段名的映射
    backendToFrontend: Record<string, string>
    // 已棄用的字段映射（向後兼容）
    deprecatedFields: Record<string, string>
  }
}

// 主要字段映射配置
export const FIELD_MAPPING_CONFIG: FieldMappingConfig = {
  1: { // Step 1: 申請人基本資料
    frontendToBackend: {
      'name': 'applicant_name',
      'id': 'applicant_id',
      'phone': 'applicant_phone',
      'phone2': 'applicant_phone2',
      'county': 'county',
      'countyId': 'county_id',
      'town': 'town',
      'townId': 'town_id',
      'village': 'village',
      'villageId': 'village_id',
      'address': 'address',
      'undertracker': 'undertracker',    // 統一使用新字段名
      'office': 'office',                // 統一使用新字段名
      'officeId': 'office_id',
      'caseNumber': 'case_number',
      'receivedDate': 'received_date',
      'receivedTime': 'received_time',
      'valid': 'valid',
      'isDisasterCase': 'is_disaster_case', // 新增災害案件字段
      'disasterCaseDescription': 'disaster_case_description' // 新增災害
    },
    backendToFrontend: {
      'applicant_name': 'name',
      'applicant_id': 'id',
      'applicant_phone': 'phone',
      'applicant_phone2': 'phone2',
      'county': 'county',
      'county_id': 'countyId',
      'town': 'town',
      'town_id': 'townId',
      'village': 'village',
      'village_id': 'villageId',
      'address': 'address',
      'undertracker': 'undertracker',    // 統一使用新字段名
      'office': 'office',                // 統一使用新字段名
      'office_id': 'officeId',
      'case_number': 'caseNumber',
      'received_date': 'receivedDate',
      'received_time': 'receivedTime',
      'valid': 'valid',
      'is_disaster_case': 'isDisasterCase', // 新增災害案件字段
      'disaster_case_description': 'disasterCaseDescription', // 新增災害
      'is_legacy': 'is_Legacy' // 新增是否為舊版案件字段
    },
    deprecatedFields: {
      // 'manager': 'undertracker',         // 舊字段名 -> 新字段名
      // 'department': 'office',            // 舊字段名 -> 新字段名
      // 'departmentId': 'officeId'         // 舊字段名 -> 新字段名
    }
  },
  2: { // Step 2: 土地資訊
    frontendToBackend: {
      'landCounty': 'land_county',
      'landTown': 'land_town',
      'landSec': 'land_section',
      'landNumber': 'land_number',
      'landArea': 'land_area',
      'facilityArea': 'facility_area'
      // ... 其他 step2 字段
    },
    backendToFrontend: {
      'land_county': 'landCounty',
      'land_town': 'landTown',
      'land_section': 'landSec',
      'land_number': 'landNumber',
      'land_area': 'landArea',
      'facility_area': 'facilityArea'
      // ... 其他 step2 字段
    },
    deprecatedFields: {}
  }
  // ... 其他步驟
}

// 字段驗證和轉換工具類
export class FieldMappingUtils {

  /**
   * 驗證 API 響應字段是否符合預期
   */
  static validateApiResponse(step: number, data: Record<string, any>): {
    isValid: boolean
    missingFields: string[]
    unexpectedFields: string[]
    deprecatedFields: string[]
  } {
    const config = FIELD_MAPPING_CONFIG[step]
    if (!config) {
      return { isValid: false, missingFields: [], unexpectedFields: [], deprecatedFields: [] }
    }

    // 定義通用元數據字段（所有 API 響應都會包含的基本字段）
    const commonMetadataFields = new Set(['id', 'case_number', 'current_step', 'status'])

    const expectedFields = new Set(Object.keys(config.backendToFrontend).map(
      backendField => config.backendToFrontend[backendField]
    ))
    const receivedFields = new Set(Object.keys(data))
    const deprecatedFields = new Set(Object.keys(config.deprecatedFields))

    const missingFields = [...expectedFields].filter(field => !receivedFields.has(field))
    const unexpectedFields = [...receivedFields].filter(field =>
      !expectedFields.has(field) && !deprecatedFields.has(field) && !commonMetadataFields.has(field)
    )
    const foundDeprecatedFields = [...receivedFields].filter(field =>
      deprecatedFields.has(field)
    )

    return {
      isValid: missingFields.length === 0 && foundDeprecatedFields.length === 0,
      missingFields,
      unexpectedFields,
      deprecatedFields: foundDeprecatedFields
    }
  }

  /**
   * 標準化 API 響應數據，處理舊字段名
   */
  static normalizeApiResponse(step: number, data: Record<string, any>): Record<string, any> {
    const config = FIELD_MAPPING_CONFIG[step]
    if (!config) return data

    const normalizedData = { ...data }

    // 處理棄用字段的映射
    Object.entries(config.deprecatedFields).forEach(([oldField, newField]) => {
      if (oldField in normalizedData && !(newField in normalizedData)) {
        normalizedData[newField] = normalizedData[oldField]
        delete normalizedData[oldField]
        console.warn(`⚠️ 檢測到棄用字段 "${oldField}"，已自動映射為 "${newField}"`)
      }
    })

    return normalizedData
  }

  /**
   * 轉換前端數據為後端格式（用於 API 請求）
   */
  static frontendToBackend(step: number, data: Record<string, any>): Record<string, any> {
    const config = FIELD_MAPPING_CONFIG[step]
    if (!config) return data

    const backendData: Record<string, any> = {}

    Object.entries(data).forEach(([frontendField, value]) => {
      const backendField = config.frontendToBackend[frontendField]
      if (backendField) {
        backendData[backendField] = value
      } else {
        console.warn(`⚠️ 未知的前端字段: ${frontendField}`)
        backendData[frontendField] = value // 保留未知字段
      }
    })

    return backendData
  }

  /**
   * 轉換後端數據為前端格式（用於 API 響應處理）
   */
  static backendToFrontend(step: number, data: Record<string, any>): Record<string, any> {
    const config = FIELD_MAPPING_CONFIG[step]
    if (!config) return data

    const frontendData: Record<string, any> = {}

    Object.entries(data).forEach(([backendField, value]) => {
      const frontendField = config.backendToFrontend[backendField]
      if (frontendField) {
        frontendData[frontendField] = value
      } else {
        console.warn(`⚠️ 未知的後端字段: ${backendField}`)
        frontendData[backendField] = value // 保留未知字段
      }
    })

    return frontendData
  }
}

// 類型檢查工具
export function ensureStep1DataIntegrity(data: any): data is Step1Data {
  const requiredFields: (keyof Step1Data)[] = [
    'name', 'id', 'phone', 'county', 'town', 'village', 'address',
    'undertracker', 'office', 'caseNumber', 'receivedDate', 'receivedTime'
  ]

  return requiredFields.every(field => field in data)
}

// 開發模式下的調試工具
export function debugFieldMapping(step: number, apiData: DataRecord) {
  if (!import.meta.env.DEV) return

  const validation = FieldMappingUtils.validateApiResponse(step, apiData)

  if (!validation.isValid) {
    console.group(`🔍 Step ${step} 字段映射調試信息`)

    if (validation.missingFields.length > 0) {
      console.warn('❌ 缺少的字段:', validation.missingFields)
    }

    if (validation.unexpectedFields.length > 0) {
      console.warn('⚠️ 未預期的字段:', validation.unexpectedFields)
    }

    if (validation.deprecatedFields.length > 0) {
      console.warn('🔄 檢測到棄用字段:', validation.deprecatedFields)
    }

    console.groupEnd()
  } else {
    console.log(`✅ Step ${step} 字段映射驗證通過`)
  }
}

// 新增：運行時字段映射自動驗證器
export class FieldMappingValidator {
  private static errorReported = new Set<string>()

  /**
   * 驗證 API 響應數據的字段完整性
   */
  static validateApiResponse(step: number, data: DataRecord, source: string = 'unknown'): {
    isValid: boolean
    errors: string[]
    warnings: string[]
  } {
    const config = FIELD_MAPPING_CONFIG[step]
    const errors: string[] = []
    const warnings: string[] = []

    if (!config) {
      errors.push(`未找到 Step ${step} 的字段映射配置`)
      return { isValid: false, errors, warnings }
    }

    // 定義通用元數據字段（所有 API 響應都會包含的基本字段）
    const commonMetadataFields = new Set(['id', 'case_number', 'current_step', 'status'])

    const expectedFields = new Set(Object.keys(config.backendToFrontend))
    const receivedFields = new Set(Object.keys(data))
    const deprecatedFields = new Set(Object.keys(config.deprecatedFields))

    // 檢查缺失字段
    const missingFields = [...expectedFields].filter(field => !receivedFields.has(field))
    if (missingFields.length > 0) {
      errors.push(`缺少必要字段: ${missingFields.join(', ')}`)
    }

    // 檢查未預期字段（排除棄用字段和通用元數據字段）
    const unexpectedFields = [...receivedFields].filter(field =>
      !expectedFields.has(field) && !deprecatedFields.has(field) && !commonMetadataFields.has(field)
    )
    if (unexpectedFields.length > 0) {
      warnings.push(`未預期的字段: ${unexpectedFields.join(', ')}`)
    }

    // 檢查棄用字段
    const foundDeprecatedFields = [...receivedFields].filter(field => deprecatedFields.has(field))
    if (foundDeprecatedFields.length > 0) {
      warnings.push(`發現棄用字段: ${foundDeprecatedFields.join(', ')}`)
    }

    // 在開發模式下報告錯誤
    if (import.meta.env.DEV) {
      const errorKey = `${source}-step${step}`
      if ((errors.length > 0 || warnings.length > 0) && !this.errorReported.has(errorKey)) {
        console.group(`🔍 字段映射驗證 [${source}] Step ${step}`)

        if (errors.length > 0) {
          console.error('❌ 錯誤:', errors)
        }

        if (warnings.length > 0) {
          console.warn('⚠️ 警告:', warnings)
        }

        console.groupEnd()
        this.errorReported.add(errorKey)
      }
    }

    return {
      isValid: errors.length === 0,
      errors,
      warnings
    }
  }

  /**
   * 驗證前端數據是否符合 TypeScript 類型
   */
  static validateFrontendData(step: number, data: DataRecord, typeName: string): {
    isValid: boolean
    errors: string[]
  } {
    const errors: string[] = []

    if (step === 1 && typeName === 'Step1Data') {
      const requiredFields: (keyof Step1Data)[] = [
        'name', 'id', 'phone', 'county', 'town', 'village', 'address',
        'undertracker', 'office', 'caseNumber', 'receivedDate', 'receivedTime'
      ]

      const missingFields = requiredFields.filter(field => !(field in data))
      if (missingFields.length > 0) {
        errors.push(`${typeName} 缺少必要字段: ${missingFields.join(', ')}`)
      }
    }

    return {
      isValid: errors.length === 0,
      errors
    }
  }

  /**
   * 重置錯誤報告狀態（用於測試）
   */
  static resetErrorReporting(): void {
    this.errorReported.clear()
  }
}

// 新增：字段映射中間件
export function createFieldMappingMiddleware() {
  return {
    /**
     * API 請求前的字段轉換中間件
     */
    beforeRequest: (step: number, data: DataRecord, endpoint: string) => {
      // 驗證前端數據
      if (step === 1) {
        const validation = FieldMappingValidator.validateFrontendData(step, data, 'Step1Data')
        if (!validation.isValid && import.meta.env.DEV) {
          console.warn(`📤 API 請求前數據驗證失敗 [${endpoint}]:`, validation.errors)
        }
      }

      // 轉換為後端格式
      const transformedData = FieldMappingUtils.frontendToBackend(step, data)

      if (import.meta.env.DEV) {
        console.log(`📤 API 請求字段轉換 [${endpoint}] Step ${step}:`, {
          original: data,
          transformed: transformedData
        })
      }

      return transformedData
    },

    /**
     * API 響應後的字段轉換中間件
     */
    afterResponse: (step: number, data: DataRecord, endpoint: string) => {
      // 驗證後端響應
      const validation = FieldMappingValidator.validateApiResponse(step, data, endpoint)

      // 轉換為前端格式
      const transformedData = FieldMappingUtils.backendToFrontend(step, data)

      if (import.meta.env.DEV) {
        console.log(`📥 API 響應字段轉換 [${endpoint}] Step ${step}:`, {
          original: data,
          transformed: transformedData,
          validation
        })
      }

      return transformedData
    }
  }
}

// 導出字段映射中間件實例
export const fieldMappingMiddleware = createFieldMappingMiddleware()
