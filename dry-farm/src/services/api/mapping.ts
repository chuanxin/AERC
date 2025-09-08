import { AUTH, DOMICILE, OFFICES, USERS, GRANTS, PIPE_FITTINGS, PF_MODULES, PF_DIAMETERS, PF_MATERIALS, PF_ANNUAL_PRICES, IRRIGATION_TYPES, GIS, QUALIFICATION } from './endpoints';

// 取得當前的 API 版本前綴
const API_BASE_URL = import.meta.env.FAST_API_BASE_URL || '';
const API_VERSION = import.meta.env.FAST_API_VERSION || '';
const API_PREFIX = `${API_BASE_URL}/${API_VERSION}`;

/**
 * 移除 API 前綴，取得純淨的路徑
 * @param path 包含前綴的完整路徑
 * @returns 移除前綴後的路徑
 */
function removeApiPrefix(path: string): string {
  // 動態移除當前配置的 API 前綴
  if (path.startsWith(API_PREFIX)) {
    return path.substring(API_PREFIX.length);
  }
  return path;
}

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
  // // 筆記相關
  // NOTES: {
  //   LIST: '/notes',
  //   CREATE: '/notes',
  //   DETAIL: (id: number | string) => `/note/${id}`,
  //   UPDATE: (id: number | string) => `/note/${id}`,
  //   DELETE: (id: number | string) => `/note/${id}`
  // },
  OFFICES: {
    LIST: '/offices',
  },
  DOMICILE: {
    COUNTIES_LIST: '/counties',
    TOWNS_LIST: '/towns',
    // TOWNS_LIST: (countyId: number) => `/towns?county_id=${countyId}`,
    VILLAGES_LIST: '/villages',
    SECTIONS_LIST: '/sections',
  },
  GRANTS: {
    CREATE: '/grants',
    // DETAIL: (id: number | string) => `/grants/${id}`,
    DETAIL: (id: string) => `/grants/case/${id}`,
    // BY_CASE_NUMBER: (caseNumber: string) => `/grants?case_number=${caseNumber}`,
    BY_CASE_NUMBER: (caseNumber: string) => `/grants/case/${caseNumber}`,
    // STEP: (step: number) => `/grants/step/${step}`
    STEP: (caseNumber: string, step: number) => `/grants/case/${caseNumber}/step/${step}`,
    UPDATE_CURRENT_STEP: (caseNumber: string) => `/grants/case/${caseNumber}/current-step`,
    DELETE: (id: number | string) => `/grants/${id}`,
  },
  PIPE_FITTINGS: { // Added PIPE_FITTINGS backend paths
    LIST: '/pipe_fittings/', // For GET all and POST create
    DETAIL: (pomno: number | string) => `/pipe_fittings/${pomno}`, // For GET one, PUT, DELETE
    BY_OFFICE_ID: (officeId: number | string) => `/pipe_fittings/office/${officeId}`,
  },
  PF_MODULES: {
    LIST: '/pf_modules/',
    // DETAIL: (id: number | string) => `/pf_modules/${id}`,
    // CREATE: '/pf_modules',
    // UPDATE: (id: number | string) => `/pf_modules/${id}`,
    // DELETE: (id: number | string) => `/pf_modules/${id}`,
  },
  PF_DIAMETERS: {
    LIST: '/pf_diameters/',
  },
  PF_MATERIALS: {
    LIST: '/pf_materials/',
  },
  PF_ANNUAL_PRICES: {
    LIST: '/pf_annual_prices/',
    DETAIL: (id: number | string) => `/pf_annual_prices/${id}`,
    BY_PIPE_FITTING: (pipeFittingId: number | string) => `/pf_annual_prices/pipe_fitting/${pipeFittingId}`,
    CURRENT_PRICE: (pipeFittingId: number | string) => `/pf_annual_prices/pipe_fitting/${pipeFittingId}/current`,
  },
  IRRIGATION_TYPES: {
    LIST: '/irrigation_types/',
    OPTIONS: '/irrigation_types/options',
    DETAIL: (id: number | string) => `/irrigation_types/${id}`,
  },
  GIS: {
    POINTS: '/gis/points',
    STATS: '/gis/stats',
    SEARCH: '/gis/search',
  },
  QUALIFICATION: {
    SEARCH: '/qualification/search',
    HEALTH: '/qualification/health',
    INDIGENOUS_CHECK: '/qualification/indigenous-check',
    SLOPE_AREA_CHECK: '/qualification/slope-area-check',
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
  [PIPE_FITTINGS.LIST]: BACKEND_PATHS.PIPE_FITTINGS.LIST,
  [PIPE_FITTINGS.CREATE]: BACKEND_PATHS.PIPE_FITTINGS.LIST, // Assuming POST to the same base path
  [PF_ANNUAL_PRICES.LIST]: BACKEND_PATHS.PF_ANNUAL_PRICES.LIST,
  [PF_ANNUAL_PRICES.CREATE]: BACKEND_PATHS.PF_ANNUAL_PRICES.LIST,
  [PF_MODULES.LIST]: BACKEND_PATHS.PF_MODULES.LIST,
  [PF_DIAMETERS.LIST]: BACKEND_PATHS.PF_DIAMETERS.LIST,
  [PF_MATERIALS.LIST]: BACKEND_PATHS.PF_MATERIALS.LIST,
  [IRRIGATION_TYPES.LIST]: BACKEND_PATHS.IRRIGATION_TYPES.LIST,
  [IRRIGATION_TYPES.OPTIONS]: BACKEND_PATHS.IRRIGATION_TYPES.OPTIONS,
  [GIS.POINTS]: BACKEND_PATHS.GIS.POINTS,
  [GIS.STATS]: BACKEND_PATHS.GIS.STATS,
  [GIS.SEARCH]: BACKEND_PATHS.GIS.SEARCH,
  [QUALIFICATION.SEARCH]: BACKEND_PATHS.QUALIFICATION.SEARCH,
  [QUALIFICATION.HEALTH]: BACKEND_PATHS.QUALIFICATION.HEALTH,
  [QUALIFICATION.INDIGENOUS_CHECK]: BACKEND_PATHS.QUALIFICATION.INDIGENOUS_CHECK,
  [QUALIFICATION.SLOPE_AREA_CHECK]: BACKEND_PATHS.QUALIFICATION.SLOPE_AREA_CHECK,
}

// 動態參數路徑匹配規則
export const DYNAMIC_PATH_PATTERNS = [
  {
    // 匹配用戶詳情路徑 {API_PREFIX}/users/123
    pattern: new RegExp(`^${USERS.BASE.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}/([\\d]+)$`),
    transform: (matches: RegExpMatchArray) => BACKEND_PATHS.USERS.DETAIL(matches[1])
  },
  {
    // 匹配管道配件相關路徑
    pattern: new RegExp(`^${PIPE_FITTINGS.BASE.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}/office/([^/]+)$`),
    transform: (matches: RegExpMatchArray) => BACKEND_PATHS.PIPE_FITTINGS.BY_OFFICE_ID(matches[1])
  },
  {
    // 匹配管道配件詳情路徑
    pattern: new RegExp(`^${PIPE_FITTINGS.BASE.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}/(?!office/)([^/]+)$`),
    transform: (matches: RegExpMatchArray) => BACKEND_PATHS.PIPE_FITTINGS.DETAIL(matches[1])
  },
  {
    pattern: new RegExp(`^${PF_ANNUAL_PRICES.BASE.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}/pipe_fitting/([^/]+)$`),
    transform: (matches: RegExpMatchArray) => BACKEND_PATHS.PF_ANNUAL_PRICES.BY_PIPE_FITTING(matches[1])
  },
  {
    pattern: new RegExp(`^${PF_ANNUAL_PRICES.BASE.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}/pipe_fitting/([^/]+)/current$`),
    transform: (matches: RegExpMatchArray) => BACKEND_PATHS.PF_ANNUAL_PRICES.CURRENT_PRICE(matches[1])
  },
  {
    pattern: new RegExp(`^${PF_ANNUAL_PRICES.BASE.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}/([^/]+)$`),
    transform: (matches: RegExpMatchArray) => BACKEND_PATHS.PF_ANNUAL_PRICES.DETAIL(matches[1])
  }
];

/**
 * 將前端 API 路徑映射為後端實際路徑
 * @param frontendPath 前端 API 路徑 (e.g., /api/v1/grants/case/114020001/current-step)
 * @returns 對應的後端實際路徑 (e.g., /grants/case/114020001/current-step)
 */
export function mapApiPath(frontendPath: string): string {
  console.log('[mapApiPath] Input path:', frontendPath);
  const [basePathFromFrontend, queryString] = frontendPath.split('?');

  let mappedBasePath: string | undefined;

  // 1. Try static mapping first
  mappedBasePath = API_MAPPING[basePathFromFrontend];
  if (mappedBasePath) {
    console.debug(`[mapApiPath] Static mapping found for ${basePathFromFrontend}: ${mappedBasePath}`);
    if (queryString) {
      return `${mappedBasePath}?${queryString}`;
    }
    return mappedBasePath;
  }

  // 2. 移除 API 前綴，取得純淨的路徑進行動態匹配
  const cleanPath = removeApiPrefix(basePathFromFrontend);
  console.debug(`[mapApiPath] Cleaned path (removed prefix): ${cleanPath}`);

  // 3. 使用純淨路徑進行 grants 相關的動態匹配
  // 3.1 匹配 grants case number 路徑
  const caseNumberMatch = cleanPath.match(/^\/grants\/case\/([^\/]+)$/);
  if (caseNumberMatch) {
    const caseNumber = caseNumberMatch[1];
    mappedBasePath = BACKEND_PATHS.GRANTS.BY_CASE_NUMBER(caseNumber);
    console.debug(`[mapApiPath] Grant case number dynamic mapping for ${cleanPath}: ${mappedBasePath}`);
  } else {
    // 3.2 匹配 grants step 路徑
    const stepMatch = cleanPath.match(/^\/grants\/case\/([^\/]+)\/step\/(\d+)$/);
    if (stepMatch) {
      const caseNumber = stepMatch[1];
      const step = parseInt(stepMatch[2], 10);
      mappedBasePath = BACKEND_PATHS.GRANTS.STEP(caseNumber, step);
      console.debug(`[mapApiPath] Grant step dynamic mapping for ${cleanPath}: ${mappedBasePath}`);
    } else {
      // 3.3 匹配 grants current-step 路徑
      const currentStepMatch = cleanPath.match(/^\/grants\/case\/([^\/]+)\/current-step$/);
      if (currentStepMatch) {
        const caseNumber = currentStepMatch[1];
        mappedBasePath = BACKEND_PATHS.GRANTS.UPDATE_CURRENT_STEP(caseNumber);
        console.debug(`[mapApiPath] Grant current-step dynamic mapping for ${cleanPath}: ${mappedBasePath}`);
      } else {
        // 3.4 匹配 grants delete 路徑 (DELETE /grants/{id})
        const deleteMatch = cleanPath.match(/^\/grants\/(\d+)$/);
        if (deleteMatch) {
          const grantId = deleteMatch[1];
          mappedBasePath = BACKEND_PATHS.GRANTS.DELETE(grantId);
          console.debug(`[mapApiPath] Grant delete dynamic mapping for ${cleanPath}: ${mappedBasePath}`);
        }
      }
    }
  }

  // 4. 回退到通用動態模式匹配 (使用原始路徑)
  if (!mappedBasePath) {
    for (const { pattern, transform } of DYNAMIC_PATH_PATTERNS) {
      if (!pattern) continue;

      const matches = basePathFromFrontend.match(pattern);
      if (matches && transform) {
        const transformedPath = transform(matches);
        if (transformedPath) {
          mappedBasePath = transformedPath;
          console.debug(`[mapApiPath] Generic dynamic mapping for ${basePathFromFrontend} using pattern ${pattern}: ${mappedBasePath}`);
          break;
        }
      }
    }
  }

  // 5. 處理沒有找到映射的情況
  if (!mappedBasePath) {
    console.warn(`[mapApiPath] No mapping found for ${basePathFromFrontend}. Using original path.`);
    mappedBasePath = basePathFromFrontend;
  }

  // 6. 重新附加查詢參數
  if (queryString) {
    mappedBasePath = `${mappedBasePath}?${queryString}`;
  }

  console.debug(`[mapApiPath] Final mapped output for ${frontendPath}: ${mappedBasePath}`);
  return mappedBasePath;
}
