<template>
  <v-container
    fluid
    class="fill-height pa-0 background"
  >
    <v-col class="login-content-col">
      <v-img
        src="@/assets/logo-xl.png"
        cover
        width="350"
        min-width="350"
        class="mx-auto mb-5"
      />
      <v-sheet
        class="mx-auto sheet-container"
        max-width="380"
        min-width="340"

        rounded="xl"
        elevation="4"
      >
        <v-sheet
          class="pa-2 pb-0 text-right"
          rounded="t-xl"
        >
          <v-container fluid>
            <v-row>
              <v-col
                cols="12"
                class="pa-0"
              >
                <v-chip
                  :variant="activeForm === 'login' ? 'outlined' : 'text'"
                  :color="activeForm === 'login' ? 'primary' : undefined"
                  class="px-3 mb-2"
                  rounded="xl"
                  @click="activeForm = 'login'"
                >
                  我要登入
                </v-chip>

                <v-chip
                  :variant="activeForm === 'register' ? 'outlined' : 'text'"
                  :color="activeForm === 'register' ? 'primary' : undefined"
                  class="px-3 mb-2"
                  rounded="xl"
                  @click="activeForm = 'register'"
                >
                  我要註冊
                </v-chip>
              </v-col>
              <v-col
                cols="12"
                class="pa-0 ma-0 text-center"
              >
                <div class="text-h5 text-sm-h5">
                  <strong>推廣管路灌溉設施管理資料庫</strong>
                </div>
              </v-col>
            </v-row>
          </v-container>
        </v-sheet>
        <v-divider class="ma-0" />
        <div class="px-4">
          <!-- Form content -->
          <v-window
            v-model="activeForm"
            class="pa-4"
            direction="vertical"
            reverse
          >
            <!-- Login form -->
            <v-window-item value="login">
              <v-form
                id="loginForm"
                @submit.prevent="handleLogin"
              >
                <v-text-field
                  v-model="loginForm.account"
                  label="帳號"
                  prepend-inner-icon="mdi-account"
                  variant="outlined"
                  density="comfortable"
                  class="mt-0 mb-n5"
                />
                <div class="d-flex justify-end mt-0 pt-0">
                  <a
                    class="text-caption text-decoration-none text-blue forgot-password-link"
                    href="/password/reset"
                    rel="noopener noreferrer"
                    target="_blank"
                  >
                    忘記密碼?</a>
                </div>
                <v-text-field
                  v-model="loginForm.password"
                  label="密碼"
                  :type="showPassword ? 'text' : 'password'"
                  prepend-inner-icon="mdi-lock"
                  :append-inner-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
                  variant="outlined"
                  density="comfortable"
                  class="mb-0"
                  @click:append-inner="showPassword = !showPassword"
                />
                <!-- Add CAPTCHA field -->
                <div class="d-flex align-center mb-0">
                  <v-text-field
                    v-model="userCaptcha"
                    label="驗證碼"
                    prepend-inner-icon="mdi-shield-check"
                    variant="outlined"
                    density="comfortable"
                    :error="captchaError"
                    :error-messages="captchaError ? '驗證碼不正確' : ''"
                    class="flex-grow-1 mb-n2"
                  >
                    <template #append>
                      <v-btn
                        variant="text"
                        density="comfortable"
                        min-width="80"
                        class="font-weight-bold pa-0 ma-0 text-typography"
                        style="font-family: monospace;"
                        @click="generateCaptcha"
                      >
                        {{ captcha }}
                      </v-btn>
                    </template>
                  </v-text-field>
                </div>

                <div class="d-flex align-center justify-space-between ma-0 pa-0">
                  <v-checkbox
                    v-model="rememberMe"
                    label="記住登入資訊"
                    color="primary"
                    hide-details
                    class="mt-0"
                    density="compact"
                  />
                </div>
              </v-form>
            </v-window-item>

            <!-- Register form -->
            <v-window-item value="register">
              <v-stepper
                v-model="currentStep"
                flat
                class="no-transition"
              >
                <v-stepper-header
                  class="ma-0 pt-0 pl-0 pr-0 elevation-0"
                >
                  <v-stepper-item
                    value="1"
                    class="pb-0 pt-0 pl-0"
                  >
                    帳號設定
                  </v-stepper-item>
                  <v-divider />
                  <v-stepper-item
                    value="2"
                    class="pb-0 pt-0 pr-0"
                  >
                    基本資料
                  </v-stepper-item>
                </v-stepper-header>

                <v-stepper-window
                  v-model="currentStep"
                  class="pa-0 ma-0"
                >
                  <!-- Step 1 -->
                  <v-stepper-window-item value="1">
                    <v-form class="mt-6">
                      <v-text-field
                        v-model="registerForm.account"
                        label="帳號"
                        prepend-inner-icon="mdi-account"
                        variant="outlined"
                        density="comfortable"
                      />
                      <v-text-field
                        v-model="registerForm.password"
                        label="密碼"
                        :type="showPassword ? 'text' : 'password'"
                        prepend-inner-icon="mdi-lock"
                        :append-inner-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
                        variant="outlined"
                        density="comfortable"
                        @click:append-inner="showPassword = !showPassword"
                      />
                      <v-text-field
                        v-model="registerForm.confirmPassword"
                        label="確認密碼"
                        :type="showConfirmPassword ? 'text' : 'password'"
                        prepend-inner-icon="mdi-lock-check"
                        :append-inner-icon="showConfirmPassword ? 'mdi-eye' : 'mdi-eye-off'"
                        variant="outlined"
                        density="comfortable"
                        @click:append-inner="showConfirmPassword = !showConfirmPassword"
                      />
                    </v-form>
                  </v-stepper-window-item>

                  <!-- Step 2 -->
                  <v-stepper-window-item value="2">
                    <v-form class="mt-6">
                      <v-text-field
                        v-model="registerForm.name"
                        label="職員姓名"
                        prepend-inner-icon="mdi-account"
                        variant="outlined"
                        density="comfortable"
                      />
                      <v-select
                        v-model="registerForm.department"
                        :items="departments"
                        label="單位"
                        prepend-inner-icon="mdi-office-building"
                        variant="outlined"
                        density="comfortable"
                      >
                        <template #item="{ props, item }">
                          <v-list-item
                            v-bind="props"
                            :title="item.raw?.title"
                            :value="item.raw?.value"
                            :class="{ 'light-blue-text': item.raw?.classification == 2 }"
                          />
                        </template>
                        <!-- item
                              ├── title      // Extracted from your data for convenience
                              ├── value      // Extracted from your data for convenience
                              └── raw        // Your complete original object with all properties
                                  ├── title
                                  ├── value
                                  └── classification  // Your custom property -->
                      </v-select>
                    </v-form>
                  </v-stepper-window-item>
                </v-stepper-window>
              </v-stepper>
            </v-window-item>
          </v-window>
        </div>

        <v-divider />

        <div class="pa-0 ma-0">
          <v-btn
            v-if="currentStep === '2' && activeForm === 'register'"
            variant="text"
            class="mb-2"
            block
            @click="handleStep('prev')"
          >
            上一步
          </v-btn>
          <v-btn
            :type="activeForm === 'login' ? 'submit' : 'button'"
            color="#FF9C00"
            rounded="t-0 b-xl"
            size="x-large"
            :text="getButtonText"
            variant="flat"
            block
            :loading="isSubmitting"
            :disabled="isSubmitting"
            :form="activeForm === 'login' ? 'loginForm' : undefined"
            @click="activeForm === 'register' ? handleStep('next') : undefined"
          />
        </div>
        <v-alert
          v-if="errorMessage"
          type="error"
          variant="tonal"
          closable
          class="mb-4"
        >
          {{ errorMessage }}
        </v-alert>
      </v-sheet>

      <!-- Version info container with same width as v-sheet -->
      <div class="version-container">
        <div class="version-info-container">
          <v-chip
            size="default"
            color="primary"
            label
            rounded="md"
            class="text-body-2 font-weight-medium version-chip"
          >
            <v-icon
              start
              icon="mdi-tag-outline"
              size="small"
            />
            release v.{{ packageInfo.version }}
          </v-chip>
        </div>
      </div>
    </v-col>
  </v-container>
</template>

<script lang="ts" setup>
  import { useUserStore } from '@/stores/users'
  import { useOfficesStore } from '@/stores/offices'
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

  const captcha = ref('')
  const userCaptcha = ref('')
  const captchaError = ref(false)

  const errorMessage = ref('');
  const isSubmitting = ref(false);

  const generateCaptcha = () => {
    const characters = '0123456789'
    const length = 4
    let result = ''
    for (let i = 0; i < length; i++) {
      result += characters.charAt(Math.floor(Math.random() * characters.length))
    }
    captcha.value = result
    userCaptcha.value = '' // Clear user input
    captchaError.value = false // Reset error state
  }

  // Watch for user input changes to clear error state
  watch(userCaptcha, () => {
    if (captchaError.value) {
      captchaError.value = false
    }
  })

  // Generate initial CAPTCHA on component mount
  onMounted(async () => {
    collectEnvInfo()
    generateCaptcha()

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
    } else {
      addLog('Offices already loaded')
    }

    addLog('Component mounted - end')
    addLog(`Final testStep value: ${testStep.value} (type: ${typeof testStep.value})`)
    addLog(`Final currentStep value: ${currentStep.value} (type: ${typeof currentStep.value})`)

    // 使用 nextTick 確保所有響應式更新完成後再次檢查
    await nextTick()
    addLog('After nextTick:')
    addLog(`testStep value: ${testStep.value} (type: ${typeof testStep.value})`)
    addLog(`currentStep value: ${currentStep.value} (type: ${typeof currentStep.value})`)
  })

  const handleLogin = async () => {
    // try {
    //   if (userCaptcha.value !== captcha.value) {
    //     // console.log('Captcha value is:', captcha.value)
    //     captchaError.value = true
    //     return
    //   }
    //   // Add your login API call here
    //   console.log('Login attempted:', loginForm.value)

    //   // Simulate successful login
    //   await router.push('/')
    // } catch (error) {
    //   console.error('Login failed:', error)
    //   // Add error handling here
    // }
    try {
      // First clear any previous error
      errorMessage.value = ''

      // Validate captcha
      if (userCaptcha.value !== captcha.value) {
        captchaError.value = true
        return
      }

      // Reset error state
      captchaError.value = false

      // Ensure field names match backend expectations
      const loginData = {
        username: loginForm.value.account,
        password: loginForm.value.password
      }

      console.log('Attempting login, sending data:', loginData)

      // Call store login method
      const result = await userStore.login(loginData)

      console.log('Login result:', result ? 'success' : 'failure')

      if (result) {
        // If remember me is selected, set longer expiration
        if (rememberMe.value) {
          localStorage.setItem('remember_login', 'true')
        }

        // Navigate to the redirect path or home page
        await router.push(redirectPath.value)
      } else {
        // Show error message
        alert(userStore.error || '登入失敗，請檢查帳號和密碼')
      }
    } catch (error) {
      console.error('Error during login:', error)

      errorMessage.value = '登入時發生未知錯誤'

      if (error && typeof error === 'object') {
        // Handle Axios error types
        if ('response' in error && error.response && typeof error.response === 'object') {
          const response = error.response as { data?: { detail?: string } }
          if (response.data && response.data.detail) {
            errorMessage.value = response.data.detail
          }
        }
        // Handle standard Error types
        else if ('message' in error && typeof error.message === 'string') {
          errorMessage.value = error.message
        }
      }
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

  const currentStep = ref('1')
  const testStep = ref(1) // 測試用的 stepper

  // 添加調試相關的變量
  const initLogs = ref<string[]>([])
  const debugInfo = ref({
    nodeEnv: 'unknown',
    mode: 'unknown',
    ssr: 'unknown',
    client: 'unknown',
    dev: 'unknown',
    prod: 'unknown'
  })

  // 記錄初始化日誌的函數
  const addLog = (message: string) => {
    const timestamp = new Date().toISOString().split('T')[1].split('.')[0]
    initLogs.value.push(`[${timestamp}] ${message}`)
    console.log(`🔧 [${timestamp}] ${message}`)
  }

  // 收集環境信息
  const collectEnvInfo = () => {
    try {
      // 使用較安全的方式獲取環境變量
      const env = (window as any).__ENV__ || {}
      const globalProcess = (window as any).process || (globalThis as any).process || {}
      debugInfo.value = {
        nodeEnv: env.NODE_ENV || globalProcess?.env?.NODE_ENV || 'undefined',
        mode: env.MODE || 'undefined',
        ssr: env.SSR || 'undefined',
        client: String(!env.SSR) || 'undefined',
        dev: env.DEV || 'undefined',
        prod: env.PROD || 'undefined'
      }
      addLog(`Environment collected: ${JSON.stringify(debugInfo.value)}`)
    } catch (error) {
      addLog(`Error collecting env info: ${error}`)
    }
  }

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
      if (currentStep.value === '2') {
        handleRegistration()
        return
      }
      currentStep.value = (parseInt(currentStep.value) + 1).toString()
    } else {
      currentStep.value = (parseInt(currentStep.value) - 1).toString()
    }
  }

  const getButtonText = computed(() => {
    if (activeForm.value === 'login') return '登入'
    return currentStep.value === '1' ? '下一步' : '註冊'
  })

  // Watch for activeForm changes and reset currentStep when switching to register
  watch(activeForm, (newForm) => {
    if (newForm === 'register') {
      currentStep.value = '1'
    }
  })

  // Watch testStep changes for debugging
  watch(testStep, (newStep, oldStep) => {
    const changeInfo = {
      from: oldStep,
      to: newStep,
      newType: typeof newStep,
      oldType: typeof oldStep,
      timestamp: new Date().toISOString(),
      environment: (window as any)?.__VITE_ENV__?.MODE || 'unknown',
      userAgent: navigator.userAgent.substring(0, 50),
      vuetifyVersion: (window as any)?.$vuetify?.version || 'unknown'
    }
    console.log('🔍 Test Step Changed:', changeInfo)
    addLog(`testStep changed: ${oldStep} (${typeof oldStep}) -> ${newStep} (${typeof newStep})`)
  }, { immediate: true })

  // 添加對 v-stepper 內部值的監聽
  watch(() => testStep.value, (newVal) => {
    addLog(`testStep reactive value changed to: ${newVal} (${typeof newVal})`)
  })

  // Platform detection functions
  const getPlatformInfo = () => {
    const platform = navigator.platform || 'Unknown'
    const userAgent = navigator.userAgent

    if (userAgent.indexOf('Windows') !== -1) return `Windows (${platform})`
    if (userAgent.indexOf('Mac') !== -1) return `macOS (${platform})`
    if (userAgent.indexOf('Linux') !== -1) return `Linux (${platform})`
    return platform
  }

  const getBrowserInfo = () => {
    const userAgent = navigator.userAgent

    if (userAgent.indexOf('Chrome') !== -1 && userAgent.indexOf('Edg') === -1) return 'Chrome'
    if (userAgent.indexOf('Firefox') !== -1) return 'Firefox'
    if (userAgent.indexOf('Safari') !== -1 && userAgent.indexOf('Chrome') === -1) return 'Safari'
    if (userAgent.indexOf('Edg') !== -1) return 'Edge'
    return 'Unknown'
  }

  const getVueVersion = () => {
    // 嘗試獲取 Vue 版本
    try {
      return (window as any).Vue?.version || '3.x'
    } catch {
      return '3.x'
    }
  }
</script>

<style scoped>
  .background {
    background-image: url('@/assets/bg_login.svg');
    background-size: cover;
    background-position: fixed;
    background-color: rgba(255, 255, 255, 1);
    /* background-blend-mode: overlay; */
  }

  .login-content-col {
    margin-bottom: 120px !important; /* 固定底部間距 */
    padding-bottom: 60px; /* 額外內部間距 */
  }

  .sheet-container {
    position: relative; /* 為版本資訊定位提供相對定位基準 */
  }

  .version-container {
    width: 390px; /* 與 v-sheet 相同寬度 */
    margin: 0 auto; /* 置中對齊 */
    margin-top: 10px; /* 與 v-sheet 間距 */
  }

  .version-info-container {
    display: flex;
    justify-content: flex-end; /* 在容器內靠右對齊 */
    padding-right: 8px; /* 與 v-sheet 邊界保持一致 */
  }

  .version-chip {
    background: linear-gradient(135deg, #1976d2 0%, #1565c0 100%) !important;
    color: white !important;
    box-shadow: 0 3px 6px rgba(25, 118, 210, 0.3) !important;
    /* border-radius: 16px !important; */
    transition: all 0.3s ease;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
  }

  .version-chip .v-icon {
    margin-right: 4px;
  }

  /* Test container styles */
  .test-container {
    max-width: 100%;
    margin-bottom: 40px;
  }

  .test-info div {
    padding: 2px 0;
    font-family: monospace;
    font-size: 0.875rem;
  }

  .gap-2 > * + * {
    margin-left: 8px;
  }
  /* Disable all possible stepper transitions */
  :deep(.v-stepper) {
    .v-stepper-window__container,
    .v-window__container,
    .v-stepper-window-item,
    .v-window-item,
    .v-stepper-window-item--active,
    .v-window-item--active {
      transition: none !important;
    }
  }
  .forgot-password-link {
    position: relative;
    z-index: 999;
  }
  /* Add this new style for light blue items */
  .light-blue-text {
    color: #90CAF9 !important; /* Light blue color */
  }

  /* Optional: Add hover effect to maintain visibility on hover */
  .light-blue-text:hover {
    color: #64B5F6 !important; /* Slightly darker blue on hover */
  }
</style>

<route lang="yaml">
  meta:
    layout: auth
</route>
