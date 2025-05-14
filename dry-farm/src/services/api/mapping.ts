import { AUTH, DOMICILE, OFFICES, USERS, GRANTS, PIPE_FITTINGS } from './endpoints';

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
  },
  PIPE_FITTINGS: { // Added PIPE_FITTINGS backend paths
    LIST: '/pipe_fittings', // For GET all and POST create
    DETAIL: (pomno: number | string) => `/pipe_fittings/${pomno}`, // For GET one, PUT, DELETE
    BY_OFFICE_ID: (officeId: number | string) => `/pipe_fittings/office/${officeId}`,
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
  [PIPE_FITTINGS.LIST]: BACKEND_PATHS.PIPE_FITTINGS.LIST,
  [PIPE_FITTINGS.CREATE]: BACKEND_PATHS.PIPE_FITTINGS.LIST, // Assuming POST to the same base path
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
  },
  {
    // Assuming PIPE_FITTINGS.BASE is /api/v1/pipe_fittings from endpoints.ts
    pattern: new RegExp(`^${PIPE_FITTINGS.BASE}/office/([^/]+)$`),
    transform: (matches: RegExpMatchArray) => BACKEND_PATHS.PIPE_FITTINGS.BY_OFFICE_ID(matches[1])
  },
  // Pattern for /pipe_fittings/{pomno}
  {
    // (?!office/) is a negative lookahead to prevent matching "/office/" as a pomno
    pattern: new RegExp(`^${PIPE_FITTINGS.BASE}/(?!office/)([^/]+)$`),
    transform: (matches: RegExpMatchArray) => BACKEND_PATHS.PIPE_FITTINGS.DETAIL(matches[1])
  },
];

// /**
//  * 將前端 API 路徑映射為後端實際路徑
//  * @param path 前端 API 路徑
//  * @returns 對應的後端實際路徑
//  */
// export function mapApiPath(path: string): string {
//   console.log('[mapApiPath] Input path:', path);
//   // Split the path from the query parameters
//   const [basePath, queryString] = path.split('?');

//   // 1. Map the base path using static mappings
//   let mappedPath = API_MAPPING[basePath] || basePath;
//   // let mappedBasePath = API_MAPPING[basePathFromFrontend];
//   // console.log('[mapApiPath] Static mapping lookup for', basePathFromFrontend, 'resulted in:', mappedBasePath);

//   // 2. Check for dynamic mappings if no static mapping found
//   if (!API_MAPPING[basePath]) {
//     // 2.1 First try specific grant patterns
//     const caseNumberMatch = basePath.match(/\/grants\/case\/([^\/]+)$/);
//     if (caseNumberMatch) {
//       const caseNumber = caseNumberMatch[1];
//       mappedPath = BACKEND_PATHS.GRANTS.BY_CASE_NUMBER(caseNumber);
//     } else {
//       // 2.2 Check for grant step pattern
//       const stepMatch = basePath.match(/\/grants\/case\/([^\/]+)\/step\/(\d+)$/);
//       if (stepMatch) {
//         const caseNumber = stepMatch[1];
//         const step = parseInt(stepMatch[2], 10);
//         mappedPath = BACKEND_PATHS.GRANTS.STEP(caseNumber, step);
//       } else {
//         // 2.3 Fall back to other dynamic pattern rules
//         for (const { pattern, transform } of DYNAMIC_PATH_PATTERNS) {
//           if (!pattern) continue;

//           const matches = basePath.match(pattern);
//           if (matches && transform) {
//             mappedPath = transform(matches);
//             break;
//           }
//         }
//       }
//     }
//   }

//   // If no mapping occurred (neither static nor dynamic), mappedPath will be undefined here.
//   // We should then probably use the original basePath, or decide if this is an error.
//   // Your original code defaulted to basePath if API_MAPPING[basePath] was null.
//   // Let's ensure mappedPath has a value. If it's still undefined after dynamic checks,
//   // it means the original basePath didn't get transformed.
//   if (!mappedPath) {
//       mappedPath = basePath; // Fallback to original basePath if no rules applied
//                            // This is what would cause the /api/v1 duplication if basePath still has it.
//                            // The goal of the mappings is to REMOVE /api/v1 if present in basePath.
//                            // So, if a path is not mapped, it's an issue.
//                            // For now, this matches your previous fallback.
//   }

//   // 3. Reattach query parameters if they exist
//   if (queryString) {
//     mappedPath = `${mappedPath}?${queryString}`;
//   }

//   // 4. Log for debugging
//   console.debug(`Mapped API path: ${path} -> ${mappedPath}`);

//   return mappedPath;
// }

/**
 * 將前端 API 路徑映射為後端實際路徑
 * @param frontendPath 前端 API 路徑 (e.g., /v1/pipe_fittings)
 * @returns 對應的後端實際路徑 (e.g., /pipe_fittings)
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

  // 2. No static mapping, try dynamic patterns
  //    (Your existing grant-specific logic can be here or integrated into DYNAMIC_PATH_PATTERNS)

  // 2.1 First try specific grant patterns (as in your existing code)
  const caseNumberMatch = basePathFromFrontend.match(/\/grants\/case\/([^\/]+)$/);
  if (caseNumberMatch) {
    const caseNumber = caseNumberMatch[1];
    mappedBasePath = BACKEND_PATHS.GRANTS.BY_CASE_NUMBER(caseNumber);
    console.debug(`[mapApiPath] Grant case number dynamic mapping for ${basePathFromFrontend}: ${mappedBasePath}`);
  } else {
    const stepMatch = basePathFromFrontend.match(/\/grants\/case\/([^\/]+)\/step\/(\d+)$/);
    if (stepMatch) {
      const caseNumber = stepMatch[1];
      const step = parseInt(stepMatch[2], 10);
      mappedBasePath = BACKEND_PATHS.GRANTS.STEP(caseNumber, step);
      console.debug(`[mapApiPath] Grant step dynamic mapping for ${basePathFromFrontend}: ${mappedBasePath}`);
    } else {
      // 2.2 Fall back to generic dynamic pattern rules from DYNAMIC_PATH_PATTERNS
      for (const { pattern, transform } of DYNAMIC_PATH_PATTERNS) {
        if (!pattern) continue; // Skip if pattern is somehow undefined

        const matches = basePathFromFrontend.match(pattern);
        if (matches && transform) {
          const transformedPath = transform(matches);
          if (transformedPath) { // Ensure transform actually returned a path
            mappedBasePath = transformedPath;
            console.debug(`[mapApiPath] Generic dynamic mapping for ${basePathFromFrontend} using pattern ${pattern}: ${mappedBasePath}`);
            break;
          }
        }
      }
    }
  }

  // 3. Handle cases where no mapping was found
  if (!mappedBasePath) {
    // If no mapping rule applied, this is a problem.
    // It means the frontend is requesting a path that the mapping logic doesn't know how to handle.
    // This will likely lead to incorrect URLs if the apiClient.baseURL also contains a prefix like /v1.
    console.warn(`[mapApiPath] No mapping found for ${basePathFromFrontend}. Using original path. This might lead to URL issues if prefixes are duplicated.`);
    mappedBasePath = basePathFromFrontend; // Fallback, but be aware of potential prefix duplication
  }

  // 4. Reattach query parameters if they exist
  if (queryString) {
    mappedBasePath = `${mappedBasePath}?${queryString}`;
  }

  console.debug(`[mapApiPath] Final mapped output for ${frontendPath}: ${mappedBasePath}`);
  return mappedBasePath;
}
