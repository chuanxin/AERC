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
      <!-- Desktop/Tablet: Left half for form -->
      <v-col
        v-if="$vuetify.display.mdAndUp"
        cols="12"
        md="7"
        lg="6"
        class="d-flex align-center justify-center"
      >
        <v-responsive :max-width="400">
          <div class="login-form-wrapper">
            <!-- Request Password Reset Mode -->
            <div v-if="!hasToken && !successMessage">
              <h2 class="login-title text-center mb-2">
                忘記密碼
              </h2>
              <p class="text-center text-body-2 mb-6 subtitle-text">
                請輸入您的註冊信箱，我們將寄送密碼重設連結給您
              </p>

              <v-form @submit.prevent="handleRequestReset">
                <v-text-field
                  v-model="email"
                  placeholder="電子郵件"
                  type="email"
                  variant="outlined"
                  density="comfortable"
                  class="login-input mb-4"
                  :error="!!emailError"
                  :error-messages="emailError"
                  hide-details="auto"
                  required
                />

                <v-btn
                  type="submit"
                  color="primary"
                  size="x-large"
                  class="login-button"
                  block
                  :loading="isSubmitting"
                  :disabled="isSubmitting || !email"
                >
                  寄送重設連結
                </v-btn>

                <div class="login-footer-links">
                  <a
                    href="/login"
                    class="footer-link"
                  >返回登入</a>
                </div>
              </v-form>
            </div>

            <!-- Reset Password Mode -->
            <div v-else-if="hasToken && !successMessage">
              <h2 class="login-title text-center mb-2">
                重設密碼
              </h2>
              <p class="text-center text-body-2 mb-6 subtitle-text">
                請輸入您的新密碼
              </p>

              <v-form @submit.prevent="handleResetPassword">
                <v-text-field
                  v-model="newPassword"
                  placeholder="新密碼"
                  :type="showPassword ? 'text' : 'password'"
                  variant="outlined"
                  density="comfortable"
                  class="login-input mb-3"
                  :error="!!passwordError"
                  :error-messages="passwordError"
                  hide-details="auto"
                  required
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
                  v-model="confirmPassword"
                  placeholder="確認新密碼"
                  :type="showConfirmPassword ? 'text' : 'password'"
                  variant="outlined"
                  density="comfortable"
                  class="login-input mb-2"
                  :error="!!confirmPasswordError"
                  :error-messages="confirmPasswordError"
                  hide-details="auto"
                  required
                >
                  <template #append-inner>
                    <v-icon
                      :icon="showConfirmPassword ? 'mdi-eye-off' : 'mdi-eye'"
                      class="password-toggle-icon"
                      @click="showConfirmPassword = !showConfirmPassword"
                    />
                  </template>
                </v-text-field>

                <!-- Password Requirements -->
                <div class="password-requirements mb-4">
                  <p class="text-caption mb-1">
                    密碼要求：
                  </p>
                  <ul class="text-caption">
                    <li :class="{ 'requirement-met': passwordRequirements.length }">
                      至少 8 個字元
                    </li>
                    <li :class="{ 'requirement-met': passwordRequirements.uppercase }">
                      包含至少一個大寫字母
                    </li>
                    <li :class="{ 'requirement-met': passwordRequirements.lowercase }">
                      包含至少一個小寫字母
                    </li>
                    <li :class="{ 'requirement-met': passwordRequirements.number }">
                      包含至少一個數字
                    </li>
                  </ul>
                </div>

                <v-btn
                  type="submit"
                  color="primary"
                  size="x-large"
                  class="login-button"
                  block
                  :loading="isSubmitting"
                  :disabled="isSubmitting || !isPasswordValid"
                >
                  重設密碼
                </v-btn>

                <div class="login-footer-links">
                  <a
                    href="/login"
                    class="footer-link"
                  >返回登入</a>
                </div>
              </v-form>
            </div>

            <!-- Success Message -->
            <div
              v-else-if="successMessage"
              class="text-center"
            >
              <v-icon
                icon="mdi-check-circle"
                size="64"
                color="success"
                class="mb-4"
              />
              <h2 class="login-title mb-4">
                {{ successTitle }}
              </h2>
              <p class="text-body-1 mb-6 subtitle-text">
                {{ successMessage }}
              </p>
              <v-btn
                color="primary"
                size="large"
                class="login-button"
                @click="router.push('/login')"
              >
                前往登入
              </v-btn>
            </div>
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

        <!-- Form -->
        <div class="small-screen-form-wrapper">
          <v-responsive :max-width="352">
            <div class="login-form-wrapper">
              <!-- Request Password Reset Mode -->
              <div v-if="!hasToken && !successMessage">
                <h2 class="login-title text-center mb-2">
                  忘記密碼
                </h2>
                <p class="text-center text-body-2 mb-6 subtitle-text">
                  請輸入您的註冊信箱，我們將寄送密碼重設連結給您
                </p>

                <v-form @submit.prevent="handleRequestReset">
                  <v-text-field
                    v-model="email"
                    placeholder="電子郵件"
                    type="email"
                    variant="outlined"
                    density="comfortable"
                    class="login-input mb-4"
                    :error="!!emailError"
                    :error-messages="emailError"
                    hide-details="auto"
                    required
                  />

                  <v-btn
                    type="submit"
                    color="primary"
                    :size="$vuetify.display.xs ? 'large' : 'x-large'"
                    class="login-button"
                    block
                    :loading="isSubmitting"
                    :disabled="isSubmitting || !email"
                  >
                    寄送重設連結
                  </v-btn>

                  <div class="login-footer-links">
                    <a
                      href="/login"
                      class="footer-link"
                    >返回登入</a>
                  </div>
                </v-form>
              </div>

              <!-- Reset Password Mode -->
              <div v-else-if="hasToken && !successMessage">
                <h2 class="login-title text-center mb-2">
                  重設密碼
                </h2>
                <p class="text-center text-body-2 mb-6 subtitle-text">
                  請輸入您的新密碼
                </p>

                <v-form @submit.prevent="handleResetPassword">
                  <v-text-field
                    v-model="newPassword"
                    placeholder="新密碼"
                    :type="showPassword ? 'text' : 'password'"
                    variant="outlined"
                    density="comfortable"
                    class="login-input mb-3"
                    :error="!!passwordError"
                    :error-messages="passwordError"
                    hide-details="auto"
                    required
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
                    v-model="confirmPassword"
                    placeholder="確認新密碼"
                    :type="showConfirmPassword ? 'text' : 'password'"
                    variant="outlined"
                    density="comfortable"
                    class="login-input mb-2"
                    :error="!!confirmPasswordError"
                    :error-messages="confirmPasswordError"
                    hide-details="auto"
                    required
                  >
                    <template #append-inner>
                      <v-icon
                        :icon="showConfirmPassword ? 'mdi-eye-off' : 'mdi-eye'"
                        class="password-toggle-icon"
                        @click="showConfirmPassword = !showConfirmPassword"
                      />
                    </template>
                  </v-text-field>

                  <!-- Password Requirements -->
                  <div class="password-requirements mb-4">
                    <p class="text-caption mb-1">
                      密碼要求：
                    </p>
                    <ul class="text-caption">
                      <li :class="{ 'requirement-met': passwordRequirements.length }">
                        至少 8 個字元
                      </li>
                      <li :class="{ 'requirement-met': passwordRequirements.uppercase }">
                        包含至少一個大寫字母
                      </li>
                      <li :class="{ 'requirement-met': passwordRequirements.lowercase }">
                        包含至少一個小寫字母
                      </li>
                      <li :class="{ 'requirement-met': passwordRequirements.number }">
                        包含至少一個數字
                      </li>
                    </ul>
                  </div>

                  <v-btn
                    type="submit"
                    color="primary"
                    :size="$vuetify.display.xs ? 'large' : 'x-large'"
                    class="login-button"
                    block
                    :loading="isSubmitting"
                    :disabled="isSubmitting || !isPasswordValid"
                  >
                    重設密碼
                  </v-btn>

                  <div class="login-footer-links">
                    <a
                      href="/login"
                      class="footer-link"
                    >返回登入</a>
                  </div>
                </v-form>
              </div>

              <!-- Success Message -->
              <div
                v-else-if="successMessage"
                class="text-center"
              >
                <v-icon
                  icon="mdi-check-circle"
                  size="64"
                  color="success"
                  class="mb-4"
                />
                <h2 class="login-title mb-4">
                  {{ successTitle }}
                </h2>
                <p class="text-body-1 mb-6 subtitle-text">
                  {{ successMessage }}
                </p>
                <v-btn
                  color="primary"
                  size="large"
                  class="login-button"
                  @click="router.push('/login')"
                >
                  前往登入
                </v-btn>
              </div>
            </div>
          </v-responsive>
        </div>

        <!-- Footer -->
        <div class="small-screen-footer">
          <div class="d-flex flex-column align-center">
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
        <p class="footer-text">
          &copy; 2025 農田水利署. All rights reserved.
        </p>
      </div>
    </div>
  </v-container>
</template>

<script lang="ts" setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { apiService } from '@/services/api/http'
import { AUTH } from '@/services/api/endpoints'

const route = useRoute()
const router = useRouter()

// Check if we're in reset mode (has token) or request mode (no token)
const hasToken = computed(() => !!route.query.token)
const token = computed(() => route.query.token as string)

// Form state
const email = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const showPassword = ref(false)
const showConfirmPassword = ref(false)
const isSubmitting = ref(false)

// Error state
const emailError = ref('')
const passwordError = ref('')
const confirmPasswordError = ref('')

// Success state
const successMessage = ref('')
const successTitle = ref('')

// Password requirements validation
const passwordRequirements = computed(() => ({
  length: newPassword.value.length >= 8,
  uppercase: /[A-Z]/.test(newPassword.value),
  lowercase: /[a-z]/.test(newPassword.value),
  number: /\d/.test(newPassword.value),
}))

const isPasswordValid = computed(() => {
  return (
    passwordRequirements.value.length &&
    passwordRequirements.value.uppercase &&
    passwordRequirements.value.lowercase &&
    passwordRequirements.value.number &&
    newPassword.value === confirmPassword.value
  )
})

// Validate email format
const isValidEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

// Handle request password reset
const handleRequestReset = async () => {
  emailError.value = ''

  if (!email.value) {
    emailError.value = '請輸入電子郵件'
    return
  }

  if (!isValidEmail(email.value)) {
    emailError.value = '請輸入有效的電子郵件格式'
    return
  }

  isSubmitting.value = true

  try {
    const response: any = await apiService.post(AUTH.REQUEST_PASSWORD_RESET, {
      email: email.value,
    })

    if (response.success) {
      successTitle.value = '重設連結已寄送'
      // 使用後端返回的訊息（避免洩漏帳號存在）
      successMessage.value = response.message || '如果該電子郵件已註冊，您將收到密碼重設信。'
    }
  } catch (error: any) {
    // 只顯示通用錯誤訊息，不洩漏系統資訊
    emailError.value = '寄送失敗，請稍後再試或聯繫系統管理員'
  } finally {
    isSubmitting.value = false
  }
}

// Handle reset password
const handleResetPassword = async () => {
  passwordError.value = ''
  confirmPasswordError.value = ''

  // Validate password
  if (!newPassword.value) {
    passwordError.value = '請輸入新密碼'
    return
  }

  if (newPassword.value.length < 8) {
    passwordError.value = '密碼長度至少需要 8 個字元'
    return
  }

  if (!passwordRequirements.value.uppercase) {
    passwordError.value = '密碼需包含至少一個大寫字母'
    return
  }

  if (!passwordRequirements.value.lowercase) {
    passwordError.value = '密碼需包含至少一個小寫字母'
    return
  }

  if (!passwordRequirements.value.number) {
    passwordError.value = '密碼需包含至少一個數字'
    return
  }

  // Validate confirm password
  if (!confirmPassword.value) {
    confirmPasswordError.value = '請確認新密碼'
    return
  }

  if (newPassword.value !== confirmPassword.value) {
    confirmPasswordError.value = '兩次輸入的密碼不一致'
    return
  }

  isSubmitting.value = true

  try {
    const response: any = await apiService.post(AUTH.RESET_PASSWORD, {
      token: token.value,
      new_password: newPassword.value,
    })

    if (response.success) {
      successTitle.value = '密碼重設成功'
      // 使用後端返回的訊息
      successMessage.value = response.message || '您的密碼已成功重設，請使用新密碼登入系統。'
    }
  } catch (error: any) {
    // 統一的錯誤處理，避免洩漏系統資訊
    if (error.response?.status === 400) {
      passwordError.value = '重設連結無效或已過期，請重新申請密碼重設'
    } else if (error.response?.status === 422) {
      // Pydantic 驗證錯誤（密碼格式不符）
      passwordError.value = '密碼格式不符合要求，請檢查密碼強度'
    } else {
      // 其他錯誤不顯示詳細訊息
      passwordError.value = '重設失敗，請稍後再試或聯繫系統管理員'
    }
  } finally {
    isSubmitting.value = false
  }
}

// Check token validity on mount (if in reset mode)
onMounted(async () => {
  if (hasToken.value) {
    // Optionally validate token here
    console.log('Reset mode with token:', token.value)
  }
})
</script>

<style scoped>
/* Reuse login page styles */
.login-background {
  min-height: 100vh;
  background-size: cover;
  background-position: top left;
  background-repeat: no-repeat;
  transition: background-image 0.3s ease-in-out;
}

@media (min-width: 960px) {
  .login-background {
    background-image: url('@/assets/login/newlogin_empty.jpg');
  }
}

@media (max-width: 959px) {
  .login-background {
    background-image: url('@/assets/login/Background.png');
  }
}

/* Desktop Layout */
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

/* Small screens Layout */
.small-screen-header {
  position: relative;
  background-size: cover;
  background-position: top left;
  background-repeat: no-repeat;
  background-image: url('@/assets/login/Tablet_header.png');
  padding-bottom: 21.50%;
}

@media (max-width: 759px) {
  .small-screen-header {
    padding-bottom: 30%;
    background-position: top left;
  }
}

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

@media (max-width: 959px) {
  .small-screen-layout {
    display: flex !important;
    flex-direction: column !important;
    min-height: 100vh !important;
    padding: 0 !important;
  }

  .small-screen-layout .small-screen-header {
    flex: 0 0 auto;
  }

  .small-screen-form-wrapper {
    flex: 1 0 auto;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .small-screen-layout .small-screen-footer {
    flex: 0 0 auto;
    display: flex;
    align-items: flex-end;
    justify-content: center;
    padding-bottom: 16px;
  }
}

/* Form Styles */
.login-form-wrapper {
  background-color: transparent;
  padding: 2rem;
}

.login-title {
  font-family: 'HunInn', sans-serif !important;
  color: #000000 !important;
  font-weight: normal;
  font-size: 25pt !important;
}

.subtitle-text {
  font-family: 'HunInn', sans-serif !important;
  color: #666666 !important;
}

/* Input Styles */
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

/* Button Styles */
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

/* Footer Links */
.login-footer-links {
  margin-top: 15px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.footer-link {
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

/* Password Toggle Icon */
.password-toggle-icon {
  cursor: pointer;
  color: #666666 !important;
  transition: color 0.2s ease;
}

.password-toggle-icon:hover {
  color: #3ea0a3 !important;
}

/* Password Requirements */
.password-requirements {
  padding: 12px 16px;
  background-color: #f5f5f5;
  border-radius: 8px;
  border-left: 3px solid #3ea0a3;
}

.password-requirements p {
  font-family: 'HunInn', sans-serif !important;
  color: #333333;
  font-weight: 500;
}

.password-requirements ul {
  list-style: none;
  padding-left: 0;
  margin: 0;
}

.password-requirements li {
  font-family: 'HunInn', sans-serif !important;
  color: #999999;
  padding: 2px 0;
  position: relative;
  padding-left: 20px;
}

.password-requirements li::before {
  content: '○';
  position: absolute;
  left: 0;
  color: #999999;
}

.password-requirements li.requirement-met {
  color: #4caf50;
}

.password-requirements li.requirement-met::before {
  content: '✓';
  color: #4caf50;
  font-weight: bold;
}
</style>

<route lang="yaml">
meta:
  layout: auth
  public: true
</route>
