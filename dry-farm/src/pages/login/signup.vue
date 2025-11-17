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
      max-width="500"
      persistent
    >
      <v-card class="signup-card">
        <v-card-title class="signup-title text-center pt-6">
          帳號申請
        </v-card-title>

        <v-card-text class="px-6">
          <v-form
            ref="formRef"
            @submit.prevent="handleSignup"
          >
            <!-- Step 1: Basic Info -->
            <div v-if="currentStep === 1">
              <v-text-field
                v-model="signupForm.username"
                label="帳號"
                placeholder="請輸入帳號（至少 3 個字元）"
                variant="outlined"
                density="comfortable"
                class="mb-3"
                :error-messages="formErrors.username"
                @input="clearError('username')"
              />

              <v-text-field
                v-model="signupForm.email"
                label="電子郵件"
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
                label="姓名"
                placeholder="請輸入您的姓名"
                variant="outlined"
                density="comfortable"
                class="mb-3"
                :error-messages="formErrors.full_name"
                @input="clearError('full_name')"
              />

              <v-select
                v-model="signupForm.office_id"
                label="所屬單位"
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
            </div>

            <!-- Step 2: Password -->
            <div v-if="currentStep === 2">
              <v-text-field
                v-model="signupForm.password"
                label="密碼"
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
                label="確認密碼"
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
            </div>

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
          </v-form>
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
            v-if="currentStep === 2"
            variant="text"
            @click="currentStep = 1"
          >
            上一步
          </v-btn>
          <v-btn
            color="primary"
            variant="flat"
            :loading="isSubmitting"
            :disabled="isSubmitting"
            @click="handleNextOrSubmit"
          >
            {{ currentStep === 1 ? '下一步' : '送出申請' }}
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
  import { USERS } from '@/services/api/endpoints'

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

  const signupForm = ref({
    username: '',
    email: '',
    full_name: '',
    office_id: null as number | null,
    password: '',
    confirmPassword: ''
  })

  const formErrors = ref({
    username: '',
    email: '',
    full_name: '',
    office_id: '',
    password: '',
    confirmPassword: ''
  })

  const offices = computed(() => officesStore.items)

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

  const validateStep1 = (): boolean => {
    let isValid = true

    if (!signupForm.value.username || signupForm.value.username.length < 3) {
      formErrors.value.username = '帳號長度至少需要 3 個字元'
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

    return isValid
  }

  const validateStep2 = (): boolean => {
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
    } else {
      handleSignup()
    }
  }

  const handleSignup = async () => {
    if (!validateStep2()) {
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
        password: signupForm.value.password
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
    router.push('/login')
  }

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

  // Watch dialog close
  watch(showDialog, (newVal) => {
    if (!newVal) {
      router.push('/login')
    }
  })
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

  /* ============================================== */
  /* Signup Dialog Styles */
  /* ============================================== */
  .signup-card {
    border-radius: 12px !important;
  }

  .signup-title {
    font-family: 'HunInn', sans-serif !important;
    font-size: 20pt !important;
    color: #333333;
  }

  /* ============================================== */
  /* Password Requirements */
  /* ============================================== */
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
