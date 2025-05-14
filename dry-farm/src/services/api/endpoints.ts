// API version
const API_VERSION = import.meta.env.FAST_API_VERSION || ''

// base URL for the API
const BASE = `${import.meta.env.FAST_API_BASE_URL || ''}/${API_VERSION}`

// // path for the backend API
// const BACKEND_PATHS = {
//   AUTH: {
//     LOGIN: '/login',
//     REGISTER: '/register',
//     WHO_AM_I: '/users/whoami',
//     LOGOUT: '/logout'
//   },
//   USERS: {
//     LIST: '/users',
//     DETAIL: (id: number | string) => `/user/${id}`,
//     DELETE: (id: number | string) => `/user/${id}`
//   },
//   NOTES: {
//     LIST: '/notes',
//     CREATE: '/notes',
//     DETAIL: (id: number | string) => `/note/${id}`,
//     UPDATE: (id: number | string) => `/note/${id}`,
//     DELETE: (id: number | string) => `/note/${id}`
//   }
// }

// authentication related endpoints
export const AUTH = {
  REGISTER: `${BASE}/auth/register`,
  LOGIN: `${BASE}/auth/login`,
  LOGOUT: `${BASE}/auth/logout`,
  REFRESH: `${BASE}/auth/refresh`,
  ME: `${BASE}/auth/me`,
  FORGOT_PASSWORD: `${BASE}/auth/forgot-password`,
  RESET_PASSWORD: `${BASE}/auth/reset-password`,
  CHANGE_PASSWORD: `${BASE}/auth/change-password`,
  VERIFY_EMAIL: `${BASE}/auth/verify-email`,
  RESEND_VERIFICATION: `${BASE}/auth/resend-verification`,
}

// user management related endpoints
export const USERS = {
  BASE: `${BASE}/users`,
  LIST: `${BASE}/users`,
  DETAIL: (id: number | string) => `${BASE}/users/${id}`,
  UPDATE: (id: number | string) => `${BASE}/users/${id}`,
  DELETE: (id: number | string) => `${BASE}/users/${id}`,
}

// budget related endpoints
export const BUDGET = {
  EXECUTION: `${BASE}/budget/execution`,
  EXPORT: `${BASE}/budget/export`,
  DETAIL: (year: string, month: string) => `${BASE}/budget/${year}/${month}`,
}

// grant related endpoints
export const GRANTS = {
  // BASE: `${BASE}/grants`,
  DETAIL: (id: number | string) => `${BASE}/grants/${id}`,
  // CREATE: `${BASE}/grants/new`,
  UPDATE: (id: number | string) => `${BASE}/grants/${id}`,
  DELETE: (id: number | string) => `${BASE}/grants/${id}`,
  // STEPS: {
  //   STEP1: (id: number | string) => `${BASE}/grants/${id}/step1`,
  //   STEP2: (id: number | string) => `${BASE}/grants/${id}/step2`,
  //   // ... 其他步驟
  // },
  CREATE: `${BASE}/grants`,
  // DETAIL: (id: string) => `${BASE}/grants/${id}`,
  BY_CASE_NUMBER: (caseNumber: string) => `${BASE}/grants/case/${caseNumber}`,
  // STEP: (id: number | string, step: number) => `${BASE}/grants/${id}/step/${step}`,
  STEP: (caseNumber: string, step: number) => `${BASE}/grants/case/${caseNumber}/step/${step}`,

}

// Pipe Fittings related endpoints
export const PIPE_FITTINGS = {
  BASE: `${BASE}/pipe_fittings`,
  CREATE: `${BASE}/pipe_fittings`,
  LIST: `${BASE}/pipe_fittings`, // For getting all with pagination
  DETAIL: (pomno: number | string) => `${BASE}/pipe_fittings/${pomno}`,
  UPDATE: (pomno: number | string) => `${BASE}/pipe_fittings/${pomno}`,
  DELETE: (pomno: number | string) => `${BASE}/pipe_fittings/${pomno}`,
  BY_OFFICE_ID: (officeId: number | string) => `${BASE}/pipe_fittings/office/${officeId}`,
}

export const PF_MODULES = {
  CREATE: '/pf_modules/',
  LIST: '/pf_modules/',
  DETAIL: (id: number | string) => `/pf_modules/${id}`,
  UPDATE: (id: number | string) => `/pf_modules/${id}`,
  DELETE: (id: number | string) => `/pf_modules/${id}`,
};

export const PF_MATERIALS = {
  CREATE: '/pf_materials/',
  LIST: '/pf_materials/',
  DETAIL: (id: number | string) => `/pf_materials/${id}`,
  UPDATE: (id: number | string) => `/pf_materials/${id}`,
  DELETE: (id: number | string) => `/pf_materials/${id}`,
};

export const PF_DIAMETERS = {
  CREATE: '/pf_diameters/',
  LIST: '/pf_diameters/',
  DETAIL: (id: number | string) => `/pf_diameters/${id}`,
  UPDATE: (id: number | string) => `/pf_diameters/${id}`,
  DELETE: (id: number | string) => `/pf_diameters/${id}`,
};

// statistics related endpoints
export const REPORTS = {
  BASE: `${BASE}/reports`,
  LIST: `${BASE}/reports/list`,
  DETAIL: (id: number | string) => `${BASE}/reports/${id}`,
  GENERATE: `${BASE}/reports/generate`,
}

// qualification related endpoints
export const QUALIFICATION = {
  CHECK: `${BASE}/qualification/check`,
  INDIGENOUS: `${BASE}/qualification/indigenous`,
}

export const OFFICES = {
  LIST: `${BASE}/offices`,
  // DETAIL: (id: number) => `${BASE}/offices/${id}`,
  CREATE: `${BASE}/offices`,
  UPDATE: (id: number) => `${BASE}/offices/${id}`,
  DELETE: (id: number) => `${BASE}/offices/${id}`,
}

export const DOMICILE = {
  COUNTIES_LIST: `${BASE}/domicile`,
  TOWNS_LIST: `${BASE}/domicile/towns`,
  VILLAGES_LIST: `${BASE}/domicile/villages`,
}

// export const API_MAPPING = {
//   [`${BASE}/auth/login`]: BACKEND_PATHS.AUTH.LOGIN,
//   [`${BASE}/auth/register`]: BACKEND_PATHS.AUTH.REGISTER,
//   [`${BASE}/auth/me`]: BACKEND_PATHS.AUTH.WHO_AM_I,
//   [`${BASE}/users`]: BACKEND_PATHS.USERS.LIST,
//   [`${BASE}/notes`]: BACKEND_PATHS.NOTES.LIST,
//   [`${BASE}/notes/create`]: BACKEND_PATHS.NOTES.CREATE
// }

// export const mapApiPath = (path: string): string => {
//   // 直接映射
//   if (API_MAPPING[path]) {
//     return API_MAPPING[path]
//   }

//   // 處理動態路徑映射
//   // 如 /api/v1/users/123 -> /user/123

//   // 用戶詳情
//   const userDetailRegex = new RegExp(`^${BASE}/users/(\\d+)$`);
//   if (userDetailRegex.test(path)) {
//     const id = path.match(userDetailRegex)?.[1]
//     return BACKEND_PATHS.USERS.DETAIL(id as string)
//   }

//   // 筆記詳情
//   const noteDetailRegex = new RegExp(`^${BASE}/notes/(\\d+)$`)
//   if (noteDetailRegex.test(path)) {
//     const id = path.match(noteDetailRegex)?.[1]
//     return BACKEND_PATHS.NOTES.DETAIL(id as string)
//   }

//   // 如果沒有映射規則，返回原路徑
//   return path
// }
// other related endpoints
