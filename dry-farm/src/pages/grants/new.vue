<template>
  <v-container
    fluid
    class="grants-new-container px-6 pb-10 pt-0"
    style="background-color: white"
  >
    <!-- 建立案件進度對話框 - 移到父組件 -->
    <v-dialog
      v-model="isProcessing"
      persistent
      width="420"
      transition="dialog-transition"
    >
      <v-card
        class="pa-4 text-center"
        elevation="12"
        rounded="xl"
      >
        <v-card-text class="pa-8">
          <!-- 進度圓圈 -->
          <div class="mb-6">
            <v-progress-circular
              indeterminate
              color="#3ea0a3"
              size="90"
              width="8"
              class="mb-4"
            />
          </div>

          <!-- 主要訊息 -->
          <div class="text-h5 font-weight-bold mb-3 text-primary">
            正在建立案件
          </div>

          <!-- 副訊息 -->
          <div class="text-body-1 text-medium-emphasis mb-4">
            <span v-if="!currentCaseNumber">
              請稍候，系統正在取得新的案件編號
            </span>
            <span v-else>
              準備跳轉到編輯頁面，案件編號：<span class="font-weight-medium text-primary">{{ currentCaseNumber }}</span>
            </span>
          </div>

          <!-- 步驟指示 -->
          <!-- <div class="mb-4">
            <v-chip
              color="#3ea0a3"
              variant="flat"
              size="small"
              class="mx-1"
            >
              <v-icon
                start
                size="small"
              >
                mdi-check-circle
              </v-icon>
              驗證資料
            </v-chip>

            <v-chip
              color="#3ea0a3"
              variant="outlined"
              size="small"
              class="mx-1"
            >
              <v-progress-circular
                indeterminate
                size="12"
                width="2"
                class="mr-2"
              />
              建立案件
            </v-chip>
          </div> -->

          <!-- 安全提示 -->
          <!-- <v-chip
            color="success"
            variant="tonal"
            size="small"
            class="mt-2"
          >
            <v-icon
              start
              size="small"
            >
              mdi-shield-check
            </v-icon>
            安全傳輸
          </v-chip> -->
        </v-card-text>
      </v-card>
    </v-dialog>

    <v-row justify="center">
      <v-col
        cols="10"
        lg="10"
        align-self="center"
        class="pt-8"
      >
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
              <v-card
                class="content-card mb-0"
                rounded="lg"
                elevation="0"
              >
                <step0
                  @create:case="createCase"
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
import step0 from './components/step0.vue'
// import { useUserStore } from '@/stores/users'
import { useGrantsStore } from '@/stores/grants'
import { useRouter, useRoute } from 'vue-router'
import type { GrantCreateRequest } from '@/types/grantForms'

// const userStore = useUserStore()
const grantsStore = useGrantsStore()

const appRouter = useRouter()
const route = useRoute()

const currentStep = ref(1);
const displayStep = ref(1);
const submitting = ref(false);
const isProcessing = ref(false); // 進度對話框狀態
const currentCaseNumber = ref(''); // 當前建立的案件編號

// 步驟定義
// const steps = [
//   { title: '申請人資料', value: 1, subtitle: '請填寫申請人資料完成立案' },
// ];

// 初始表單數據函數
// const createInitialFormData = (): GrantCreateRequest => ({
//   name: '',
//   id: '',
//   phone: '',
//   county: '',
//   countyId: null,
//   town: '',
//   townId: null,
//   village: '',
//   villageId: null,
//   address: '',
//   undertracker: '',
//   office: userStore.currentUser?.office?.name || '',
//   officeId: userStore.currentUser?.office?.id || null,
//   valid: false
// });

// const formData = reactive<GrantCreateRequest>(createInitialFormData());

const createCase = async (data: GrantCreateRequest) => {
  try {
    console.log('🚀 [new.vue] 開始建立案件流程');

    // 開始顯示進度對話框
    isProcessing.value = true;
    currentCaseNumber.value = ''; // 清空之前的案件編號

    // 呼叫 store 建立專案
    const result = await grantsStore.createProject(data);

    // 處理建立案件邏輯
    await handleCreateCase({ caseNumber: result.case_number });

  } catch (error) {
    console.error('❌ [new.vue] 建立案件失敗:', error);

    // 關閉進度指示器並清空案件編號
    isProcessing.value = false;
    currentCaseNumber.value = '';

    // 可以在這裡顯示錯誤提示給使用者
    throw error; // 重新拋出錯誤讓上層處理
  }
};

// 處理建立案件
const handleCreateCase = async (data: { caseNumber: string }) => {
  submitting.value = true;
  try {
    // 短暫延遲讓使用者看到成功狀態，然後跳轉
    await new Promise(resolve => setTimeout(resolve, 3000));
    // 設置當前案件編號用於顯示
    currentCaseNumber.value = data.caseNumber;

    // 設置路由監聽器來確保導航完成
    const unwatch = appRouter.afterEach(async (to) => {
      // 檢查是否是我們要導航到的目標頁面
      if (to.path === '/grants/edit' && to.query.id === data.caseNumber) {
        // 使用 nextTick 確保 DOM 完全更新
        await nextTick();

        // 再等待一點時間確保新頁面組件已掛載
        setTimeout(() => {
          isProcessing.value = false;
          // 移除監聽器
          unwatch();
        }, 500);
      }
    });

    // 導航到編輯頁面
    try {
      await appRouter.push({
        path: '/grants/edit',
        query: { id: data.caseNumber }
      });
      console.log('[new.vue] 路由 push 操作完成');
    } catch (navError) {
      console.error('[new.vue] 導航失敗:', navError);
      // 如果導航失敗，移除監聽器並關閉進度指示器
      unwatch();
      isProcessing.value = false;
      currentCaseNumber.value = '';
      throw navError;
    }

  } catch (error) {
    console.error('創建失敗:', error);
    // 錯誤時也要關閉進度指示器並清空案件編號
    isProcessing.value = false;
    currentCaseNumber.value = '';
  } finally {
    submitting.value = false;
  }
};

// 重置到步驟1並更新 URL
// const resetToStep1 = () => {
//   currentStep.value = 1;
//   displayStep.value = 1;

//   // 更新 URL 添加 step=1 參數
//   appRouter.replace({
//     query: { ...route.query, step: '1' }
//   });
// };

onMounted(() => {
  // const stepParam = route.query.step;

  // if (stepParam) {
  //   // 嘗試從 URL 參數獲取步驟值
  //   const stepValue = parseInt(stepParam as string, 10);
  //   // 確保步驟值有效
  //   if (!isNaN(stepValue) && stepValue >= 1 && stepValue <= steps.length) {
  //     currentStep.value = stepValue;
  //     displayStep.value = stepValue;
  //   } else {
  //     // 如果步驟值無效，重置為第一步
  //     resetToStep1();
  //   }
  // } else {
  //   // 如果 URL 中沒有步驟參數，則重置為第一步
  //   resetToStep1();
  // }

  // 嘗試從 localStorage 恢復表單數據
  // const savedForms = localStorage.getItem('grantForms');
  // if (savedForms) {
  //   try {
  //     const parsedForms = JSON.parse(savedForms);
  //     if (parsedForms.step1) {
  //       Object.assign(formData, parsedForms.step1);
  //     }
  //   } catch (e) {
  //     console.error('無法解析已保存的表單數據', e);
  //   }
  // }
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
