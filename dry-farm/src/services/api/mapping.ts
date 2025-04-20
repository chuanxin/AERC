import { AUTH, USERS } from './endpoints';

// 後端實際路徑定義
export const BACKEND_PATHS = {
  // 用戶認證相關
  AUTH: {
    LOGIN: '/login',
    REGISTER: '/register',
    WHO_AM_I: '/users/whoami',
    LOGOUT: '/logout'
  },
  // 用戶管理相關
  USERS: {
    LIST: '/users',
    DETAIL: (id: number | string) => `/user/${id}`,
    DELETE: (id: number | string) => `/user/${id}`
  },
  // 筆記相關
  NOTES: {
    LIST: '/notes',
    CREATE: '/notes',
    DETAIL: (id: number | string) => `/note/${id}`,
    UPDATE: (id: number | string) => `/note/${id}`,
    DELETE: (id: number | string) => `/note/${id}`
  }
};

// 前端到後端的直接映射表
export const API_MAPPING: Record<string, string> = {
  [AUTH.LOGIN]: BACKEND_PATHS.AUTH.LOGIN,
  [AUTH.REGISTER]: BACKEND_PATHS.AUTH.REGISTER,
  [AUTH.ME]: BACKEND_PATHS.AUTH.WHO_AM_I,
  [USERS.LIST]: BACKEND_PATHS.USERS.LIST,
};

// 動態參數路徑匹配規則
export const DYNAMIC_PATH_PATTERNS = [
  {
    // 匹配用戶詳情路徑 /api/v1/users/123
    pattern: new RegExp(`^${USERS.BASE}/([\\d]+)$`),
    transform: (matches: RegExpMatchArray) => BACKEND_PATHS.USERS.DETAIL(matches[1])
  },
  {
    // // 匹配筆記詳情路徑 /api/v1/notes/123
    // pattern: new RegExp(`^${NOTES.BASE}/([\\d]+)$`),
    // transform: (matches: RegExpMatchArray) => BACKEND_PATHS.NOTES.DETAIL(matches[1])
  }
];

/**
 * 將前端 API 路徑映射為後端實際路徑
 * @param path 前端 API 路徑
 * @returns 對應的後端實際路徑
 */
export function mapApiPath(path: string): string {
  // 1. 檢查直接映射
  if (API_MAPPING[path]) {
    return API_MAPPING[path];
  }

  // 2. 檢查動態路徑規則
  for (const { pattern, transform } of DYNAMIC_PATH_PATTERNS) {
    const matches = pattern ? path.match(pattern) : null;
    if (matches) {
      if (transform) {
        return transform(matches);
      }
    }
  }

  // 3. 沒有找到映射規則，返回原路徑
  // 可以在這裡添加警告日誌
  console.warn(`No mapping rule found for path: ${path}`);
  return path;
}
