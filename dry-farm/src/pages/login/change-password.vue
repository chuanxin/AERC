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
            <h2 class="login-title text-center mb-2">
              更換密碼
            </h2>
            <p class="text-center text-body-2 mb-6 subtitle-text">
              您的密碼已超過 90 天未更換，請設定新密碼後繼續使用系統
            </p>

            <v-form @submit.prevent="handleChangePassword">
              <v-text-field
                v-model="newPassword"
                placeholder="新密碼"
                :type="showNewPassword ? 'text' : 'password'"
                variant="outlined"
                density="comfortable"
                class="login-input mb-3"
                :error="!!newPasswordError"
                :error-messages="newPasswordError"
                hide-details="auto"
                required
              >
                <template #append-inner>
                  <v-icon
                    :icon="showNewPassword ? 'mdi-eye-off' : 'mdi-eye'"
                    class="password-toggle-icon"
                    @click="showNewPassword = !showNewPassword"
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

              <!-- 密碼強度即時檢核 -->
              <v-card
                variant="tonal"
                :color="isPasswordValid ? 'success' : 'info'"
                class="mb-4"
              >
                <v-card-text class="text-medium-emphasis text-caption pa-3">
                  <div class="font-weight-medium mb-1">
                    密碼要求：
                  </div>
                  <template v-if="policyLoading">
                    <div class="d-flex align-center text-grey py-1">
                      <v-progress-circular size="14" width="2" indeterminate class="mr-2" />
                      密碼規則載入中...
                    </div>
                  </template>
                  <template v-else-if="policyLoadError">
                    <div class="d-flex align-center text-error py-1">
                      <v-icon size="small" icon="mdi-alert-circle" class="mr-1" />
                      無法取得密碼規則，請重新整理頁面
                    </div>
                  </template>
                  <template v-else-if="passwordRequirements">
                    <div class="d-flex align-center mb-1">
                      <v-icon
                        :icon="passwordRequirements.length ? 'mdi-check-circle' : 'mdi-circle-outline'"
                        :color="passwordRequirements.length ? 'success' : 'grey'"
                        size="x-small"
                        class="mr-1"
                      />
                      <span>{{ passwordRequirements.labels.min_length }}</span>
                    </div>
                    <div class="d-flex align-center mb-1">
                      <v-icon
                        :icon="passwordRequirements.characterTypesValid ? 'mdi-check-circle' : 'mdi-circle-outline'"
                        :color="passwordRequirements.characterTypesValid ? 'success' : 'grey'"
                        size="x-small"
                        class="mr-1"
                      />
                      <span>{{ passwordRequirements.labels.required_types }} (目前 {{ passwordRequirements.characterTypesMet }}/{{ passwordRequirements.totalTypesCount }})</span>
                    </div>
                    <div class="ml-4">
                      <div class="d-flex align-center">
                        <v-icon
                          :icon="passwordRequirements.number ? 'mdi-check' : 'mdi-minus'"
                          :color="passwordRequirements.number ? 'success' : 'grey'"
                          size="x-small"
                          class="mr-1"
                        />
                        <span>{{ passwordRequirements.labels.has_digit }}</span>
                        <span class="mx-1">•</span>
                        <v-icon
                          :icon="passwordRequirements.uppercase ? 'mdi-check' : 'mdi-minus'"
                          :color="passwordRequirements.uppercase ? 'success' : 'grey'"
                          size="x-small"
                          class="mr-1"
                        />
                        <span>{{ passwordRequirements.labels.has_upper }}</span>
                      </div>
                      <div class="d-flex align-center">
                        <v-icon
                          :icon="passwordRequirements.lowercase ? 'mdi-check' : 'mdi-minus'"
                          :color="passwordRequirements.lowercase ? 'success' : 'grey'"
                          size="x-small"
                          class="mr-1"
                        />
                        <span>{{ passwordRequirements.labels.has_lower }}</span>
                        <span class="mx-1">•</span>
                        <v-icon
                          :icon="passwordRequirements.special ? 'mdi-check' : 'mdi-minus'"
                          :color="passwordRequirements.special ? 'success' : 'grey'"
                          size="x-small"
                          class="mr-1"
                        />
                        <span>{{ passwordRequirements.labels.has_special }}</span>
                      </div>
                    </div>
                  </template>
                </v-card-text>
              </v-card>

              <!-- 後端錯誤訊息 -->
              <v-alert
                v-if="errorMessage"
                type="error"
                variant="tonal"
                density="compact"
                class="mb-4"
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
                :disabled="isSubmitting || !canSubmit"
              >
                確認更換
              </v-btn>

              <div class="login-footer-links">
                <a
                  href="/login"
                  class="footer-link"
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

        <!-- Form -->
        <div class="small-screen-form-wrapper">
          <v-responsive :max-width="352">
            <div class="login-form-wrapper">
              <h2 class="login-title text-center mb-2">
                更換密碼
              </h2>
              <p class="text-center text-body-2 mb-6 subtitle-text">
                您的密碼已超過 90 天未更換，請設定新密碼
              </p>

              <v-form @submit.prevent="handleChangePassword">
                <v-text-field
                  v-model="newPassword"
                  placeholder="新密碼"
                  :type="showNewPassword ? 'text' : 'password'"
                  variant="outlined"
                  density="comfortable"
                  class="login-input mb-3"
                  :error="!!newPasswordError"
                  :error-messages="newPasswordError"
                  hide-details="auto"
                  required
                >
                  <template #append-inner>
                    <v-icon
                      :icon="showNewPassword ? 'mdi-eye-off' : 'mdi-eye'"
                      class="password-toggle-icon"
                      @click="showNewPassword = !showNewPassword"
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

                <!-- 密碼強度即時檢核 -->
                <v-card
                  variant="tonal"
                  :color="isPasswordValid ? 'success' : 'info'"
                  class="mb-4"
                >
                  <v-card-text class="text-medium-emphasis text-caption pa-3">
                    <div class="font-weight-medium mb-1">
                      密碼要求：
                    </div>
                    <template v-if="policyLoading">
                      <div class="d-flex align-center text-grey py-1">
                        <v-progress-circular size="14" width="2" indeterminate class="mr-2" />
                        密碼規則載入中...
                      </div>
                    </template>
                    <template v-else-if="policyLoadError">
                      <div class="d-flex align-center text-error py-1">
                        <v-icon size="small" icon="mdi-alert-circle" class="mr-1" />
                        無法取得密碼規則，請重新整理頁面
                      </div>
                    </template>
                    <template v-else-if="passwordRequirements">
                      <div class="d-flex align-center mb-1">
                        <v-icon
                          :icon="passwordRequirements.length ? 'mdi-check-circle' : 'mdi-circle-outline'"
                          :color="passwordRequirements.length ? 'success' : 'grey'"
                          size="x-small"
                          class="mr-1"
                        />
                        <span>{{ passwordRequirements.labels.min_length }}</span>
                      </div>
                      <div class="d-flex align-center mb-1">
                        <v-icon
                          :icon="passwordRequirements.characterTypesValid ? 'mdi-check-circle' : 'mdi-circle-outline'"
                          :color="passwordRequirements.characterTypesValid ? 'success' : 'grey'"
                          size="x-small"
                          class="mr-1"
                        />
                        <span>{{ passwordRequirements.labels.required_types }} (目前 {{ passwordRequirements.characterTypesMet }}/{{ passwordRequirements.totalTypesCount }})</span>
                      </div>
                      <div class="ml-4">
                        <div class="d-flex align-center">
                          <v-icon
                            :icon="passwordRequirements.number ? 'mdi-check' : 'mdi-minus'"
                            :color="passwordRequirements.number ? 'success' : 'grey'"
                            size="x-small"
                            class="mr-1"
                          />
                          <span>{{ passwordRequirements.labels.has_digit }}</span>
                          <span class="mx-1">•</span>
                          <v-icon
                            :icon="passwordRequirements.uppercase ? 'mdi-check' : 'mdi-minus'"
                            :color="passwordRequirements.uppercase ? 'success' : 'grey'"
                            size="x-small"
                            class="mr-1"
                          />
                          <span>{{ passwordRequirements.labels.has_upper }}</span>
                        </div>
                        <div class="d-flex align-center">
                          <v-icon
                            :icon="passwordRequirements.lowercase ? 'mdi-check' : 'mdi-minus'"
                            :color="passwordRequirements.lowercase ? 'success' : 'grey'"
                            size="x-small"
                            class="mr-1"
                          />
                          <span>{{ passwordRequirements.labels.has_lower }}</span>
                          <span class="mx-1">•</span>
                          <v-icon
                            :icon="passwordRequirements.special ? 'mdi-check' : 'mdi-minus'"
                            :color="passwordRequirements.special ? 'success' : 'grey'"
                            size="x-small"
                            class="mr-1"
                          />
                          <span>{{ passwordRequirements.labels.has_special }}</span>
                        </div>
                      </div>
                    </template>
                  </v-card-text>
                </v-card>

                <!-- 後端錯誤訊息 -->
                <v-alert
                  v-if="errorMessage"
                  type="error"
                  variant="tonal"
                  density="compact"
                  class="mb-4"
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
                  :disabled="isSubmitting || !canSubmit"
                >
                  確認更換
                </v-btn>

                <div class="login-footer-links">
                  <a
                    href="/login"
                    class="footer-link"
                  >返回登入</a>
                </div>
              </v-form>
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
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/users'
import { getPasswordPolicy, policyLoading, policyLoadError } from '@/services/passwordPolicyService'

const router = useRouter()
const userStore = useUserStore()

// 表單狀態
const newPassword = ref('')
const confirmPassword = ref('')
const showNewPassword = ref(false)
const showConfirmPassword = ref(false)
const isSubmitting = ref(false)

// 錯誤狀態
const newPasswordError = ref('')
const confirmPasswordError = ref('')
const errorMessage = ref('')

// 密碼強度即時計算
const passwordRequirements = computed(() => {
  const policy = getPasswordPolicy()
  if (!policy) return null

  const p = policy.char_type_patterns
  const reqs = {
    length:    newPassword.value.length >= policy.min_length,
    uppercase: new RegExp(p.upper).test(newPassword.value),
    lowercase: new RegExp(p.lower).test(newPassword.value),
    number:    new RegExp(p.digit).test(newPassword.value),
    special:   new RegExp(p.special).test(newPassword.value),
  }
  const characterTypesMet = [reqs.uppercase, reqs.lowercase, reqs.number, reqs.special].filter(Boolean).length
  return {
    ...reqs,
    characterTypesMet,
    characterTypesValid: characterTypesMet >= policy.required_types_count,
    totalTypesCount: policy.total_types_count,
    labels: policy.labels,
  }
})

const isPasswordValid = computed(() =>
  passwordRequirements.value?.length &&
  passwordRequirements.value?.characterTypesValid &&
  newPassword.value === confirmPassword.value &&
  confirmPassword.value.length > 0
)

const canSubmit = computed(() => isPasswordValid.value)

const handleChangePassword = async () => {
  // 清除所有錯誤
  newPasswordError.value = ''
  confirmPasswordError.value = ''
  errorMessage.value = ''

  // 本地驗證
  const policy = getPasswordPolicy()
  if (!policy) {
    newPasswordError.value = '密碼規則尚未載入，請重新整理頁面'
    return
  }
  if (!newPassword.value) {
    newPasswordError.value = '請輸入新密碼'
    return
  }
  if (!passwordRequirements.value?.length) {
    newPasswordError.value = policy.labels.min_length
    return
  }
  if (!passwordRequirements.value?.characterTypesValid) {
    const typeList = [
      policy.labels.has_digit,
      policy.labels.has_upper,
      policy.labels.has_lower,
      policy.labels.has_special,
    ].join('、')
    newPasswordError.value = `密碼需符合以下 ${policy.required_types_count} 項中的至少 ${policy.required_types_count} 項：${typeList}`
    return
  }
  if (!confirmPassword.value) {
    confirmPasswordError.value = '請確認新密碼'
    return
  }
  if (newPassword.value !== confirmPassword.value) {
    confirmPasswordError.value = '兩次輸入的密碼不一致'
    return
  }

  isSubmitting.value = true

  // wrapAsync：成功回傳 true，失敗回傳 null
  const result = await userStore.changePassword(newPassword.value)

  isSubmitting.value = false

  if (result === null) {
    // 失敗：顯示後端錯誤訊息，留在當前頁面讓使用者修正後重試
    errorMessage.value = userStore.error || '密碼更換失敗，請稍後再試'
    return
  }

  // 成功：登出並導向登入頁，要求以新密碼重新登入
  await userStore.logout()
  await router.push({ path: '/login', query: { message: 'password_changed' } })
}
</script>

<style scoped>
/* 與 reset.vue 完全一致的樣式 */
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
    1px 1px 4px rgba(0, 0, 0, 0.2);
}

.password-toggle-icon {
  cursor: pointer;
  opacity: 0.6;
}

.password-toggle-icon:hover {
  opacity: 1;
}
</style>
