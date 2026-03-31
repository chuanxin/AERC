import { apiService } from './api/http'
import { DOWNLOADS } from './api/endpoints'

export interface DownloadRequest {
  year: string
  case_number_start?: string | null
  case_number_end?: string | null
  file_type: string
  office_id?: number // added by Joya
  enable_pagination?: boolean
  tag?: string | null
}

export interface DataCheckResponse {
  has_data: boolean
  total_count: number
  message: string
}

// 靜態下載相關介面
export interface StaticFileInfo {
  id: string
  base_name: string
  filename: string
  format: string
  size: number
  created_at: string
  modified_at: string
  category: string | null
  description: string | null
  download_url: string
}

export interface FileGroup {
  base_name: string
  display_name: string
  formats: StaticFileInfo[]
  category: string | null
  description: string | null
  total_files: number
  latest_modified: string
}

export interface StaticDownloadsListResponse {
  file_groups: FileGroup[]
  total_groups: number
  total_files: number
  categories: string[]
}

export interface StaticDownloadsFilterRequest {
  category?: string | null
  format?: string | null
  search_keyword?: string | null
  date_range?: string | null
}

export interface BatchDownloadRequest {
  file_ids: string[]
  download_name?: string | null
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
        params,
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
        params
        // 不傳入filename參數，讓apiService從Content-Disposition header提取
      )

      return blob
    } catch (error) {
      console.error('下載工程預算書失敗:', error)
      throw error
    }
  }

  async downloadConstructionPhotos(params: DownloadRequest): Promise<Blob> {
    try {
      const blob = await apiService.downloadPost(DOWNLOADS.CONSTRUCTION_PHOTOS, params)
      return blob
    } catch (error) {
      console.error('下載施工前後照片失敗:', error)
      throw error
    }
  }

  async downloadAddressLabels(params: DownloadRequest): Promise<void> {
    try {
      await apiService.downloadPost(DOWNLOADS.ADDRESS_LABELS, params)
    } catch (error) {
      console.error('下載住址標籤失敗:', error)
      throw error
    }
  }

  async downloadClosingDocs(params: DownloadRequest): Promise<void> {
    try {
      await apiService.downloadPost(DOWNLOADS.CLOSING_DOCS, params)
    } catch (error) {
      console.error('下載結案文件失敗:', error)
      throw error
    }
  }

  async downloadReceipts(params: DownloadRequest): Promise<void> {
    try {
      await apiService.downloadPost(DOWNLOADS.RECEIPTS, params)
    } catch (error) {
      console.error('下載領款收據失敗:', error)
      throw error
    }
  }

  async downloadTestReports(params: DownloadRequest): Promise<void> {
    try {
      await apiService.downloadPost(DOWNLOADS.TEST_REPORTS, params)
    } catch (error) {
      console.error('下載功能測試報告書失敗:', error)
      throw error
    }
  }

  async downloadReviewForm(params: DownloadRequest): Promise<void> {
    try {
      await apiService.downloadPost(DOWNLOADS.REVIEW_FORM, params)
    } catch (error) {
      console.error('下載書面審查表失敗:', error)
      throw error
    }
  }

  async downloadCoverPage(params: DownloadRequest): Promise<void> {
    try {
      await apiService.downloadPost(DOWNLOADS.COVER_PAGE, params)
    } catch (error) {
      console.error('下載封面失敗:', error)
      throw error
    }
  }

  async downloadSubsidyDetailsList(params: DownloadRequest): Promise<void> {
    try {
      await apiService.downloadPost(DOWNLOADS.SUBSIDY_DETAILS_LIST, params, `subsidy_details_list_${params.year}.xlsx`)
    } catch (error) {
      console.error('下載管路補助金額明細表失敗:', error)
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

  // === 靜態檔案下載功能 ===

  /**
   * 取得靜態下載檔案清單
   * @param filter 篩選條件
   * @returns Promise<StaticDownloadsListResponse>
   */
  async getStaticFilesList(filter: StaticDownloadsFilterRequest = {}): Promise<StaticDownloadsListResponse> {
    try {
      const response = await apiService.post(
        DOWNLOADS.STATIC_FILES_LIST,
        filter as Record<string, unknown>
      )
      return response as StaticDownloadsListResponse
    } catch (error) {
      console.error('取得靜態檔案清單失敗:', error)
      throw error
    }
  }

  /**
   * 下載單一靜態檔案
   * @param fileId 檔案ID
   * @param filename 檔案名稱（用於下載）
   * @returns Promise<Blob>
   */
  async downloadStaticFile(fileId: string, filename: string): Promise<Blob> {
    try {
      const blob = await apiService.download(
        DOWNLOADS.STATIC_FILE_DOWNLOAD(fileId),
        undefined,
        filename
      )
      return blob
    } catch (error) {
      console.error('下載靜態檔案失敗:', error)
      throw error
    }
  }

  /**
   * 批量下載多個靜態檔案
   * @param request 批量下載請求
   * @returns Promise<Blob>
   */
  async batchDownloadStaticFiles(request: BatchDownloadRequest): Promise<Blob> {
    try {
      const blob = await apiService.downloadPost(
        DOWNLOADS.STATIC_FILES_BATCH,
        request as unknown as Record<string, unknown>,
        request.download_name || 'batch_download.zip'
      )
      return blob
    } catch (error) {
      console.error('批量下載靜態檔案失敗:', error)
      throw error
    }
  }

  // === 工具函數 ===

  /**
   * 格式化檔案大小
   * @param bytes 位元組數
   * @returns 格式化後的檔案大小字串
   */
  formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  /**
   * 格式化日期時間（民國年）
   * @param dateString 日期字串
   * @returns 格式化後的日期時間字串
   */
  formatDateTime(dateString: string): string {
    const date = new Date(dateString)
    const rocYear = date.getFullYear() - 1911 // 轉換為民國年
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    const hour = String(date.getHours()).padStart(2, '0')
    const minute = String(date.getMinutes()).padStart(2, '0')

    return `${rocYear}/${month}/${day} ${hour}:${minute}`
  }

  /**
   * 取得檔案圖示
   * @param format 檔案格式
   * @returns Material Design Icon 名稱
   */
  getFileIcon(format: string): string {
    const iconMap: Record<string, string> = {
      'pdf': 'mdi-file-pdf-box',
      'xlsx': 'mdi-file-excel',
      'xls': 'mdi-file-excel',
      'doc': 'mdi-file-word',
      'docx': 'mdi-file-word',
      'zip': 'mdi-folder-zip',
      'rar': 'mdi-folder-zip',
      'csv': 'mdi-file-delimited',
      'txt': 'mdi-file-document',
      'jpg': 'mdi-file-image',
      'jpeg': 'mdi-file-image',
      'png': 'mdi-file-image',
      'gif': 'mdi-file-image',
    }
    return iconMap[format.toLowerCase()] || 'mdi-file'
  }

  /**
   * 取得檔案圖示顏色
   * @param format 檔案格式
   * @returns 顏色名稱
   */
  getFileIconColor(format: string): string {
    const colorMap: Record<string, string> = {
      'pdf': 'red',
      'xlsx': 'green',
      'xls': 'green',
      'doc': 'blue',
      'docx': 'blue',
      'zip': 'orange',
      'rar': 'orange',
      'csv': 'teal',
      'txt': 'grey',
      'jpg': 'purple',
      'jpeg': 'purple',
      'png': 'purple',
      'gif': 'purple',
    }
    return colorMap[format.toLowerCase()] || 'grey'
  }
}

export const downloadsService = new DownloadsService()
export default downloadsService