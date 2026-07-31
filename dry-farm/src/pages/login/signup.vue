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
      <v-card
        v-if="showSuccessPage"
        class="signup-card"
      >
        <v-card-text class="text-center pa-10">
          <v-icon
            color="success"
            size="64"
            class="mb-6"
          >
            mdi-check-circle-outline
          </v-icon>
          <div class="text-h6 mb-3">
            申請已送出
          </div>
          <div class="text-body-1 text-medium-emphasis mb-8">
            您的帳號申請已成功送出，請等待管理員審核。<br>
            審核結果將寄送至您的電子郵件。
          </div>
          <v-btn
            color="primary"
            variant="flat"
            @click="router.push('/login')"
          >
            返回登入頁
          </v-btn>
        </v-card-text>
      </v-card>

      <v-card
        v-else
        class="signup-card"
      >
        <v-card-title class="signup-title text-center pt-6">
          帳號申請
        </v-card-title>

        <v-card-text class="px-6 py-0">
          <v-stepper
            v-model="currentStep"
            :items="stepperItems"
            flat
            hide-actions
          >
            <!-- Step 1: All Info (except password) -->
            <template #[`item.1`]>
              <!-- Row 1: Username + Email -->
              <v-row
                no-gutters
                class="mb-2"
              >
                <v-col
                  cols="12"
                  md="6"
                  class="pr-md-2"
                >
                  <v-text-field
                    v-model="signupForm.username"
                    label="擬申請帳號 *"
                    placeholder="至少 3 個字元"
                    variant="outlined"
                    density="compact"
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
                </v-col>
                <v-col
                  cols="12"
                  md="6"
                  class="pl-md-2"
                >
                  <v-text-field
                    v-model="signupForm.email"
                    label="E-Mail *"
                    placeholder="請輸入電子郵件"
                    type="email"
                    variant="outlined"
                    density="compact"
                    :error-messages="formErrors.email"
                    :loading="emailChecking"
                    @input="handleEmailInput"
                  >
                    <template #append-inner>
                      <v-icon
                        v-if="emailAvailable === true"
                        color="success"
                        icon="mdi-check-circle"
                      />
                      <v-icon
                        v-else-if="emailAvailable === false"
                        color="error"
                        icon="mdi-close-circle"
                      />
                    </template>
                  </v-text-field>
                </v-col>
              </v-row>

              <!-- Row 2: 姓名 + 職稱 -->
              <v-row
                no-gutters
                class="mb-2"
              >
                <v-col
                  cols="12"
                  md="6"
                  class="pr-md-2"
                >
                  <v-text-field
                    v-model="signupForm.full_name"
                    label="姓名 *"
                    placeholder="請輸入您的姓名"
                    variant="outlined"
                    density="compact"
                    :error-messages="formErrors.full_name"
                    @input="clearError('full_name')"
                  />
                </v-col>
                <v-col
                  cols="12"
                  md="6"
                  class="pl-md-2"
                >
                  <v-text-field
                    v-model="signupForm.job_title"
                    label="職稱"
                    placeholder="選填"
                    variant="outlined"
                    density="compact"
                  />
                </v-col>
              </v-row>

              <!-- Row 3: 管理處 + 分處（v-if） + 工作站（v-if） — 同一 row，動態欄寬 -->
              <v-row
                no-gutters
                class="mb-2"
              >
                <v-col
                  cols="12"
                  :md="unitCols"
                  :class="{ 'pe-md-1': hasBranches || hasStations }"
                >
                  <v-select
                    v-model="signupForm.office_id"
                    label="所屬單位（管理處）*"
                    :items="offices"
                    item-title="title"
                    item-value="value"
                    variant="outlined"
                    density="compact"
                    :loading="isOfficesLoading"
                    :error-messages="formErrors.office_id"
                    @update:model-value="clearError('office_id')"
                  />
                </v-col>
                <v-col
                  v-if="hasBranches"
                  cols="12"
                  :md="unitCols"
                  :class="hasStations ? 'px-md-1' : 'ps-md-1'"
                >
                  <v-select
                    v-model="selectedBranchOffice"
                    :items="branchOffices"
                    label="分處"
                    item-title="title"
                    item-value="value"
                    variant="outlined"
                    density="compact"
                    clearable
                    hide-details
                    @update:model-value="clearError('department')"
                  />
                </v-col>
                <v-col
                  v-if="hasStations"
                  cols="12"
                  :md="unitCols"
                  class="ps-md-1"
                >
                  <v-select
                    v-model="selectedWorkStation"
                    :items="workStations"
                    label="工作站"
                    item-title="title"
                    item-value="value"
                    variant="outlined"
                    density="compact"
                    clearable
                    :disabled="hasBranches && !selectedBranchOffice"
                    :error-messages="formErrors.department"
                    @update:model-value="clearError('department')"
                  />
                  <div
                    v-if="!hasStations && formErrors.department"
                    class="text-error text-caption mt-1"
                  >
                    {{ formErrors.department }}
                  </div>
                </v-col>
              </v-row>

              <!-- Row 4: Phone + Extension + Mobile -->
              <v-row
                no-gutters
                class="mb-2"
              >
                <v-col
                  cols="12"
                  md="5"
                  class="pr-md-2"
                >
                  <v-text-field
                    v-model="signupForm.phone"
                    label="聯絡電話 *"
                    placeholder="例：02-12345678"
                    variant="outlined"
                    density="compact"
                    :error-messages="formErrors.phone"
                    @input="clearError('phone')"
                  />
                </v-col>
                <v-col
                  cols="4"
                  md="2"
                  class="px-md-1"
                >
                  <v-text-field
                    v-model="signupForm.phone_ext"
                    label="分機"
                    placeholder="選填"
                    variant="outlined"
                    density="compact"
                  />
                </v-col>
                <v-col
                  cols="8"
                  md="5"
                  class="pl-md-2"
                >
                  <v-text-field
                    v-model="signupForm.mobile"
                    label="手機"
                    placeholder="例：0912345678"
                    variant="outlined"
                    density="compact"
                  />
                </v-col>
              </v-row>

              <!-- Row 5: Application Reason -->
              <v-textarea
                v-model="signupForm.application_reason"
                label="申請原因說明 *"
                placeholder="請說明申請帳號的原因與用途"
                variant="outlined"
                density="compact"
                rows="2"
                auto-grow
                class="mb-2"
                :error-messages="formErrors.application_reason"
                @input="clearError('application_reason')"
              />
            </template>

            <!-- Step 2: Email OTP Verification -->
            <template #[`item.2`]>
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
            <template #[`item.3`]>
              <v-row
                no-gutters
                class="mb-2"
              >
                <v-col
                  cols="12"
                  md="6"
                  class="pr-md-2"
                >
                  <v-text-field
                    v-model="signupForm.password"
                    label="密碼 *"
                    placeholder="請輸入密碼"
                    :type="showPassword ? 'text' : 'password'"
                    variant="outlined"
                    density="compact"
                    :disabled="policyLoading || policyLoadError"
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
                </v-col>
                <v-col
                  cols="12"
                  md="6"
                  class="pl-md-2"
                >
                  <v-text-field
                    v-model="signupForm.confirmPassword"
                    label="確認密碼 *"
                    placeholder="請再次輸入密碼"
                    :type="showConfirmPassword ? 'text' : 'password'"
                    variant="outlined"
                    density="compact"
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
                </v-col>
              </v-row>

              <!-- Password Requirements - Compact Grid Layout -->
              <div class="password-requirements mb-2">
                <template v-if="policyLoading">
                  <div class="d-flex align-center text-grey text-caption py-1">
                    <v-progress-circular size="14" width="2" indeterminate class="mr-2" />
                    密碼規則載入中...
                  </div>
                </template>
                <template v-else-if="policyLoadError">
                  <div class="d-flex align-center text-error text-caption py-1">
                    <v-icon size="small" icon="mdi-alert-circle" class="mr-1" />
                    無法取得密碼規則，請重新整理頁面
                  </div>
                </template>
                <template v-else>
                  <div
                    class="requirement requirement-primary"
                    :class="{ met: passwordRequirements!.minLength }"
                  >
                    <v-icon
                      :icon="passwordRequirements!.minLength ? 'mdi-check-circle' : 'mdi-circle-outline'"
                      size="small"
                    />
                    {{ passwordRequirements!.labels.min_length }}
                  </div>
                  <div class="requirement-divider" />
                  <v-row
                    no-gutters
                    dense
                    class="mt-1"
                  >
                    <v-col
                      cols="6"
                      class="pr-1"
                    >
                      <div
                        class="requirement requirement-compact"
                        :class="{ met: passwordRequirements!.hasDigit }"
                      >
                        <v-icon
                          :icon="passwordRequirements!.hasDigit ? 'mdi-check-circle' : 'mdi-circle-outline'"
                          size="x-small"
                        />
                        {{ passwordRequirements!.labels.has_digit }}
                      </div>
                    </v-col>
                    <v-col
                      cols="6"
                      class="pl-1"
                    >
                      <div
                        class="requirement requirement-compact"
                        :class="{ met: passwordRequirements!.hasUpper }"
                      >
                        <v-icon
                          :icon="passwordRequirements!.hasUpper ? 'mdi-check-circle' : 'mdi-circle-outline'"
                          size="x-small"
                        />
                        {{ passwordRequirements!.labels.has_upper }}
                      </div>
                    </v-col>
                    <v-col
                      cols="6"
                      class="pr-1"
                    >
                      <div
                        class="requirement requirement-compact"
                        :class="{ met: passwordRequirements!.hasLower }"
                      >
                        <v-icon
                          :icon="passwordRequirements!.hasLower ? 'mdi-check-circle' : 'mdi-circle-outline'"
                          size="x-small"
                        />
                        {{ passwordRequirements!.labels.has_lower }}
                      </div>
                    </v-col>
                    <v-col
                      cols="6"
                      class="pl-1"
                    >
                      <div
                        class="requirement requirement-compact"
                        :class="{ met: passwordRequirements!.hasSpecial }"
                      >
                        <v-icon
                          :icon="passwordRequirements!.hasSpecial ? 'mdi-check-circle' : 'mdi-circle-outline'"
                          size="x-small"
                        />
                        {{ passwordRequirements!.labels.has_special }}
                      </div>
                    </v-col>
                  </v-row>
                  <div class="requirement-divider" />
                  <div
                    class="requirement requirement-summary"
                    :class="{ met: passwordRequirements!.characterTypesValid }"
                  >
                    <v-icon
                      :icon="passwordRequirements!.characterTypesValid ? 'mdi-check-circle' : 'mdi-circle-outline'"
                      size="small"
                    />
                    <strong>符合 {{ passwordRequirements!.typesCount }}/{{ passwordRequirements!.totalTypesCount }} 項（至少 {{ passwordPolicy!.required_types_count }} 項）</strong>
                  </div>
                </template>
              </div>
            </template>
          </v-stepper>

          <!-- Error Alert -->
          <v-alert
            v-if="submitError"
            type="error"
            variant="tonal"
            density="compact"
            class="mb-2"
          >
            {{ submitError }}
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
  import { USERS, OFFICES } from '@/services/api/endpoints'
  import { passwordPolicy, policyLoading, policyLoadError } from '@/services/passwordPolicyService'
  import { encryptPassword, generateNonce } from '@/utils/passwordEncryption'
  import { getServerPublicKey } from '@/services/authKeyService'

  const router = useRouter()
  const officesStore = useOfficesStore()

  const showDialog = ref(true)
  const currentStep = ref(1)
  const showPassword = ref(false)
  const showConfirmPassword = ref(false)
  const isSubmitting = ref(false)
  const isOfficesLoading = ref(false)
  const submitError = ref('')
  const showSuccessPage = ref(false)

  // Username real-time check
  const usernameChecking = ref(false)
  const usernameAvailable = ref<boolean | null>(null)
  let usernameCheckTimeout: ReturnType<typeof setTimeout> | null = null

  // Email real-time check
  const emailChecking = ref(false)
  const emailAvailable = ref<boolean | null>(null)
  let emailCheckTimeout: ReturnType<typeof setTimeout> | null = null

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

  // 排除 sentinel 虛擬項目（如「作業基金」id=-1），僅顯示真實 DB 單位
  const offices = computed(() => officesStore.items.filter(o => o.value !== -1))

  // 分處 + 工作站二級聯動（依賴 office_id）
  interface SelectOption { title: string; value: string }
  const selectedBranchOffice = ref<string | null>(null)
  const selectedWorkStation = ref<string | null>(null)
  const branchOffices = ref<SelectOption[]>([])
  const workStations = ref<SelectOption[]>([])
  const hasBranches = computed(() => branchOffices.value.length > 0)
  const hasStations = computed(() => workStations.value.length > 0)
  // 動態欄寬：管理處+分處+工作站三者平均分配同一 row
  const unitCols = computed(() => {
    const count = 1 + (hasBranches.value ? 1 : 0) + (hasStations.value ? 1 : 0)
    return 12 / count  // 12 / 6 / 4
  })

  const _loadBranches = async (officeId: number) => {
    try {
      const list = await apiService.get<Array<{code: string; name: string}>>(OFFICES.BRANCHES(officeId))
      branchOffices.value = list.map(b => ({ title: b.name, value: b.code }))
    } catch {
      branchOffices.value = []
    }
  }

  const _loadStations = async (officeId: number, branchCode?: string) => {
    try {
      const url = branchCode
        ? OFFICES.STATIONS_BY_BRANCH(officeId, branchCode)
        : OFFICES.STATIONS(officeId)
      const list = await apiService.get<Array<{code: string; name: string}>>(url)
      workStations.value = list.map(s => ({ title: s.name, value: s.code }))
    } catch {
      workStations.value = []
    }
  }

  watch(() => signupForm.value.office_id, async (officeId) => {
    selectedBranchOffice.value = null
    selectedWorkStation.value = null
    branchOffices.value = []
    workStations.value = []
    if (!officeId) return
    await _loadBranches(officeId)
    if (!hasBranches.value) await _loadStations(officeId)
  })

  watch(selectedBranchOffice, async (branchCode) => {
    selectedWorkStation.value = null
    workStations.value = []
    if (!branchCode || !signupForm.value.office_id) return
    await _loadStations(signupForm.value.office_id, branchCode)
  })

  const buildDepartmentPayload = (): string | null => {
    const data: Record<string, {code: string; name: string}> = {}
    if (selectedBranchOffice.value) {
      const b = branchOffices.value.find(x => x.value === selectedBranchOffice.value)
      if (b) data.branch = { code: b.value, name: b.title }
    }
    if (selectedWorkStation.value) {
      const s = workStations.value.find(x => x.value === selectedWorkStation.value)
      if (s) data.station = { code: s.value, name: s.title }
    }
    return Object.keys(data).length > 0 ? JSON.stringify(data) : null
  }

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
    const policy = passwordPolicy.value
    if (!policy) return null

    const password = signupForm.value.password
    const p = policy.char_type_patterns

    const hasDigit   = new RegExp(p.digit).test(password)
    const hasUpper   = new RegExp(p.upper).test(password)
    const hasLower   = new RegExp(p.lower).test(password)
    const hasSpecial = new RegExp(p.special).test(password)
    const typesCount = [hasDigit, hasUpper, hasLower, hasSpecial].filter(Boolean).length

    return {
      minLength: password.length >= policy.min_length,
      hasDigit,
      hasUpper,
      hasLower,
      hasSpecial,
      typesCount,
      totalTypesCount: policy.total_types_count,
      characterTypesValid: typesCount >= policy.required_types_count,
      labels: policy.labels,
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
        console.error('[handleUsernameInput] 帳號可用性檢查失敗:', error)
      } finally {
        usernameChecking.value = false
      }
    }, 500) // Debounce 500ms
  }

  // Real-time email availability check
  const handleEmailInput = () => {
    clearError('email')
    emailAvailable.value = null

    if (emailCheckTimeout) {
      clearTimeout(emailCheckTimeout)
    }

    const email = signupForm.value.email
    // Basic format check before API call
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailPattern.test(email)) {
      return
    }

    emailCheckTimeout = setTimeout(async () => {
      emailChecking.value = true
      try {
        const response: any = await apiService.get(`${USERS.BASE}/check-email/${encodeURIComponent(email)}`)
        emailAvailable.value = response.available
        if (!response.available) {
          formErrors.value.email = response.message
        }
      } catch (error) {
        console.error('[handleEmailInput] Email 可用性檢查失敗:', error)
      } finally {
        emailChecking.value = false
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
    } else if (emailAvailable.value === false) {
      formErrors.value.email = '此電子郵件已被使用'
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

    if ((hasBranches.value || hasStations.value) && !selectedBranchOffice.value && !selectedWorkStation.value) {
      formErrors.value.department = '請選擇分處或工作站'
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

    if (!passwordPolicy.value) {
      formErrors.value.password = '密碼規則尚未載入，請重新整理頁面'
      return false
    }
    if (!signupForm.value.password) {
      formErrors.value.password = '請輸入密碼'
      isValid = false
    } else if (!passwordRequirements.value!.minLength) {
      formErrors.value.password = passwordRequirements.value!.labels.min_length
      isValid = false
    } else if (!passwordRequirements.value!.characterTypesValid) {
      const policy = passwordPolicy.value
      const typeList = [
        policy.labels.has_digit,
        policy.labels.has_upper,
        policy.labels.has_lower,
        policy.labels.has_special,
      ].join('、')
      formErrors.value.password = `密碼需符合以下 ${policy.required_types_count} 項中的至少一項：${typeList}`
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
      const keyInfo = await getServerPublicKey()
      const { encrypted_password, encrypted_key, iv } = await encryptPassword(
        signupForm.value.password,
        keyInfo.publicKey,
      )

      const payload = {
        username: signupForm.value.username,
        email: signupForm.value.email,
        full_name: signupForm.value.full_name,
        office_id: signupForm.value.office_id,
        department: buildDepartmentPayload(),
        job_title: signupForm.value.job_title || null,
        phone: signupForm.value.phone,
        phone_ext: signupForm.value.phone_ext || null,
        mobile: signupForm.value.mobile || null,
        application_reason: signupForm.value.application_reason,
        verified_token: verifiedToken.value,
        encrypted_password,
        encrypted_key,
        iv,
        kid: keyInfo.kid,
        timestamp: Date.now(),
        nonce: generateNonce(),
      }

      await apiService.post(USERS.BASE + '/register', payload)

      showSuccessPage.value = true
    } catch (error: any) {
      showSuccessPage.value = false

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
        // ignore — offices will be empty, user sees no dropdown options
      } finally {
        isOfficesLoading.value = false
      }
    }
  })

  // Cleanup on unmount
  onUnmounted(() => {
    if (countdownInterval) clearInterval(countdownInterval)
    if (usernameCheckTimeout) clearTimeout(usernameCheckTimeout)
    if (emailCheckTimeout) clearTimeout(emailCheckTimeout)
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
    margin-bottom: 16px;
  }

  /* Fix overflow issue to prevent label clipping */
  :deep(.v-stepper-window) {
    overflow: visible !important;
    margin: 10 !important;
  }

  :deep(.v-stepper-window-item) {
    padding: 0 !important;
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
    padding: 10px 12px;
    border-radius: 8px;
    font-size: 0.8125rem;
  }

  .requirement {
    display: flex;
    align-items: center;
    gap: 6px;
    color: #666666;
    margin-bottom: 2px;
  }

  .requirement.met {
    color: #4caf50;
  }

  .requirement-primary {
    font-weight: 500;
    margin-bottom: 6px;
  }

  .requirement-compact {
    font-size: 0.75rem;
    gap: 4px;
  }

  .requirement-summary {
    font-weight: 500;
    margin-top: 6px;
  }

  .requirement-divider {
    height: 1px;
    background-color: #e0e0e0;
    margin: 6px 0;
  }
</style>

<route lang="yaml">
  meta:
    layout: auth
</route>
