import { AUTH, DOMICILE, OFFICES, USERS, GRANTS } from './endpoints';

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
  },
  OFFICES: {
    LIST: '/offices',
  },
  DOMICILE: {
    COUNTIES_LIST: '/counties',
    TOWNS_LIST: '/towns',
    // TOWNS_LIST: (countyId: number) => `/towns?county_id=${countyId}`,
    VILLAGES_LIST: '/villages',
  },
  GRANTS: {
    CREATE: '/grants',
    // DETAIL: (id: number | string) => `/grants/${id}`,
    DETAIL: (id: string) => `/grants/case/${id}`,
    // BY_CASE_NUMBER: (caseNumber: string) => `/grants?case_number=${caseNumber}`,
    BY_CASE_NUMBER: (caseNumber: string) => `/grants/case/${caseNumber}`,
    // STEP: (step: number) => `/grants/step/${step}`
    STEP: (caseNumber: string, step: number) => `/grants/case/${caseNumber}/step/${step}`,
  }
};

// 前端到後端的直接映射表
export const API_MAPPING: Record<string, string> = {
  [AUTH.LOGIN]: BACKEND_PATHS.AUTH.LOGIN,
  [AUTH.REGISTER]: BACKEND_PATHS.AUTH.REGISTER,
  [AUTH.ME]: BACKEND_PATHS.AUTH.WHO_AM_I,
  [USERS.LIST]: BACKEND_PATHS.USERS.LIST,
  [OFFICES.LIST]: BACKEND_PATHS.OFFICES.LIST,
  [DOMICILE.COUNTIES_LIST]: BACKEND_PATHS.DOMICILE.COUNTIES_LIST,
  [DOMICILE.TOWNS_LIST]: BACKEND_PATHS.DOMICILE.TOWNS_LIST,
  [DOMICILE.VILLAGES_LIST]: BACKEND_PATHS.DOMICILE.VILLAGES_LIST,
  [GRANTS.CREATE]: BACKEND_PATHS.GRANTS.CREATE,
  // [GRANTS.BY_CASE_NUMBER]: BACKEND_PATHS.GRANTS.BY_CASE_NUMBER,
  // [GRANTS.DETAIL]: BACKEND_PATHS.GRANTS.DETAIL,
  // [GRANTS.BY_CASE_NUMBER]: BACKEND_PATHS.GRANTS.BY_CASE_NUMBER,
  // [GRANTS.STEP]: BACKEND_PATHS.GRANTS.STEP,
}

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
  // Split the path from the query parameters
  const [basePath, queryString] = path.split('?');

  // 1. Map the base path using static mappings
  let mappedPath = API_MAPPING[basePath] || basePath;

  // 2. Check for dynamic mappings if no static mapping found
  if (!API_MAPPING[basePath]) {
    // 2.1 First try specific grant patterns
    const caseNumberMatch = basePath.match(/\/grants\/case\/([^\/]+)$/);
    if (caseNumberMatch) {
      const caseNumber = caseNumberMatch[1];
      mappedPath = BACKEND_PATHS.GRANTS.BY_CASE_NUMBER(caseNumber);
    } else {
      // 2.2 Check for grant step pattern
      const stepMatch = basePath.match(/\/grants\/case\/([^\/]+)\/step\/(\d+)$/);
      if (stepMatch) {
        const caseNumber = stepMatch[1];
        const step = parseInt(stepMatch[2], 10);
        mappedPath = BACKEND_PATHS.GRANTS.STEP(caseNumber, step);
      } else {
        // 2.3 Fall back to other dynamic pattern rules
        for (const { pattern, transform } of DYNAMIC_PATH_PATTERNS) {
          if (!pattern) continue;

          const matches = basePath.match(pattern);
          if (matches && transform) {
            mappedPath = transform(matches);
            break;
          }
        }
      }
    }
  }

  // 3. Reattach query parameters if they exist
  if (queryString) {
    mappedPath = `${mappedPath}?${queryString}`;
  }

  // 4. Log for debugging
  console.debug(`Mapped API path: ${path} -> ${mappedPath}`);

  return mappedPath;
}
