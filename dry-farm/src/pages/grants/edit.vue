<template>
  <v-container
    fluid
    class="grants-edit-container px-6 pb-0 pt-0"
    style="background-color: white"
  >
    <!-- Loading indicator -->
    <v-overlay
      v-if="!isDataLoaded"
      :value="!isDataLoaded"
      class="d-flex align-center justify-center"
    >
      <v-progress-circular
        indeterminate
        size="64"
        color="#3ea0a3"
      />
      <span class="ml-4 text-h6">載入資料中...</span>
    </v-overlay>

    <!-- Error display -->
    <v-alert
      v-if="grantsStore.error"
      type="error"
      class="mb-4"
      dismissible
      @click:close="grantsStore.clearError()"
    >
      {{ grantsStore.error }}
    </v-alert>

    <!-- Main content -->
    <v-row justify="center">
      <v-col
        cols="12"
        lg="11"
        align-self="center"
      >
        <div class="section-wrapper">
          <!-- Navigation Drawer with Glass Effect -->
          <v-layout class="pb-1">
            <v-navigation-drawer
              v-model="drawerOpen"
              rounded="lg"
              :rail-width="60"
              :permanent="!isSmallScreen"
              :temporary="isSmallScreen"
              :width="drawerWidth"
              :rail="isRailMode"
              class="navigation-drawer-glass"
            >
              <v-list
                height="55"
                class="pt-0 mt-0"
              >
                <v-list-item>
                  <v-list-item-title
                    class="text-h6 font-weight-bold"
                    style="color: #2d8c8f"
                  >
                    補助申請業務 {{ currentStep }}/{{ steps.length }}
                  </v-list-item-title>
                  <template #append>
                    <v-btn
                      icon
                      variant="text"
                      rounded="circle"
                      class="pl-0"
                      @click="isRailMode = !isRailMode"
                    >
                      <v-icon>{{ isRailMode ? 'mdi-chevron-right' : 'mdi-chevron-left' }}</v-icon>
                    </v-btn>
                  </template>
                </v-list-item>
              </v-list>

              <v-divider />

              <!-- Step navigation list -->
              <v-list
                nav
                class="step-list"
              >
                <v-list-item
                  v-for="step in steps"
                  :key="step.value"
                  :value="step.value"
                  :active="currentStep === step.value"
                  :disabled="isNavigating"
                  variant="elevated"
                  elevation="0"
                  class="step-list-item"
                  @click="handleStepClick(step.value)"
                >
                  <template #prepend>
                    <v-icon
                      :color="getStepIconColor(step.value)"
                      size="large"
                    >
                      {{ getStepIcon(step.value) }}
                    </v-icon>
                  </template>

                  <v-list-item-title>
                    <span :class="{ 'text-primary font-weight-bold': currentStep === step.value }">
                      {{ step.title }}
                    </span>
                  </v-list-item-title>

                  <v-list-item-subtitle
                    v-if="!isRailMode"
                    :class="[
                      currentStep === step.value ? 'text-primary' : 'text-medium-emphasis'
                    ]"
                  >
                    {{ step.subtitle }}
                  </v-list-item-subtitle>

                  <template
                    v-if="currentStep === step.value && !isRailMode"
                    #append
                  >
                    <v-icon
                      color="primary"
                      size="small"
                      rounded="circle"
                    >
                      mdi-arrow-right
                    </v-icon>
                  </template>
                </v-list-item>
              </v-list>
            </v-navigation-drawer>

            <!-- Main content area -->
            <v-main class="pt-7">
              <div class="px-4 mb-1">
                <!-- Small screen step indicator -->
                <v-card
                  v-if="isSmallScreen"
                  class="mb-4 mt-0 pa-2 pt-0 mobile-step-card"
                >
                  <div class="d-flex align-center">
                    <v-btn
                      icon
                      variant="text"
                      @click="drawerOpen = !drawerOpen"
                    >
                      <v-icon>mdi-menu</v-icon>
                    </v-btn>

                    <div class="ml-2">
                      <div class="text-subtitle-1">
                        補助申請業務 {{ currentStep }}/{{ steps.length }}
                      </div>
                      <div class="text-body-2">
                        {{ steps.find(s => s.value === currentStep)?.subtitle }}
                      </div>
                    </div>

                    <v-spacer />

                    <div class="d-flex">
                      <v-btn
                        v-if="currentStep > 1"
                        :disabled="isNavigating"
                        icon
                        variant="text"
                        rounded="circle"
                        @click="handleGoBack"
                      >
                        <v-icon>mdi-arrow-left</v-icon>
                      </v-btn>

                      <v-btn
                        v-if="currentStep < steps.length"
                        :disabled="isNavigating"
                        icon
                        variant="text"
                        rounded="circle"
                        @click="goToNextStep"
                      >
                        <v-icon>mdi-arrow-right</v-icon>
                      </v-btn>
                    </div>
                  </div>
                </v-card>

                <!-- Step components container -->
                <v-card
                  class="section-card pb-0 mb-0"
                  rounded="lg"
                >
                  <v-card-item class="custom-title">
                    <v-card-title class="text-h5 font-weight-black">
                      {{ steps.find(s => s.value === currentStep)?.title }}
                      <span
                        v-if="grantsStore.currentGrant?.case_number"
                        class="text-disabled"
                      >
                        <v-chip
                          color="grey-lighten-3"
                          size="small"
                          class="ml-4 mb-1"
                          variant="flat"
                          rounded="sm"
                        >
                          <span>案號: {{ grantsStore.currentGrant?.case_number }}</span>
                          <v-divider
                            v-if="grantsStore.currentGrant?.active_version?.version"
                            vertical
                            class="mx-2"
                            style="opacity: 0.5;"
                          />
                          <span
                            v-if="grantsStore.currentGrant?.active_version?.version"
                            class="text-caption"
                            style="opacity: 0.7; font-weight: 500;"
                          >
                            版本 {{ grantsStore.currentGrant.active_version.version }}
                          </span>
                        </v-chip>
                      </span>
                    </v-card-title>
                  </v-card-item>

                  <v-card-text class="pb-0 mb-0">
                    <!-- Autosave indicator when there are unsaved changes -->
                    <v-snackbar
                      v-model="grantsStore.hasUnsavedChanges"
                      variant="text"
                      color="info"
                      lines="one"
                      icon="mdi-content-save"
                      class="mb-4"
                    >
                      <template #text>
                        資料變更尚未儲存，系統將自動儲存
                        <span
                          v-if="grantsStore.lastSavedAt"
                          class="ms-2 text-caption"
                        >
                          (上次儲存於 {{ grantsStore.lastSavedTime }})
                        </span>
                      </template>

                      <template #actions>
                        <v-btn
                          variant="text"
                          :loading="grantsStore.isSaving"
                          @click="saveAllChanges"
                        >
                          立即儲存
                        </v-btn>
                      </template>
                      <v-progress-linear
                        :active="grantsStore.hasUnsavedChanges"
                        :indeterminate="grantsStore.hasUnsavedChanges"
                        color="cyan"
                        stream
                        location="bottom"
                      />
                    </v-snackbar>

                    <!-- Content Card for Step Components -->
                    <v-card
                      class="content-card"
                      rounded="lg"
                      elevation="0"
                    >
                      <!-- Step components -->
                      <step1
                        v-if="currentStep === 1"
                        ref="step1Ref"
                        :current-step="currentStep"
                        @step-data-changed="handleStepDataChanged"
                        @validation-changed="handleStepValidationChanged"
                        @ready-to-proceed="handleStepReadyToProceed"
                        @go-back-requested="handleGoBack"
                      />
                      <step2
                        v-if="currentStep === 2"
                        ref="step2Ref"
                        :current-step="currentStep"
                        @step-data-changed="handleStepDataChanged"
                        @validation-changed="handleStepValidationChanged"
                        @ready-to-proceed="handleStepReadyToProceed"
                        @go-back-requested="handleGoBack"
                      />
                      <step3
                        v-if="currentStep === 3"
                        :form-data="grantsStore.formData[3]"
                        :current-step="currentStep"
                        @update:form-data="handleFormDataUpdate(3, $event)"
                        @validated="handleStepValidated"
                        @go-back="handleGoBack"
                      />
                      <step4
                        v-if="currentStep === 4"
                        :form-data="grantsStore.formData[4]"
                        :current-step="currentStep"
                        @update:form-data="handleFormDataUpdate(4, $event)"
                        @validated="handleStepValidated"
                        @go-back="handleGoBack"
                      />
                      <step5
                        v-if="currentStep === 5"
                        :form-data="grantsStore.formData[5]"
                        :current-step="currentStep"
                        @update:form-data="handleFormDataUpdate(5, $event)"
                        @validated="handleStepValidated"
                        @go-back="handleGoBack"
                      />
                      <step6
                        v-if="currentStep === 6"
                        :form-data="grantsStore.formData[6]"
                        :current-step="currentStep"
                        @update:form-data="handleFormDataUpdate(6, $event)"
                        @validated="handleStepValidated"
                        @go-back="handleGoBack"
                      />
                      <step7
                        v-if="currentStep === 7"
                        ref="step7Ref"
                        :form-data="grantsStore.formData[7]"
                        :current-step="currentStep"
                        @update:form-data="handleFormDataUpdate(7, $event)"
                        @validated="handleStepValidated"
                        @go-back="handleGoBack"
                        @button-config-changed="handleStep7ButtonConfigChanged"
                        @save-for-improvement="handleSaveForImprovement"
                        @proceed-to-next-step="goToNextStep"
                      />
                      <step8
                        v-if="currentStep === 8"
                        :form-data="grantsStore.formData[8]"
                        :current-step="currentStep"
                        @update:form-data="handleFormDataUpdate(8, $event)"
                        @validated="handleStepValidated"
                        @go-back="handleGoBack"
                      />
                      <step9
                        v-if="currentStep === 9"
                        :form-data="grantsStore.formData[9]"
                        :current-step="currentStep"
                        @update:form-data="handleFormDataUpdate(9, $event)"
                        @validated="handleStepValidated"
                        @go-back="handleGoBack"
                      />
                    </v-card>
                  </v-card-text>

                  <!-- Step navigation buttons for desktop -->
                  <v-card-actions
                    v-if="!isSmallScreen"
                    class="pt-0"
                  >
                    <v-spacer />

                    <v-btn
                      v-if="currentStep > 1"
                      :disabled="isNavigating"
                      size="x-large"
                      class="ml-6 mb-1 pr-6 navigation-btn"
                      color="#3ea0a3"
                      variant="text"
                      density="compact"
                      rounded="lg"
                      :ripple="false"
                      @click="handleGoBack"
                    >
                      <v-icon start>
                        mdi-arrow-left
                      </v-icon>
                      上一步
                    </v-btn>

                    <v-btn
                      :disabled="isNavigating"
                      :color="currentStep === 7 ? step7ButtonConfig.color : '#3ea0a3'"
                      class="mr-6 pl-6 next-btn"
                      size="x-large"
                      variant="outlined"
                      density="compact"
                      rounded="lg"
                      :ripple="false"
                      @click="handleMainButtonClick"
                    >
                      <!-- 替換為更詳細的邏輯顯示不同的按鈕文字 -->
                      <template v-if="currentStep === 8">
                        完成
                      </template>
                      <template v-else-if="currentStep === 7">
                        {{ step7ButtonConfig.text }}
                      </template>
                      <template v-else-if="currentStep === 6">
                        完成申報
                      </template>
                      <template v-else>
                        下一步
                      </template>

                      <v-icon
                        v-if="currentStep === 8"
                        end
                      >
                        mdi-check
                      </v-icon>
                      <v-icon
                        v-else-if="currentStep === 7"
                        end
                      >
                        {{ step7ButtonConfig.icon }}
                      </v-icon>
                      <v-icon
                        v-else
                        end
                      >
                        mdi-arrow-right
                      </v-icon>
                    </v-btn>
                  </v-card-actions>
                </v-card>
              </div>
            </v-main>
          </v-layout>
        </div>
      </v-col>
    </v-row>

    <!-- 處理中對話框 -->
    <v-dialog
      v-model="isNavigating"
      persistent
      width="300"
    >
      <v-card>
        <v-card-text class="text-center pa-5">
          <v-progress-circular
            indeterminate
            color="#3ea0a3"
            size="64"
            class="mb-3"
          />
          <div class="text-body-1">
            處理中，請稍候...
          </div>
        </v-card-text>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup lang="ts">
import { useDisplay, useGoTo } from 'vuetify'
import { useRoute, useRouter, onBeforeRouteLeave } from 'vue-router'
import { useGrantsStore } from '@/stores/grants'
import { GrantStorage } from '@/utils/grant-storage'
import { debounce } from 'lodash'

// Import step components
import step1 from '@/pages/grants/steps/step1.vue'
import step2 from '@/pages/grants/steps/step2.vue'
import step3 from '@/pages/grants/steps/step3.vue'
import step4 from '@/pages/grants/steps/step4.vue'
import step5 from '@/pages/grants/steps/step5.vue'
import step6 from '@/pages/grants/steps/step6.vue'
import step7 from '@/pages/grants/steps/step7.vue'
import step8 from '@/pages/grants/steps/step8.vue'

// Setup
const route = useRoute()
const router = useRouter()
const { name } = useDisplay()
const isSmallScreen = computed(() => name.value === 'xs' || name.value === 'sm')
const grantsStore = useGrantsStore()

// State refs
const currentStep = ref(1)
const submitting = ref(false)
const isDataLoaded = ref(false)
const isNavigating = ref(false)
const autoSaveTimer = ref<number | null>(null)

// Step7 按鈕配置
const step7ButtonConfig = ref({
  text: '結案',
  color: '#3ea0a3',
  icon: 'mdi-arrow-right',
  action: 'proceed'
})

// Step7 組件引用
const step7Ref = ref<{ handleActionRequest: (action: string) => void } | null>(null)

// 🆕 統一事件驅動架構：組件引用接口定義
interface StepComponent {
  handleProceedToNext: () => void;
  handleGoBack: () => void;
}

// 🆕 統一事件驅動架構：步驟組件引用映射
const stepRefs = reactive<Record<number, StepComponent | null>>({
  1: null,
  2: null,
  3: null,
  4: null,
  5: null,
  6: null,
  7: null,
  8: null
})

// 保持現有引用以便向後兼容
const step1Ref = ref<StepComponent | null>(null)
const step2Ref = ref<StepComponent | null>(null)

// Navigation drawer state
const drawerOpen = ref(true)
const isRailMode = ref(false) // Default to expanded
const drawerWidth = ref(280)

// Step definitions
const steps = [
  { title: '申請人資料', value: 1, subtitle: '申請人資料' },
  { title: '土地資料', value: 2, subtitle: '請填寫土地資料' },
  { title: '灌溉調控設施', value: 3, subtitle: '請填寫灌溉調控設施' },
  { title: '田間管路', value: 4, subtitle: '請填寫田間管路' },
  { title: '現場勘查', value: 5, subtitle: '請填寫現場勘查' },
  { title: '文件列印及完成申報', value: 6, subtitle: '請填寫補助申請資料' },
  { title: '功能測試', value: 7, subtitle: '請填寫結案申報' },
  { title: '佐證及相關文件上傳', value: 8, subtitle: '請上傳佐證及相關文件' },
  { title: '變更設計', value: 9, subtitle: '變更設計' }
]

// Step icon and color logic
const getStepIcon = (stepValue: number): string => {
  if (submitting.value && currentStep.value === stepValue) return 'mdi-loading mdi-spin'
  if (currentStep.value > stepValue) return 'mdi-check-circle'
  if (currentStep.value === stepValue) return 'mdi-numeric-'+stepValue+'-circle'
  return 'mdi-circle-outline'
}

const getStepIconColor = (stepValue: number) => {
  if (currentStep.value > stepValue) return 'success'
  if (currentStep.value === stepValue) return '#3ea0a3'
  return 'grey'
}

// Debounced URL update to prevent recursive update issues
const debouncedUpdateStepInURL = debounce((step: number) => {
  router.replace({
    query: { ...route.query, step: step.toString() }
  })
}, 100)

// URL management function that uses debouncing
const updateStepInURL = (step: number) => {
  debouncedUpdateStepInURL(step)
}

// Helper function to trigger next step
const goToNextStep = () => {
  if (currentStep.value < steps.length) {
    // 🆕 統一事件驅動：使用映射表統一處理所有步驟
    const stepComponent = stepRefs[currentStep.value]
    if (stepComponent) {
      console.log(`🎯 edit.vue: Calling step${currentStep.value}Ref.handleProceedToNext()`)
      stepComponent.handleProceedToNext()
    } else {
      // 對於沒有引用的步驟，使用傳統驗證方式
      console.log(`🎯 edit.vue: Step ${currentStep.value} has no ref, using traditional validation`)
      handleStepValidated({ valid: true, step: currentStep.value })
    }
  }
}

// 處理 Step7 按鈕配置變化
const handleStep7ButtonConfigChanged = (buttonConfig: { text: string; color: string; icon: string; action: string }) => {
  console.log('Step7 按鈕配置變化:', buttonConfig)
  step7ButtonConfig.value = buttonConfig
}

// 處理存檔功能（限期改善）
const handleSaveForImprovement = async () => {
  console.log('處理存檔功能：現場勘查未通過驗收，將於改善後複驗')

  try {
    submitting.value = true

    // 保存當前數據
    await saveAllChanges()

    // 顯示成功訊息
    // 這裡可以添加 snackbar 或其他提示
    console.log('存檔成功，待改善後複驗')

    // 不進入下一步，停留在當前步驟
  } catch (error) {
    console.error('存檔失敗:', error)
  } finally {
    submitting.value = false
  }
}

// 修改按鈕點擊邏輯
const handleMainButtonClick = () => {
  console.log('主按鈕點擊:', {
    currentStep: currentStep.value,
    buttonConfig: step7ButtonConfig.value
  })

  if (currentStep.value === 7) {
    // 委派給 step7 組件處理對應的動作
    console.log('委派給 step7 組件處理動作:', step7ButtonConfig.value.action)
    if (step7Ref.value && step7Ref.value.handleActionRequest) {
      step7Ref.value.handleActionRequest(step7ButtonConfig.value.action)
    } else {
      console.error('step7Ref 或 handleActionRequest 方法不存在')
    }
  } else {
    // 其他步驟的正常邏輯
    goToNextStep()
  }
}

// Helper function to scroll to top using multiple strategies
const goTo = useGoTo()
const scrollToTop = () => {
  // Strategy 1: Force scroll on v-main with more specific targeting
  const mainElement = document.querySelector('main.v-main')
  if (mainElement) {
    try {
      mainElement.scrollTop = 0  // Direct property assignment
      mainElement.scrollTo({ top: 0, behavior: 'smooth' })
    } catch {
      // Silent fallback
    }
  }

  // Strategy 2: Try v-main__wrap if it exists
  const wrapElement = document.querySelector('.v-main__wrap')
  if (wrapElement) {
    wrapElement.scrollTop = 0
    wrapElement.scrollTo({ top: 0, behavior: 'smooth' })
  }

  // Strategy 3: Try the application wrapper
  const appWrap = document.querySelector('.v-application__wrap')
  if (appWrap) {
    appWrap.scrollTop = 0
    appWrap.scrollTo({ top: 0, behavior: 'smooth' })
  }

  // Strategy 4: Try all potentially scrollable elements
  const allScrollableElements = document.querySelectorAll('*')
  for (const element of allScrollableElements) {
    if (element.scrollHeight > element.clientHeight && element.scrollTop > 0) {
      element.scrollTop = 0
      element.scrollTo({ top: 0, behavior: 'smooth' })
    }
  }

  // Strategy 5: Force document and window scroll
  document.documentElement.scrollTop = 0
  document.body.scrollTop = 0
  window.scrollTo(0, 0)

  // Strategy 6: Try Vuetify's useGoTo with specific container
  try {
    // Try to find the main scroll container
    const scrollContainer = document.querySelector('main.v-main') || document.querySelector('.v-main__wrap')
    if (scrollContainer && scrollContainer instanceof HTMLElement) {
      goTo(0, { container: scrollContainer })
    } else {
      goTo(0)
    }
  } catch {
    // Silent fallback
  }
}

// Step validation handling with improved flow control
const handleStepValidated = async ({ valid, step }: { valid: boolean; step: number }) => {
  if (valid && !isNavigating.value) {
    try {
      isNavigating.value = true
      submitting.value = true

      // Save current step data through the store
      await saveAllChanges()

      // Proceed to next step if not on the last step
      if (step < steps.length) {
        currentStep.value = step + 1

        // 更新 grantsStore 中的 current_step
        grantsStore.updateCurrentStep(currentStep.value);
        console.log(`Step validated: Updating grantsStore.current_step to ${currentStep.value}`)

        // Update URL and load data for the next step
        updateStepInURL(currentStep.value)
        await loadStepData(currentStep.value)

        // Scroll to top after loading new step data
        scrollToTop()
      } else {
        // 在最後一步完成時也更新 current_step
        grantsStore.updateCurrentStep(steps.length);
        console.log(`Final step completed: Setting grantsStore.current_step to ${steps.length}`)

        // Complete the form if this was the last step
        router.push('/grants')
      }
    } catch (error) {
      console.error('Error saving step data:', error)
    } finally {
      submitting.value = false
      // Add a delay before allowing navigation again
      setTimeout(() => {
        isNavigating.value = false
      }, 500)
    }
  }
}

// Handle form data updates from step components
const handleFormDataUpdate = (step: number, data: Record<string, unknown>) => {
  console.log(`🔄 edit.vue handleFormDataUpdate called for step ${step}`);
  console.log('📤 Received data keys:', Object.keys(data));
  console.log('📤 Received data sample:', {
    fieldLength: data.fieldLength,
    fieldWidth: data.fieldWidth,
    facilityArea: data.facilityArea,
    fundingSourceId: data.fundingSourceId
  });

  // 確保 grantsStore.currentStep 與接收到的 step 一致
  if (grantsStore.currentStep !== step) {
    console.log(`🔧 edit.vue: Correcting grantsStore.currentStep from ${grantsStore.currentStep} to ${step}`);
    grantsStore.updateCurrentStep(step);
  }

  // 同時更新本地的 currentStep ref
  if (currentStep.value !== step) {
    console.log(`🔧 edit.vue: Correcting local currentStep from ${currentStep.value} to ${step}`);
    currentStep.value = step;
  }

  grantsStore.updateFormData(step, data)

  console.log('📊 After updateFormData - grantsStore.hasUnsavedChanges:', grantsStore.hasUnsavedChanges);
  console.log('📊 grantsStore.currentStep:', grantsStore.currentStep);
  console.log('📊 local currentStep.value:', currentStep.value);
  console.log('📊 grantsStore.formData[' + step + '] sample:', {
    fieldLength: grantsStore.formData[step]?.fieldLength,
    fieldWidth: grantsStore.formData[step]?.fieldWidth,
    facilityArea: grantsStore.formData[step]?.facilityArea
  });

  // Setup autosave if changes are made
  if (grantsStore.hasUnsavedChanges && !autoSaveTimer.value) {
    console.log('⏰ Setting up autosave timer (3 seconds)');
    autoSaveTimer.value = window.setTimeout(async () => {
      console.log('💾 Autosave triggered for step', grantsStore.currentStep);
      await saveAllChanges()
      autoSaveTimer.value = null
    }, 3000) // Autosave after 3 seconds of inactivity
  } else if (grantsStore.hasUnsavedChanges) {
    console.log('⏰ Autosave timer already exists');
  } else {
    console.log('⚠️ No unsaved changes detected');
  }
}

// 🆕 統一事件驅動架構：通用步驟事件處理器
interface StepEventData {
  step: number
  data: Record<string, unknown>
  valid: boolean
}

// 🆕 統一資料變更事件處理
const handleStepDataChanged = (eventData: StepEventData) => {
  const { step, data, valid } = eventData
  console.log(`📥 edit.vue: Received step-data-changed event from step${step}`)
  console.log(`📊 Step: ${step}, Valid: ${valid}, Data keys:`, Object.keys(data))

  // 使用現有的 handleFormDataUpdate 邏輯處理資料
  handleFormDataUpdate(step, { ...data, valid })
}

// 🆕 統一驗證狀態變更事件處理
const handleStepValidationChanged = (eventData: { step: number, valid: boolean }) => {
  const { step, valid } = eventData
  console.log(`📋 edit.vue: Received validation-changed event from step${step} - Step: ${step}, Valid: ${valid}`)

  // 確保步驟狀態同步
  if (grantsStore.currentStep !== step) {
    grantsStore.updateCurrentStep(step)
  }

  // 更新驗證狀態到 grantsStore
  if (grantsStore.formData[step]) {
    grantsStore.formData[step].valid = valid
  }
}

// 🆕 統一準備進入下一步事件處理
const handleStepReadyToProceed = async (eventData: { step: number, data: Record<string, unknown> }) => {
  const { step, data } = eventData
  console.log(`✅ edit.vue: Received ready-to-proceed event from step${step}`)
  console.log(`📊 Step: ${step}, Data keys:`, Object.keys(data))

  // 先更新最新的資料
  handleFormDataUpdate(step, { ...data, valid: true })

  // 觸發步驟驗證邏輯（進入下一步）
  await handleStepValidated({ valid: true, step })
}

// Save all unsaved changes
const saveAllChanges = async () => {
  if (autoSaveTimer.value) {
    clearTimeout(autoSaveTimer.value)
    autoSaveTimer.value = null
  }

  return grantsStore.saveAllChanges()
}

// Step click handler with improved error handling
const handleStepClick = (stepValue: number) => {
  if (stepValue === currentStep.value || isNavigating.value) return // Skip if clicking current step or already navigating

  isNavigating.value = true

  // Save current data before switching
  saveAllChanges().then(() => {
    // Update current step
    currentStep.value = stepValue

    // 更新 grantsStore 中的 current_step
    grantsStore.updateCurrentStep(stepValue)
    console.log(`Step clicked: Updating grantsStore.current_step to ${stepValue}`)

    // Update URL and load data for selected step
    updateStepInURL(stepValue)
    loadStepData(stepValue).then(() => {
      // Scroll to top after loading new step data
      scrollToTop()
    })

    // Close drawer on mobile after selection
    if (isSmallScreen.value) {
      drawerOpen.value = false
    }

    setTimeout(() => {
      isNavigating.value = false
    }, 500)
  }).catch(error => {
    console.error('Failed to save data before step change:', error)
    isNavigating.value = false
  })
}

// Go back handler with improved navigation flow
const handleGoBack = async () => {
  if (currentStep.value > 1 && !isNavigating.value) {
    try {
      isNavigating.value = true
      submitting.value = true

      // Save current step data before going back
      await saveAllChanges()

      // Go to previous step
      currentStep.value -= 1

      // 更新 grantsStore 中的 current_step
      grantsStore.updateCurrentStep(currentStep.value)
      console.log(`Going back: Updating grantsStore.current_step to ${currentStep.value}`)

      // Update URL and load previous step data
      updateStepInURL(currentStep.value)
      await loadStepData(currentStep.value)

      // Scroll to top after loading the previous step
      scrollToTop()
    } catch (error) {
      console.error('Error saving step data before going back:', error)
    } finally {
      submitting.value = false
      setTimeout(() => {
        isNavigating.value = false
      }, 500)
    }
  }
}

const ensureCorrectStep = (expectedStep: number) => {
  if (grantsStore.currentStep !== expectedStep) {
    console.warn(`Step mismatch detected. Expected: ${expectedStep}, Actual: ${grantsStore.currentStep}`)
    grantsStore.updateCurrentStep(expectedStep)
  }
}

// Improved data loading with race condition prevention
let isLoadingData = false
const loadStepData = async (step: number) => {
  if (!route.query.id || isLoadingData) return;

  ensureCorrectStep(step)

  // 🆕 架構重構：step1.vue 和 step2.vue 採用自主載入模式
  // step1.vue 和 step2.vue 會在自己的 onMounted 中直接載入資料，不需要父組件控制
  // 這解決了從 index 導航時的 watch 時序問題
  if (step === 1 || step === 2) {
    console.log(`[edit.vue loadStepData] Skipping step ${step} - autonomous loading`);
    isDataLoaded.value = true;
    return;
  }

  isLoadingData = true;
  const caseNum = route.query.id as string;
  submitting.value = true; // This seems more like an isLoadingData flag
  isDataLoaded.value = false; // Indicate data for the new step is not yet loaded
  console.log(`[edit.vue loadStepData] Attempting to load data for step: ${step}, caseNumber: ${caseNum}`);

  try {
    await grantsStore.loadStepData(caseNum, step);
    console.log(`[edit.vue loadStepData] grantsStore.loadStepData for step ${step} successful. Form data for step ${step}:`, JSON.stringify(grantsStore.formData[step], null, 2));
    isDataLoaded.value = true;
  } catch (error) {
    console.error(`[edit.vue loadStepData] Failed to load data for step ${step}:`, error);
  } finally {
    submitting.value = false; // Reset the flag
    isLoadingData = false;
  }
};

// Initialize data with better error handling
onMounted(async () => {
  const caseNumberFromRoute = route.query.id as string;
  const stepParam = route.query.step;
  console.log(`[edit.vue onMounted] Case number from route: ${caseNumberFromRoute}, Step param: ${stepParam}`);

  if (!caseNumberFromRoute) {
    console.error('[edit.vue onMounted] No case number in route, redirecting to /grants.');
    router.push('/grants');
    return;
  }

  try {
    console.log(`[edit.vue onMounted] Calling grantsStore.loadGrant with caseNumber: ${caseNumberFromRoute}`);
    await grantsStore.loadGrant(caseNumberFromRoute);
    console.log('[edit.vue onMounted] grantsStore.loadGrant successful. Current grant:', JSON.stringify(grantsStore.currentGrant, null, 2));

    // 檢查 localStorage 中是否有已保存的 currentStep
    const grantData = GrantStorage.getGrant(caseNumberFromRoute);
    const savedCurrentStep = grantData?.currentStep;

    let startStep = 1;
    if (stepParam) {
      // URL 中有指定步驟，使用 URL 中的步驟
      const stepValue = parseInt(stepParam as string, 10);
      if (!isNaN(stepValue) && stepValue >= 1 && stepValue <= steps.length) {
        startStep = stepValue;
        console.log(`[edit.vue onMounted] startStep determined from route.query.step: ${startStep}`);
      } else {
        console.warn(`[edit.vue onMounted] Invalid stepParam in route: ${stepParam}. Using saved step: ${savedCurrentStep} or defaulting to 1.`);
        startStep = savedCurrentStep || 1;
      }
    } else {
      // URL 中沒有步驟參數，優先使用 localStorage 中保存的步驟
      if (savedCurrentStep && savedCurrentStep >= 1 && savedCurrentStep <= steps.length) {
        startStep = savedCurrentStep;
        console.log(`[edit.vue onMounted] Using saved current_step from localStorage: ${startStep}`);
      } else {
        console.log('[edit.vue onMounted] No valid saved step found, defaulting to step 1.');
        startStep = 1;
      }
    }

    // 使用 updateCurrentStep 來確保步驟同步到 localStorage
    grantsStore.updateCurrentStep(startStep);
    currentStep.value = startStep; // Update local currentStep ref

    console.log(`[edit.vue onMounted] Final startStep: ${startStep}. grantsStore.current_step updated to: ${grantsStore.currentStep}`);

    if (!stepParam) {
      updateStepInURL(startStep); // Update URL if it was not set
    }

    console.log(`[edit.vue onMounted] Calling loadStepData for step: ${startStep}`);
    await loadStepData(startStep);
    console.log(`[edit.vue onMounted] loadStepData for step ${startStep} finished. grantsStore.formData[${startStep}]:`, JSON.stringify(grantsStore.formData[startStep], null, 2));

    isDataLoaded.value = true;
  } catch (error) {
    console.error('[edit.vue onMounted] Failed to initialize grant data:', error);
    // grantsStore.handleError might be called internally, or add a specific error display here
  }
});

// Watch for URL step parameter changes with improved logic
watch(() => route.query.step, (newStepParam, oldStepParam) => {
  // Skip if values are effectively the same or we're currently navigating
  if (isNavigating.value ||
      newStepParam === oldStepParam ||
      (newStepParam && parseInt(newStepParam as string) === currentStep.value)) {
    return
  }

  if (newStepParam) {
    const newStep = parseInt(newStepParam as string, 10)
    if (!isNaN(newStep) && newStep >= 1 && newStep <= steps.length && newStep !== currentStep.value) {
      // Set navigating flag to prevent other updates during this operation
      isNavigating.value = true

      // If step changed in URL, save current step data before changing
      saveAllChanges().then(() => {
        currentStep.value = newStep
        return loadStepData(newStep)
      }).catch(error => {
        console.error('Failed to save data before step change:', error)
      }).finally(() => {
        // Release the navigation lock after a short delay
        setTimeout(() => {
          isNavigating.value = false
        }, 500)
      })
    }
  }
})

// Watch for screen size changes and adapt UI
watch(isSmallScreen, (smallScreen) => {
  if (smallScreen) {
    isRailMode.value = false
    drawerOpen.value = false
  } else {
    drawerOpen.value = true
    isRailMode.value = false // Keep expanded by default
  }
}, { immediate: true })

// Clean up on component unmount
onUnmounted(() => {
  if (autoSaveTimer.value) {
    clearTimeout(autoSaveTimer.value)
    autoSaveTimer.value = null
  }
})

// Route leave guard with unsaved changes check
onBeforeRouteLeave((to, from, next) => {
  // If there are unsaved changes, confirm before leaving
  if (grantsStore.hasUnsavedChanges) {
    if (window.confirm('您有未保存的更改，確定要離開嗎？')) {
      next()
    } else {
      next(false)
    }
  } else {
    next()
  }
})
</script>

<style scoped>
/* 添加背景圖片樣式 */
.grants-edit-container {
  background-image: url('@/assets/bg_index.svg');
  /* background-size: cover;
  background-position: center bottom;
  background-repeat: no-repeat;
  background-attachment: fixed;
  min-height: 100vh; */
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

/* Navigation drawer with glass effect */
.navigation-drawer-glass {
  /* background-color: rgba(255, 255, 255, 0.5) !important;
  backdrop-filter: blur(8px) !important;
  -webkit-backdrop-filter: blur(8px) !important;
  border-right: 1px solid rgba(255, 255, 255, 0.3) !important; */

  /* position: relative; */
  /* overflow: visible !important; */
  /* border-top-left-radius: 0 !important; */
  /* transition: all 0.3s ease; */

  /* 毛玻璃效果 */
  background-color: rgba(255, 255, 255, 0.6) !important;
  backdrop-filter: blur(10px) !important;
  -webkit-backdrop-filter: blur(10px) !important;

  /* 調整邊框和陰影效果與 section-card 一致 */
  border: 1px solid rgba(255, 255, 255, 0.25) !important;
  /* box-shadow: 0 8px 32px rgba(0, 0, 0, 0.05) !important; */
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08) !important;

  /* 關鍵修改：調整邊距和高度 */
  margin: 0px 0 !important; /* 與 section-card 一致的上下邊距 */
  max-height: calc(100% - 8px) !important; /* 減去上下邊距總和 */
  border-radius: 12px !important; /* 添加與卡片相同的圓角 */
  overflow: hidden !important;
}

/* Step list items */
.step-list-item {
  margin-bottom: 4px;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.step-list-item:hover {
  background-color: rgba(62, 160, 163, 0.1) !important;
}

/* Mobile step card with glass effect */
.mobile-step-card {
  background-color: rgba(255, 255, 255, 0.7) !important;
  backdrop-filter: blur(8px) !important;
  -webkit-backdrop-filter: blur(8px) !important;
  border: 1px solid rgba(255, 255, 255, 0.3) !important;
  border-radius: 12px;
}

/* 按鈕懸停效果 */
.next-btn {
  font-weight: 500;
  margin: 8px 0 12px 0;
  transition: all 0.2s ease;
}

.next-btn:hover {
  /* transform: translateY(-1px);
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1); */
  background-color: #3ea0a3 !important;
  color: white !important;
}

/* Navigation buttons */
.navigation-btn {
  transition: all 0.2s ease;
  font-weight: 500;
}

.navigation-btn:hover {
  /* transform: translateY(-2px); */
  box-shadow: 0 2px 8px rgba(62, 160, 163, 0.2) !important;
}

/* Spinner animation for loading icon */
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.mdi-loading.mdi-spin {
  animation: spin 1s infinite linear;
}
</style>
