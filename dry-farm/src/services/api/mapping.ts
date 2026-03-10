import { AUTH, DOMICILE, OFFICES, USERS, USER_MANAGEMENT, PERMISSIONS, GRANTS, STATISTICS, PIPE_FITTINGS, PF_MODULES, PF_DIAMETERS, PF_MATERIALS, PF_ANNUAL_PRICES, IRRIGATION_TYPES, CROPS, GIS, QUALIFICATION, SPATIAL, DOWNLOADS, ATTACHMENTS, LEISURE_FARMS, NLSC } from './endpoints';

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
    LOGIN_SECURE: '/login-secure',
    REGISTER: '/register',
    WHO_AM_I: '/users/whoami',
    LOGOUT: '/logout',
    REFRESH: '/refresh',
    CAPTCHA: '/captcha',
    REQUEST_PASSWORD_RESET: '/request-password-reset',
    VERIFY_OTP: '/verify-otp',
    RESET_PASSWORD: '/reset-password',
    SEND_VERIFICATION_EMAIL: '/send-verification-email',
    VERIFY_EMAIL: '/verify-email'
  },
  // 用戶管理相關
  USERS: {
    LIST: '/users',
    DETAIL: (id: number | string) => `/user/${id}`,
    DELETE: (id: number | string) => `/user/${id}`,
    CHECK_USERNAME: (username: string) => `/check-username/${username}`,
    SEND_REGISTRATION_OTP: '/send-registration-otp',
    VERIFY_REGISTRATION_OTP: '/verify-registration-otp',
    REGISTER: '/register',
    MIGRATE_VERIFY_OTP: '/login/migrate/verify-otp',
    MIGRATE: '/login/migrate/complete',
  },
  // 用戶管理（管理員）相關
  USER_MANAGEMENT: {
    LIST: '/user-management',
    DETAIL: (id: number) => `/user-management/${id}`,
    UPDATE_PERMISSIONS: (id: number) => `/user-management/${id}/permissions`,
    BATCH_ACTIVATE: '/user-management/batch-activate',
    BATCH_DEACTIVATE: '/user-management/batch-deactivate',
    PENDING_APPROVAL: '/user-management/pending-approval',
    APPROVE: (id: number) => `/user-management/${id}/approve`,
    REJECT: (id: number) => `/user-management/${id}/reject`,
  },
  // 權限相關
  PERMISSIONS: {
    CHECK: '/permissions/check',
    SUMMARY: '/permissions/summary',
  },
  OFFICES: {
    LIST: '/offices',
    BRANCHES: (officeId: number) => `/offices/branches/${officeId}`,
    STATIONS: (officeId: number) => `/offices/stations/${officeId}`,
    STATIONS_BY_BRANCH: (officeId: number, branchCode: string) => `/offices/stations/${officeId}/${branchCode}`,
  },
  DOMICILE: {
    COUNTIES_LIST: '/counties',
    TOWNS_LIST: '/towns',
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
    APPLICANT_SUBSIDY_SUMMARY: (applicantId: string, year: number) =>
    `/grants/applicant-subsidy-summary/${applicantId}/${year}`,
    UPDATE_STATUS: (caseNumber: string) => `/grants/case/${caseNumber}/status`,
    CLAIM_OWNERSHIP: (grantId: number) => `/grants/${grantId}/claim-ownership`,
    COMPLETION_STATEMENT: (caseNumber: string) => `/grants/case/${caseNumber}/completion-statement`,
    DECLARATION: (caseNumber: string) => `/grants/case/${caseNumber}/declaration`,
    AUTHORIZATION: (caseNumber: string) => `/grants/case/${caseNumber}/authorization`,
    BUDGET_STATEMENT: (caseNumber: string) => `/grants/case/${caseNumber}/budget-statement`,
  },
  // 統計相關
  STATISTICS: {
    EXECUTION_PROGRESS: '/grants/statistics/execution-progress',
    BUDGET_ANALYSIS: '/grants/statistics/budget-analysis',
    EXECUTION_PROGRESS_EXCEL: '/grants/statistics/execution-progress/excel',
    BUDGET_ANALYSIS_EXCEL: '/grants/statistics/budget-analysis/excel',
    COUNTY_TOWN_EXCEL: '/grants/statistics/county-town/excel',
    OFFICE_SUMMARY_EXCEL: '/grants/statistics/office-summary/excel',
    COUNTY_TOWN_YEARLY_EXCEL: '/grants/statistics/county-town-yearly/excel',
    OFFICE_SUMMARY_YEARLY_EXCEL: '/grants/statistics/office-summary-yearly/excel',
    ABORIGINAL_STATS_EXCEL: '/grants/statistics/aboriginal/excel',
    ABORIGINAL_YEARLY_EXCEL: '/grants/statistics/aboriginal-yearly/excel',
    B01_1_EXCEL: '/grants/statistics/b01-1/excel',
    B01_2_EXCEL: '/grants/statistics/b01-2/excel',
    B01_3_EXCEL: '/grants/statistics/b01-3/excel',
    B01_4_EXCEL: '/grants/statistics/b01-4/excel',
    A09_EXCEL: '/grants/statistics/a09/excel',
    A10_EXCEL: '/grants/statistics/a10/excel',
    B03_EXCEL: '/grants/statistics/b03/excel',
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
  CROPS: {
    CATEGORIES: '/crop-categories',
    CATEGORY_DETAIL: (id: number) => `/crop-categories/${id}`,
    NAMES: '/crop-names',
    NAMES_BY_CATEGORY: (categoryId: number) => `/crop-names/category/${categoryId}`,
    GROUPED: '/crops/grouped',
    DICT: '/crops/dict',
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
  },
  SPATIAL: {
    OFFICE: '/spatial/office',
    COUNTY: '/spatial/county',
  },
  DOWNLOADS: {
    PHOTOGRAPH_CARRY_FORM: '/download/photograph-carry-form',
    BUDGET_BOOK: '/download/budget-book',
    CONSTRUCTION_PHOTOS: '/download/construction-photos',
    ADDRESS_LABELS: '/download/address-labels',
    CLOSING_DOCS: '/download/closing-docs',
    RECEIPTS: '/download/receipts',
    TEST_REPORTS: '/download/test-reports',
    REVIEW_FORM: '/download/review-form',
    CHECK_DATA: '/download/check-data',
    STATIC_FILES_LIST: '/download/static-files',
    STATIC_FILE_DOWNLOAD: (fileId: string) => `/download/static-file/${fileId}`,
    STATIC_FILES_BATCH: '/download/static-files/batch',
    TEST: '/download/test',
  },
  ATTACHMENTS: {
    UPLOAD: (grantId: number, step: number) => `/attachments/upload/${grantId}/${step}`,
    LIST: (grantId: number, step: number) => `/attachments/list/${grantId}/${step}`,
    DOWNLOAD: (attachmentId: number) => `/attachments/download/${attachmentId}`,
    INFO: (attachmentId: number) => `/attachments/info/${attachmentId}`,
    DELETE: (attachmentId: number) => `/attachments/${attachmentId}`,
    BATCH_OPERATION: '/attachments/batch-operation',
  },
  // 休閒農場相關
  LEISURE_FARMS: {
    NEARBY: '/leisure-farms/nearby',
    CHECK: '/leisure-farms/check',
    BY_LOCATION: '/leisure-farms/by-location',
    STATS: '/leisure-farms/stats',
  },
  // NLSC (國土測繪中心)
  // ✅ 重構更新（2025-12-12）：RESTful 命名 + 統一資源端點
  NLSC: {
    // ✅ 統一資源端點（推薦使用）
    CADASTRAL_MAP: '/nlsc/cadastral/map', // 地籍圖統一查詢端點

    // ✅ 其他端點
    CADASTRAL_TILES: (z: number, y: number, x: number) =>
      `/nlsc/cadastral/tiles/${z}/${y}/${x}`,
    SECTIONS: (countyLandCode: string, townLandCode: string) =>
      `/nlsc/sections/${countyLandCode}/${townLandCode}`,
    HEALTH: '/nlsc/health',

    // 🗑️ 舊端點（向後相容，deprecated）
    CADASTRAL_LAND: '/nlsc/cadastral/land', // @deprecated - 請使用 CADASTRAL_MAP
    CADASTRAL_POINT: '/nlsc/cadastral/point', // @deprecated - 請使用 CADASTRAL_MAP
    CADASTRAL_QUERY_BY_LAND_NUMBER: '/nlsc/cadastral/query-by-land-number', // @deprecated - 請使用 CADASTRAL_MAP
    CADASTRAL_QUERY_BY_POINT: '/nlsc/cadastral/query-by-point', // @deprecated - 請使用 CADASTRAL_MAP
    WMTS_CADASTRAL_TILE: (tileMatrix: number, tileRow: number, tileCol: number) =>
      `/nlsc/cadastral/tiles/${tileMatrix}/${tileRow}/${tileCol}`, // @deprecated - 請使用 CADASTRAL_TILES
  },
};

// 前端到後端的直接映射表
export const API_MAPPING: Record<string, string> = {
  [AUTH.LOGIN]: BACKEND_PATHS.AUTH.LOGIN,
  [AUTH.LOGIN_SECURE]: BACKEND_PATHS.AUTH.LOGIN_SECURE,
  [AUTH.REGISTER]: BACKEND_PATHS.AUTH.REGISTER,
  [AUTH.REFRESH]: BACKEND_PATHS.AUTH.REFRESH,
  [AUTH.ME]: BACKEND_PATHS.AUTH.WHO_AM_I,
  [AUTH.CAPTCHA]: BACKEND_PATHS.AUTH.CAPTCHA,
  [AUTH.REQUEST_PASSWORD_RESET]: BACKEND_PATHS.AUTH.REQUEST_PASSWORD_RESET,
  [AUTH.VERIFY_OTP]: BACKEND_PATHS.AUTH.VERIFY_OTP,
  [AUTH.RESET_PASSWORD]: BACKEND_PATHS.AUTH.RESET_PASSWORD,
  [AUTH.SEND_VERIFICATION_EMAIL]: BACKEND_PATHS.AUTH.SEND_VERIFICATION_EMAIL,
  [AUTH.VERIFY_EMAIL]: BACKEND_PATHS.AUTH.VERIFY_EMAIL,
  [USERS.LIST]: BACKEND_PATHS.USERS.LIST,
  [USERS.MIGRATE_VERIFY_OTP]: BACKEND_PATHS.USERS.MIGRATE_VERIFY_OTP,
  [USERS.MIGRATE]: BACKEND_PATHS.USERS.MIGRATE,
  // 用戶管理（管理員）
  [USER_MANAGEMENT.LIST]: BACKEND_PATHS.USER_MANAGEMENT.LIST,
  [USER_MANAGEMENT.BATCH_ACTIVATE]: BACKEND_PATHS.USER_MANAGEMENT.BATCH_ACTIVATE,
  [USER_MANAGEMENT.BATCH_DEACTIVATE]: BACKEND_PATHS.USER_MANAGEMENT.BATCH_DEACTIVATE,
  [USER_MANAGEMENT.PENDING_APPROVAL]: BACKEND_PATHS.USER_MANAGEMENT.PENDING_APPROVAL,
  // 權限
  [PERMISSIONS.CHECK]: BACKEND_PATHS.PERMISSIONS.CHECK,
  [PERMISSIONS.SUMMARY]: BACKEND_PATHS.PERMISSIONS.SUMMARY,
  [OFFICES.LIST]: BACKEND_PATHS.OFFICES.LIST,
  [DOMICILE.COUNTIES_LIST]: BACKEND_PATHS.DOMICILE.COUNTIES_LIST,
  [DOMICILE.TOWNS_LIST]: BACKEND_PATHS.DOMICILE.TOWNS_LIST,
  [DOMICILE.VILLAGES_LIST]: BACKEND_PATHS.DOMICILE.VILLAGES_LIST,
  [DOMICILE.SECTIONS_LIST]: BACKEND_PATHS.DOMICILE.SECTIONS_LIST,
  [GRANTS.CREATE]: BACKEND_PATHS.GRANTS.CREATE,
  // 統計
  [STATISTICS.EXECUTION_PROGRESS]: BACKEND_PATHS.STATISTICS.EXECUTION_PROGRESS,
  [STATISTICS.BUDGET_ANALYSIS]: BACKEND_PATHS.STATISTICS.BUDGET_ANALYSIS,
  [STATISTICS.EXECUTION_PROGRESS_EXCEL]: BACKEND_PATHS.STATISTICS.EXECUTION_PROGRESS_EXCEL,
  [STATISTICS.BUDGET_ANALYSIS_EXCEL]: BACKEND_PATHS.STATISTICS.BUDGET_ANALYSIS_EXCEL,
  [STATISTICS.COUNTY_TOWN_EXCEL]: BACKEND_PATHS.STATISTICS.COUNTY_TOWN_EXCEL,
  [STATISTICS.OFFICE_SUMMARY_EXCEL]: BACKEND_PATHS.STATISTICS.OFFICE_SUMMARY_EXCEL,
  [STATISTICS.COUNTY_TOWN_YEARLY_EXCEL]: BACKEND_PATHS.STATISTICS.COUNTY_TOWN_YEARLY_EXCEL,
  [STATISTICS.OFFICE_SUMMARY_YEARLY_EXCEL]: BACKEND_PATHS.STATISTICS.OFFICE_SUMMARY_YEARLY_EXCEL,
  [STATISTICS.ABORIGINAL_STATS_EXCEL]:BACKEND_PATHS.STATISTICS.ABORIGINAL_STATS_EXCEL,
  [STATISTICS.ABORIGINAL_YEARLY_EXCEL]:BACKEND_PATHS.STATISTICS.ABORIGINAL_YEARLY_EXCEL,
  [STATISTICS.B01_1_EXCEL]:BACKEND_PATHS.STATISTICS.B01_1_EXCEL,
  [STATISTICS.B01_2_EXCEL]:BACKEND_PATHS.STATISTICS.B01_2_EXCEL,
  [STATISTICS.B01_3_EXCEL]:BACKEND_PATHS.STATISTICS.B01_3_EXCEL,
  [STATISTICS.B01_4_EXCEL]:BACKEND_PATHS.STATISTICS.B01_4_EXCEL,
  [STATISTICS.A09_EXCEL]:BACKEND_PATHS.STATISTICS.A09_EXCEL,
  [STATISTICS.A10_EXCEL]:BACKEND_PATHS.STATISTICS.A10_EXCEL,
  [STATISTICS.B03_EXCEL]:BACKEND_PATHS.STATISTICS.B03_EXCEL,
  [PIPE_FITTINGS.LIST]: BACKEND_PATHS.PIPE_FITTINGS.LIST,
  [PIPE_FITTINGS.CREATE]: BACKEND_PATHS.PIPE_FITTINGS.LIST, // Assuming POST to the same base path
  [PF_ANNUAL_PRICES.LIST]: BACKEND_PATHS.PF_ANNUAL_PRICES.LIST,
  [PF_ANNUAL_PRICES.CREATE]: BACKEND_PATHS.PF_ANNUAL_PRICES.LIST,
  [PF_MODULES.LIST]: BACKEND_PATHS.PF_MODULES.LIST,
  [PF_DIAMETERS.LIST]: BACKEND_PATHS.PF_DIAMETERS.LIST,
  [PF_MATERIALS.LIST]: BACKEND_PATHS.PF_MATERIALS.LIST,
  [IRRIGATION_TYPES.LIST]: BACKEND_PATHS.IRRIGATION_TYPES.LIST,
  [IRRIGATION_TYPES.OPTIONS]: BACKEND_PATHS.IRRIGATION_TYPES.OPTIONS,
  [CROPS.CATEGORIES]: BACKEND_PATHS.CROPS.CATEGORIES,
  [CROPS.NAMES]: BACKEND_PATHS.CROPS.NAMES,
  [CROPS.GROUPED]: BACKEND_PATHS.CROPS.GROUPED,
  [CROPS.DICT]: BACKEND_PATHS.CROPS.DICT,
  [GIS.POINTS]: BACKEND_PATHS.GIS.POINTS,
  [GIS.STATS]: BACKEND_PATHS.GIS.STATS,
  [GIS.SEARCH]: BACKEND_PATHS.GIS.SEARCH,
  [QUALIFICATION.SEARCH]: BACKEND_PATHS.QUALIFICATION.SEARCH,
  [QUALIFICATION.HEALTH]: BACKEND_PATHS.QUALIFICATION.HEALTH,
  [QUALIFICATION.INDIGENOUS_CHECK]: BACKEND_PATHS.QUALIFICATION.INDIGENOUS_CHECK,
  [QUALIFICATION.SLOPE_AREA_CHECK]: BACKEND_PATHS.QUALIFICATION.SLOPE_AREA_CHECK,
  [SPATIAL.COUNTY]: BACKEND_PATHS.SPATIAL.COUNTY,
  [SPATIAL.OFFICE]: BACKEND_PATHS.SPATIAL.OFFICE,
  [DOWNLOADS.PHOTOGRAPH_CARRY_FORM]: BACKEND_PATHS.DOWNLOADS.PHOTOGRAPH_CARRY_FORM,
  [DOWNLOADS.BUDGET_BOOK]: BACKEND_PATHS.DOWNLOADS.BUDGET_BOOK,
  [DOWNLOADS.CONSTRUCTION_PHOTOS]: BACKEND_PATHS.DOWNLOADS.CONSTRUCTION_PHOTOS,
  [DOWNLOADS.ADDRESS_LABELS]: BACKEND_PATHS.DOWNLOADS.ADDRESS_LABELS,
  [DOWNLOADS.CLOSING_DOCS]: BACKEND_PATHS.DOWNLOADS.CLOSING_DOCS,
  [DOWNLOADS.RECEIPTS]: BACKEND_PATHS.DOWNLOADS.RECEIPTS,
  [DOWNLOADS.TEST_REPORTS]: BACKEND_PATHS.DOWNLOADS.TEST_REPORTS,
  [DOWNLOADS.REVIEW_FORM]: BACKEND_PATHS.DOWNLOADS.REVIEW_FORM,
  [DOWNLOADS.CHECK_DATA]: BACKEND_PATHS.DOWNLOADS.CHECK_DATA,
  [DOWNLOADS.STATIC_FILES_LIST]: BACKEND_PATHS.DOWNLOADS.STATIC_FILES_LIST,
  [DOWNLOADS.STATIC_FILES_BATCH]: BACKEND_PATHS.DOWNLOADS.STATIC_FILES_BATCH,
  [DOWNLOADS.TEST]: BACKEND_PATHS.DOWNLOADS.TEST,
  [ATTACHMENTS.BATCH_OPERATION]: BACKEND_PATHS.ATTACHMENTS.BATCH_OPERATION,
  // 休閒農場
  [LEISURE_FARMS.NEARBY]: BACKEND_PATHS.LEISURE_FARMS.NEARBY,
  [LEISURE_FARMS.CHECK]: BACKEND_PATHS.LEISURE_FARMS.CHECK,
  [LEISURE_FARMS.BY_LOCATION]: BACKEND_PATHS.LEISURE_FARMS.BY_LOCATION,
  [LEISURE_FARMS.STATS]: BACKEND_PATHS.LEISURE_FARMS.STATS,
  // NLSC - ✅ 統一資源端點（推薦使用）
  [NLSC.CADASTRAL_MAP]: BACKEND_PATHS.NLSC.CADASTRAL_MAP,
  [NLSC.HEALTH]: BACKEND_PATHS.NLSC.HEALTH,
  // NLSC - 🗑️ 舊端點（deprecated，向後相容）
  [NLSC.CADASTRAL_LAND]: BACKEND_PATHS.NLSC.CADASTRAL_LAND, // @deprecated
  [NLSC.CADASTRAL_POINT]: BACKEND_PATHS.NLSC.CADASTRAL_POINT, // @deprecated
  [NLSC.CADASTRAL_QUERY_BY_LAND_NUMBER]: BACKEND_PATHS.NLSC.CADASTRAL_QUERY_BY_LAND_NUMBER, // @deprecated
  [NLSC.CADASTRAL_QUERY_BY_POINT]: BACKEND_PATHS.NLSC.CADASTRAL_QUERY_BY_POINT, // @deprecated
  // 🔥 移除錯誤的靜態映射：APPLICANT_SUBSIDY_SUMMARY 是函數，不能作為 Record key
  // [GRANTS.APPLICANT_SUBSIDY_SUMMARY]: BACKEND_PATHS.GRANTS.APPLICANT_SUBSIDY_SUMMARY,
}

// 動態參數路徑匹配規則
export const DYNAMIC_PATH_PATTERNS = [
  // ========== Grants 相關路徑（優先匹配，順序很重要）==========
  {
    // 🔥 匹配申請人補助額度摘要路徑 /grants/applicant-subsidy-summary/{applicantId}/{year}
    pattern: /^\/grants\/applicant-subsidy-summary\/([^\/]+)\/(\d+)$/,
    transform: (matches: RegExpMatchArray) => BACKEND_PATHS.GRANTS.APPLICANT_SUBSIDY_SUMMARY(matches[1], parseInt(matches[2], 10))
  },
  {
    // 匹配 grants authorization 路徑 /grants/case/{case_number}/authorization
    pattern: /^\/grants\/case\/([^\/]+)\/authorization$/,
    transform: (matches: RegExpMatchArray) => BACKEND_PATHS.GRANTS.AUTHORIZATION(matches[1])
  },
  {
    // 匹配 grants budget-statement 路徑 /grants/case/{case_number}/budget-statement
    pattern: /^\/grants\/case\/([^\/]+)\/budget-statement$/,
    transform: (matches: RegExpMatchArray) => BACKEND_PATHS.GRANTS.BUDGET_STATEMENT(matches[1])
  },
  {
    // 匹配 grants declaration 路徑 /grants/case/{case_number}/declaration
    pattern: /^\/grants\/case\/([^\/]+)\/declaration$/,
    transform: (matches: RegExpMatchArray) => BACKEND_PATHS.GRANTS.DECLARATION(matches[1])
  },
  {
    // 匹配 grants completion-statement 路徑 /grants/case/{case_number}/completion-statement
    pattern: /^\/grants\/case\/([^\/]+)\/completion-statement$/,
    transform: (matches: RegExpMatchArray) => BACKEND_PATHS.GRANTS.COMPLETION_STATEMENT(matches[1])
  },
  {
    // 匹配 grants status 路徑 /grants/case/{case_number}/status
    pattern: /^\/grants\/case\/([^\/]+)\/status$/,
    transform: (matches: RegExpMatchArray) => BACKEND_PATHS.GRANTS.UPDATE_STATUS(matches[1])
  },
  {
    // 匹配 grants current-step 路徑 /grants/case/{case_number}/current-step
    pattern: /^\/grants\/case\/([^\/]+)\/current-step$/,
    transform: (matches: RegExpMatchArray) => BACKEND_PATHS.GRANTS.UPDATE_CURRENT_STEP(matches[1])
  },
  {
    // 匹配 grants step 路徑 /grants/case/{case_number}/step/{step}
    pattern: /^\/grants\/case\/([^\/]+)\/step\/(\d+)$/,
    transform: (matches: RegExpMatchArray) => BACKEND_PATHS.GRANTS.STEP(matches[1], parseInt(matches[2], 10))
  },
  {
    // 匹配 grants case number 路徑 /grants/case/{case_number}
    pattern: /^\/grants\/case\/([^\/]+)$/,
    transform: (matches: RegExpMatchArray) => BACKEND_PATHS.GRANTS.BY_CASE_NUMBER(matches[1])
  },
  {
    // 匹配 grants delete 路徑 /grants/{id}
    pattern: /^\/grants\/(\d+)$/,
    transform: (matches: RegExpMatchArray) => BACKEND_PATHS.GRANTS.DELETE(matches[1])
  },
  // ========== 其他路徑 ==========
  {
    // 匹配申請人補助額度摘要路徑 {API_PREFIX}/grants/applicant-subsidy-summary/{applicantId}/{year}
    pattern: new RegExp(`^${GRANTS.BASE.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}/applicant-subsidy-summary/([^/]+)/(\\d+)$`),
    transform: (matches: RegExpMatchArray) => BACKEND_PATHS.GRANTS.APPLICANT_SUBSIDY_SUMMARY(matches[1], parseInt(matches[2], 10))
  },
  {
    // 匹配用戶詳情路徑 {API_PREFIX}/users/123
    pattern: new RegExp(`^${USERS.BASE.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}/([\\d]+)$`),
    transform: (matches: RegExpMatchArray) => BACKEND_PATHS.USERS.DETAIL(matches[1])
  },
  {
    // 匹配帳號檢查路徑 {API_PREFIX}/users/check-username/{username}
    pattern: new RegExp(`^${USERS.BASE.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}/check-username/([^/]+)$`),
    transform: (matches: RegExpMatchArray) => BACKEND_PATHS.USERS.CHECK_USERNAME(matches[1])
  },
  {
    // 匹配發送註冊 OTP 路徑 {API_PREFIX}/users/send-registration-otp
    pattern: new RegExp(`^${USERS.BASE.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}/send-registration-otp$`),
    transform: () => BACKEND_PATHS.USERS.SEND_REGISTRATION_OTP
  },
  {
    // 匹配驗證註冊 OTP 路徑 {API_PREFIX}/users/verify-registration-otp
    pattern: new RegExp(`^${USERS.BASE.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}/verify-registration-otp$`),
    transform: () => BACKEND_PATHS.USERS.VERIFY_REGISTRATION_OTP
  },
  {
    // 匹配帳號註冊路徑 {API_PREFIX}/users/register
    pattern: new RegExp(`^${USERS.BASE.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}/register$`),
    transform: () => BACKEND_PATHS.USERS.REGISTER
  },
  // 用戶管理（管理員）動態路徑
  {
    // 匹配用戶管理詳情路徑 {API_PREFIX}/user-management/{id}
    pattern: new RegExp(`^${USER_MANAGEMENT.BASE.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}/(\\d+)$`),
    transform: (matches: RegExpMatchArray) => BACKEND_PATHS.USER_MANAGEMENT.DETAIL(parseInt(matches[1], 10))
  },
  {
    // 匹配更新用戶權限路徑 {API_PREFIX}/user-management/{id}/permissions
    pattern: new RegExp(`^${USER_MANAGEMENT.BASE.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}/(\\d+)/permissions$`),
    transform: (matches: RegExpMatchArray) => BACKEND_PATHS.USER_MANAGEMENT.UPDATE_PERMISSIONS(parseInt(matches[1], 10))
  },
  {
    // 匹配用戶審核通過路徑 {API_PREFIX}/user-management/{id}/approve
    pattern: new RegExp(`^${USER_MANAGEMENT.BASE.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}/(\\d+)/approve$`),
    transform: (matches: RegExpMatchArray) => BACKEND_PATHS.USER_MANAGEMENT.APPROVE(parseInt(matches[1], 10))
  },
  {
    // 匹配用戶審核拒絕路徑 {API_PREFIX}/user-management/{id}/reject
    pattern: new RegExp(`^${USER_MANAGEMENT.BASE.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}/(\\d+)/reject$`),
    transform: (matches: RegExpMatchArray) => BACKEND_PATHS.USER_MANAGEMENT.REJECT(parseInt(matches[1], 10))
  },
  {
    // 匹配管理處分處列表路徑 {API_PREFIX}/offices/branches/{officeId}
    pattern: new RegExp(`^${OFFICES.LIST.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}/branches/(\\d+)$`),
    transform: (matches: RegExpMatchArray) => BACKEND_PATHS.OFFICES.BRANCHES(parseInt(matches[1], 10))
  },
  {
    // 匹配管理處工作站列表路徑 {API_PREFIX}/offices/stations/{officeId}
    pattern: new RegExp(`^${OFFICES.LIST.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}/stations/(\\d+)$`),
    transform: (matches: RegExpMatchArray) => BACKEND_PATHS.OFFICES.STATIONS(parseInt(matches[1], 10))
  },
  {
    // 匹配分處工作站列表路徑 {API_PREFIX}/offices/stations/{officeId}/{branchCode}
    pattern: new RegExp(`^${OFFICES.LIST.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}/stations/(\\d+)/([^/]+)$`),
    transform: (matches: RegExpMatchArray) => BACKEND_PATHS.OFFICES.STATIONS_BY_BRANCH(parseInt(matches[1], 10), matches[2])
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
  },
  {
    // 匹配作物類別詳情路徑 {API_PREFIX}/crop-categories/{id}
    pattern: new RegExp(`^${CROPS.CATEGORIES.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}/(\\d+)$`),
    transform: (matches: RegExpMatchArray) => BACKEND_PATHS.CROPS.CATEGORY_DETAIL(parseInt(matches[1], 10))
  },
  {
    // 匹配作物名稱（依類別）路徑 {API_PREFIX}/crop-names/category/{categoryId}
    pattern: new RegExp(`^${CROPS.NAMES.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}/category/(\\d+)$`),
    transform: (matches: RegExpMatchArray) => BACKEND_PATHS.CROPS.NAMES_BY_CATEGORY(parseInt(matches[1], 10))
  },
  {
    // 匹配靜態檔案下載路徑 {API_PREFIX}/download/static-file/{fileId}
    pattern: new RegExp(`^${DOWNLOADS.BASE.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}/static-file/([^/]+)$`),
    transform: (matches: RegExpMatchArray) => BACKEND_PATHS.DOWNLOADS.STATIC_FILE_DOWNLOAD(matches[1])
  },
  {
    // 匹配附件上傳路徑 {API_PREFIX}/attachments/upload/{grantId}/{step}
    pattern: new RegExp(`^${ATTACHMENTS.BASE.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}/upload/(\\d+)/(\\d+)$`),
    transform: (matches: RegExpMatchArray) => BACKEND_PATHS.ATTACHMENTS.UPLOAD(parseInt(matches[1], 10), parseInt(matches[2], 10))
  },
  {
    // 匹配附件列表路徑 {API_PREFIX}/attachments/list/{grantId}/{step}
    pattern: new RegExp(`^${ATTACHMENTS.BASE.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}/list/(\\d+)/(\\d+)$`),
    transform: (matches: RegExpMatchArray) => BACKEND_PATHS.ATTACHMENTS.LIST(parseInt(matches[1], 10), parseInt(matches[2], 10))
  },
  {
    // 匹配附件下載路徑 {API_PREFIX}/attachments/download/{attachmentId}
    pattern: new RegExp(`^${ATTACHMENTS.BASE.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}/download/(\\d+)$`),
    transform: (matches: RegExpMatchArray) => BACKEND_PATHS.ATTACHMENTS.DOWNLOAD(parseInt(matches[1], 10))
  },
  {
    // 匹配附件資訊路徑 {API_PREFIX}/attachments/info/{attachmentId}
    pattern: new RegExp(`^${ATTACHMENTS.BASE.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}/info/(\\d+)$`),
    transform: (matches: RegExpMatchArray) => BACKEND_PATHS.ATTACHMENTS.INFO(parseInt(matches[1], 10))
  },
  {
    // 匹配附件刪除路徑 {API_PREFIX}/attachments/{attachmentId}
    // 注意: 這個要放在最後，避免與 upload/list/download/info 衝突
    pattern: new RegExp(`^${ATTACHMENTS.BASE.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}/(?!upload|list|download|info|batch-operation)(\\d+)$`),
    transform: (matches: RegExpMatchArray) => BACKEND_PATHS.ATTACHMENTS.DELETE(parseInt(matches[1], 10))
  },
  {
    // 匹配 NLSC 地籍圖磚塊路徑（新舊格式統一）
    // 新格式: {API_PREFIX}/nlsc/cadastral/tiles/{z}/{y}/{x}
    // 舊格式: {API_PREFIX}/nlsc/wmts/cadastral/{tileMatrix}/{tileRow}/{tileCol}
    pattern: new RegExp(`^${NLSC.BASE.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}/(?:cadastral/tiles|wmts/cadastral)/(\\d+)/(\\d+)/(\\d+)$`),
    transform: (matches: RegExpMatchArray) => BACKEND_PATHS.NLSC.CADASTRAL_TILES(
      parseInt(matches[1], 10),
      parseInt(matches[2], 10),
      parseInt(matches[3], 10)
    )
  },
  {
    // 匹配 NLSC 地段清單路徑 {API_PREFIX}/nlsc/sections/{countyLandCode}/{townLandCode}
    pattern: new RegExp(`^${NLSC.BASE.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}/sections/([^/]+)/([^/]+)$`),
    transform: (matches: RegExpMatchArray) => BACKEND_PATHS.NLSC.SECTIONS(matches[1], matches[2])
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

  // 3. 使用純淨路徑進行動態匹配（優先匹配 cleanPath）
  for (const { pattern, transform } of DYNAMIC_PATH_PATTERNS) {
    if (!pattern || !transform) continue;

    const matches = cleanPath.match(pattern);
    if (matches) {
      mappedBasePath = transform(matches);
      console.debug(`[mapApiPath] Dynamic mapping found for ${cleanPath}: ${mappedBasePath}`);
      break;
    }
  }

  // 4. 回退到原始路徑匹配（帶 API_PREFIX 的路徑）
  if (!mappedBasePath) {
    for (const { pattern, transform } of DYNAMIC_PATH_PATTERNS) {
      if (!pattern || !transform) continue;

      const matches = basePathFromFrontend.match(pattern);
      if (matches) {
        mappedBasePath = transform(matches);
        console.debug(`[mapApiPath] Generic dynamic mapping for ${basePathFromFrontend}: ${mappedBasePath}`);
        break;
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
