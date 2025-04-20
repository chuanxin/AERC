import type { AxiosInstance, InternalAxiosRequestConfig, AxiosResponse } from 'axios'
import { mapApiPath } from './mapping'

/**
 * 設置 Axios 實例的攔截器
 * @param api Axios 實例
 * @param options 配置選項
 */
export function setupInterceptors(
  api: AxiosInstance,
  options: {
    debug?: boolean;
    onUnauthorized?: () => void;
  } = {}
) {
  const { debug = false, onUnauthorized } = options;

  // 請求攔截器 - 處理 API 路徑映射和認證
  api.interceptors.request.use(
    (config: InternalAxiosRequestConfig): InternalAxiosRequestConfig => {
      // 保存原始 URL 以便調試
      const originalUrl = config.url;

      // 進行 API 路徑映射
      if (config.url) {
        // 將前端邏輯路徑映射為後端實際路徑
        const mappedUrl = mapApiPath(config.url);
        config.url = mappedUrl;

        if (debug) {
          // 記錄映射信息到請求頭，方便在網絡面板查看
          config.headers.set('X-Original-URL', originalUrl);
          config.headers.set('X-Mapped-URL', mappedUrl);

          // 打印日誌
          console.log(`API Request: ${config.method?.toUpperCase()} ${originalUrl} -> ${mappedUrl}`);
        }
      }

      // 添加授權令牌到請求頭
      const token = localStorage.getItem('auth_token');
      if (token) {
        config.headers.set('Authorization', `Bearer ${token}`);
      }

      return config;
    },
    error => {
      if (debug) {
        console.error('Request error:', error);
      }
      return Promise.reject(error);
    }
  );

  // 響應攔截器 - 處理錯誤和響應格式化
  api.interceptors.response.use(
    (response: AxiosResponse): AxiosResponse => {
      if (debug) {
        console.log(`API Response: ${response.config.method?.toUpperCase()} ${response.config.url} - Status: ${response.status}`);
      }
      return response;
    },
    error => {
      // 錯誤處理
      if (debug) {
        console.error('Response error:', {
          url: error.config?.url,
          method: error.config?.method,
          status: error.response?.status,
          data: error.response?.data
        });
      }

      // 處理未授權錯誤 (401)
      if (error.response?.status === 401) {
        // 清除認證信息
        localStorage.removeItem('auth_token');

        // 調用自定義未授權處理函數
        if (onUnauthorized) {
          onUnauthorized();
        } else {
          // 默認行為：重定向到登入頁面
          window.location.href = '/login';
        }
      }

      // 處理禁止訪問錯誤 (403)
      if (error.response?.status === 403) {
        console.error('權限不足，無法執行此操作');
      }

      return Promise.reject(error);
    }
  );

  // 返回配置好的 API 實例以支持鏈式調用
  return api;
}

/**
 * 建立一個測試用的攔截器，用於記錄和調試 API 請求
 * 僅在開發環境中使用
 */
export function setupDebugInterceptors(api: AxiosInstance) {
  const requestLog: {
    id: string;
    timestamp: string;
    method?: string;
    url?: string;
    params?: Record<string, unknown>;
    data?: unknown;
    headers?: Record<string, string | number | boolean | undefined>;
    status: string;
    statusCode?: number;
    responseData?: unknown;
    responseTime?: string;
    errorMessage?: string;
  }[] = [];

  // 記錄所有請求
  api.interceptors.request.use(
    config => {
      const timestamp = new Date().toISOString();
      const requestId = `${timestamp}-${Math.random().toString(36).substring(2, 9)}`;

      // 將請求信息保存到日誌
      requestLog.push({
        id: requestId,
        timestamp,
        method: config.method?.toUpperCase(),
        url: config.url,
        params: config.params,
        data: config.data,
        headers: config.headers,
        status: 'pending'
      });

      // 保存請求 ID 以便在響應中匹配
      config.headers.set('X-Request-ID', requestId);

      return config;
    }
  );

  // 記錄所有響應
  api.interceptors.response.use(
    response => {
      const requestId = response.config.headers['X-Request-ID'];
      const requestEntry = requestLog.find(entry => entry.id === requestId);

      if (requestEntry) {
        requestEntry.status = 'success';
        requestEntry.statusCode = response.status;
        requestEntry.responseData = response.data;
        requestEntry.responseTime = new Date().toISOString();
      }

      return response;
    },
    error => {
      const requestId = error.config?.headers?.['X-Request-ID'];
      const requestEntry = requestLog.find(entry => entry.id === requestId);

      if (requestEntry) {
        requestEntry.status = 'error';
        requestEntry.statusCode = error.response?.status;
        requestEntry.errorMessage = error.message;
        requestEntry.responseData = error.response?.data;
        requestEntry.responseTime = new Date().toISOString();
      }

      return Promise.reject(error);
    }
  );

  // 提供一個方法來訪問請求日誌
  interface ApiDebug {
    getRequestLog: () => typeof requestLog;
    clearRequestLog: () => void;
  }

  (window as unknown as { __apiDebug?: ApiDebug }).__apiDebug = {
    getRequestLog: () => requestLog,
    clearRequestLog: () => {
      requestLog.length = 0;
    }
  };

  return api;
}
