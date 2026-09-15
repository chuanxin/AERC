/**
 * 智慧灌溉入口平台 SSO（042-portal-sso-integration）
 *
 * 落地頁 /sso 的兩支呼叫。失敗一律拋出、不在此吞掉：400／403／409 各代表不同的使用者下一步
 * （回入口重新進入／聯繫管理員／改以正確帳號登入），必須由落地頁依 HTTP 狀態分支呈現。
 */
import { apiService } from './api/http'
import { SSO } from './api/endpoints'

/** 與既有登入成功回應同形狀（POST /login-secure） */
export interface SsoExchangeResponse {
  message: string
  access_token: string
  password_expired: boolean
}

export interface SsoBindResponse {
  success: boolean
  message: string
}

export const ssoService = {
  /** 以一次性交接碼（60 秒）換取正式登入狀態 */
  exchange(code: string): Promise<SsoExchangeResponse> {
    return apiService.post<SsoExchangeResponse>(SSO.EXCHANGE, { code })
  },

  /** 持綁定票據完成首次綁定；呼叫前使用者必須已以帳號密碼登入 */
  bind(ticket: string): Promise<SsoBindResponse> {
    return apiService.post<SsoBindResponse>(SSO.BIND, { ticket })
  },
}
