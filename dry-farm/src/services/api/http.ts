import axios from 'axios'
import type { AxiosInstance, InternalAxiosRequestConfig, AxiosProgressEvent } from 'axios'
import { setupInterceptors, setupDebugInterceptors } from './interceptors'


// Axios instance
const api: AxiosInstance = axios.create({
  baseURL: (import.meta.env.FAST_API_BASE_URL || '') + '/' + (import.meta.env.FAST_API_VERSION || ''),
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
})

// 設置攔截器
setupInterceptors(api, {
  debug: import.meta.env.DEV, // 僅在開發環境啟用調試
  onUnauthorized: () => {
    // 處理未授權情況的自定義邏輯
    console.warn('用戶未授權，重定向到登入頁面');
    window.location.href = '/login'
  }
})

if (import.meta.env.DEV) {
  setupDebugInterceptors(api);
}

// encapsulate API service methods and support directly calling endpoints
const apiService = {
  /**
   * send GET request
   * @param url path or URL defined in endpoints
   * @param params query parameters
   * @param config additional configuration
   */
  async get<T = unknown>(
    url: string,
    config?: { params?: Record<string, unknown> } & Partial<InternalAxiosRequestConfig>
  ): Promise<T> {
    // 直接將傳入的 config (包含了 params 屬性) 傳遞給底層 api.get
    const response = await api.get<T>(url, config as InternalAxiosRequestConfig);
    return response.data;
  },

  /**
   * send POST request
   * @param url request URL or path defined in endpoints
   * @param data request body data
   * @param config additional configuration (supports responseType, headers, etc.)
   */
  async post<T = unknown, D extends object = object>(
    url: string,
    data?: D,
    config?: Partial<InternalAxiosRequestConfig>
  ): Promise<T> {
    const response = await api.post<T>(url, data, config as InternalAxiosRequestConfig)
    return response.data
  },

  async postForm<T>(url: string, data: Record<string, string>): Promise<T> {
    const formData = new URLSearchParams();
    for (const key in data) {
      formData.append(key, data[key]);
    }

    const response = await api.post<T>(url, formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    });
    return response.data;
  },

  /**
   * send PUT request
   * @param url request URL or path defined in endpoints
   * @param data request body data
   * @param config additional configuration
   */
  async put<T = unknown, D extends object = object>(url: string, data?: D, config?: InternalAxiosRequestConfig): Promise<T> {
    const response = await api.put<T>(url, data, config)
    return response.data
  },

  /**
   * send PATCH request
   * @param url request URL or path defined in endpoints
   * @param data request body data
   * @param config additional configuration
   */
  async patch<T = unknown, D extends object = object>(url: string, data?: D, config?: InternalAxiosRequestConfig): Promise<T> {
    const response = await api.patch<T>(url, data, config)
    return response.data
  },

  /**
   * send DELETE request
   * @param url request URL or path defined in endpoints
   * @param config additional configuration
   */
  async delete<T = unknown>(url: string, config?: InternalAxiosRequestConfig): Promise<T> {
    const response = await api.delete<T>(url, config)
    return response.data
  },

  /**
   * send upload request with optional progress tracking
   * @param url request URL or path defined in endpoints
   * @param formData form data
   * @param config additional configuration including onUploadProgress
   */
  async upload<T = unknown>(
    url: string,
    formData: FormData,
    config?: {
      onUploadProgress?: (progressEvent: AxiosProgressEvent) => void
    } & Partial<InternalAxiosRequestConfig>
  ): Promise<T> {
    const response = await api.post<T>(url, formData, {
      ...config,
      headers: {
        ...config?.headers,
        'Content-Type': 'multipart/form-data'
      }
    } as InternalAxiosRequestConfig)
    return response.data
  },

  /**
   * send download request (GET)
   * @param url request URL or path defined in endpoints
   * @param params query parameters
   * @param filename download filename
   */
  async download(url: string, params?: Record<string, unknown>, filename?: string): Promise<Blob> {
    const response = await api.get(url, {
      params,
      responseType: 'blob'
    })

    // Create a blob URL for the response data
    // and create a link element to trigger the download
    const blob = new Blob([response.data])
    const downloadUrl = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = downloadUrl

    // Set the download attribute to specify the filename
    // If filename is not provided, try to extract it from the response headers
    const contentDisposition = response.headers['content-disposition']
    let downloadFilename = filename

    if (!downloadFilename && contentDisposition) {
      const filenameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/
      const matches = filenameRegex.exec(contentDisposition)
      if (matches != null && matches[1]) {
        downloadFilename = matches[1].replace(/['"]/g, '')
      }
    }

    if (downloadFilename) {
      link.setAttribute('download', downloadFilename)
    }

    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(downloadUrl)

    return blob
  },

  /**
   * send download request (POST)
   * @param url request URL or path defined in endpoints
   * @param data request body data
   * @param filename download filename
   */
  async downloadPost<D extends object = object>(url: string, data?: D, filename?: string): Promise<Blob> {
    const response = await api.post(url, data, {
      responseType: 'blob'
    })

    // Create a blob URL for the response data
    // and create a link element to trigger the download
    const blob = new Blob([response.data])
    const downloadUrl = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = downloadUrl

    // Set the download attribute to specify the filename
    // If filename is not provided, try to extract it from the response headers
    const contentDisposition = response.headers['content-disposition']
    let downloadFilename = filename

    if (!downloadFilename && contentDisposition) {
      const filenameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/
      const matches = filenameRegex.exec(contentDisposition)
      if (matches != null && matches[1]) {
        downloadFilename = matches[1].replace(/['"]/g, '')
      }
    }

    if (downloadFilename) {
      link.setAttribute('download', downloadFilename)
    }

    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(downloadUrl)

    return blob
  }
}

export default api
export { apiService }
