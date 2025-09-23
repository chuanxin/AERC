import { apiService } from './api/http'
import { DOWNLOADS } from './api/endpoints'

export interface DownloadRequest {
  year: string
  case_number_start?: string | null
  case_number_end?: string | null
  file_type: string
  enable_pagination?: boolean
}

export interface DataCheckResponse {
  has_data: boolean
  total_count: number
  message: string
}

/**
 * Downloads Service - 處理各種文件下載功能
 */
class DownloadsService {
  /**
   * 下載外出拍攝照片攜帶表
   * @param params 下載參數
   * @returns Promise<Blob>
   */
  async downloadPhotographCarryForm(params: DownloadRequest): Promise<Blob> {
    try {
      // 使用統一的 apiService 和 downloadPost 方法
      const blob = await apiService.downloadPost(
        DOWNLOADS.PHOTOGRAPH_CARRY_FORM,
        params as Record<string, unknown>,
        `photograph_carry_form_${params.year}.xlsx`
      )

      return blob
    } catch (error) {
      console.error('下載外出拍攝照片攜帶表失敗:', error)
      throw error
    }
  }

  /**
   * 檢查指定條件下是否有資料
   * @param params 查詢參數
   * @returns Promise<DataCheckResponse>
   */
  async checkDataAvailability(params: Omit<DownloadRequest, 'enable_pagination'>): Promise<DataCheckResponse> {
    return apiService.post(DOWNLOADS.CHECK_DATA, params)
  }

  /**
   * 下載工程預算書PDF
   * @param params 下載參數
   * @returns Promise<Blob>
   */
  async downloadBudgetBook(params: DownloadRequest): Promise<Blob> {
    try {
      // 不傳入檔名，讓後端的 Content-Disposition header 決定檔名和副檔名
      // 這樣可以正確處理單檔PDF和多檔ZIP的情況
      const blob = await apiService.downloadPost(
        DOWNLOADS.BUDGET_BOOK,
        params as Record<string, unknown>
        // 不傳入filename參數，讓apiService從Content-Disposition header提取
      )

      return blob
    } catch (error) {
      console.error('下載工程預算書失敗:', error)
      throw error
    }
  }

  /**
   * 測試下載端點
   * @returns Promise<any>
   */
  async testDownloadEndpoint(): Promise<any> {
    return apiService.get(DOWNLOADS.TEST)
  }
}

export const downloadsService = new DownloadsService()
export default downloadsService