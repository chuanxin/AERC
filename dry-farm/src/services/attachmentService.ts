import { apiService } from './api/http'
import { ATTACHMENTS } from './api/endpoints'
import { ApplicationError } from '@/utils/asyncHelpers'

/**
 * 附件資料介面 - 對應後端 GrantAttachments 模型
 */
export interface AttachmentInfo {
  id: number
  grant_id: number
  step: number
  category: string
  original_filename: string
  internal_filename: string
  filepath: string
  filesize: number
  mime_type: string
  checksum?: string
  description?: string
  status: string
  uploaded_at: string
  uploaded_by?: {
    id: number
    username: string
    full_name: string
  }
}

/**
 * 附件列表回應介面
 */
export interface AttachmentListResponse {
  attachments: Array<{
    id: number
    original_filename: string
    filesize: number
    mime_type: string
    category: string
    description?: string
    uploaded_at: string
    uploaded_by: string
  }>
  total_count: number
  has_more: boolean
}

/**
 * 上傳回應介面
 */
export interface UploadResponse {
  success: boolean
  attachments: Array<{
    id: number
    category: string
    existed: boolean
  }>
  filename: string
  internal_filename: string
  filesize: number
  checksum: string
  file_reused: boolean
  categories_count: number
}

/**
 * 批量操作請求介面
 */
export interface BatchOperationRequest {
  operation: string
  attachment_ids: number[]
  parameters?: Record<string, unknown>
}

/**
 * 批量操作回應介面
 */
export interface BatchOperationResponse {
  success: boolean
  message: string
  processed_count: number
}

/**
 * 附件服務類 - 處理補助申請案件附件相關操作
 */
class AttachmentService {
  /**
   * 上傳附件
   * @param grantId 補助申請案件 ID
   * @param step 步驟編號 (5-8)
   * @param file 檔案物件
   * @param categories 檔案類別陣列（支援多個類別）
   * @param description 檔案說明（選填）
   * @param onProgress 上傳進度回調函數（選填）
   * @returns 上傳結果
   */
  async upload(
    grantId: number,
    step: number,
    file: File,
    categories: string | string[],
    description?: string,
    onProgress?: (progress: number) => void
  ): Promise<UploadResponse> {
    try {
      const formData = new FormData()
      formData.append('file', file)

      // 支援單一類別或多個類別
      if (Array.isArray(categories)) {
        // 多個類別：使用 categories 參數（JSON 陣列）
        formData.append('categories', JSON.stringify(categories))
      } else {
        // 單一類別：使用 category 參數
        formData.append('category', categories)
      }

      if (description) {
        formData.append('description', description)
      }

      // apiService.post 已經返回 response.data
      const data = await apiService.post<UploadResponse>(
        ATTACHMENTS.UPLOAD(grantId, step),
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          },
          onUploadProgress: (progressEvent) => {
            if (onProgress && progressEvent.total) {
              const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total)
              onProgress(percentCompleted)
            }
          }
        }
      )

      return data
    } catch (error) {
      console.error('上傳附件失敗:', error)
      throw new ApplicationError('上傳附件失敗', error)
    }
  }

  /**
   * 取得附件列表
   * @param grantId 補助申請案件 ID
   * @param step 步驟編號
   * @param category 檔案類別（選填）
   * @param limit 每頁數量
   * @param offset 偏移量
   * @returns 附件列表
   */
  async list(
    grantId: number,
    step: number,
    category?: string,
    limit: number = 100,
    offset: number = 0
  ): Promise<AttachmentListResponse> {
    try {
      const params: Record<string, string | number> = { limit, offset }
      if (category) {
        params.category = category
      }

      const url = ATTACHMENTS.LIST(grantId, step)
      console.log('[AttachmentService.list] Request URL:', url)
      console.log('[AttachmentService.list] Request params:', params)

      // apiService.get 已經返回 response.data，不需要再次訪問 .data
      const data = await apiService.get<AttachmentListResponse>(
        url,
        { params }
      )

      console.log('[AttachmentService.list] Response data:', data)
      return data
    } catch (error: any) {
      console.error('[AttachmentService.list] Error:', {
        error,
        message: error?.message,
        response: error?.response?.data,
        status: error?.response?.status,
        url: ATTACHMENTS.LIST(grantId, step),
        grantId,
        step
      })
      throw new ApplicationError('取得附件列表失敗', error)
    }
  }

  /**
   * 下載附件
   * @param attachmentId 附件 ID
   * @returns Blob 資料
   */
  async download(attachmentId: number): Promise<Blob> {
    try {
      // apiService.get 已經返回 response.data
      const blob = await apiService.get(ATTACHMENTS.DOWNLOAD(attachmentId), {
        responseType: 'blob'
      })

      return blob as Blob
    } catch (error) {
      console.error('下載附件失敗:', error)
      throw new ApplicationError('下載附件失敗', error)
    }
  }

  /**
   * 取得附件詳細資訊
   * @param attachmentId 附件 ID
   * @returns 附件資訊
   */
  async getInfo(attachmentId: number): Promise<AttachmentInfo> {
    try {
      // apiService.get 已經返回 response.data
      const data = await apiService.get<AttachmentInfo>(ATTACHMENTS.INFO(attachmentId))
      return data
    } catch (error) {
      console.error('取得附件資訊失敗:', error)
      throw new ApplicationError('取得附件資訊失敗', error)
    }
  }

  /**
   * 刪除附件
   * @param attachmentId 附件 ID
   * @returns 刪除結果
   */
  async delete(attachmentId: number): Promise<{ success: boolean; message: string }> {
    try {
      // apiService.delete 已經返回 response.data
      const data = await apiService.delete<{ success: boolean; message: string }>(
        ATTACHMENTS.DELETE(attachmentId)
      )
      return data
    } catch (error) {
      console.error('刪除附件失敗:', error)
      throw new ApplicationError('刪除附件失敗', error)
    }
  }

  /**
   * 批量操作附件
   * @param request 批量操作請求
   * @returns 批量操作結果
   */
  async batchOperation(request: BatchOperationRequest): Promise<BatchOperationResponse> {
    try {
      // apiService.post 已經返回 response.data
      const data = await apiService.post<BatchOperationResponse>(
        ATTACHMENTS.BATCH_OPERATION,
        request
      )
      return data
    } catch (error) {
      console.error('批量操作失敗:', error)
      throw new ApplicationError('批量操作失敗', error)
    }
  }

  /**
   * 輔助函數：觸發瀏覽器下載
   * @param blob Blob 資料
   * @param filename 檔案名稱
   */
  triggerDownload(blob: Blob, filename: string): void {
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  }
}

// 導出單例
export const attachmentService = new AttachmentService()
