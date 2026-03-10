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
  CHANGE_PASSWORD: `${BASE}/change-password`,
}

// user management related endpoints
export const USERS = {
  BASE: `${BASE}/users`,
  LIST: `${BASE}/users`,
  DETAIL: (id: number | string) => `${BASE}/users/${id}`,
  UPDATE: (id: number | string) => `${BASE}/users/${id}`,
  DELETE: (id: number | string) => `${BASE}/users/${id}`,
  MIGRATE_VERIFY_OTP: `${BASE}/login/migrate/verify-otp`,
  MIGRATE: `${BASE}/login/migrate/complete`,
}

// user management (admin) related endpoints
export const USER_MANAGEMENT = {
  BASE: `${BASE}/user-management`,
  LIST: `${BASE}/user-management`,
  DETAIL: (id: number) => `${BASE}/user-management/${id}`,
  UPDATE_PERMISSIONS: (id: number) => `${BASE}/user-management/${id}/permissions`,
  BATCH_ACTIVATE: `${BASE}/user-management/batch-activate`,
  BATCH_DEACTIVATE: `${BASE}/user-management/batch-deactivate`,
  PENDING_APPROVAL: `${BASE}/user-management/pending-approval`,
  APPROVE: (id: number) => `${BASE}/user-management/${id}/approve`,
  REJECT: (id: number) => `${BASE}/user-management/${id}/reject`,
}

// permissions related endpoints
export const PERMISSIONS = {
  BASE: `${BASE}/permissions`,
  CHECK: `${BASE}/permissions/check`,
  SUMMARY: `${BASE}/permissions/summary`,
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
  CLAIM_OWNERSHIP: (grantId: number) => `${BASE}/grants/${grantId}/claim-ownership`,
  APPLICANT_SUBSIDY_SUMMARY: (applicantId: string, year: number) =>
    `${BASE}/grants/applicant-subsidy-summary/${applicantId}/${year}`,
  COMPLETION_STATEMENT: (caseNumber: string) => `${BASE}/grants/case/${caseNumber}/completion-statement`,
  DECLARATION: (caseNumber: string) => `${BASE}/grants/case/${caseNumber}/declaration`,
  AUTHORIZATION: (caseNumber: string) => `${BASE}/grants/case/${caseNumber}/authorization`,
  BUDGET_STATEMENT: (caseNumber: string) => `${BASE}/grants/case/${caseNumber}/budget-statement`,
}

// Statistics related endpoints
export const STATISTICS = {
  EXECUTION_PROGRESS: `${BASE}/grants/statistics/execution-progress`,
  BUDGET_ANALYSIS: `${BASE}/grants/statistics/budget-analysis`,
  // Excel 報表下載
  EXECUTION_PROGRESS_EXCEL: `${BASE}/grants/statistics/execution-progress/excel`,
  BUDGET_ANALYSIS_EXCEL: `${BASE}/grants/statistics/budget-analysis/excel`,
  // A02 系列
  COUNTY_TOWN_EXCEL: `${BASE}/grants/statistics/county-town/excel`,
  OFFICE_SUMMARY_EXCEL: `${BASE}/grants/statistics/office-summary/excel`,
  COUNTY_TOWN_YEARLY_EXCEL: `${BASE}/grants/statistics/county-town-yearly/excel`,
  OFFICE_SUMMARY_YEARLY_EXCEL: `${BASE}/grants/statistics/office-summary-yearly/excel`,
  // A07 原民區域統計
  ABORIGINAL_STATS_EXCEL: `${BASE}/grants/statistics/aboriginal/excel`,
  // A08 歷年原民區域統計
  ABORIGINAL_YEARLY_EXCEL: `${BASE}/grants/statistics/aboriginal-yearly/excel`,
  // B01 系列推動成果統計（管理區內外分組）
  B01_1_EXCEL: `${BASE}/grants/statistics/b01-1/excel`,
  B01_2_EXCEL: `${BASE}/grants/statistics/b01-2/excel`,
  B01_3_EXCEL: `${BASE}/grants/statistics/b01-3/excel`,
  B01_4_EXCEL: `${BASE}/grants/statistics/b01-4/excel`,
  // A09/A10 事業區域內外推動成果統計
  A09_EXCEL: `${BASE}/grants/statistics/a09/excel`,
  A10_EXCEL: `${BASE}/grants/statistics/a10/excel`,
  // B03 各縣市鄉鎮區各類補助項目統計
  B03_EXCEL: `${BASE}/grants/statistics/b03/excel`,
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
  BRANCHES: (officeId: number) => `${BASE}/offices/branches/${officeId}`,
  STATIONS: (officeId: number) => `${BASE}/offices/stations/${officeId}`,
  STATIONS_BY_BRANCH: (officeId: number, branchCode: string) => `${BASE}/offices/stations/${officeId}/${branchCode}`,
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
  // 🗑️ Deprecated: 已遷移到 NLSC.SECTIONS
  LAND_SECTIONS: (countyLandCode: string, townLandCode: string) =>
    `${BASE}/spatial/land-sections/${countyLandCode}/${townLandCode}`, // @deprecated
  // 🗑️ Deprecated: 已遷移到 NLSC.HEALTH
  LAND_SECTIONS_HEALTH: `${BASE}/spatial/land-sections/health`, // @deprecated
}

export const IRRIGATION_TYPES = {
  LIST: `${BASE}/irrigation_types`,
  OPTIONS: `${BASE}/irrigation_types/options`,
  DETAIL: (id: number | string) => `${BASE}/irrigation_types/${id}`,
}

// crops related endpoints
export const CROPS = {
  CATEGORIES: `${BASE}/crop-categories`,
  CATEGORY_DETAIL: (id: number) => `${BASE}/crop-categories/${id}`,
  NAMES: `${BASE}/crop-names`,
  NAMES_BY_CATEGORY: (categoryId: number) => `${BASE}/crop-names/category/${categoryId}`,
  GROUPED: `${BASE}/crops/grouped`,
  DICT: `${BASE}/crops/dict`,
}

// downloads related endpoints
export const DOWNLOADS = {
  BASE: `${BASE}/download`,
  PHOTOGRAPH_CARRY_FORM: `${BASE}/download/photograph-carry-form`,
  BUDGET_BOOK: `${BASE}/download/budget-book`,
  CONSTRUCTION_PHOTOS: `${BASE}/download/construction-photos`,
  ADDRESS_LABELS: `${BASE}/download/address-labels`,
  CLOSING_DOCS: `${BASE}/download/closing-docs`,
  RECEIPTS: `${BASE}/download/receipts`,
  COMPLETION_STATEMENT: `${BASE}/download/completion-statement`,
  CHECK_DATA: `${BASE}/download/check-data`,
  TEST: `${BASE}/download/test`,
  // 靜態檔案下載端點
  STATIC_FILES_LIST: `${BASE}/download/static-files`,
  STATIC_FILE_DOWNLOAD: (fileId: string) => `${BASE}/download/static-file/${encodeURIComponent(fileId)}`,
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

// leisure farms related endpoints
export const LEISURE_FARMS = {
  BASE: `${BASE}/leisure-farms`,
  NEARBY: `${BASE}/leisure-farms/nearby`,
  CHECK: `${BASE}/leisure-farms/check`,
  BY_LOCATION: `${BASE}/leisure-farms/by-location`,
  STATS: `${BASE}/leisure-farms/stats`,
}

// NLSC (國土測繪中心) related endpoints
// ✅ 重構更新（2025-12-12）：RESTful 命名 + 統一資源端點
export const NLSC = {
  BASE: `${BASE}/nlsc`,

  // ✅ 地籍圖查詢（統一資源端點）- 推薦使用
  CADASTRAL_MAP: `${BASE}/nlsc/cadastral/map`, // 統一端點：依地號或座標查詢

  // ✅ WMTS 磚塊
  CADASTRAL_TILES: (z: number, y: number, x: number) =>
    `${BASE}/nlsc/cadastral/tiles/${z}/${y}/${x}`, // WMTS 磚塊

  // ✅ 地段清單查詢（從 /spatial 遷移）
  SECTIONS: (countyLandCode: string, townLandCode: string) =>
    `${BASE}/nlsc/sections/${countyLandCode}/${townLandCode}`,

  // ✅ NLSC API 健康檢查（從 /spatial 遷移）
  HEALTH: `${BASE}/nlsc/health`,

  // 🗑️ 舊端點（向後相容，已標記 deprecated）
  CADASTRAL_LAND: `${BASE}/nlsc/cadastral/land`, // @deprecated - 請使用 CADASTRAL_MAP
  CADASTRAL_POINT: `${BASE}/nlsc/cadastral/point`, // @deprecated - 請使用 CADASTRAL_MAP
  CADASTRAL_QUERY_BY_LAND_NUMBER: `${BASE}/nlsc/cadastral/query-by-land-number`, // @deprecated - 請使用 CADASTRAL_MAP
  CADASTRAL_QUERY_BY_POINT: `${BASE}/nlsc/cadastral/query-by-point`, // @deprecated - 請使用 CADASTRAL_MAP
  WMTS_CADASTRAL_TILE: (tileMatrix: number, tileRow: number, tileCol: number) =>
    `${BASE}/nlsc/cadastral/tiles/${tileMatrix}/${tileRow}/${tileCol}`, // @deprecated - 請使用 CADASTRAL_TILES
}
