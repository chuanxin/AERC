<template>
  <v-container
    fluid
    class="fill-height bg-light pa-0 background"
  >
    <v-col>
      <v-img
        src="@/assets/logo-xl.png"
        cover
        width="350"
        min-width="350"
        class="mx-auto mb-5"
      />
      <v-sheet
        class="mx-auto"
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
                  登入
                </v-chip>

                <v-chip
                  :variant="activeForm === 'register' ? 'outlined' : 'text'"
                  :color="activeForm === 'register' ? 'primary' : undefined"
                  class="px-3 mb-2"
                  rounded="xl"
                  @click="activeForm = 'register'"
                >
                  註冊
                </v-chip>
              </v-col>
              <v-col
                cols="12"
                class="pa-0 ma-0 text-center"
              >
                <div class="text-h6 text-sm-h5">
                  推廣管路灌溉設施管理資訊系統
                </div>
              </v-col>
            </v-row>
          </v-container>
        </v-sheet>
        <v-divider class="ma-0" />
        <div class="pa-4">
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
                  <v-stepper-window-item value="0">
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
                  <v-stepper-window-item value="1">
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
                      />
                    </v-form>
                  </v-stepper-window-item>
                </v-stepper-window>
              </v-stepper>
            </v-window-item>
          </v-window>
        </div>

        <v-divider />

        <div class="pa-0">
          <v-btn
            v-if="currentStep === 1 && activeForm === 'register'"
            variant="text"
            class="mb-2"
            block
            @click="handleStep('prev')"
          >
            上一步
          </v-btn>
          <v-btn
            :type="activeForm === 'login' ? 'submit' : 'button'"
            color="secondary-darken"
            rounded="t-0 b-xl"
            size="x-large"
            :text="getButtonText"
            variant="flat"
            block
            :form="activeForm === 'login' ? 'loginForm' : undefined"
            @click="activeForm === 'register' ? handleStep('next') : undefined"
          />
        </div>
      </v-sheet>
    </v-col>
  </v-container>
</template>

<script lang="ts" setup>
  const router = useRouter()
  const activeForm = ref('login')
  const showPassword = ref(false)
  const showConfirmPassword = ref(false)
  const rememberMe = ref(false)

  const captcha = ref('')
  const userCaptcha = ref('')
  const captchaError = ref(false)

  const generateCaptcha = () => {
    const characters = '23456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    const length = 6
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
  onMounted(() => {
    generateCaptcha()
  })

  const handleLogin = async () => {
    try {
      if (userCaptcha.value !== captcha.value) {
        // console.log('Captcha value is:', captcha.value)
        captchaError.value = true
        return
      }
      // Add your login API call here
      console.log('Login attempted:', loginForm.value)

      // Simulate successful login
      await router.push('/')
    } catch (error) {
      console.error('Login failed:', error)
      // Add error handling here
    }
  }
  // const handleForgotPassword = () => {
  //   // Add your forgot password logic here
  //   console.log('Forgot password clicked')
  // }
  const handleRegistration = () => {
    // Add your registration logic here
    console.log('Registration submitted:', registerForm.value)
  }

  const currentStep = ref(0)
  const loginForm = ref({
    account: '',
    password: ''
  })
  const registerForm = ref({
    account: '',
    password: '',
    confirmPassword: '',
    name: '',
    department: ''
  })

  const departments = [
    '農工中心',
    '農試所',
    '林試所'
  ]

  const handleStep = (direction: 'next' | 'prev') => {
    if (direction === 'next') {
      if (currentStep.value === 1) {
        handleRegistration()
        return
      }
      currentStep.value++
    } else {
      currentStep.value--
    }
  }

  const getButtonText = computed(() => {
    if (activeForm.value === 'login') return '登入'
    return currentStep.value === 0 ? '下一步' : '註冊'
  })
</script>

<style scoped>
  .background {
    background-image: url('@/assets/bg_login.jpg');
    background-size: cover;
    background-position: fixed;
    background-color: rgba(255, 255, 255, 0.2);  /* 白色半透明遮罩 */
    background-blend-mode: overlay;
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
</style>

<route lang="yaml">
  meta:
    layout: auth
</route>
