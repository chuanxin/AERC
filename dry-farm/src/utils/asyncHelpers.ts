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

export interface ApiError {
  response?: {
    status?: number;
    data?: {
      detail?: string;
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

    // 嘗試從 response.data.detail 獲取錯誤信息
    if (apiError.response?.data?.detail) {
      return apiError.response.data.detail;
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
