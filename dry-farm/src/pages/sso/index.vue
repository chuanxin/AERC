<template>
  <v-container class="sso-landing-container">
    <div class="section-wrapper sso-landing">
      <v-card
        class="mx-auto section-card pa-4"
        rounded="lg"
        variant="outlined"
        max-width="520"
      >
        <v-card-item class="custom-title">
          <v-card-title class="text-h5 font-weight-black px-4">
            {{ view.title }}
          </v-card-title>
        </v-card-item>

        <v-card-text class="pt-4">
          <div
            v-if="view.loading"
            class="d-flex flex-column align-center py-6"
          >
            <v-progress-circular
              indeterminate
              color="primary"
            />
            <p class="mt-4 text-body-1">
              {{ view.message }}
            </p>
          </div>

          <template v-else>
            <v-alert
              :type="view.alertType"
              variant="tonal"
              border="start"
            >
              {{ view.message }}
            </v-alert>
            <p
              v-if="view.hint"
              class="text-body-2 text-grey-darken-1 mt-3 mb-0"
            >
              {{ view.hint }}
            </p>
          </template>
        </v-card-text>

        <v-card-actions
          v-if="!view.loading"
          class="flex-column ga-2 px-4"
        >
          <v-btn
            v-for="action in view.actions"
            :key="action.label"
            block
            rounded="lg"
            :ripple="false"
            :color="action.primary ? 'primary' : undefined"
            :variant="action.primary ? 'flat' : 'outlined'"
            @click="action.run"
          >
            {{ action.label }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </div>
  </v-container>
</template>

<script setup lang="ts">
/**
 * 智慧灌溉入口平台 SSO 落地頁（042-portal-sso-integration）
 *
 * 後端 /TokenLogin 驗證憑證後以 302 導向此頁，依查詢參數分支：
 *   ?code=     交接碼 → 換取登入狀態 → 以取代方式進入首頁
 *   ?bind=     綁定票據 → 請使用者以原帳密登入一次 → 回到此頁完成綁定
 *   ?reason=   帳號狀態類結果（未啟用／未設定密碼／查無帳號／無法唯一辨識）
 *
 * 伺服器端的導向寫不進前端的 localStorage 登入狀態，因此由此頁主動換取（FR-045）。
 *
 * ⚠️ 不要在前端加「auth_source 為 sso 就略過密碼過期導向」之類的條件：password_expired
 * 已在後端依登入來源計算（/sso/exchange 與 /users/whoami 同一條規則），前端另寫一份會漂移。
 */
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ssoService } from '@/services/ssoService'
import { useUserStore } from '@/stores/users'

type AlertType = 'info' | 'warning' | 'error'

interface LandingAction {
  label: string
  primary?: boolean
  run: () => void
}

interface LandingView {
  loading: boolean
  title: string
  message: string
  alertType?: AlertType
  hint?: string
  actions: LandingAction[]
}

interface PendingBinding {
  ticket: string
  /** 使用者已按下「以帳號密碼登入」。只有此旗標為真才會自動完成綁定，避免沿用登入前就存在的工作階段 */
  loginRequested: boolean
}

// 綁定需跨越一次登入頁往返。放 sessionStorage：不跨分頁、不長期殘留，也不留在網址與瀏覽歷史
const BINDING_STORAGE_KEY = 'sso_binding'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const loadingView = (title: string, message: string): LandingView => ({ loading: true, title, message, actions: [] })

const messageView = (
  title: string,
  message: string,
  alertType: AlertType,
  hint?: string,
  actions: LandingAction[] = [],
): LandingView => ({ loading: false, title, message, alertType, hint, actions })

const view = ref<LandingView>(loadingView('智慧灌溉入口平台', '處理中，請稍候…'))

const backToLogin: LandingAction = { label: '返回登入頁', run: () => router.push('/login') }

// ── 帳號狀態類結果（後端 /TokenLogin 分流 2–6） ────────────────────────────

const REASON_VIEWS: Record<string, () => LandingView> = {
  account_inactive: () => messageView(
    '帳號尚未啟用', '您的帳號尚未啟用，請等待管理處人員審核。', 'warning',
    '如需協助，請聯繫所屬管理處。', [backToLogin],
  ),
  password_setup_required: () => messageView(
    '尚未設定密碼', '您的帳號尚未設定密碼，請先完成密碼設定。', 'warning',
    '完成設定後，請自智慧灌溉入口平台重新進入。',
    [{ label: '前往設定密碼', primary: true, run: () => router.push('/login/reset') }],
  ),
  no_account: () => messageView(
    '查無帳號', '系統中查無您的帳號。', 'info',
    '請由智慧灌溉入口平台完成註冊申請。', [backToLogin],
  ),
  // 不得與 no_account 共用：使用者確實有帳號，導去申請會造成重複帳號
  ambiguous_account: () => messageView(
    '無法辨識帳號', '無法唯一辨識您的帳號，請聯繫系統管理員。', 'error',
    '請提供您的電子郵件，由系統管理員協助確認帳號。', [backToLogin],
  ),
}

const invalidLinkView = (): LandingView => messageView(
  '連結無效', '此登入連結不完整或已無效，請自智慧灌溉入口平台重新進入。', 'warning', undefined, [backToLogin],
)

// ── 共用 ──────────────────────────────────────────────────────────────────

function responseStatus(error: unknown): number | undefined {
  return (error as { response?: { status?: number } })?.response?.status
}

function responseDetail(error: unknown): string | undefined {
  const detail = (error as { response?: { data?: { detail?: unknown } } })?.response?.data?.detail
  return typeof detail === 'string' ? detail : undefined
}

function readPendingBinding(): PendingBinding | null {
  try {
    const parsed = JSON.parse(sessionStorage.getItem(BINDING_STORAGE_KEY) ?? 'null') as PendingBinding | null
    return parsed?.ticket ? parsed : null
  } catch {
    sessionStorage.removeItem(BINDING_STORAGE_KEY)
    return null
  }
}

function savePendingBinding(binding: PendingBinding) {
  sessionStorage.setItem(BINDING_STORAGE_KEY, JSON.stringify(binding))
}

function clearPendingBinding() {
  sessionStorage.removeItem(BINDING_STORAGE_KEY)
}

// ── 交接碼交換（分流 1） ──────────────────────────────────────────────────

function exchangeFailureView(status: number | undefined): LandingView {
  // 400 是實際會走到的路徑：交接碼一次性，重新整理、收藏網址、多分頁開啟都會遇到
  if (status === 400) {
    return messageView('登入連結已失效', '登入連結已失效，請自智慧灌溉入口平台重新進入。', 'warning', undefined, [backToLogin])
  }
  if (status === 403) {
    return messageView('帳號已停用', '您的帳號已停用，請聯繫系統管理員。', 'error', undefined, [backToLogin])
  }
  return messageView('登入失敗', '登入時發生錯誤，請稍後再自智慧灌溉入口平台重新進入。', 'error', undefined, [backToLogin])
}

async function exchangeHandoffCode(code: string) {
  view.value = loadingView('登入中', '正在完成登入，請稍候…')
  try {
    const response = await ssoService.exchange(code)
    localStorage.setItem('auth_token', response.access_token)
    userStore.setToken(response.access_token)
    userStore.passwordExpired = response.password_expired
    await userStore.fetchCurrentUser()
    // 取代而非推入：/sso?code=... 若留在瀏覽歷史，按上一頁會以已使用的交接碼再呼叫一次
    await router.replace('/')
  } catch (error) {
    view.value = exchangeFailureView(responseStatus(error))
  }
}

// ── 首次綁定（分流 7） ────────────────────────────────────────────────────

function startBindingLogin() {
  const pending = readPendingBinding()
  if (!pending) {
    view.value = invalidLinkView()
    return
  }
  savePendingBinding({ ...pending, loginRequested: true })
  router.push({ path: '/login', query: { redirect: '/sso' } })
}

const bindingInstructionView = (): LandingView => messageView(
  '完成帳號綁定',
  '這是您第一次由智慧灌溉入口平台進入本系統，請以您原本的帳號密碼登入一次，以完成帳號綁定。',
  'info',
  '若登入過程中被要求更換密碼，更換完成後請自智慧灌溉入口平台重新進入一次。',
  [{ label: '以帳號密碼登入', primary: true, run: startBindingLogin }],
)

function receiveBindingTicket(ticket: string) {
  savePendingBinding({ ticket, loginRequested: false })
  view.value = bindingInstructionView()
  // 票據本身即為憑據，不留在網址與瀏覽歷史
  router.replace({ path: '/sso' })
}

function bindingFailureView(status: number | undefined, detail: string | undefined): LandingView {
  if (status === 400) {
    return messageView('綁定連結已失效', '綁定連結已失效，請自智慧灌溉入口平台重新進入。', 'warning', undefined, [backToLogin])
  }
  if (status === 403) {
    // 票據未被消耗，保留讓使用者改以正確帳號登入
    return messageView(
      '登入帳號不符', detail ?? '此綁定連結不屬於目前登入的帳號。', 'warning',
      '請改以您原本的帳號登入。', [{ label: '改以正確的帳號登入', primary: true, run: startBindingLogin }],
    )
  }
  if (status === 409) {
    return messageView('無法完成綁定', detail ?? '此帳號或入口身分已有綁定。', 'error', '請聯繫系統管理員協助處理。', [backToLogin])
  }
  return messageView('綁定失敗', '綁定時發生錯誤，請稍後再自智慧灌溉入口平台重新進入。', 'error', undefined, [backToLogin])
}

async function completeBinding(ticket: string) {
  view.value = loadingView('完成綁定中', '正在完成帳號綁定，請稍候…')
  try {
    await ssoService.bind(ticket)
    clearPendingBinding()
    await router.replace('/')
  } catch (error) {
    const status = responseStatus(error)
    // 401：登入已失效，攔截器會帶 redirect=/sso 導回登入頁；票據保留，重新登入後回到此頁繼續
    if (status === 401) return
    if (status !== 403) clearPendingBinding()
    view.value = bindingFailureView(status, responseDetail(error))
  }
}

function resumeOrReject() {
  const pending = readPendingBinding()
  if (pending?.loginRequested && userStore.token) {
    completeBinding(pending.ticket)
    return
  }
  view.value = pending ? bindingInstructionView() : invalidLinkView()
}

onMounted(() => {
  const { code, bind, reason } = route.query
  if (typeof code === 'string' && code) {
    exchangeHandoffCode(code)
  } else if (typeof bind === 'string' && bind) {
    receiveBindingTicket(bind)
  } else if (typeof reason === 'string' && REASON_VIEWS[reason]) {
    view.value = REASON_VIEWS[reason]()
  } else {
    resumeOrReject()
  }
})
</script>

<style scoped>
.sso-landing-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  /* custom-title 以 top: -50px 懸在卡片上方，須預留空間 */
  padding-top: 72px;
}

.sso-landing {
  width: 100%;
}

/* 以下沿用 components/Dashboard.vue 的區塊語彙（scoped，各頁自帶） */
.section-wrapper {
  padding: 8px 4px 0px 4px;
}

.section-card {
  position: relative;
  margin: 24px 0;
  overflow: visible !important;
  border-top-left-radius: 0 !important;
  transition: all 0.3s ease;
  background-color: rgba(255, 255, 255, 0.6) !important;
  backdrop-filter: blur(10px) !important;
  -webkit-backdrop-filter: blur(10px) !important;
  border: 1px solid rgba(255, 255, 255, 0.25) !important;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.05) !important;
}

.section-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08) !important;
  background-color: rgba(255, 255, 255, 0.85) !important;
}

.section-card:hover .custom-title {
  background-color: #2d8c8f !important;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.08);
}

.custom-title {
  position: absolute;
  top: -50px;
  left: -1px;
  width: auto !important;
  min-width: 130px;
  height: 50px;
  padding: 0 0px !important;
  background-color: #3ea0a3 !important;
  border-radius: 8px 8px 0 0;
  z-index: 1;
  transition: all 0.3s ease;
}

.custom-title .v-card-title {
  color: white !important;
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
}
</style>

<route lang="yaml">
meta:
  layout: auth
  public: true
</route>
