<template>
  <v-container
    fluid
    class="fill-height pa-0 login-background"
  >
    <!-- Desktop: Header with Logo and Title (absolute positioned) -->
    <v-row
      v-if="$vuetify.display.mdAndUp"
      class="desktop-header"
      no-gutters
    >
      <v-col
        cols="auto"
        class="header-logo"
      >
        <v-img
          src="@/assets/login/Logo.png"
          contain
        />
      </v-col>
      <v-spacer />
      <v-col
        cols="auto"
        class="header-title"
      >
        <v-img
          src="@/assets/login/Headline.png"
          contain
        />
      </v-col>
    </v-row>

    <!-- Main Content -->
    <v-row
      class="fill-height"
      :class="{ 'desktop-layout': $vuetify.display.mdAndUp }"
      no-gutters
    >
      <!-- Desktop/Tablet: Left half for login form -->
      <v-col
        v-if="$vuetify.display.mdAndUp"
        cols="12"
        md="7"
        lg="6"
        class="d-flex align-center justify-center"
      >
        <v-responsive :max-width="352">
          <div class="login-form-wrapper">
            <h2 class="login-title text-center mb-4">
              登入
            </h2>

            <v-form
              v-if="!mfaRequired"
              id="loginForm"
              @submit.prevent="handleLogin"
            >
              <v-text-field
                v-model="loginForm.account"
                placeholder="帳號"
                variant="outlined"
                density="comfortable"
                class="login-input mb-2"
                hide-details
              />

              <v-text-field
                v-model="loginForm.password"
                placeholder="密碼"
                :type="showPassword ? 'text' : 'password'"
                variant="outlined"
                density="comfortable"
                class="login-input mb-2"
                hide-details
              >
                <template #append-inner>
                  <v-icon
                    :icon="showPassword ? 'mdi-eye-off' : 'mdi-eye'"
                    class="password-toggle-icon"
                    @click="showPassword = !showPassword"
                  />
                </template>
              </v-text-field>

              <v-text-field
                v-model="userCaptcha"
                placeholder="驗證碼"
                variant="outlined"
                density="comfortable"
                class="login-input captcha-input mb-2"
                hide-details
                :error="captchaError"
                :error-messages="captchaError ? '驗證碼不正確' : ''"
              >
                <template #append-inner>
                  <div
                    class="captcha-display"
                    @click="generateCaptcha"
                  >
                    {{ captcha }}
                  </div>
                </template>
              </v-text-field>

              <!-- 密碼更換成功提示 -->
              <v-alert
                v-if="successMessage"
                type="success"
                variant="tonal"
                density="compact"
                class="mb-3"
              >
                {{ successMessage }}
              </v-alert>

              <!-- Error Message Display -->
              <v-alert
                v-if="errorMessage"
                type="error"
                variant="tonal"
                density="compact"
                class="mb-3"
              >
                {{ errorMessage }}
              </v-alert>

              <v-btn
                type="submit"
                color="primary"
                size="x-large"
                class="login-button"
                block
                :loading="isSubmitting"
                :disabled="isSubmitting"
              >
                登入
              </v-btn>

              <div class="login-footer-links">
                <a
                  href="/login/reset"
                  class="footer-link"
                >忘記密碼?</a>
                <span class="footer-separator">|</span>
                <a
                  href="/login/signup"
                  class="footer-link"
                >帳號申請</a>
              </div>
            </v-form>

            <!-- MFA 驗證碼輸入步驟（白名單外來源登入，見 User Story 1） -->
            <v-form
              v-else
              id="mfaForm"
              @submit.prevent="verifyMfaOtp"
            >
              <p class="mfa-hint mb-3">
                請點擊右側「發送驗證碼」後，輸入寄送至信箱{{ maskedEmail ? `（${maskedEmail}）` : '' }}的 6 碼驗證碼，完成二因子驗證
              </p>

              <v-text-field
                v-model="otpCode"
                placeholder="6 碼驗證碼"
                variant="outlined"
                density="comfortable"
                class="login-input otp-input mb-2"
                maxlength="6"
                inputmode="numeric"
                hide-details
              >
                <template #append-inner>
                  <v-btn
                    variant="text"
                    size="small"
                    color="primary"
                    class="otp-send-btn"
                    :loading="otpSending"
                    @click.stop="sendMfaOtp"
                  >
                    {{ otpCountdown > 0 ? `(${otpCountdown}s)` : (maskedEmail ? '重新發送' : '發送驗證碼') }}
                  </v-btn>
                </template>
              </v-text-field>

              <v-alert
                v-if="otpError"
                type="error"
                variant="tonal"
                density="compact"
                class="mb-3"
              >
                {{ otpError }}<template v-if="otpAttemptsRemaining !== null">（剩餘 {{ otpAttemptsRemaining }} 次）</template>
              </v-alert>

              <v-btn
                type="submit"
                color="primary"
                size="x-large"
                class="login-button mb-2"
                block
                :loading="otpVerifying"
                :disabled="otpVerifying || otpCode.length !== 6"
              >
                驗證並登入
              </v-btn>

              <div class="login-footer-links">
                <a
                  href="#"
                  class="footer-link"
                  @click.prevent="clearMfaSession"
                >返回登入</a>
              </div>
            </v-form>
          </div>
        </v-responsive>
      </v-col>

      <!-- Small screens: Vertical layout (header - form - footer) -->
      <v-col
        v-if="$vuetify.display.smAndDown"
        cols="12"
        class="small-screen-layout"
      >
        <!-- Header -->
        <div class="small-screen-header">
          <img
            src="@/assets/login/Logo.png"
            alt="Logo"
            class="small-screen-logo"
          >
        </div>

        <!-- Login Form -->
        <div class="small-screen-form-wrapper">
          <v-responsive :max-width="$vuetify.display.smAndDown ? 352 : 352">
            <div class="login-form-wrapper">
              <h2 class="login-title text-center mb-4">
                登入
              </h2>

              <v-form
                v-if="!mfaRequired"
                id="loginFormMobile"
                @submit.prevent="handleLogin"
              >
                <v-text-field
                  v-model="loginForm.account"
                  placeholder="帳號"
                  variant="outlined"
                  density="comfortable"
                  class="login-input mb-2"
                  hide-details
                />

                <v-text-field
                  v-model="loginForm.password"
                  placeholder="密碼"
                  :type="showPassword ? 'text' : 'password'"
                  variant="outlined"
                  density="comfortable"
                  class="login-input mb-2"
                  hide-details
                >
                  <template #append-inner>
                    <v-icon
                      :icon="showPassword ? 'mdi-eye-off' : 'mdi-eye'"
                      class="password-toggle-icon"
                      @click="showPassword = !showPassword"
                    />
                  </template>
                </v-text-field>

                <v-text-field
                  v-model="userCaptcha"
                  placeholder="驗證碼"
                  variant="outlined"
                  density="comfortable"
                  class="login-input captcha-input mb-2"
                  :error="captchaError"
                  :error-messages="captchaError ? '驗證碼不正確' : ''"
                >
                  <template #append-inner>
                    <div
                      class="captcha-display"
                      @click="generateCaptcha"
                    >
                      {{ captcha }}
                    </div>
                  </template>
                </v-text-field>

                <!-- 密碼更換成功提示 -->
                <v-alert
                  v-if="successMessage"
                  type="success"
                  variant="tonal"
                  density="compact"
                  class="mb-3"
                >
                  {{ successMessage }}
                </v-alert>

                <!-- Error Message Display -->
                <v-alert
                  v-if="errorMessage"
                  type="error"
                  variant="tonal"
                  density="compact"
                  class="mb-3"
                >
                  {{ errorMessage }}
                </v-alert>

                <v-btn
                  type="submit"
                  color="primary"
                  :size="$vuetify.display.xs ? 'large' : 'x-large'"
                  class="login-button"
                  block
                  :loading="isSubmitting"
                  :disabled="isSubmitting"
                >
                  登入
                </v-btn>

                <div class="login-footer-links">
                  <a
                    href="/login/reset"
                    class="footer-link"
                  >忘記密碼?</a>
                  <span class="footer-separator">|</span>
                  <a
                    href="#"
                    class="footer-link"
                  >帳號申請</a>
                </div>
              </v-form>

              <!-- MFA 驗證碼輸入步驟（白名單外來源登入，見 User Story 1） -->
              <v-form
                v-else
                id="mfaFormMobile"
                @submit.prevent="verifyMfaOtp"
              >
                <p class="mfa-hint mb-3">
                  請點擊右側「發送驗證碼」後，輸入寄送至信箱{{ maskedEmail ? `（${maskedEmail}）` : '' }}的 6 碼驗證碼，完成二因子驗證
                </p>

                <v-text-field
                  v-model="otpCode"
                  placeholder="6 碼驗證碼"
                  variant="outlined"
                  density="comfortable"
                  class="login-input otp-input mb-2"
                  maxlength="6"
                  inputmode="numeric"
                  hide-details
                >
                  <template #append-inner>
                    <v-btn
                      variant="text"
                      size="small"
                      color="primary"
                      class="otp-send-btn"
                      :loading="otpSending"
                      @click.stop="sendMfaOtp"
                    >
                      {{ otpCountdown > 0 ? `(${otpCountdown}s)` : (maskedEmail ? '重新發送' : '發送驗證碼') }}
                    </v-btn>
                  </template>
                </v-text-field>

                <v-alert
                  v-if="otpError"
                  type="error"
                  variant="tonal"
                  density="compact"
                  class="mb-3"
                >
                  {{ otpError }}<template v-if="otpAttemptsRemaining !== null">（剩餘 {{ otpAttemptsRemaining }} 次）</template>
                </v-alert>

                <v-btn
                  type="submit"
                  color="primary"
                  :size="$vuetify.display.xs ? 'large' : 'x-large'"
                  class="login-button mb-2"
                  block
                  :loading="otpVerifying"
                  :disabled="otpVerifying || otpCode.length !== 6"
                >
                  驗證並登入
                </v-btn>

                <div class="login-footer-links">
                  <a
                    href="#"
                    class="footer-link"
                    @click.prevent="clearMfaSession"
                  >返回登入</a>
                </div>
              </v-form>
            </div>
          </v-responsive>
        </div>

        <!-- Footer -->
        <div class="small-screen-footer">
          <div class="d-flex flex-column align-center">
            <v-chip
              color="teal-darken-1"
              variant="flat"
              class="text-body-2 font-weight-medium mb-2"
            >
              <v-icon
                start
                icon="mdi-tag-outline"
                size="small"
              />
              release v.{{ packageInfo.version }}
            </v-chip>
            <p class="footer-text">
              &copy; 2025 農田水利署. All rights reserved.
            </p>
          </div>
        </div>
      </v-col>
    </v-row>

    <!-- Desktop: Footer (bottom right) -->
    <div
      v-if="$vuetify.display.mdAndUp"
      class="desktop-footer"
    >
      <div class="d-flex flex-column align-end">
        <v-chip
          color="teal-darken-1"
          variant="flat"
          class="text-body-2 font-weight-medium mb-2"
        >
          <v-icon
            start
            icon="mdi-tag-outline"
            size="small"
          />
          release v.{{ packageInfo.version }}
        </v-chip>
        <p class="footer-text">
          &copy; 2025 農田水利署. All rights reserved.
        </p>
      </div>
    </div>
  </v-container>
</template>

<script lang="ts" setup>
  import { useUserStore } from '@/stores/users'
  import { useOfficesStore } from '@/stores/offices'
  import { apiService } from '@/services/api/http'
  import { AUTH, MFA } from '@/services/api/endpoints'
  import { getServerPublicKey } from '@/services/authKeyService'
  import { encryptPassword, generateNonce } from '@/utils/passwordEncryption'
  import { userService } from '@/services/userService'
  import packageInfo from '../../../package.json'
// import { de } from 'vuetify/locale'

  // Add these lines to handle redirection
  const route = useRoute()
  const router = useRouter()
  const redirectPath = computed(() => route.query.redirect?.toString() || '/')

  const userStore = useUserStore()
  const officesStore = useOfficesStore()
  // const { isLoading, error } = storeToRefs(userStore)

  const activeForm = ref('login')
  const showPassword = ref(false)
  const showConfirmPassword = ref(false)
  const rememberMe = ref(false)

  const captchaToken = ref('')
  const captcha = ref('')
  const userCaptcha = ref('')
  const captchaError = ref(false)
  const captchaLoading = ref(false)

  const errorMessage = ref('');
  const isSubmitting = ref(false);
  const successMessage = ref(route.query.message === 'password_changed' ? '密碼已成功更換，請以新密碼重新登入' : '');

  // MFA（第二因子驗證）狀態，見 contracts/frontend-mfa-flow-contract.md
  const MFA_SESSION_KEY = 'mfa_session'
  const mfaRequired = ref(false)
  const mfaToken = ref('')
  const otpCode = ref('')
  const otpSentAt = ref<number | null>(null)
  const otpError = ref('')
  const otpAttemptsRemaining = ref<number | null>(null)
  const maskedEmail = ref('')
  const otpSending = ref(false)
  const otpVerifying = ref(false)
  const otpCountdown = ref(0)
  let countdownTimer: ReturnType<typeof setInterval> | null = null

  function stopCountdown() {
    if (countdownTimer) {
      clearInterval(countdownTimer)
      countdownTimer = null
    }
  }

  // 倒數僅供 UX 參考顯示，不作為「重新發送」按鈕是否可點擊的判斷依據（見 frontend-mfa-flow-contract.md 強制規則）
  function startCountdown(seconds: number) {
    stopCountdown()
    otpCountdown.value = seconds
    countdownTimer = setInterval(() => {
      if (otpCountdown.value > 0) {
        otpCountdown.value -= 1
      } else {
        stopCountdown()
      }
    }, 1000)
  }

  function saveMfaSession() {
    sessionStorage.setItem(MFA_SESSION_KEY, JSON.stringify({
      mfaToken: mfaToken.value,
      otpSentAt: otpSentAt.value,
    }))
  }

  function enterMfaStep(token: string) {
    mfaToken.value = token
    otpSentAt.value = null
    otpCode.value = ''
    otpError.value = ''
    otpAttemptsRemaining.value = null
    maskedEmail.value = ''
    mfaRequired.value = true
    saveMfaSession()
  }

  function clearMfaSession() {
    sessionStorage.removeItem(MFA_SESSION_KEY)
    mfaRequired.value = false
    mfaToken.value = ''
    otpCode.value = ''
    otpSentAt.value = null
    otpError.value = ''
    otpAttemptsRemaining.value = null
    maskedEmail.value = ''
    stopCountdown()
  }

  async function sendMfaOtp() {
    otpSending.value = true
    otpError.value = ''
    try {
      const response: any = await apiService.post(MFA.SEND, { mfa_token: mfaToken.value })
      maskedEmail.value = response?.masked_email ?? ''
      otpSentAt.value = Date.now()
      saveMfaSession()
      startCountdown(response?.retry_after_seconds ?? 60)
    } catch (error: any) {
      const detail = error?.response?.data?.detail
      const detailMessage = typeof detail === 'string' ? detail : detail?.message
      if (error?.response?.status === 429 && detail?.retry_after_seconds) {
        startCountdown(detail.retry_after_seconds)
      }
      otpError.value = detailMessage || '發送失敗，請稍後再試'
    } finally {
      otpSending.value = false
    }
  }

  async function verifyMfaOtp() {
    otpVerifying.value = true
    otpError.value = ''
    try {
      const response: any = await apiService.post(MFA.VERIFY, {
        mfa_token: mfaToken.value,
        otp: otpCode.value,
      })
      const accessToken = response?.access_token
      if (accessToken) {
        localStorage.setItem('auth_token', accessToken)
        userStore.setToken(accessToken)
        userStore.passwordExpired = response?.password_expired ?? false
        await userStore.fetchCurrentUser()
        clearMfaSession()
        if (response?.password_expired) {
          await router.push('/login/change-password')
        } else {
          await router.push(redirectPath.value)
        }
      } else {
        otpError.value = '驗證失敗，未收到有效 token'
      }
    } catch (error: any) {
      const status = error?.response?.status
      const detail = error?.response?.data?.detail
      const detailMessage = typeof detail === 'string' ? detail : detail?.message
      if (status === 401) {
        // 達失敗次數上限，mfa_token 已失效，須重新登入
        clearMfaSession()
        errorMessage.value = detailMessage || '驗證失敗次數過多，請重新登入'
      } else if (status === 422) {
        otpAttemptsRemaining.value = detail?.attempts_remaining ?? null
        otpError.value = detailMessage || '驗證碼錯誤'
      } else {
        otpError.value = detailMessage || '驗證失敗，請稍後再試'
      }
    } finally {
      otpVerifying.value = false
    }
  }

  const generateCaptcha = async () => {
    captchaLoading.value = true
    captchaError.value = false
    userCaptcha.value = '' // Clear user input

    try {
      const response: any = await apiService.get(AUTH.CAPTCHA)
      captchaToken.value = response.captcha_token
      captcha.value = response.captcha_code
    } catch (error) {
      console.error('Failed to generate captcha:', error)
      // Fallback to client-side generation if backend fails
      const characters = '0123456789'
      const length = 4
      let result = ''
      for (let i = 0; i < length; i++) {
        result += characters.charAt(Math.floor(Math.random() * characters.length))
      }
      captcha.value = result
      captchaToken.value = '' // No backend captcha
    } finally {
      captchaLoading.value = false
    }
  }

  // Watch for user input changes to clear error state
  watch(userCaptcha, () => {
    if (captchaError.value) {
      captchaError.value = false
    }
  })

  // Generate initial CAPTCHA on component mount
  onMounted(async () => {
    // MFA 頁面重整復原（User Story 3）：純靠 sessionStorage 自行還原，不呼叫任何後端狀態查詢端點
    const savedMfaSession = sessionStorage.getItem(MFA_SESSION_KEY)
    if (savedMfaSession) {
      try {
        const parsed = JSON.parse(savedMfaSession) as { mfaToken: string; otpSentAt: number | null }
        if (parsed?.mfaToken) {
          mfaToken.value = parsed.mfaToken
          otpSentAt.value = parsed.otpSentAt
          mfaRequired.value = true
          if (parsed.otpSentAt) {
            // 60 秒為冷卻常數的參考值，僅供 UX 顯示；實際是否可重新發送一律由伺服器回應決定
            const elapsedSeconds = Math.floor((Date.now() - parsed.otpSentAt) / 1000)
            const remainingSeconds = 60 - elapsedSeconds
            if (remainingSeconds > 0) {
              startCountdown(remainingSeconds)
            }
          }
        }
      } catch {
        sessionStorage.removeItem(MFA_SESSION_KEY)
      }
    }

    await generateCaptcha()

    // Load offices if not already loaded
    if (!officesStore.isOfficesLoaded) {
      isOfficesLoading.value = true
      try {
        await officesStore.fetchOffices()
      } catch (error) {
        console.error('Failed to load offices:', error)
      } finally {
        isOfficesLoading.value = false
      }
    }
  })

  const handleLogin = async () => {
    try {
      // First clear any previous error
      errorMessage.value = ''
      captchaError.value = false
      isSubmitting.value = true

      // 前端驗證：檢查 captcha 是否已輸入且為 4 位數字
      if (!userCaptcha.value || userCaptcha.value.length !== 4) {
        captchaError.value = true
        errorMessage.value = '請輸入 4 位數字驗證碼'
        isSubmitting.value = false
        return
      }

      if (!/^\d{4}$/.test(userCaptcha.value)) {
        captchaError.value = true
        errorMessage.value = '驗證碼必須是 4 位數字'
        isSubmitting.value = false
        return
      }

      // Check if we have backend captcha
      if (captchaToken.value) {
        // Use backend validation
        const keyInfo = await getServerPublicKey()
        const { encrypted_password, encrypted_key, iv } = await encryptPassword(
          loginForm.value.password,
          keyInfo.publicKey,
        )
        const loginData = {
          username: loginForm.value.account,
          captcha_token: captchaToken.value,
          captcha_code: userCaptcha.value,
          encrypted_password,
          encrypted_key,
          iv,
          kid: keyInfo.kid,
          timestamp: Date.now(),
          nonce: generateNonce(),
        }

        const response: any = await apiService.post(AUTH.LOGIN_SECURE, loginData)

        console.log('Login response:', response)

        // IP 白名單外來源：進入 MFA 驗證步驟（FR-001）
        if (response?.mfa_required && response?.mfa_token) {
          enterMfaStep(response.mfa_token)
          return
        }

        // 處理 token
        const accessToken = response?.access_token
        if (accessToken) {
          // Update both localStorage and store's token ref
          localStorage.setItem('auth_token', accessToken)
          userStore.setToken(accessToken)
          // 設定密碼過期狀態（主要登入路徑）
          userStore.passwordExpired = response?.password_expired ?? false

          // Fetch current user info
          await userStore.fetchCurrentUser()

          // If remember me is selected, set longer expiration
          if (rememberMe.value) {
            localStorage.setItem('remember_login', 'true')
          }

          // 密碼過期則強制跳轉更換頁，否則導向原目標路徑
          if (response?.password_expired) {
            await router.push('/login/change-password')
          } else {
            await router.push(redirectPath.value)
          }
        } else {
          errorMessage.value = '登入失敗，未收到有效 token'
          await generateCaptcha() // Refresh captcha on failure
        }
      } else {
        // Fallback to client-side validation (when backend captcha not available)
        if (userCaptcha.value !== captcha.value) {
          captchaError.value = true
          return
        }

        // Use original login flow
        const loginData = {
          username: loginForm.value.account,
          password: loginForm.value.password
        }

        console.log('Attempting login with client-side captcha')

        const response = await userService.login(loginData)

        // IP 白名單外來源：進入 MFA 驗證步驟（FR-001，/login 為現行備援路徑，須與 /login-secure 同步保護）
        if (response?.mfa_required && response?.mfa_token) {
          enterMfaStep(response.mfa_token)
          return
        }

        if (response?.access_token) {
          userStore.setToken(response.access_token)
          userStore.passwordExpired = response.password_expired ?? false
          await userStore.fetchCurrentUser()

          if (rememberMe.value) {
            localStorage.setItem('remember_login', 'true')
          }
          if (response.password_expired) {
            await router.push('/login/change-password')
          } else {
            await router.push(redirectPath.value)
          }
        } else {
          alert('登入失敗，請檢查帳號和密碼')
          await generateCaptcha()
        }
      }
    } catch (error: any) {
      console.error('Error during login:', error)

      // Handle specific error types
      if (error?.response?.status === 400) {
        // Captcha error
        captchaError.value = true
        errorMessage.value = error.response?.data?.detail || '驗證碼錯誤或已過期'
      } else if (error?.response?.status === 401) {
        // Authentication error
        errorMessage.value = error.response?.data?.detail || '使用者名稱或密碼不正確'
      } else if (error?.response?.data?.detail) {
        errorMessage.value = error.response.data.detail
      } else if (error?.message) {
        errorMessage.value = error.message
      } else {
        errorMessage.value = '登入時發生未知錯誤'
      }

      // Refresh captcha after any error
      await generateCaptcha()
    } finally {
      isSubmitting.value = false
    }
  }
  // const handleForgotPassword = () => {
  //   // Add your forgot password logic here
  //   console.log('Forgot password clicked')
  // }
  const handleRegistration = async () => {
    try {
      // 重置錯誤
      (Object.keys(formErrors.value) as Array<keyof typeof formErrors.value>).forEach((key) => {
        formErrors.value[key] = ''
      })

      // 表單驗證
      let isValid = true

      if (!registerForm.value.account || registerForm.value.account.length < 3) {
        formErrors.value.account = '帳號長度至少需要3個字元'
        isValid = false
      }

      if (!registerForm.value.password || registerForm.value.password.length < 6) {
        formErrors.value.password = '密碼長度至少需要6個字元'
        isValid = false
      }

      if (registerForm.value.password !== registerForm.value.confirmPassword) {
        formErrors.value.confirmPassword = '兩次輸入的密碼不一致'
        isValid = false
      }

      if (!registerForm.value.name) {
        formErrors.value.name = '請輸入姓名'
        isValid = false
      }

      if (!registerForm.value.department) {
        formErrors.value.department = '請選擇單位'
        isValid = false
      }

      if (!isValid) {
        return
      }

      // 調用 store 的註冊方法
      const result = await userStore.register({
        username: registerForm.value.account,
        password: registerForm.value.password,
        full_name: registerForm.value.name,
        office_id: Number(registerForm.value.department)
      })

      if (result) {
        // 註冊成功，顯示成功消息
        alert('註冊成功！已自動登入。')

        // 導航到首頁
        await router.push('/')
      }
    } catch (error) {
      console.error('註冊失敗:', error)
    }

    console.log('Registration submitted:', registerForm.value)
  }

  const currentStep = ref("1")
  const loginForm = ref({
    account: '',
    password: ''
  })
  const registerForm = ref({
    account: '',
    password: '',
    confirmPassword: '',
    name: '',
    department: null as number | null
  })

  // 處理表單驗證錯誤
  const formErrors = ref<Record<'account' | 'password' | 'confirmPassword' | 'name' | 'department', string>>({
    account: '',
    password: '',
    confirmPassword: '',
    name: '',
    department: ''
  })

  // const officesStore = useOfficesStore()
  const isOfficesLoading = ref(false)

  // Update how departments are loaded
  const departments = computed(() => officesStore.items)

  const handleStep = (direction: 'next' | 'prev') => {
    if (direction === 'next') {
      if (currentStep.value === "2") {
        handleRegistration()
        return
      }
      currentStep.value = currentStep.value === "1" ? "2" : "1"
    } else {
      currentStep.value = currentStep.value === "2" ? "1" : "2"
    }
  }

  const getButtonText = computed(() => {
    if (activeForm.value === 'login') return '登入'
    return currentStep.value === "1" ? '下一步' : '註冊'
  })

  // watchEffect(() => {
  //   console.log('Departments:', departments.value)
  //   if (departments.value?.length > 0) {
  //     console.log('First item:', departments.value[0])
  //     console.log('Classification type:', typeof departments.value[0].classification)
  //   }
  // })
</script>

<style scoped>
  /* ============================================== */
  /* 背景圖響應式設定 */
  /* ============================================== */
  .login-background {
    min-height: 100vh;
    background-size: cover;
    background-position: top left;
    background-repeat: no-repeat;
    transition: background-image 0.3s ease-in-out;
  }

  /* Desktop/Tablet (≥960px): newlogin_empty.jpg */
  @media (min-width: 960px) {
    .login-background {
      background-image: url('@/assets/login/newlogin_empty.jpg');
    }
  }

  /* Mobile (<960px): Background.png */
  @media (max-width: 959px) {
    .login-background {
      background-image: url('@/assets/login/Background.png');
    }
  }

  /* ============================================== */
  /* Desktop Layout */
  /* ============================================== */
  .desktop-header {
    position: absolute;
    top: 20px;
    left: 0;
    right: 0;
    padding: 5px 150px;
    z-index: 10;
  }

  .header-logo {
    width: 30%;
  }

  .header-title {
    width: 45%;
  }

  /* Tablet (960-1279px): Adjust logo/title sizes and padding */
  @media (min-width: 960px) and (max-width: 1279px) {
    .desktop-header {
      padding: 5px 50px;
      padding-top: calc((1279px - 100vw) * 0.02);
    }
    .header-logo {
      width: 35%;
    }
    .header-title {
      width: 50%;
    }
  }

  .desktop-layout {
    justify-content: flex-start;
  }

  .desktop-footer {
    position: absolute;
    bottom: 10px;
    right: 20px;
    color: #333333;
  }

  .footer-text {
    font-family: 'HunInn', sans-serif !important;
    font-size: 15pt;
    margin: 0;
    text-shadow:
      0 1px 3px rgba(255, 255, 255, 0.9),
      0 0 10px rgba(255, 255, 255, 0.7),
      1px 1px 4px rgba(0, 0, 0, 0.2);
    font-weight: 500;
  }

  /* ============================================== */
  /* Small screens Header & Footer (<960px) */
  /* ============================================== */
  .small-screen-header {
    position: relative;
    background-size: cover;
    background-position: top left;
    background-repeat: no-repeat;
    background-image: url('@/assets/login/Tablet_header.png');
    padding-bottom: 21.50%;
  }

  /* <760px 增加 header 高度以容納更大的 Logo */
  @media (max-width: 759px) {
    .small-screen-header {
      padding-bottom: 30%;
      background-position: top left;
    }
  }

  /* Logo 套疊在 header 上,置中顯示 */
  .small-screen-logo {
    position: absolute;
    top: 30%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: min(352px, 90vw);
    max-width: 352px;
    height: auto;
    object-fit: contain;
  }

  .small-screen-footer {
    background-size: cover;
    background-position: top center;
    background-repeat: no-repeat;
    align-items: flex-end;
    background-image: url('@/assets/login/Tablet_footer.png');
    padding-top: 60%;
  }

  .small-screen-footer .footer-text {
    font-size: 12pt;
    margin: 0;
    color: #333333;
    text-shadow:
      0 1px 2px rgba(255, 255, 255, 0.9),
      0 0 8px rgba(255, 255, 255, 0.7),
      1px 1px 3px rgba(0, 0, 0, 0.2);
    font-weight: 500;
  }

  /* <960px 使用垂直佈局: header - form - footer */
  @media (max-width: 959px) {
    /* 單一 column 內垂直排列三個區塊 */
    .small-screen-layout {
      display: flex !important;
      flex-direction: column !important;
      min-height: 100vh !important;
      padding: 0 !important;
    }

    /* Header 區塊 */
    .small-screen-layout .small-screen-header {
      flex: 0 0 auto;
    }

    /* 登入表單區塊 - 佔據剩餘空間並居中 */
    .small-screen-form-wrapper {
      flex: 1 0 auto;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    /* Footer 區塊 */
    .small-screen-layout .small-screen-footer {
      flex: 0 0 auto;
      display: flex;
      align-items: flex-end;
      justify-content: center;
      padding-bottom: 16px;
    }
  }

  /* ============================================== */
  /* 登入表單樣式 */
  /* ============================================== */
  .login-form-wrapper {
    background-color: transparent;
    padding: 2rem;
  }

  /* 登入標題 */
  .login-title {
    font-family: 'HunInn', sans-serif !important;
    color: #000000 !important;
    font-weight: normal;
    font-size: 25pt !important;
  }

  /* MFA 驗證碼步驟提示文字 */
  .mfa-hint {
    font-family: 'HunInn', sans-serif !important;
    color: #333333 !important;
    font-size: 11pt;
    line-height: 1.5;
  }

  /* ============================================== */
  /* Input 組件樣式覆寫 */
  /* ============================================== */
  :deep(.login-input) {
    font-family: 'HunInn', sans-serif !important;
  }

  :deep(.login-input .v-field) {
    background-color: #ffffff !important;
    border-radius: 22pt !important;
  }

  :deep(.login-input .v-field__outline) {
    border-color: #000000 !important;
    border-width: 0.5pt !important;
  }

  :deep(.login-input input) {
    color: #666666 !important;
  }

  :deep(.login-input input::placeholder) {
    font-family: 'HunInn', sans-serif !important;
    color: #666666 !important;
    opacity: 1 !important;
  }

  /* ============================================== */
  /* Button 組件樣式覆寫 */
  /* ============================================== */
  :deep(.login-button) {
    font-family: 'HunInn', sans-serif !important;
    color: #ffffff !important;
    background-color: #3ea0a3 !important;
    border: 0.5pt solid #000000 !important;
    border-radius: 22pt !important;
    box-shadow: none !important;
    text-transform: none !important;
    letter-spacing: normal !important;
    transition: background-color 0.3s ease;
  }

  :deep(.login-button:hover) {
    background-color: #358b8e !important;
  }

  /* ============================================== */
  /* 登入框下方連結樣式 */
  /* ============================================== */
  .login-footer-links {
    margin-top: 15px;
    display: flex;
    justify-content: flex-end;
    align-items: center;
  }

  .footer-link,
  .footer-separator {
    font-family: 'HunInn', sans-serif !important;
    font-size: 12pt !important;
    color: #333333 !important;
    text-decoration: none;
    text-shadow:
      0 1px 2px rgba(255, 255, 255, 0.8),
      0 0 8px rgba(255, 255, 255, 0.6),
      1px 1px 3px rgba(0, 0, 0, 0.2);
    font-weight: 500;
    transition: all 0.2s ease;
  }

  .footer-link:hover {
    color: #3ea0a3 !important;
    text-decoration: underline;
    text-shadow:
      0 1px 3px rgba(255, 255, 255, 0.9),
      0 0 10px rgba(255, 255, 255, 0.7),
      1px 1px 4px rgba(62, 160, 163, 0.3);
  }

  .footer-separator {
    margin: 0 5px;
  }

  /* ============================================== */
  /* 驗證碼顯示樣式 */
  /* ============================================== */
  .captcha-display {
    font-family: 'HunInn', sans-serif;
    font-size: 12pt;
    font-weight: bold;
    color: #ffffff;
    text-shadow: 0px 0px 3px rgba(0, 0, 0, 0.5), 1px 1px 1px rgba(0, 0, 0, 0.3);
    background: linear-gradient(135deg,
      #3ea0a3 0%,
      #5bb5b8 25%,
      #78c9cc 50%,
      #4da8ab 75%,
      #3ea0a3 100%);
    background-size: 200% 200%;
    animation: captcha-gradient 1.5s ease infinite;
    padding: 8px 16px;
    border-radius: 8px;
    cursor: pointer;
    user-select: none;
    letter-spacing: 3px;
    transition: filter 0.2s ease;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    opacity: 0.95;
  }

  @keyframes captcha-gradient {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
  }

  .captcha-display:hover {
    filter: brightness(1.1);
  }

  /* Adjust input padding for captcha field */
  :deep(.captcha-input input) {
    padding-right: 8px !important;
  }

  /* ============================================== */
  /* 密碼顯示/隱藏圖示樣式 */
  /* ============================================== */
  .password-toggle-icon {
    cursor: pointer;
    color: #666666 !important;
    transition: color 0.2s ease;
  }

  .password-toggle-icon:hover {
    color: #3ea0a3 !important;
  }

  /* ============================================== */
  /* MFA 驗證碼發送按鈕（整併於輸入欄位內） */
  /* ============================================== */
  .otp-send-btn {
    font-family: 'HunInn', sans-serif !important;
    text-transform: none !important;
    letter-spacing: normal !important;
    min-width: 0 !important;
    padding: 0 8px !important;
    font-size: 11pt !important;
  }

  :deep(.otp-input input) {
    padding-right: 4px !important;
  }
</style>

<route lang="yaml">
  meta:
    layout: auth
</route>
