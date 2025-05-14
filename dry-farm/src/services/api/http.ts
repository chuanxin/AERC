import axios from 'axios'
import type { AxiosInstance, InternalAxiosRequestConfig } from 'axios'
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

// // Interceptors
// api.interceptors.request.use(
//   (config: InternalAxiosRequestConfig): InternalAxiosRequestConfig => {
//     // Add token to headers if available (get token from local storage or any other storage)
//     const token = localStorage.getItem('auth_token')
//     if (token) {
//       config.headers.set('Authorization', `Bearer ${token}`)
//     }
//     return config
//   },
//   error => {
//     return Promise.reject(error)
//   }
// )

// // Response interceptor
// api.interceptors.response.use(
//   (response: AxiosResponse): AxiosResponse => {
//     return response
//   },
//   error => {
//     // Handle errors globally
//     if (error.response) {
//       // Server responded with a status code outside the range of 2xx
//       if (error.response.status === 401) {
//         // unauthorized
//         console.error('未授權，請重新登入')
//         localStorage.removeItem('auth_token')
//         window.location.href = '/login'
//       } else if (error.response.status === 403) {
//         // Forbidden
//         console.error('權限不足')
//       } else if (error.response.status === 500) {
//         // Internal Server Error
//         console.error('伺服器錯誤')
//       }
//     } else if (error.request) {
//       // Request was made but no response was received
//       console.error('網路錯誤，請檢查網路連接')
//     } else {
//       // Something happened in setting up the request that triggered an Error
//       // This is usually a configuration error
//       // or a problem with the request itself
//       // e.g. `axios.create` was called with an invalid config
//       console.error('請求錯誤', error.message)
//     }
//     return Promise.reject(error)
//   }
// )

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
  // async get<T = unknown>(url: string, params?: Record<string, unknown>, config?: InternalAxiosRequestConfig): Promise<T> {
  //   const response = await api.get<T>(url, {
  //     ...config,
  //     params
  //   })
  //   return response.data
  // },
  async get<T = unknown>(
    url: string,
    config?: InternalAxiosRequestConfig // 直接接收 Axios 配置對象
  ): Promise<T> {
    // 直接將傳入的 config (包含了 params 屬性) 傳遞給底層 api.get
    const response = await api.get<T>(url, config);
    return response.data;
  },

  /**
   * send POST request
   * @param url request URL or path defined in endpoints
   * @param data request body data
   * @param config additional configuration
   */
  async post<T = unknown>(url: string, data?: Record<string, unknown>, config?: InternalAxiosRequestConfig): Promise<T> {
    const response = await api.post<T>(url, data, config)
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

  // async postForm<T = unknown>(url: string, data?: Record<string, unknown>, config?: InternalAxiosRequestConfig): Promise<T> {
  //   const formData = new URLSearchParams();

  //   if (data) {
  //     Object.entries(data).forEach(([key, value]) => {
  //       if (value !== undefined && value !== null) {
  //         formData.append(key, String(value));
  //       }
  //     });
  //   }

  //   const response = await api.post<T>(url, formData, {
  //     ...config,
  //     headers: {
  //       'Content-Type': 'application/x-www-form-urlencoded',
  //       ...config?.headers
  //     }
  //   });

  //   return response.data;
  // },

  /**
   * send PUT request
   * @param url request URL or path defined in endpoints
   * @param data request body data
   * @param config additional configuration
   */
  async put<T = unknown>(url: string, data?: Record<string, unknown>, config?: InternalAxiosRequestConfig): Promise<T> {
    const response = await api.put<T>(url, data, config)
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
   * send upload request
   * @param url request URL or path defined in endpoints
   * @param formData form data
   * @param config additional configuration
   */
  async upload<T = unknown>(url: string, formData: FormData, config?: InternalAxiosRequestConfig): Promise<T> {
    const response = await api.post<T>(url, formData, {
      ...config,
      headers: {
        ...config?.headers,
        'Content-Type': 'multipart/form-data'
      }
    })
    return response.data
  },

  /**
   * send download request
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
  }
}

export default api
export { apiService }
