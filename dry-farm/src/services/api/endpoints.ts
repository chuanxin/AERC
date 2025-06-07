// API version
const API_VERSION = import.meta.env.FAST_API_VERSION || ''

// base URL for the API
const BASE = `${import.meta.env.FAST_API_BASE_URL || ''}/${API_VERSION}`

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
  CREATE: `${BASE}/pipe_fittings/`,
  LIST: `${BASE}/pipe_fittings/`, // For getting all with pagination
  DETAIL: (pomno: number | string) => `${BASE}/pipe_fittings/${pomno}`,
  UPDATE: (pomno: number | string) => `${BASE}/pipe_fittings/${pomno}`,
  DELETE: (pomno: number | string) => `${BASE}/pipe_fittings/${pomno}`,
  BY_OFFICE_ID: (officeId: number | string) => `${BASE}/pipe_fittings/office/${officeId}`,
}

export const PF_ANNUAL_PRICES = {
  BASE: `${BASE}/pf_annual_prices`,
  CREATE: `${BASE}/pf_annual_prices/`,
  LIST: `${BASE}/pf_annual_prices/`,
  DETAIL: (id: number | string) => `${BASE}/pf_annual_prices/${id}`,
  BY_PIPE_FITTING: (pipeFittingId: number | string) => `${BASE}/pf_annual_prices/pipe_fitting/${pipeFittingId}`,
  CURRENT_PRICE: (pipeFittingId: number | string) => `${BASE}/pf_annual_prices/pipe_fitting/${pipeFittingId}/current`,
  UPDATE: (id: number | string) => `${BASE}/pf_annual_prices/${id}`,
  DELETE: (id: number | string) => `${BASE}/pf_annual_prices/${id}`,
}

export const PF_MODULES = {
  CREATE: `${BASE}/pf_modules`,
  LIST: `${BASE}/pf_modules/`,
  DETAIL: (id: number | string) => `${BASE}/pf_modules/${id}`,
  UPDATE: (id: number | string) => `${BASE}/pf_modules/${id}`,
  DELETE: (id: number | string) => `${BASE}/pf_modules/${id}`,
};

export const PF_MATERIALS = {
  CREATE: `${BASE}/pf_materials/`,
  LIST: `${BASE}/pf_materials/`,
  DETAIL: (id: number | string) => `${BASE}/pf_materials/${id}`,
  UPDATE: (id: number | string) => `${BASE}/pf_materials/${id}`,
  DELETE: (id: number | string) => `${BASE}/pf_materials/${id}`,
};

export const PF_DIAMETERS = {
  CREATE: `${BASE}/pf_diameters/`,
  LIST: `${BASE}/pf_diameters/`,
  DETAIL: (id: number | string) => `${BASE}/pf_diameters/${id}`,
  UPDATE: (id: number | string) => `${BASE}/pf_diameters/${id}`,
  DELETE: (id: number | string) => `${BASE}/pf_diameters/${id}`,
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

export const IRRIGATION_TYPES = {
  LIST: `${BASE}/irrigation_types`,
  OPTIONS: `${BASE}/irrigation_types/options`,
  DETAIL: (id: number | string) => `${BASE}/irrigation_types/${id}`,
}

// Grant versions related endpoints
export const GRANT_VERSIONS = {
  BASE: `${BASE}/grant-versions`,
  CREATE: `${BASE}/grant-versions`,
  BY_GRANT: (grantId: number | string) => `${BASE}/grant-versions/grant/${grantId}`,
  DETAIL: (versionId: number | string) => `${BASE}/grant-versions/${versionId}`,
  UPDATE: (versionId: number | string) => `${BASE}/grant-versions/${versionId}`,
  DELETE: (versionId: number | string) => `${BASE}/grant-versions/${versionId}`,
  COMPARE: `${BASE}/grant-versions/compare`,
  SET_ACTIVE: (grantId: number | string, versionId: number | string) => `${BASE}/grant-versions/grant/${grantId}/active-version/${versionId}`,
  GET_ACTIVE: (grantId: number | string) => `${BASE}/grant-versions/grant/${grantId}/active`,
  FROM_CURRENT: (caseNumber: string) => `${BASE}/grant-versions/from-current/${caseNumber}`,
  SUMMARY: (grantId: number | string) => `${BASE}/grant-versions/grant/${grantId}/summary`,
}

// other related endpoints
