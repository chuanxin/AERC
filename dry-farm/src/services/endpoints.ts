// API version
const API_VERSION = 'v1';

// base URL for the API
const BASE = `/api/${API_VERSION}`;

// authentication related endpoints
export const AUTH = {
  LOGIN: `${BASE}/auth/login`,
  LOGOUT: `${BASE}/auth/logout`,
  REFRESH: `${BASE}/auth/refresh`,
  ME: `${BASE}/auth/me`,
};

// user management related endpoints
export const USERS = {
  BASE: `${BASE}/users`,
  DETAIL: (id: number | string) => `${BASE}/users/${id}`,
  UPDATE: (id: number | string) => `${BASE}/users/${id}`,
  DELETE: (id: number | string) => `${BASE}/users/${id}`,
};

// budget related endpoints
export const BUDGET = {
  EXECUTION: `${BASE}/budget/execution`,
  EXPORT: `${BASE}/budget/export`,
  DETAIL: (year: string, month: string) => `${BASE}/budget/${year}/${month}`,
};

// grant related endpoints
export const GRANTS = {
  BASE: `${BASE}/grants`,
  DETAIL: (id: number | string) => `${BASE}/grants/${id}`,
  CREATE: `${BASE}/grants/new`,
  UPDATE: (id: number | string) => `${BASE}/grants/${id}`,
  DELETE: (id: number | string) => `${BASE}/grants/${id}`,
  STEPS: {
    STEP1: (id: number | string) => `${BASE}/grants/${id}/step1`,
    STEP2: (id: number | string) => `${BASE}/grants/${id}/step2`,
    // ... 其他步驟
  },
};

// statistics related endpoints
export const REPORTS = {
  BASE: `${BASE}/reports`,
  LIST: `${BASE}/reports/list`,
  DETAIL: (id: number | string) => `${BASE}/reports/${id}`,
  GENERATE: `${BASE}/reports/generate`,
};

// qualification related endpoints
export const QUALIFICATION = {
  CHECK: `${BASE}/qualification/check`,
  INDIGENOUS: `${BASE}/qualification/indigenous`,
};

// other related endpoints
