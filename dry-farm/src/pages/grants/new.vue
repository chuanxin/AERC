<template>
  <v-container fluid class="grants-new-container px-6 pb-10 pt-0" style="background-color: white">
    <v-row justify="center">
      <v-col cols="10" lg="10" align-self="center" class="pt-8">
        <div class="section-wrapper">
          <v-card
            class="mx-auto section-card pt-4"
            variant="outlined"
            rounded="lg"
          >
            <v-card-item class="custom-title">
              <v-card-title class="text-h5 font-weight-black">
                建立新案件
              </v-card-title>
            </v-card-item>

            <v-card-text>
              <!-- 案件表單內容 -->
              <v-card class="content-card mb-0" rounded="lg" elevation="0">
                <step0
                  :case-number="caseNumber"
                  :form-data="formData"
                  @update-data="updateFormData"
                  @create-case="handleCreateCase"
                  @cancel="cancelForm"
                />
              </v-card>
            </v-card-text>
          </v-card>
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts" setup>
import { useDisplay } from 'vuetify'
import step0 from './components/step0.vue'

const appRouter = useRouter()
const route = useRoute()
const { name } = useDisplay()
const isSmallScreen = computed(() => name.value === 'xs' || name.value === 'sm')

const caseNumber = ref('');
const currentStep = ref(1);
const displayStep = ref(1);
const submitting = ref(false);

// 步驟定義
const steps = [
  { title: '申請人資料', value: 1, subtitle: '請填寫申請人資料完成立案' },
];

// 表單數據
const formData = reactive({
  applicantName: '',
  identityNumber: '',
  contactPhone: '',
  city: '',
  district: '',
  addressDetail: '',
  undertracker: '',
  managementOffice: '',
  valid: false
});

// 處理表單數據更新
const updateFormData = (data) => {
  Object.assign(formData, data);
};

// 處理表單取消
const cancelForm = () => {
  appRouter.push('/grants');
};

// 處理建立案件
const handleCreateCase = async (data) => {
  submitting.value = true;
  try {
    // 實際應用中應該調用 API 建立案件
    await new Promise(resolve => setTimeout(resolve, 1500)); // 模擬 API 請求
    const result = data;
    console.log('創建成功:', result);

    // 導航到編輯頁面
    appRouter.push({
      path: '/grants/edit',
      query: { id: result.projectId }
    });
  } catch (error) {
    console.error('創建失敗:', error);
  } finally {
    submitting.value = false;
  }
};

// 重置到步驟1並更新 URL
const resetToStep1 = () => {
  currentStep.value = 1;
  displayStep.value = 1;

  // 更新 URL 添加 step=1 參數
  appRouter.replace({
    query: { ...route.query, step: '1' }
  });
};

onMounted(() => {
  const stepParam = route.query.step;

  if (stepParam) {
    // 嘗試從 URL 參數獲取步驟值
    const stepValue = parseInt(stepParam as string, 10);
    // 確保步驟值有效
    if (!isNaN(stepValue) && stepValue >= 1 && stepValue <= steps.length) {
      currentStep.value = stepValue;
      displayStep.value = stepValue;
    } else {
      // 如果步驟值無效，重置為第一步
      resetToStep1();
    }
  } else {
    // 如果 URL 中沒有步驟參數，則重置為第一步
    resetToStep1();
  }

  // 嘗試從 localStorage 恢復表單數據
  const savedForms = localStorage.getItem('grantForms');
  if (savedForms) {
    try {
      const parsedForms = JSON.parse(savedForms);
      if (parsedForms.step1) {
        updateFormData(parsedForms.step1);
      }
    } catch (e) {
      console.error('無法解析已保存的表單數據', e);
    }
  }
});

watch(currentStep, (newStep) => {
  displayStep.value = newStep;

  // 更新 URL 查詢參數，但不重新加載頁面
  appRouter.replace({
    query: { ...route.query, step: newStep.toString() }
  });
});

// 監聽 displayStep 變化，更新 currentStep
watch(displayStep, (newStep) => {
  // 避免自動跳到最後一步，只允許前進或後退一步
  if (Math.abs(newStep - currentStep.value) <= 1) {
    currentStep.value = newStep;
  } else {
    // 如果步驟差距太大，重置為當前步驟
    nextTick(() => {
      displayStep.value = currentStep.value;
    });
  }
});
</script>

<style scoped>
/* 添加背景圖片樣式 */
.grants-new-container {
  background-image: url('@/assets/bg_index.svg');
  background-size: cover;
  background-position: center bottom;
  background-repeat: no-repeat;
  background-attachment: fixed;
  min-height: 100vh;
}

/* 區塊共通容器 */
.section-wrapper {
  padding: 8px 4px 0px 4px;
}

/* 卡片與標題樣式 */
.section-card {
  position: relative;
  margin: 24px 0;
  overflow: visible !important;
  border-top-left-radius: 0 !important;
  transition: all 0.3s ease;

  /* 毛玻璃效果 */
  background-color: rgba(255, 255, 255, 0.6) !important; /* 半透明白色背景 */
  backdrop-filter: blur(10px) !important; /* 背景模糊效果 */
  -webkit-backdrop-filter: blur(10px) !important; /* Safari 支持 */
  border: 1px solid rgba(255, 255, 255, 0.25) !important; /* 細微邊框增強玻璃感 */
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.05) !important; /* 柔和陰影增強玻璃感 */
}

.section-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08) !important;
  background-color: rgba(255, 255, 255, 0.85) !important; /* 懸停時略微增加不透明度 */
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
  /* padding: 0 16px !important; */
  background-color: #3ea0a3 !important;
  border-radius: 8px 8px 0 0;
  z-index: 1;
  transition: all 0.3s ease;
}

.v-card-title {
  color: white !important;
  display: flex;
  justify-content: flex-start;
  align-items: center;
  width: 100%;
  height: 100%;
  /* padding-left: 16px; */
}

/* 內容卡片樣式 */
.content-card {
  background-color: rgba(255, 255, 255, 0.7) !important;
  border: 1px solid rgba(62, 160, 163, 0.1);
  overflow: hidden;
}
</style>
