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
    >
      {{ grantsStore.error }}
    </v-alert>

    <!-- Step navigation -->
    <v-snackbar
      v-model="isSnackbarVisible"
      timeout="-1"
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
            <template
              v-for="step in steps"
              :key="step.value"
            >
              <v-stepper-item
                :value="step.value"
                :title="step.title"
                class="pa-3 ml-3 mr-3"
                rounded="lg"
                :ripple="false"
              />
              <v-divider
                v-if="step.value > 0 && step.value < 8"
              />
            </template>
          </v-stepper-header>
        </v-stepper>
      </v-card>
    </v-snackbar>

    <!-- Main content area with vertical stepper -->
    <div ref="stepperContainer">
      <v-stepper-vertical
        v-model="displayStep"
        hide-actions
      >
        <template
          v-for="step in steps"
          :key="step.value"
        >
          <v-stepper-vertical-item
            :complete="currentStep > step.value"
            :step="`Step ${step.value}`"
            :value="step.value"
            editable
            @click="handleStepClick(step.value)"
          >
            <template #icon>
              <v-icon size="24">
                {{ currentStep > step.value ? 'mdi-check-circle' : 'mdi-circle-outline' }}
                {{ currentStep === step.value ? 'mdi-circle' : '' }}
                {{ currentStep < step.value ? 'mdi-circle-outline' : '' }}
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

            <!-- Step components -->
            <step1
              v-if="step.value === 1 && currentStep === 1"
              :form-data="grantsStore.formData[1]"
              @update:form-data="grantsStore.updateFormData(1, $event)"
              @validated="handleStepValidated"
              @go-back="handleGoBack"
            />
            <step2
              v-if="step.value === 2 && currentStep === 2"
              :form-data="grantsStore.formData[2]"
              :current-step="currentStep"
              @update:form-data="grantsStore.updateFormData(2, $event)"
              @validated="handleStepValidated"
              @go-back="handleGoBack"
            />
            <step3
              v-if="step.value === 3 && currentStep === 3"
              :form-data="grantsStore.formData[3]"
              :current-step="currentStep"
              @update:form-data="grantsStore.updateFormData(3, $event)"
              @validated="handleStepValidated"
              @go-back="handleGoBack"
            />
            <step4
              v-if="step.value === 4 && currentStep === 4"
              :form-data="grantsStore.formData[4]"
              :current-step="currentStep"
              @update:form-data="grantsStore.updateFormData(4, $event)"
              @validated="handleStepValidated"
              @go-back="handleGoBack"
            />
            <step5
              v-if="step.value === 5 && currentStep === 5"
              :form-data="grantsStore.formData[5]"
              :current-step="currentStep"
              @update:form-data="grantsStore.updateFormData(5, $event)"
              @validated="handleStepValidated"
              @go-back="handleGoBack"
            />
            <step6
              v-if="step.value === 6 && currentStep === 6"
              :form-data="grantsStore.formData[6]"
              :current-step="currentStep"
              @update:form-data="grantsStore.updateFormData(6, $event)"
              @validated="handleStepValidated"
              @go-back="handleGoBack"
            />
            <step7
              v-if="step.value === 7 && currentStep === 7"
              :form-data="grantsStore.formData[7]"
              :current-step="currentStep"
              @update:form-data="grantsStore.updateFormData(7, $event)"
              @validated="handleStepValidated"
              @go-back="handleGoBack"
            />
            <step8
              v-if="step.value === 8 && currentStep === 8"
              :form-data="grantsStore.formData[8]"
              :current-step="currentStep"
              @update:form-data="grantsStore.updateFormData(8, $event)"
              @validated="handleStepValidated"
              @go-back="handleGoBack"
            />
          </v-stepper-vertical-item>
        </template>
      </v-stepper-vertical>
    </div>
  </v-container>
</template>

<script setup lang="ts">
import { useDisplay } from 'vuetify'
import { VStepperVerticalItem } from 'vuetify/labs/VStepperVertical'
import { useRoute, useRouter, onBeforeRouteLeave } from 'vue-router'
import { useGrantsStore } from '@/stores/grants'
import { GrantStorage } from '@/utils/grant-storage'

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
const isSnackbarVisible = ref(true)
const displayStep = ref(1)
const submitting = ref(false)
const isDataLoaded = ref(false)
const hasUnsavedChanges = ref(false)
const isNavigating = ref(false)

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

// Step validation handling v2
// const handleStepValidated = async ({ valid, step }) => {
//   if (valid) {
//     try {
//       submitting.value = true

//       // Save current step data
//       await saveCurrentStepData()

//       // Proceed to next step if not on the last step
//       if (step < steps.length) {
//         currentStep.value = step + 1
//         displayStep.value = currentStep.value

//         // Update URL and load data for the next step
//         updateStepInURL(currentStep.value)
//         await loadStepData(currentStep.value)
//       } else {
//         // Complete the form if this was the last step
//         router.push('/grants')
//       }
//     } catch (error) {
//       console.error('Error saving step data:', error)
//     } finally {
//       submitting.value = false
//     }
//   }
// }

// Step validation handling - No validation for steps 2-8
const handleStepValidated = async ({ valid, step }) => {
  if (valid && !isNavigating.value) {
    try {
      isNavigating.value = true
      submitting.value = true

      // Save current step data
      await saveCurrentStepData()

      // Wait a moment to ensure data is saved
      await new Promise(resolve => setTimeout(resolve, 100));

      // Proceed to next step if not on the last step
      if (step < steps.length) {
        currentStep.value = step + 1
        displayStep.value = currentStep.value

        // Update URL and load data for the next step
        updateStepInURL(currentStep.value)
        await loadStepData(currentStep.value)
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
// Step click handler v2
// const handleStepClick = (stepValue) => {
//   // console.log('Step clicked:', stepValue, currentStep.value)
//   // if (stepValue === currentStep.value) return; // Skip if clicking current step

//   saveCurrentStepData().then(() => {
//     // Update both current step and display step
//     currentStep.value = stepValue;
//     displayStep.value = stepValue;

//     // Update URL and load data
//     updateStepInURL(stepValue);
//     loadStepData(stepValue);
//   }).catch(error => {
//     console.error('Failed to save data before step change:', error);
//   });
// };

const handleStepClick = (stepValue) => {
  if (stepValue === currentStep.value || isNavigating.value) return // Skip if clicking current step or already navigating

  isNavigating.value = true

  saveCurrentStepData().then(() => {
    // Update both current step and display step
    currentStep.value = stepValue;
    displayStep.value = stepValue;

    // Update URL and load data
    updateStepInURL(stepValue);
    loadStepData(stepValue);

    setTimeout(() => {
      isNavigating.value = false
    }, 500)
  }).catch(error => {
    console.error('Failed to save data before step change:', error);
    isNavigating.value = false
  });
};

// Go back handler for step navigation v2
// const handleGoBack = async () => {
//   if (currentStep.value > 1) {
//     try {
//       submitting.value = true

//       // Save current step before going back
//       await saveCurrentStepData()

//       // Go to previous step
//       currentStep.value -= 1
//       displayStep.value = currentStep.value

//       // Update URL and load previous step data
//       updateStepInURL(currentStep.value)
//       await loadStepData(currentStep.value)
//     } catch (error) {
//       console.error('Error saving step data before going back:', error)
//     } finally {
//       submitting.value = false
//     }
//   }
// }

// Go back handler for step navigation v3
const handleGoBack = async () => {
  if (currentStep.value > 1 && !isNavigating.value) {
    try {
      isNavigating.value = true
      submitting.value = true

      // Save current step before going back
      await saveCurrentStepData()

      // Go to previous step
      currentStep.value -= 1
      displayStep.value = currentStep.value

      // Update URL and load previous step data
      updateStepInURL(currentStep.value)
      await loadStepData(currentStep.value)
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

// // Load data for a specific step v2
// const loadStepData = async (step: number) => {
//   if (!route.query.id) return

//   const caseNumber = route.query.id as string
//   submitting.value = true

//   try {
//     await grantsStore.loadStepData(caseNumber, step)
//     hasUnsavedChanges.value = false
//   } catch (error) {
//     console.error(`Failed to load data for step ${step}:`, error)
//   } finally {
//     submitting.value = false
//   }
// }

// Load data for a specific step v3
const loadStepData = async (step: number) => {
  if (!route.query.id) return

  const caseNumber = route.query.id as string
  submitting.value = true
  isDataLoaded.value = false

  try {
    if (step === 1) {
      // Step 1 loads from the API
      await grantsStore.loadStepData(caseNumber, step)
    } else {
      // Steps 2-8 load from localStorage
      const stepData = GrantStorage.getStepData(caseNumber, step) || {}
      grantsStore.formData[step] = stepData

      // If no data exists yet for this step, initialize with empty object
      if (Object.keys(stepData).length === 0) {
        grantsStore.formData[step] = {}
      }
    }

    hasUnsavedChanges.value = false
    isDataLoaded.value = true
  } catch (error) {
    console.error(`Failed to load data for step ${step}:`, error)
  } finally {
    submitting.value = false
  }
}


// // Save current step data v2
// const saveCurrentStepData = async () => {
//   const step = currentStep.value
//   if (!route.query.id) return false

//   const caseNumber = route.query.id as string
//   submitting.value = true

//   try {
//     await grantsStore.saveStepData(step, grantsStore.formData[step])
//     hasUnsavedChanges.value = false
//     return true
//   } catch (error) {
//     console.error(`Failed to save data for step ${step}:`, error)
//     return false
//   } finally {
//     submitting.value = false
//   }
// }

// Save current step data v3
const saveCurrentStepData = async () => {
  const step = currentStep.value
  if (!route.query.id) return false

  const caseNumber = route.query.id as string
  submitting.value = true

  try {
    if (step === 1) {
      // Step 1 saves to the API
      await grantsStore.saveStepData(step, grantsStore.formData[step])
    } else {
      // Steps 2-8 save to localStorage
      GrantStorage.saveStepData(caseNumber, step, grantsStore.formData[step] || {})
    }

    hasUnsavedChanges.value = false
    return true
  } catch (error) {
    console.error(`Failed to save data for step ${step}:`, error)
    return false
  } finally {
    submitting.value = false
  }
}

// URL management
const updateStepInURL = (step: number) => {
  router.replace({
    query: { ...route.query, step: step.toString() }
  })
}

// Scroll to active step element
const scrollToActiveStep = () => {
  nextTick(() => {
    const activeStepElement = document.querySelector(`.step-${currentStep.value}`)

    if (activeStepElement) {
      const headerOffset = 100 // Adjust based on your header height
      const elementPosition = activeStepElement.getBoundingClientRect().top
      const offsetPosition = elementPosition + window.pageYOffset - headerOffset

      window.scrollTo({
        top: offsetPosition,
        behavior: 'smooth'
      })
    }
  })
}

// // Initialize data v2
// onMounted(async () => {
//   // Get case number and step from URL
//   const caseNumber = route.query.id as string
//   const stepParam = route.query.step

//   if (!caseNumber) {
//     // Redirect to grants list if no case number provided
//     router.push('/grants')
//     return
//   }

//   try {
//     // First load the grant to get its basic info
//     await grantsStore.loadGrant(caseNumber)

//     // Determine starting step (from URL, grant data, or default to 1)
//     let startStep = 1

//     if (stepParam) {
//       const stepValue = parseInt(stepParam as string, 10)
//       if (!isNaN(stepValue) && stepValue >= 1 && stepValue <= steps.length) {
//         startStep = stepValue
//       }
//     } else if (grantsStore.currentGrant?.current_step) {
//       startStep = grantsStore.currentGrant.current_step
//     }

//     // Set steps and update URL if needed
//     currentStep.value = startStep
//     displayStep.value = startStep

//     if (!stepParam) {
//       updateStepInURL(startStep)
//     }

//     // Load data for the starting step
//     await loadStepData(startStep)
//     isDataLoaded.value = true
//   } catch (error) {
//     console.error('Failed to initialize grant data:', error)
//   }
// })

// Initialize data v3
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
    } else if (grantsStore.currentGrant?.current_step) {
      startStep = grantsStore.currentGrant.current_step
    }

    // Set steps and update URL if needed
    currentStep.value = startStep
    displayStep.value = startStep

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

// Watchers
// Watch URL step parameter changes
watch(() => route.query.step, (newStepParam) => {
  if (newStepParam) {
    const newStep = parseInt(newStepParam as string, 10)
    if (!isNaN(newStep) && newStep >= 1 && newStep <= steps.length && newStep !== currentStep.value) {
      // If step changed in URL, save current step data before changing
      saveCurrentStepData().then(() => {
        currentStep.value = newStep
        displayStep.value = newStep
        loadStepData(newStep)
      }).catch(error => {
        console.error('Failed to save data before step change:', error)
      })
    }
  }
})

// Watch display step changes (from stepper UI)
watch(displayStep, (newStep) => {
  if (newStep !== currentStep.value) {
    saveCurrentStepData().then(() => {
      currentStep.value = newStep
      updateStepInURL(newStep)
      loadStepData(newStep)
    }).catch(error => {
      console.error('Failed to save data before step change:', error)
      displayStep.value = currentStep.value // Reset display step if save fails
    })
  }
})

// Watch for form data changes to detect unsaved changes
watch(() => grantsStore.formData, () => {
  hasUnsavedChanges.value = true
}, { deep: true })

// Route leave guard
onBeforeRouteLeave((to, from, next) => {
  // If there are unsaved changes, confirm before leaving
  if (hasUnsavedChanges.value) {
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
.sticky-header {
  position: sticky;
  top: 110px;
  z-index: 4;
  transition: box-shadow 0.3s ease, elevation 0.3s ease;
}

.elevation-0 {
  box-shadow: none !important;
  background-color: transparent !important;
}
</style>
