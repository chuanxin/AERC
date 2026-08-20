import { ref, type Ref } from 'vue'

export class ApplicationError extends Error {
  status: number
  source: string
  originalError?: unknown

  constructor({
    message,
    status = 500,
    source = 'unknown',
    originalError
  }: {
    message: string
    status?: number
    source?: string
    originalError?: unknown
  }) {
    super(message)
    this.name = 'ApplicationError'
    this.status = status
    this.source = source
    this.originalError = originalError
  }
}

/** 後端 4xx 的 detail 可能是字串，也可能是結構化物件（如 429 節流帶 retry_after_seconds、
 *  MFA 驗證失敗帶 attempts_remaining、憑證類錯誤帶 error_code），見 api/src 共 13 處用法 */
export type ApiErrorDetail =
  | string
  | {
      message?: string;
      error_code?: string;
      retry_after_seconds?: number;
      [key: string]: unknown;
    };

export interface ApiError {
  response?: {
    status?: number;
    data?: {
      detail?: ApiErrorDetail;
      message?: string;
    }
  };
  message?: string;
}

interface UseAsyncOptions {
  loadingRef?: Ref<boolean>;
  errorRef?: Ref<string | null>;
  errorFormatter?: (error: unknown) => string;
}

export function wrapAsync<T, Args extends unknown[] = unknown[]>(
  operation: (...args: Args) => Promise<T>,
  options?: UseAsyncOptions
): (...args: Args) => Promise<T | null> {
  const {
    loadingRef = ref(false),
    errorRef = ref(null),
    errorFormatter = defaultErrorFormatter
  } = options || {};

  return async (...args: Args): Promise<T | null> => {
    loadingRef.value = true;
    errorRef.value = null;

    try {
      const result = await operation(...args);
      return result;
    } catch (error: unknown) {
      errorRef.value = errorFormatter(error);
      console.error('操作失敗:', error);
      return null;
    } finally {
      loadingRef.value = false;
    }
  };
}

function defaultErrorFormatter(error: unknown): string {
  if (!error) return '未知錯誤';

  // 處理 API 錯誤
  if (typeof error === 'object') {
    const apiError = error as ApiError;

    // 嘗試從 response.data.detail 獲取錯誤信息。
    // detail 可能是結構化物件（比照 mfa.py／user_management.py 的節流回應），直接回傳會讓
    // 呼叫端把物件塞進畫面渲染成 [object Object]，故一律正規化為字串；
    // 節流類錯誤額外把剩餘秒數併入訊息，否則使用者不知道要等多久
    const detail = apiError.response?.data?.detail;
    if (typeof detail === 'string' && detail) {
      return detail;
    }
    if (detail && typeof detail === 'object') {
      const text = typeof detail.message === 'string' ? detail.message : '操作失敗';
      const retryAfter = detail.retry_after_seconds;
      return typeof retryAfter === 'number' && retryAfter > 0
        ? `${text}（請於 ${retryAfter} 秒後再試）`
        : text;
    }

    // 嘗試從 response.data.message 獲取錯誤信息
    if (apiError.response?.data?.message) {
      return apiError.response.data.message;
    }

    // 嘗試從標準 Error.message 獲取錯誤信息
    if (apiError.message) {
      return apiError.message;
    }
  }

  // 處理字符串錯誤
  if (typeof error === 'string') {
    return error;
  }

  return '操作失敗';
}
