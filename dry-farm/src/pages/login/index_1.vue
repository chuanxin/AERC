<template>
  <v-container
    fluid
    class="fill-height pa-0"
  >
    <!-- 頁面背景 -->
    <div class="login-background">
      <!-- 頂部標識區域 -->
      <div class="header-section text-center pt-6 mb-2">
        <v-img
          src="@/assets/logo-xl.png"
          width="320"
          min-width="320"
          class="mx-auto mb-0"
        />
        <h4 class="text-h5 font-weight-black pb-0">推廣管路灌溉設施管理資料庫</h4>
      </div>

      <!-- 登入表單區域 -->
      <v-card
        class="login-card mx-auto pa-0 ma-0 bg-transparent"
        max-width="320"
        rounded="0"
        elevation="0"
      >
        <v-form @submit.prevent="handleLogin">
          <!-- 帳號 -->
          <div class="input-group mb-2">
            <div class="label-container">
              <span class="input-label">帳號</span>
            </div>
            <v-text-field
              v-model="loginForm.account"
              placeholder="請輸入您的帳號"
              variant="outlined"
              rounded="lg"
              hide-details
              density="compact"
              class="login-input"
              bg-color="white"
            />
          </div>

          <!-- 密碼 -->
          <div class="input-group mb-2">
            <div class="label-container">
              <span class="input-label">密碼</span>
            </div>
            <v-text-field
              v-model="loginForm.password"
              :type="showPassword ? 'text' : 'password'"
              placeholder="請輸入您的密碼"
              variant="outlined"
              rounded="lg"
              hide-details
              density="compact"
              class="login-input"
              bg-color="white"
              :append-inner-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
              @click:append-inner="showPassword = !showPassword"
            />
          </div>

          <!-- 驗證碼 -->
          <div class="input-group">
            <div class="label-container">
              <span class="input-label">圖形驗證碼</span>
            </div>
            <div class="captcha-container">
              <v-text-field
                v-model="userCaptcha"
                placeholder="請輸入圖形驗證碼"
                variant="outlined"
                rounded="lg"
                hide-details
                density="compact"
                class="captcha-input"
                bg-color="white"
                :error="captchaError"
              />
              <div class="captcha-image" @click="generateCaptcha">
                <!-- <img :src="captchaImageUrl" alt="驗證碼" class="captcha-img"> -->
                {{ captcha }}
              </div>
            </div>
          </div>

          <!-- 登入按鈕 -->
          <v-btn
            type="submit"
            color="#5BC2C1"
            size="large"
            to="/"
            class="login-button mt-6 text-white"
            block
            :loading="loading"
          >
            登入
          </v-btn>
        </v-form>
      </v-card>
    </div>
  </v-container>
</template>

<script lang="ts" setup>
import { ref, onMounted, watch } from 'vue';

const router = useRouter();
const showPassword = ref(false);
const loading = ref(false);
const userCaptcha = ref('');
const captchaError = ref(false);
const captchaImageUrl = ref('');
const captcha = ref('')

// 模擬表單資料
const loginForm = ref({
  account: '',
  password: ''
});

// 生成驗證碼（這裡使用實際圖片URL代替文字，您需要後端支援）
// const generateCaptcha = () => {
//   // 模擬驗證碼圖片URL
//   // 實際應用中，這應該是來自後端API的圖片URL
//   captchaImageUrl.value = 'https://via.placeholder.com/150x50/E3F2FD/2196F3?text=' + Math.floor(Math.random() * 10000);
//   userCaptcha.value = ''; // 清空用戶輸入
//   captchaError.value = false; // 重置錯誤狀態
// };

const generateCaptcha = () => {
  const characters = '1234567890'
  const length = 4
  let result = ''
  for (let i = 0; i < length; i++) {
    result += characters.charAt(Math.floor(Math.random() * characters.length))
  }
  captcha.value = result
  userCaptcha.value = '' // Clear user input
  captchaError.value = false // Reset error state
}

// 處理登入
const handleLogin = async () => {
  if (!loginForm.value.account || !loginForm.value.password || !userCaptcha.value) {
    return;
  }

  loading.value = true;

  try {
    // 模擬API請求延遲
    await new Promise(resolve => setTimeout(resolve, 1000));

    // 實際應用中，這裡應該調用登入API
    console.log('登入請求參數:', {
      account: loginForm.value.account,
      password: loginForm.value.password,
      captcha: userCaptcha.value
    });

    // 模擬導航到首頁
    await router.push('/');

  } catch (error) {
    console.error('登入失敗:', error);
    // 處理錯誤
  } finally {
    loading.value = false;
  }
};

// 監聽用戶輸入以清除錯誤狀態
watch(userCaptcha, () => {
  if (captchaError.value) {
    captchaError.value = false;
  }
});

// 組件掛載時生成驗證碼
onMounted(() => {
  generateCaptcha();
});
</script>

<style scoped>
.login-background {
  width: 100%;
  min-height: 100vh;
  /* background-image: linear-gradient(to bottom, #c5effe 0%, #bbeaf5 30%, #a2e1b9 100%); */
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 30px;
  background-image: url('@/assets/bg_login.jpg');
  background-size: cover;
  background-position: fixed;
  background-color: rgba(255, 255, 255, 0.2);  /* 白色半透明遮罩 */
  background-blend-mode: overlay;
}

.header-section h4 {
  font-weight: 1000 !important;
  margin-bottom: 10px;
}

.login-card {
  width: 100%;
  max-width: 450px;
}

.input-group {
  margin-bottom: 20px;
}

.label-container {
  margin-bottom: 8px;
}

.input-label {
  font-size: 16px;
  font-weight: 1000;
  /* font-weight: bold; */
  /* color: #333; */
}

.login-input {
  width: 100%;
}

.captcha-container {
  display: flex;
  gap: 10px;
}

.captcha-image {
  min-width: 150px;
  background-color: white;
  border: 1px solid rgba(0, 0, 0, 0.23);
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  overflow: hidden;
}

.captcha-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.login-button {
  height: 50px;
  font-weight: bold;
  font-size: 18px;
  text-transform: none;
}

.text-white {
  color: white !important;
}

/* 響應式調整 */
@media (max-width: 600px) {
  .login-card {
    width: 90%;
  }

  .captcha-container {
    flex-direction: column;
  }

  .captcha-image {
    width: 100%;
    height: 50px;
  }
}
</style>

<route lang="yaml">
  meta:
    layout: auth
</route>
