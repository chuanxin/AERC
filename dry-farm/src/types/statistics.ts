/**
 * Statistics 統計功能的 TypeScript 型別定義
 * 包含 B01 系列推動成果統計報表的資料結構
 */

// ==================== B01 系列推動成果統計報表（管理區內外分組） ====================

/**
 * 單一縣市的管理區內外統計資料
 */
export interface CountyManagementAreaStats {
  countyId: number
  countyName: string

  // 管理區內統計
  insideCases: number
  insideArea: number
  insideSubsidy: number

  // 管理區外統計
  outsideCases: number
  outsideArea: number
  outsideSubsidy: number
}

/**
 * 單一管理處的管理區內外統計資料
 */
export interface OfficeManagementAreaStats {
  officeId: number
  officeName: string

  // 管理區內統計
  insideCases: number
  insideArea: number
  insideSubsidy: number

  // 管理區外統計
  outsideCases: number
  outsideArea: number
  outsideSubsidy: number
}

/**
 * B01-1/B01-3 各縣市管理區內外統計回應
 */
export interface CountyManagementAreaStatsResponse {
  year?: number
  startYear?: number
  endYear?: number
  stats: CountyManagementAreaStats[]

  totalCases: number
  totalArea: number
  totalSubsidy: number
}

/**
 * B01-2/B01-4 各管理處管理區內外統計回應
 */
export interface OfficeManagementAreaStatsResponse {
  year?: number
  startYear?: number
  endYear?: number
  officeId?: number
  stats: OfficeManagementAreaStats[]

  totalCases: number
  totalArea: number
  totalSubsidy: number
}
