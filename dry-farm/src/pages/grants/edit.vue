<template>
  <v-container class="pt-0 mb-10">
    <!-- Loading indicator -->
    <v-overlay
      v-if="!isDataLoaded"
      :value="!isDataLoaded"
      class="d-flex align-center justify-center"
    >
      <v-progress-circular
        indeterminate
        size="64"
        color="primary"
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

    <!-- Navigation Drawer -->
    <v-layout>
      <v-navigation-drawer
        v-model="drawerOpen"
        border="b-sm"
        elevation="0"
        :rail-width="60"
        :permanent="!isSmallScreen"
        :temporary="isSmallScreen"
        :width="drawerWidth"
        :rail="isRailMode"
      >
        <v-list
          height="55"
          class="pt-0 mt-0"
        >
          <v-list-item>
            <v-list-item-title class="text-h6">
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
        <v-list nav>
          <v-list-item
            v-for="step in steps"
            :key="step.value"
            :value="step.value"
            :active="currentStep === step.value"
            :disabled="isNavigating"
            variant="elevated"
            elevation="0"
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
      <v-main>
        <div class="px-4 mb-1">
          <!-- Small screen step indicator -->
          <v-card
            v-if="isSmallScreen"
            class="mb-4 pa-2"
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
          <v-card class="pb-0 mb-0">
            <v-card-title class="text-h5 ml-4">
              {{ steps.find(s => s.value === currentStep)?.title }}<span
                v-if="grantsStore.currentGrant?.case_number"
                class="text-disabled text-h6 mb-6"
              >（{{ grantsStore.currentGrant?.case_number }}）</span>
            </v-card-title>

            <v-card-text class="pb-0 mb-0">
              <!-- Autosave indicator when there are unsaved changes -->
              <v-banner
                v-if="grantsStore.hasUnsavedChanges"
                color="info"
                lines="one"
                icon="mdi-content-save"
                class="mb-4"
              >
                <template v-slot:text>
                  資料變更尚未儲存，系統將自動儲存
                  <span v-if="grantsStore.lastSavedAt" class="ms-2 text-caption">
                    (上次儲存於 {{ grantsStore.lastSavedTime }})
                  </span>
                </template>

                <template v-slot:actions>
                  <v-btn
                    variant="text"
                    :loading="grantsStore.isSaving"
                    @click="saveAllChanges"
                  >
                    立即儲存
                  </v-btn>
                </template>
              </v-banner>

              <!-- Step components -->
              <step1
                v-if="currentStep === 1"
                :form-data="grantsStore.formData[1]"
                :current-step="currentStep"
                @update:form-data="handleFormDataUpdate(1, $event)"
                @validated="handleStepValidated"
                @go-back="handleGoBack"
              />
              <step2
                v-if="currentStep === 2"
                :form-data="grantsStore.formData[2]"
                :current-step="currentStep"
                @update:form-data="handleFormDataUpdate(2, $event)"
                @validated="handleStepValidated"
                @go-back="handleGoBack"
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
                :form-data="grantsStore.formData[7]"
                :current-step="currentStep"
                @update:form-data="handleFormDataUpdate(7, $event)"
                @validated="handleStepValidated"
                @go-back="handleGoBack"
              />
              <step8
                v-if="currentStep === 8"
                :form-data="grantsStore.formData[8]"
                :current-step="currentStep"
                @update:form-data="handleFormDataUpdate(8, $event)"
                @validated="handleStepValidated"
                @go-back="handleGoBack"
              />
            </v-card-text>

            <!-- Step navigation buttons for desktop -->
            <v-card-actions
              v-if="!isSmallScreen"
              class="pt-2"
            >
              <v-btn
                v-if="currentStep > 1"
                :disabled="isNavigating"
                size="x-large"
                class="ml-6"
                variant="outlined"
                rounded="lg"
                :ripple="false"
                @click="handleGoBack"
              >
                <v-icon start>
                  mdi-arrow-left
                </v-icon>
                上一步
              </v-btn>

              <v-spacer />

              <v-btn
                :disabled="isNavigating"
                color="primary"
                class="mr-5"
                size="x-large"
                variant="text"
                rounded="lg"
                :ripple="false"
                @click="goToNextStep"
              >
                {{ currentStep === 8 ? '完成' : '下一步' }}
                <v-icon
                  v-if="currentStep < 8"
                  end
                >
                  mdi-arrow-right
                </v-icon>
                <v-icon
                  v-else
                  end
                >
                  mdi-check
                </v-icon>
              </v-btn>
            </v-card-actions>
          </v-card>
        </div>
      </v-main>
    </v-layout>
  </v-container>
</template>

<script setup lang="ts">
import { useDisplay } from 'vuetify'
import { useRoute, useRouter, onBeforeRouteLeave } from 'vue-router'
import { useGrantsStore } from '@/stores/grants'
import { debounce } from 'lodash'

// Import step components
import step1 from './components/step1.vue'
import step2 from './components/step2.vue'
import step3 from './components/step3.vue'
import step4 from './components/step4.vue'
import step5 from './components/step5.vue'
import step6 from './components/step6.vue'
import step7 from './components/step7.vue'
import step8 from './components/step8.vue'

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
const autoSaveTimer = ref<number | null>(null);

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
  { title: '補助申請資料', value: 6, subtitle: '請填寫補助申請資料' },
  { title: '變更設計及結案申報', value: 7, subtitle: '請填寫變更設計及結案申報' },
  { title: '佐證及相關文件上傳', value: 8, subtitle: '請上傳佐證及相關文件' }
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
  if (currentStep.value === stepValue) return 'primary'
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
    handleStepValidated({ valid: true, step: currentStep.value })
  }
}

// Helper function to scroll to top
const scrollToTop = () => {
  window.scrollTo({ top: 0, behavior: 'smooth' })
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

        // Update URL and load data for the next step
        updateStepInURL(currentStep.value)
        await loadStepData(currentStep.value)

        // Scroll to top after loading new step data
        scrollToTop()
      } else {
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
const handleFormDataUpdate = (step: number, data: any) => {
  grantsStore.updateFormData(step, data)

  // Setup autosave if changes are made
  if (grantsStore.hasUnsavedChanges && !autoSaveTimer.value) {
    autoSaveTimer.value = window.setTimeout(async () => {
      await saveAllChanges()
      autoSaveTimer.value = null
    }, 3000) // Autosave after 3 seconds of inactivity
  }
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

// Improved data loading with race condition prevention
let isLoadingData = false
const loadStepData = async (step: number) => {
  if (!route.query.id || isLoadingData) return

  isLoadingData = true
  const caseNumber = route.query.id as string
  submitting.value = true
  isDataLoaded.value = false

  try {
    // Use the grantsStore's loadStepData method for both API and localStorage
    await grantsStore.loadStepData(caseNumber, step)

    isDataLoaded.value = true
  } catch (error) {
    console.error(`Failed to load data for step ${step}:`, error)
  } finally {
    submitting.value = false
    isLoadingData = false
  }
}

// Initialize data with better error handling
onMounted(async () => {
  // Get case number and step from URL
  const caseNumber = route.query.id as string
  const stepParam = route.query.step

  if (!caseNumber) {
    // Redirect to grants list if no case number provided
    router.push('/grants')
    return
  }

  try {
    // First load the grant to get its basic info
    await grantsStore.loadGrant(caseNumber)

    // Determine starting step (from URL, grant data, or default to 1)
    let startStep = 1

    if (stepParam) {
      const stepValue = parseInt(stepParam as string, 10)
      if (!isNaN(stepValue) && stepValue >= 1 && stepValue <= steps.length) {
        startStep = stepValue
      }
    } else if (grantsStore.currentStep) {
      startStep = grantsStore.currentStep
    }

    // Set step and update URL if needed
    currentStep.value = startStep

    if (!stepParam) {
      updateStepInURL(startStep)
    }

    // Load data for the starting step
    await loadStepData(startStep)
    isDataLoaded.value = true
  } catch (error) {
    console.error('Failed to initialize grant data:', error)
  }
})

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
/* Spinner animation for loading icon */
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.mdi-loading.mdi-spin {
  animation: spin 1s infinite linear;
}
</style>
