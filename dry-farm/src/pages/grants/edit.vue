<template>
  <v-container  class="pt-0">
    <v-snackbar
      timeout="-1"
      v-model="isSnackbarVisible"
      variant="plain"
      class="ma-0 pa-0"
      max-width="1200"
      location="bottom"
      vertical
    >
      <v-card class="ma-0 pa-0">
        <v-stepper
          v-model="displayStep"
          flat
          editable
          :mobile="isSmallScreen"
          max-height="50"
        >
          <v-stepper-header>
            <template v-for="step in steps" :key="step.value">
              <v-stepper-item
                :value="step.value"
                :title="step.title"
                class="pa-3 ml-3 mr-3"
                rounded="lg"
                :ripple="false"
              >
              </v-stepper-item>
              <v-divider v-if="step.value > 0 && step.value < 8"></v-divider>
            </template>
          </v-stepper-header>
        </v-stepper>
      </v-card>
    </v-snackbar>

    <div ref="stepperContainer">
      <v-stepper-vertical
        v-model="currentStep"
        hide-actions
      >
        <template v-for="step in steps" :key="step.value">
          <v-stepper-vertical-item
            :complete=" currentStep > step.value"
            :step="`Step {{ step.value }}`"
            :value="step.value"
            editable
          >
              <template #icon>
                <v-icon size="24">
                  {{ currentStep > step.value ? 'mdi-check-circle' : 'mdi-circle-outline' }}
                  {{ currentStep === step.value ? 'mdi-circle' : '' }}
                  {{ currentStep < step.value ? 'mdi-circle-outline' : '' }}
                  {{ currentStep === step.value && !submitting ? 'mdi-circle' : '' }}
                  {{ submitting ? 'mdi-loading' : '' }}
                </v-icon>
              </template>
            <template #subtitle>
              <div class="d-flex align-center">
                <span
                  :class="[
                    'text-body-1',
                    currentStep === step.value ? 'text-primary font-weight-bold' : 'text-medium-emphasis'
                  ]"
                >
                  {{ step.subtitle }}
                </span>
                <v-icon
                  v-if="currentStep === step.value"
                  color="primary"
                  size="small"
                  class="ms-2"
                >
                  mdi-arrow-right
                </v-icon>
              </div>
            </template>
            <step1 v-if="step.value === 1" :formData="forms.step1" />
            <step2 v-if="step.value === 2" :formData="forms.step2" />
            <step3 v-if="step.value === 3" :formData="forms.step3" />
            <step4 v-if="step.value === 4" :formData="forms.step4" />
            <step5 v-if="step.value === 5" :formData="forms.step5" />
            <step6 v-if="step.value === 6" :formData="forms.step6" />
            <step7 v-if="step.value === 7" :formData="forms.step7" />
            <step8 v-if="step.value === 8" :formData="forms.step8" />
          </v-stepper-vertical-item>
        </template>
      </v-stepper-vertical>
    </div>
  </v-container>
</template>

<script lang="ts" setup>
import { useDisplay } from 'vuetify'
import { VStepperVerticalItem } from 'vuetify/labs/VStepperVertical'
import step1 from './components/step1.vue'
import step2 from './components/step2.vue'
import step3 from './components/step3.vue'
import step4 from './components/step4.vue'
import step5 from './components/step5.vue'
import step6 from './components/step6.vue'
import step7 from './components/step7.vue'
import step8 from './components/step8.vue'

const appRouter = useRouter()
const route = useRoute()
const { name } = useDisplay()
const isSmallScreen = computed(() => name.value === 'xs' || name.value === 'sm')

const currentStep = ref(1)
const isSnackbarVisible = ref(true)
const displayStep = ref(1)

const submitting = ref(false)

// Ensure this is the only declaration of `steps`
const steps = [
  { title: '申請人資料', value: 1 , subtitle: '申請人資料' },
  { title: '土地資料', value: 2, subtitle: '請填寫土地資料' },
  { title: '灌溉調控設施', value: 3, subtitle: '請填寫灌溉調控設施' },
  { title: '田間管路', value: 4, subtitle: '請填寫田間管路' },
  { title: '現場勘查', value: 5, subtitle: '請填寫現場勘查' },
  { title: '補助申請資料', value: 6, subtitle: '請填寫補助申請資料' },
  { title: '變更設計及結案申報', value: 7, subtitle: '請填寫變更設計及結案申報' },
  { title: '佐證及相關文件上傳', value: 8, subtitle: '請上傳佐證及相關文件' }
]
// 定義表單數據的類型
interface Step1Form {
  valid: boolean
  name: string
  id: string
  phone: string
  address: string
  manager: string
}

interface Step2Form {
  valid: boolean
  landData: any[] // Replace `any` with a more specific type if available
}

// ... 定義其他步驟的表單數據類型

interface Forms {
  step1: Step1Form
  step2: Step2Form
  // ... 其他步驟的表單數據
}

// 定義步驟的類型
interface Step {
  title: string
  value: number
}

// 定義表單參考的類型
interface FormRef {
  validate: () => Promise<{ valid: boolean }>
}

// 定義文件上傳的驗證規則類型
type Rule = (value: any) => boolean | string

// 表單數據
const forms: Forms = reactive({
  step1: { valid: false, name: '', id: '', phone: '', address: '', manager: '' },
  step2: { valid: false, landData: [] },
  // ... 其他步驟的表單數據
})

// 表單驗證規則
const nameRules = [(v: any) => !!v || '請填寫申請人姓名']
const idRules = [(v: any) => !!v || '請填寫身分證字號', (v: string) => /^[A-Z][12]\d{8}$/.test(v) || '身分證字號格式不正確']
// ... 其他驗證規則

// 表單參考
const form1 = ref(null)
// ... 其他表單參考


// 保存步驟數據
// const saveStepData = async (step) => {
//   // 將相應步驟的數據發送到後端
//   // return axios.post(`/api/grants/new/step${step}`, forms[`step${step}`])
// }

// 提交整個表單
const submitForm = async () => {
  submitting.value = true
  try {
    // 提交完整的申請
    // await axios.post('/api/grants/new/submit', forms)
    // 成功後導航
    appRouter.push('/grants')
  } catch (error) {
    // 處理錯誤
  } finally {
    submitting.value = false
  }
}

// 檢查是否有未保存的更改
const hasUnsavedChanges = computed(() => {
  // 比較當前表單數據與保存的表單數據
  const savedForms = localStorage.getItem('grantForms')
  if (savedForms) {
    try {
      const parsedForms = JSON.parse(savedForms)
      return JSON.stringify(forms) !== JSON.stringify(parsedForms)
    } catch (e) {
      console.error('無法解析已保存的表單數據', e)
    }
  }
  return false
})

// onBeforeRouteLeave((to, from, next) => {
//   // 檢查是否有未保存的變更
//   if (hasUnsavedChanges.value) {
//     const answer = window.confirm('您有未保存的更改，確定要離開嗎？')
//     if (answer) {
//       next()
//     } else {
//       next(false)
//     }
//   } else {
//     next()
//   }
// })

// 初始化時從 URL 讀取步驟
onMounted(() => {
  const stepParam = route.query.step

  if (stepParam) {
    // 嘗試從 URL 參數獲取步驟值
    const stepValue = parseInt(stepParam as string, 10)
    // 確保步驟值有效
    if (!isNaN(stepValue) && stepValue >= 1 && stepValue <= steps.length) {
      currentStep.value = stepValue
      displayStep.value = stepValue
    } else {
      // 如果步驟值無效，重置為第一步
      currentStep.value = 1
      displayStep.value = 1
      resetToStep1()
    }
  } else {
    // 如果 URL 中沒有步驟參數，則重置為第一步
    currentStep.value = 1
    displayStep.value = 1
    resetToStep1()
  }
  // 嘗試從 localStorage 恢復表單數據
  const savedForms = localStorage.getItem('grantForms')
  if (savedForms) {
    try {
      const parsedForms = JSON.parse(savedForms)
      Object.assign(forms, parsedForms)
    } catch (e) {
      console.error('無法解析已保存的表單數據', e)
    }
  }
})

// 重置到步驟1並更新 URL
const resetToStep1 = () => {
  currentStep.value = 1
  displayStep.value = 1

  // 更新 URL 添加 step=1 參數
  appRouter.replace({
    query: { ...route.query, step: '1' }
  })
}

// 父組件中添加滾動方法
const scrollToActiveStep = () => {
  // 給渲染 DOM 一點時間
  nextTick(() => {
    // 查找當前活動步驟的元素
    const activeStepElement = document.querySelector(`.step-${currentStep.value}`);

    if (activeStepElement) {
      // 計算要滾動到的位置 (考慮頁面頂部的固定元素高度)
      const headerOffset = 70; // 調整為您頁面頂部固定元素的高度
      const elementPosition = activeStepElement.getBoundingClientRect().top;
      const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

      // 平滑滾動到該位置
      window.scrollTo({
        top: offsetPosition,
        behavior: 'smooth'
      });
    }
  });
};

// 當用戶點擊上一步或下一步時也調用
const goToNextStep = async () => {
  // 驗證邏輯...

  // 如果驗證通過，變更步驟
  currentStep.value++;
  // 滾動功能會通過 watch 自動調用
};

const goToPreviousStep = () => {
  currentStep.value--;
  // 滾動功能會通過 watch 自動調用
};

watch(currentStep, (newStep) => {
  displayStep.value = newStep
  scrollToActiveStep();

  // 更新 URL 查詢參數，但不重新加載頁面
  appRouter.replace({
    query: { ...route.query, step: newStep.toString() }
  })
})

// 監聽 displayStep 變化，更新 currentStep
watch(displayStep, (newStep) => {
  // 避免自動跳到最後一步，只允許前進或後退一步
  if (Math.abs(newStep - currentStep.value) <= 1) {
    currentStep.value = newStep
  } else {
    // 如果步驟差距太大，重置為當前步驟
    nextTick(() => {
      displayStep.value = currentStep.value
    })
  }
})

// 當表單數據變化時保存到 localStorage
watch(forms, (newForms) => {
  localStorage.setItem('grantForms', JSON.stringify(newForms))
}, { deep: true })

// 驗證當前步驟並前進
const validateAndProceed = async (step: any) => {
  const formRef = eval(`form${step}`)
  const { valid } = await formRef.value.validate()

  if (valid) {
    try {
      // 呼叫API保存當前步驟數據
      // await saveStepData(step)

      // 更新步驟 (這會觸發 watch 並更新 URL)
      currentStep.value++
    } catch (error) {
      // 顯示錯誤訊息
    }
  }
}

// 監聽 URL 參數變化
watch(
  () => route.query.step,
  (newStepParam) => {
    if (newStepParam) {
      const newStep = parseInt(newStepParam as string, 10)
      if (!isNaN(newStep) && newStep >= 1 && newStep <= steps.length) {
        // 只在 URL 參數變化來源非內部更新時更新 currentStep
        if (newStep !== currentStep.value) {
          // 檢查是否是合法的導航 (前進或後退一步)
          const isValidNavigation = Math.abs(newStep - currentStep.value) <= 1

          // 如果是從瀏覽器歷史記錄導航(例如按下瀏覽器的前進/後退按鈕)，允許跳轉
          if (isValidNavigation) {
            currentStep.value = newStep
            displayStep.value = newStep
          } else {
            // 如果是非法跳轉，重置 URL 參數
            appRouter.replace({
              query: { ...route.query, step: currentStep.value.toString() }
            })
          }
        }
      }
    }
  }
)

const navFab = ref(false);

// 判斷是否可以跳到特定步驟（通常只能跳到已完成的步驟和當前步驟的前後一步）
const canJumpToStep = (step) => {
  // 只允許跳到之前已驗證過的步驟或當前步驟
  return step <= currentStep.value + 1 && validatedSteps.has(step) || step === currentStep.value;
};

// 跳轉到指定步驟
const jumpToStep = (step) => {
  if (canJumpToStep(step)) {
    if (hasUnsavedChanges.value) {
      // 提示用戶有未保存的更改
      const confirm = window.confirm('有未保存的更改，是否繼續？');
      if (!confirm) return;
    }

    currentStep.value = step;
    displayStep.value = step;

    // 更新 URL 參數
    router.replace({
      query: { ...route.query, step: step.toString() }
    });

    // 滾動到頂部
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
};

// 跟踪已驗證的步驟
const validatedSteps = reactive(new Set());

// 當步驟驗證成功時添加到已驗證集合
const handleStepValidated = ({ valid, step }) => {
  if (valid) {
    validatedSteps.add(step);
    // 進入下一步
    if (step < steps.length) {
      currentStep.value++;
      displayStep.value = currentStep.value;
    }
  }
};


</script>

<style scoped>
.sticky-header {
  position: sticky;
  top: 110px; /* 留出主 app-bar 的空間 */
  z-index: 4;
  transition: box-shadow 0.3s ease, elevation 0.3s ease;
}

/* 當重疊時隱藏陰影的輔助類 */
.elevation-0 {
  box-shadow: none !important;
  background-color: transparent !important;
}

</style>
