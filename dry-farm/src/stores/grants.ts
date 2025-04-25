import { defineStore } from 'pinia'
import {
  createGrant,
  getGrantByCaseNumber,
  getGrantStepData,
  updateGrantStepData,
  type GrantCreateRequest,
  type GrantCreateResponse,
  type GrantStepData,
  type Step1Data
} from '@/services/grantsService'
import { ApplicationError } from '@/utils/asyncHelpers'

export const useGrantsStore = defineStore('grants', () => {
  // State
  const currentGrant = ref<GrantCreateResponse | null>(null)
  const currentStep = ref<number>(1)
  const stepData = reactive<Record<number, GrantStepData>>({})
  const isLoading = ref<boolean>(false)
  const error = ref<string | null>(null)
  const formData = reactive<Record<number, any>>({
    1: {}, // Step 1 form data
    2: {}, // Step 2 form data
    3: {}, // Step 3 form data
    4: {}, // Step 4 form data
    5: {}, // Step 5 form data
    6: {}, // Step 6 form data
    7: {}, // Step 7 form data
    8: {}, // Step 8 form data
  })

  // Getters
  const isGrantLoaded = computed(() => !!currentGrant.value)
  const currentStepData = computed(() => stepData[currentStep.value] || null)
  const caseNumber = computed(() => currentGrant.value?.case_number || '')
  const status = computed(() => currentGrant.value?.status || '')

  // Projects tracking
  const draftProjects = reactive<Record<string, GrantCreateRequest>>({})

  // Actions
  const createProject = async (projectData: GrantCreateRequest) => {
    isLoading.value = true
    error.value = null

    try {
      const result = await createGrant(projectData)
      currentGrant.value = result
      return result
    } catch (err: unknown) {
      if (err instanceof ApplicationError) {
        error.value = err.message
        console.error(`${err.source}: ${err.message}`)
      } else {
        error.value = '建立專案時發生未知錯誤'
        console.error('未知錯誤:', err)
      }
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const loadGrant = async (caseNumber: string) => {
    isLoading.value = true
    error.value = null

    try {
      const data = await getGrantByCaseNumber(caseNumber)
      currentGrant.value = data
      return data
    } catch (err) {
      handleError(err, 'loadGrant')
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const loadStepData = async (caseNumber: string, step: number) => {
    isLoading.value = true
    error.value = null
    currentStep.value = step

    try {
      const data = await getGrantStepData(caseNumber, step)
      stepData[step] = data

      // Initialize form data with step data
      initializeFormData(step, data)

      return data
    } catch (err) {
      handleError(err, 'loadStepData')
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const saveStepData = async (step: number, data: any) => {
    if (!currentGrant.value?.case_number) {
      error.value = '無法儲存：尚未載入案件'
      return null
    }

    isLoading.value = true
    error.value = null

    try {
      const result = await updateGrantStepData(currentGrant.value.case_number, step, data)

      // Update the local state
      stepData[step] = result

      // Update form data
      initializeFormData(step, result)

      return result
    } catch (err) {
      handleError(err, 'saveStepData')
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const updateFormData = (step: number, data: any) => {
    formData[step] = { ...formData[step], ...data }
  }

  const resetStepData = (step: number) => {
    if (stepData[step]) {
      initializeFormData(step, stepData[step])
    }
  }

  // Save draft project data locally (temporary storage)
  const saveDraftProject = (id: string, data: GrantCreateRequest) => {
    draftProjects[id] = data
  }

  // Get draft project data
  const getDraftProject = (id: string): GrantCreateRequest | null => {
    return draftProjects[id] || null
  }

  // Clear current grant data
  const clearCurrentGrant = () => {
    currentGrant.value = null
  }

  // Helper functions
  const initializeFormData = (step: number, data: any) => {
    // Initialize form data based on the step
    if (step === 1) {
      // Map step 1 data to form fields
      formData[1] = {
        name: data.name || '',
        id: data.id || '',
        phone: data.phone || '',
        county: data.county || '',
        town: data.town || '',
        village: data.village || '',
        address: data.address || '',
        manager: data.manager || '',
        department: data.department || '',
        departmentId: data.departmentId || null,
        caseNumber: data.caseNumber || '',
        receivedDate: data.receivedDate || '',
        receivedTime: data.receivedTime || '',
        valid: true
      }
    } else if (step === 2) {
      // Initialize step 2 form data
      formData[2] = {
        // Map step 2 specific fields here
        valid: true
      }
    }
    // Add similar mappings for other steps
  }

  const handleError = (err: unknown, source: string) => {
    if (err instanceof ApplicationError) {
      error.value = err.message
      console.error(`${source}: ${err.message}`)
    } else if (err instanceof Error) {
      error.value = err.message
      console.error(`${source}: ${err.message}`)
    } else {
      error.value = '發生未知錯誤'
      console.error(`${source}: Unknown error`, err)
    }
  }

  return {
    // State
    currentGrant,
    currentStep,
    stepData,
    isLoading,
    error,
    formData,

    // Getters
    isGrantLoaded,
    currentStepData,
    caseNumber,
    status,

    // Actions
    loadGrant,
    loadStepData,
    saveStepData,
    updateFormData,
    resetStepData,
    createProject,
    saveDraftProject,
    getDraftProject,
    clearCurrentGrant
  }
})
