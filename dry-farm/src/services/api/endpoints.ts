// API version
const API_VERSION = import.meta.env.FAST_API_VERSION || ''

// base URL for the API
const BASE = `${import.meta.env.FAST_API_BASE_URL || ''}/${API_VERSION}`

// authentication related endpoints
export const AUTH = {
  REGISTER: `${BASE}/register`,
  LOGIN: `${BASE}/login`,
  LOGIN_SECURE: `${BASE}/login-secure`,
  LOGOUT: `${BASE}/logout`,
  REFRESH: `${BASE}/refresh`,
  ME: `${BASE}/users/whoami`,
  CAPTCHA: `${BASE}/captcha`,
  REQUEST_PASSWORD_RESET: `${BASE}/request-password-reset`,
  VERIFY_OTP: `${BASE}/verify-otp`,
  RESET_PASSWORD: `${BASE}/reset-password`,
  SEND_VERIFICATION_EMAIL: `${BASE}/send-verification-email`,
  VERIFY_EMAIL: `${BASE}/verify-email`,
}

// user management related endpoints
export const USERS = {
  BASE: `${BASE}/users`,
  LIST: `${BASE}/users`,
  DETAIL: (id: number | string) => `${BASE}/users/${id}`,
  UPDATE: (id: number | string) => `${BASE}/users/${id}`,
  DELETE: (id: number | string) => `${BASE}/users/${id}`,
}

// GIS related endpoints
export const GIS = {
  BASE: `${BASE}/gis`,
  POINTS: `${BASE}/gis/points`,
  STATS: `${BASE}/gis/stats`,
  SEARCH: `${BASE}/gis/search`,
}

// budget related endpoints
export const BUDGET = {
  EXECUTION: `${BASE}/budget/execution`,
  EXPORT: `${BASE}/budget/export`,
  DETAIL: (year: string, month: string) => `${BASE}/budget/${year}/${month}`,
}

// grant related endpoints
export const GRANTS = {
  BASE: `${BASE}/grants`,
  LIST: `${BASE}/grants`,
  CREATE: `${BASE}/grants`,
  DETAIL: (id: number | string) => `${BASE}/grants/${id}`,
  UPDATE: (id: number | string) => `${BASE}/grants/${id}`,
  DELETE: (id: number | string) => `${BASE}/grants/${id}`,
  BY_CASE_NUMBER: (caseNumber: string) => `${BASE}/grants/case/${caseNumber}`,
  STEP: (caseNumber: string, step: number) => `${BASE}/grants/case/${caseNumber}/step/${step}`,
  UPDATE_CURRENT_STEP: (caseNumber: string) => `${BASE}/grants/case/${caseNumber}/current-step`,
  UPDATE_STATUS: (caseNumber: string) => `${BASE}/grants/case/${caseNumber}/status`,
  APPLICANT_SUBSIDY_SUMMARY: (applicantId: string, year: number) =>
    `${BASE}/grants/applicant-subsidy-summary/${applicantId}/${year}`,
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
  BASE: `${BASE}/qualification`,
  SEARCH: `${BASE}/qualification/search`,
  HEALTH: `${BASE}/qualification/health`,
  INDIGENOUS_CHECK: `${BASE}/qualification/indigenous-check`,
  SLOPE_AREA_CHECK: `${BASE}/qualification/slope-area-check`,
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
  SECTIONS_LIST: `${BASE}/domicile/sections`,
}

export const SPATIAL = {
  OFFICE: `${BASE}/spatial/office`,
  COUNTY: `${BASE}/spatial/county`,
}

export const IRRIGATION_TYPES = {
  LIST: `${BASE}/irrigation_types`,
  OPTIONS: `${BASE}/irrigation_types/options`,
  DETAIL: (id: number | string) => `${BASE}/irrigation_types/${id}`,
}

// downloads related endpoints
export const DOWNLOADS = {
  BASE: `${BASE}/download`,
  PHOTOGRAPH_CARRY_FORM: `${BASE}/download/photograph-carry-form`,
  BUDGET_BOOK: `${BASE}/download/budget-book`,
  CHECK_DATA: `${BASE}/download/check-data`,
  TEST: `${BASE}/download/test`,
  // 靜態檔案下載端點
  STATIC_FILES_LIST: `${BASE}/download/static-files`,
  STATIC_FILE_DOWNLOAD: (fileId: string) => `${BASE}/download/static-file/${fileId}`,
  STATIC_FILES_BATCH: `${BASE}/download/static-files/batch`,
}

// grant attachments related endpoints
export const ATTACHMENTS = {
  BASE: `${BASE}/attachments`,
  UPLOAD: (grantId: number, step: number) => `${BASE}/attachments/upload/${grantId}/${step}`,
  LIST: (grantId: number, step: number) => `${BASE}/attachments/list/${grantId}/${step}`,
  DOWNLOAD: (attachmentId: number) => `${BASE}/attachments/download/${attachmentId}`,
  INFO: (attachmentId: number) => `${BASE}/attachments/info/${attachmentId}`,
  DELETE: (attachmentId: number) => `${BASE}/attachments/${attachmentId}`,
  BATCH_OPERATION: `${BASE}/attachments/batch-operation`,
}
