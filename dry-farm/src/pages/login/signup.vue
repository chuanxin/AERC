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

    <!-- Signup Dialog -->
    <v-dialog
      v-model="showDialog"
      max-width="600"
      persistent
    >
      <v-card class="signup-card">
        <v-card-title class="signup-title text-center pt-6">
          帳號申請
        </v-card-title>

        <v-card-text class="px-6">
          <v-stepper
            v-model="currentStep"
            :items="stepperItems"
            flat
            hide-actions
          >
            <!-- Step 1: All Info (except password) -->
            <template #item.1>
              <v-text-field
                v-model="signupForm.username"
                label="擬申請帳號 *"
                placeholder="請輸入帳號（至少 3 個字元）"
                variant="outlined"
                density="comfortable"
                class="mb-3"
                :error-messages="formErrors.username"
                :loading="usernameChecking"
                @input="handleUsernameInput"
              >
                <template #append-inner>
                  <v-icon
                    v-if="usernameAvailable === true"
                    color="success"
                    icon="mdi-check-circle"
                  />
                  <v-icon
                    v-else-if="usernameAvailable === false"
                    color="error"
                    icon="mdi-close-circle"
                  />
                </template>
              </v-text-field>

              <v-text-field
                v-model="signupForm.email"
                label="E-Mail *"
                placeholder="請輸入電子郵件"
                type="email"
                variant="outlined"
                density="comfortable"
                class="mb-3"
                :error-messages="formErrors.email"
                @input="clearError('email')"
              />

              <v-text-field
                v-model="signupForm.full_name"
                label="姓名 *"
                placeholder="請輸入您的姓名"
                variant="outlined"
                density="comfortable"
                class="mb-3"
                :error-messages="formErrors.full_name"
                @input="clearError('full_name')"
              />

              <v-select
                v-model="signupForm.office_id"
                label="所屬單位（管理處）*"
                :items="offices"
                item-title="name"
                item-value="id"
                variant="outlined"
                density="comfortable"
                class="mb-3"
                :loading="isOfficesLoading"
                :error-messages="formErrors.office_id"
                @update:model-value="clearError('office_id')"
              />

              <v-text-field
                v-model="signupForm.department"
                label="所屬部門（工作站）*"
                placeholder="請輸入所屬部門或工作站"
                variant="outlined"
                density="comfortable"
                class="mb-3"
                :error-messages="formErrors.department"
                @input="clearError('department')"
              />

              <v-text-field
                v-model="signupForm.job_title"
                label="職稱"
                placeholder="請輸入您的職稱（選填）"
                variant="outlined"
                density="comfortable"
                class="mb-3"
              />

              <v-row no-gutters>
                <v-col
                  cols="8"
                  class="pr-2"
                >
                  <v-text-field
                    v-model="signupForm.phone"
                    label="聯絡電話 *"
                    placeholder="例：02-12345678"
                    variant="outlined"
                    density="comfortable"
                    class="mb-3"
                    :error-messages="formErrors.phone"
                    @input="clearError('phone')"
                  />
                </v-col>
                <v-col cols="4">
                  <v-text-field
                    v-model="signupForm.phone_ext"
                    label="分機"
                    placeholder="選填"
                    variant="outlined"
                    density="comfortable"
                    class="mb-3"
                  />
                </v-col>
              </v-row>

              <v-text-field
                v-model="signupForm.mobile"
                label="手機"
                placeholder="例：0912345678（選填）"
                variant="outlined"
                density="comfortable"
                class="mb-3"
              />

              <v-textarea
                v-model="signupForm.application_reason"
                label="申請原因說明 *"
                placeholder="請說明申請帳號的原因與用途"
                variant="outlined"
                density="comfortable"
                rows="3"
                class="mb-3"
                :error-messages="formErrors.application_reason"
                @input="clearError('application_reason')"
              />
            </template>

            <!-- Step 2: Email OTP Verification -->
            <template #item.2>
              <v-alert
                v-if="!otpSent"
                type="info"
                variant="tonal"
                class="mb-4"
              >
                我們將發送驗證碼至您的電子郵件：<br>
                <strong>{{ signupForm.email }}</strong>
              </v-alert>

              <v-alert
                v-if="otpSent && !emailVerified"
                type="success"
                variant="tonal"
                class="mb-4"
              >
                驗證碼已發送至 <strong>{{ signupForm.email }}</strong><br>
                請在 {{ otpCountdown }} 秒內輸入驗證碼
              </v-alert>

              <v-alert
                v-if="emailVerified"
                type="success"
                variant="tonal"
                class="mb-4"
              >
                <v-icon icon="mdi-check-circle" />
                電子郵件驗證成功！
              </v-alert>

              <div
                v-if="!otpSent"
                class="text-center"
              >
                <v-btn
                  color="primary"
                  size="large"
                  :loading="sendingOtp"
                  @click="sendOtp"
                >
                  發送驗證碼
                </v-btn>
              </div>

              <div v-if="otpSent && !emailVerified">
                <v-otp-input
                  v-model="otpCode"
                  :length="6"
                  type="number"
                  variant="outlined"
                  class="mb-3"
                  :error="!!formErrors.otp"
                />
                <div
                  v-if="formErrors.otp"
                  class="text-error text-caption mb-2"
                >
                  {{ formErrors.otp }}
                </div>

                <div class="d-flex justify-space-between align-center mb-3">
                  <v-btn
                    variant="text"
                    size="small"
                    :disabled="otpCountdown > 0 || sendingOtp"
                    @click="resendOtp"
                  >
                    重新發送
                  </v-btn>
                  <v-btn
                    color="primary"
                    :loading="verifyingOtp"
                    :disabled="otpCode.length !== 6"
                    @click="verifyOtp"
                  >
                    驗證
                  </v-btn>
                </div>
              </div>
            </template>

            <!-- Step 3: Password Setup -->
            <template #item.3>
              <v-text-field
                v-model="signupForm.password"
                label="密碼 *"
                placeholder="請輸入密碼"
                :type="showPassword ? 'text' : 'password'"
                variant="outlined"
                density="comfortable"
                class="mb-3"
                :error-messages="formErrors.password"
                @input="clearError('password')"
              >
                <template #append-inner>
                  <v-icon
                    :icon="showPassword ? 'mdi-eye-off' : 'mdi-eye'"
                    @click="showPassword = !showPassword"
                  />
                </template>
              </v-text-field>

              <!-- Password Requirements -->
              <div class="password-requirements mb-3">
                <div
                  class="requirement"
                  :class="{ met: passwordRequirements.minLength }"
                >
                  <v-icon
                    :icon="passwordRequirements.minLength ? 'mdi-check-circle' : 'mdi-circle-outline'"
                    size="small"
                  />
                  至少 8 個字元
                </div>
                <div class="requirement-header mt-2 mb-1">
                  以下 4 項至少符合 3 項：
                </div>
                <div
                  class="requirement"
                  :class="{ met: passwordRequirements.hasDigit }"
                >
                  <v-icon
                    :icon="passwordRequirements.hasDigit ? 'mdi-check-circle' : 'mdi-circle-outline'"
                    size="small"
                  />
                  包含數字
                </div>
                <div
                  class="requirement"
                  :class="{ met: passwordRequirements.hasUpper }"
                >
                  <v-icon
                    :icon="passwordRequirements.hasUpper ? 'mdi-check-circle' : 'mdi-circle-outline'"
                    size="small"
                  />
                  包含英文大寫
                </div>
                <div
                  class="requirement"
                  :class="{ met: passwordRequirements.hasLower }"
                >
                  <v-icon
                    :icon="passwordRequirements.hasLower ? 'mdi-check-circle' : 'mdi-circle-outline'"
                    size="small"
                  />
                  包含英文小寫
                </div>
                <div
                  class="requirement"
                  :class="{ met: passwordRequirements.hasSpecial }"
                >
                  <v-icon
                    :icon="passwordRequirements.hasSpecial ? 'mdi-check-circle' : 'mdi-circle-outline'"
                    size="small"
                  />
                  包含特殊符號
                </div>
                <div
                  class="requirement mt-2"
                  :class="{ met: passwordRequirements.characterTypesValid }"
                >
                  <v-icon
                    :icon="passwordRequirements.characterTypesValid ? 'mdi-check-circle' : 'mdi-circle-outline'"
                    size="small"
                  />
                  <strong>符合 {{ passwordRequirements.typesCount }}/4 項（至少 3 項）</strong>
                </div>
              </div>

              <v-text-field
                v-model="signupForm.confirmPassword"
                label="確認密碼 *"
                placeholder="請再次輸入密碼"
                :type="showConfirmPassword ? 'text' : 'password'"
                variant="outlined"
                density="comfortable"
                class="mb-3"
                :error-messages="formErrors.confirmPassword"
                @input="clearError('confirmPassword')"
              >
                <template #append-inner>
                  <v-icon
                    :icon="showConfirmPassword ? 'mdi-eye-off' : 'mdi-eye'"
                    @click="showConfirmPassword = !showConfirmPassword"
                  />
                </template>
              </v-text-field>
            </template>
          </v-stepper>

          <!-- Error Alert -->
          <v-alert
              v-if="submitError"
              type="error"
              variant="tonal"
              density="compact"
              class="mb-3"
            >
              {{ submitError }}
            </v-alert>

            <!-- Success Message -->
            <v-alert
              v-if="successMessage"
              type="success"
              variant="tonal"
              density="compact"
              class="mb-3"
            >
              {{ successMessage }}
            </v-alert>
        </v-card-text>

        <v-card-actions class="px-6 pb-6">
          <v-btn
            variant="text"
            @click="handleCancel"
          >
            取消
          </v-btn>
          <v-spacer />
          <v-btn
            v-if="currentStep > 1 && !emailVerified"
            variant="text"
            @click="handlePrevStep"
          >
            上一步
          </v-btn>
          <v-btn
            v-if="currentStep !== 2 || emailVerified"
            color="primary"
            variant="flat"
            :loading="isSubmitting"
            :disabled="isSubmitting || (currentStep === 2 && !emailVerified)"
            @click="handleNextOrSubmit"
          >
            {{ getStepButtonText }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

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
  import { useOfficesStore } from '@/stores/offices'
  import { apiService } from '@/services/api/http'
  import { USERS, AUTH } from '@/services/api/endpoints'

  const router = useRouter()
  const officesStore = useOfficesStore()

  const showDialog = ref(true)
  const currentStep = ref(1)
  const showPassword = ref(false)
  const showConfirmPassword = ref(false)
  const isSubmitting = ref(false)
  const isOfficesLoading = ref(false)
  const submitError = ref('')
  const successMessage = ref('')
  const formRef = ref()

  // Username real-time check
  const usernameChecking = ref(false)
  const usernameAvailable = ref<boolean | null>(null)
  let usernameCheckTimeout: ReturnType<typeof setTimeout> | null = null

  // OTP verification
  const otpSent = ref(false)
  const otpToken = ref('')
  const otpCode = ref('')
  const otpCountdown = ref(0)
  const sendingOtp = ref(false)
  const verifyingOtp = ref(false)
  const emailVerified = ref(false)
  const verifiedToken = ref('')
  let countdownInterval: ReturnType<typeof setInterval> | null = null

  const signupForm = ref({
    username: '',
    email: '',
    full_name: '',
    office_id: null as number | null,
    department: '',
    job_title: '',
    phone: '',
    phone_ext: '',
    mobile: '',
    application_reason: '',
    password: '',
    confirmPassword: ''
  })

  const formErrors = ref({
    username: '',
    email: '',
    full_name: '',
    office_id: '',
    department: '',
    phone: '',
    application_reason: '',
    password: '',
    confirmPassword: '',
    otp: ''
  })

  const offices = computed(() => officesStore.items)

  // Stepper items configuration
  const stepperItems = [
    {
      title: '填寫資料',
      subtitle: '基本資料與申請原因',
      value: 1
    },
    {
      title: '驗證信箱',
      subtitle: 'Email OTP 驗證',
      value: 2
    },
    {
      title: '設定密碼',
      subtitle: '完成帳號申請',
      value: 3
    }
  ]

  // Password requirements validation
  const passwordRequirements = computed(() => {
    const password = signupForm.value.password
    const hasDigit = /\d/.test(password)
    const hasUpper = /[A-Z]/.test(password)
    const hasLower = /[a-z]/.test(password)
    const hasSpecial = /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password)
    const typesCount = [hasDigit, hasUpper, hasLower, hasSpecial].filter(Boolean).length

    return {
      minLength: password.length >= 8,
      hasDigit,
      hasUpper,
      hasLower,
      hasSpecial,
      typesCount,
      characterTypesValid: typesCount >= 3
    }
  })

  const clearError = (field: keyof typeof formErrors.value) => {
    formErrors.value[field] = ''
    submitError.value = ''
  }

  // Real-time username availability check
  const handleUsernameInput = () => {
    clearError('username')
    usernameAvailable.value = null

    if (usernameCheckTimeout) {
      clearTimeout(usernameCheckTimeout)
    }

    const username = signupForm.value.username
    if (username.length < 3) {
      return
    }

    usernameCheckTimeout = setTimeout(async () => {
      usernameChecking.value = true
      try {
        const response: any = await apiService.get(`${USERS.BASE}/check-username/${username}`)
        usernameAvailable.value = response.available
        if (!response.available) {
          formErrors.value.username = response.message
        }
      } catch (error) {
        console.error('Username check failed:', error)
      } finally {
        usernameChecking.value = false
      }
    }, 500) // Debounce 500ms
  }

  // Send OTP
  const sendOtp = async () => {
    sendingOtp.value = true
    submitError.value = ''
    formErrors.value.otp = ''

    try {
      const response: any = await apiService.post(`${USERS.BASE}/send-registration-otp`, {
        email: signupForm.value.email
      })

      otpToken.value = response.token
      otpSent.value = true
      otpCountdown.value = response.expires_in || 900

      // Start countdown
      if (countdownInterval) clearInterval(countdownInterval)
      countdownInterval = setInterval(() => {
        if (otpCountdown.value > 0) {
          otpCountdown.value--
        } else {
          if (countdownInterval) clearInterval(countdownInterval)
        }
      }, 1000)
    } catch (error: any) {
      console.error('Send OTP failed:', error)
      if (error?.response?.status === 409) {
        submitError.value = error.response?.data?.detail || '此電子郵件已被使用'
      } else {
        submitError.value = error.response?.data?.detail || '發送驗證碼失敗，請稍後再試'
      }
    } finally {
      sendingOtp.value = false
    }
  }

  const resendOtp = () => {
    otpSent.value = false
    otpCode.value = ''
    sendOtp()
  }

  // Verify OTP
  const verifyOtp = async () => {
    if (otpCode.value.length !== 6) {
      formErrors.value.otp = '請輸入 6 位數驗證碼'
      return
    }

    verifyingOtp.value = true
    formErrors.value.otp = ''

    try {
      const response: any = await apiService.post(
        `${USERS.BASE}/verify-registration-otp?token=${encodeURIComponent(otpToken.value)}&otp=${otpCode.value}`
      )

      if (response.success) {
        emailVerified.value = true
        verifiedToken.value = response.verified_token
        if (countdownInterval) clearInterval(countdownInterval)
      }
    } catch (error: any) {
      console.error('Verify OTP failed:', error)
      formErrors.value.otp = error.response?.data?.detail || '驗證碼錯誤'
    } finally {
      verifyingOtp.value = false
    }
  }

  const validateStep1 = (): boolean => {
    let isValid = true

    if (!signupForm.value.username || signupForm.value.username.length < 3) {
      formErrors.value.username = '帳號長度至少需要 3 個字元'
      isValid = false
    } else if (!/^[a-zA-Z0-9_]+$/.test(signupForm.value.username)) {
      formErrors.value.username = '帳號只能包含英文字母、數字和底線'
      isValid = false
    } else if (usernameAvailable.value === false) {
      formErrors.value.username = '此帳號已被使用'
      isValid = false
    }

    if (!signupForm.value.email) {
      formErrors.value.email = '請輸入電子郵件'
      isValid = false
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(signupForm.value.email)) {
      formErrors.value.email = '請輸入有效的電子郵件格式'
      isValid = false
    }

    if (!signupForm.value.full_name) {
      formErrors.value.full_name = '請輸入姓名'
      isValid = false
    }

    if (!signupForm.value.office_id) {
      formErrors.value.office_id = '請選擇所屬單位'
      isValid = false
    }

    if (!signupForm.value.department) {
      formErrors.value.department = '請輸入所屬部門/工作站'
      isValid = false
    }

    if (!signupForm.value.phone) {
      formErrors.value.phone = '請輸入聯絡電話'
      isValid = false
    }

    if (!signupForm.value.application_reason) {
      formErrors.value.application_reason = '請輸入申請原因說明'
      isValid = false
    }

    return isValid
  }

  const validateStep3 = (): boolean => {
    let isValid = true

    if (!signupForm.value.password) {
      formErrors.value.password = '請輸入密碼'
      isValid = false
    } else if (!passwordRequirements.value.minLength) {
      formErrors.value.password = '密碼長度至少需要 8 個字元'
      isValid = false
    } else if (!passwordRequirements.value.characterTypesValid) {
      formErrors.value.password = '密碼需符合以下 4 項中的至少 3 項：包含數字、包含英文大寫、包含英文小寫、包含特殊符號'
      isValid = false
    }

    if (!signupForm.value.confirmPassword) {
      formErrors.value.confirmPassword = '請再次輸入密碼'
      isValid = false
    } else if (signupForm.value.password !== signupForm.value.confirmPassword) {
      formErrors.value.confirmPassword = '兩次輸入的密碼不一致'
      isValid = false
    }

    return isValid
  }

  const handleNextOrSubmit = () => {
    if (currentStep.value === 1) {
      if (validateStep1()) {
        currentStep.value = 2
      }
    } else if (currentStep.value === 2) {
      if (emailVerified.value) {
        currentStep.value = 3
      }
    } else {
      handleSignup()
    }
  }

  const handlePrevStep = () => {
    if (currentStep.value > 1) {
      currentStep.value--
    }
  }

  const handleSignup = async () => {
    if (!validateStep3()) {
      return
    }

    if (!emailVerified.value || !verifiedToken.value) {
      submitError.value = '請先完成 Email 驗證'
      return
    }

    isSubmitting.value = true
    submitError.value = ''

    try {
      const payload = {
        username: signupForm.value.username,
        email: signupForm.value.email,
        full_name: signupForm.value.full_name,
        office_id: signupForm.value.office_id,
        department: signupForm.value.department,
        job_title: signupForm.value.job_title || null,
        phone: signupForm.value.phone,
        phone_ext: signupForm.value.phone_ext || null,
        mobile: signupForm.value.mobile || null,
        application_reason: signupForm.value.application_reason,
        password: signupForm.value.password,
        verified_token: verifiedToken.value
      }

      await apiService.post(USERS.BASE + '/register', payload)

      successMessage.value = '帳號申請已送出，請等待管理員審核。審核通過後將會寄送通知至您的電子郵件。'

      // Wait 3 seconds then redirect to login
      setTimeout(() => {
        router.push('/login')
      }, 3000)
    } catch (error: any) {
      console.error('Registration error:', error)

      if (error?.response?.status === 400) {
        submitError.value = error.response?.data?.detail || '申請資料有誤，請檢查後重新送出'
      } else if (error?.response?.status === 409) {
        submitError.value = error.response?.data?.detail || '帳號或電子郵件已被使用'
      } else if (error?.response?.data?.detail) {
        submitError.value = error.response.data.detail
      } else {
        submitError.value = '系統錯誤，請稍後再試'
      }
    } finally {
      isSubmitting.value = false
    }
  }

  const handleCancel = () => {
    if (countdownInterval) clearInterval(countdownInterval)
    router.push('/login')
  }

  const getStepButtonText = computed(() => {
    if (currentStep.value === 1) return '下一步'
    if (currentStep.value === 2) return '下一步'
    return '送出申請'
  })

  // Load offices on mount
  onMounted(async () => {
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

  // Cleanup on unmount
  onUnmounted(() => {
    if (countdownInterval) clearInterval(countdownInterval)
    if (usernameCheckTimeout) clearTimeout(usernameCheckTimeout)
  })

  // Watch dialog close
  watch(showDialog, (newVal) => {
    if (!newVal) {
      router.push('/login')
    }
  })
</script>

<style scoped>
  /* Background styling */
  .login-background {
    min-height: 100vh;
    background-size: cover;
    background-position: top left;
    background-repeat: no-repeat;
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
    }
    .header-logo {
      width: 35%;
    }
    .header-title {
      width: 50%;
    }
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

  /* Signup Dialog Styles */
  .signup-card {
    border-radius: 12px !important;
  }

  .signup-title {
    font-family: 'HunInn', sans-serif !important;
    font-size: 20pt !important;
    color: #333333;
  }

  /* Stepper Customization */
  :deep(.v-stepper) {
    box-shadow: none !important;
  }

  :deep(.v-stepper-header) {
    box-shadow: none !important;
  }

  :deep(.v-stepper-item__avatar.v-avatar) {
    background-color: #e0e0e0;
  }

  :deep(.v-stepper-item--selected .v-stepper-item__avatar.v-avatar),
  :deep(.v-stepper-item--complete .v-stepper-item__avatar.v-avatar) {
    background-color: #3ea0a3;
  }

  :deep(.v-stepper-item__title) {
    font-size: 0.9rem;
    font-weight: 600;
  }

  :deep(.v-stepper-item__subtitle) {
    font-size: 0.75rem;
  }

  /* Password Requirements */
  .password-requirements {
    background-color: #f5f5f5;
    padding: 12px;
    border-radius: 8px;
    font-size: 0.875rem;
  }

  .requirement {
    display: flex;
    align-items: center;
    gap: 8px;
    color: #666666;
    margin-bottom: 4px;
  }

  .requirement.met {
    color: #4caf50;
  }

  .requirement-header {
    font-weight: 500;
    color: #333333;
  }
</style>

<route lang="yaml">
  meta:
    layout: auth
</route>
