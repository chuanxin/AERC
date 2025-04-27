import { defineStore } from 'pinia'
import {
  createGrant,
  getGrantByCaseNumber,
  getGrantStepData,
  updateGrantStepData,
  type GrantCreateRequest,
  type GrantCreateResponse,
  type GrantStepData
} from '@/services/grantsService'
import { ApplicationError } from '@/utils/asyncHelpers'
import { GrantStorage } from '@/utils/grant-storage'

/**
 * Grants Store - Centralized state management for grant applications
 *
 * Handles both API and localStorage storage with a unified interface.
 * Current implementation: Step 1 uses API, Steps 2-8 use localStorage
 */
export const useGrantsStore = defineStore('grants', () => {
  // State
  const currentGrant = ref<GrantCreateResponse | null>(null)
  const currentStep = ref<number>(1)
  const isLoading = ref<boolean>(false)
  const isSaving = ref<boolean>(false)
  const error = ref<string | null>(null)
  const lastSavedAt = ref<Date | null>(null)

  // Form data for all steps
  const formData = reactive<Record<number, any>>({
    1: {}, // Step 1 form data (API)
    2: {}, // Step 2 form data (localStorage)
    3: {}, // Step 3 form data (localStorage)
    4: {}, // Step 4 form data (localStorage)
    5: {}, // Step 5 form data (localStorage)
    6: {}, // Step 6 form data (localStorage)
    7: {}, // Step 7 form data (localStorage)
    8: {}, // Step 8 form data (localStorage)
  })

  // Request cache to prevent duplicate API calls
  const requestCache = reactive<Record<string, any>>({})

  // Getters
  const isGrantLoaded = computed(() => !!currentGrant.value)
  const caseNumber = computed(() => currentGrant.value?.case_number || '')
  const status = computed(() => currentGrant.value?.status || '')
  const lastSavedTime = computed(() => lastSavedAt.value?.toLocaleTimeString() || '')

  // Form status
  const hasUnsavedChanges = ref(false)

  /**
   * Create a new grant application
   * @param {GrantCreateRequest} projectData - Grant creation data
   * @returns {Promise<GrantCreateResponse>} The created grant
   */
  const createProject = async (projectData: GrantCreateRequest) => {
    isLoading.value = true
    error.value = null

    try {
      const result = await createGrant(projectData)
      currentGrant.value = result

      // Initialize local storage for this case
      GrantStorage.saveGrantData(result.case_number, {
        caseNumber: result.case_number,
        status: result.status,
        createdAt: new Date().toISOString(),
        steps: {}
      })

      return result
    } catch (err: unknown) {
      handleError(err, 'createProject')
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Load a grant by case number
   * @param {string} caseNumber - The grant case number
   * @returns {Promise<GrantCreateResponse>} The loaded grant
   */
  const loadGrant = async (caseNumber: string) => {
    isLoading.value = true
    error.value = null

    try {
      // Cache key for this request
      const cacheKey = `loadGrant_${caseNumber}`

      // Return cached result if available and less than 5 minutes old
      if (requestCache[cacheKey] &&
          (Date.now() - requestCache[cacheKey].timestamp) < 300000) {
        currentGrant.value = requestCache[cacheKey].data
        return requestCache[cacheKey].data
      }

      // Try from API first
      try {
        const data = await getGrantByCaseNumber(caseNumber)
        currentGrant.value = data

        // Cache the result
        requestCache[cacheKey] = {
          data,
          timestamp: Date.now()
        }

        return data
      } catch (apiError) {
        console.warn(`API error for grant ${caseNumber}, falling back to localStorage:`, apiError)

        // Try to load from localStorage if API fails
        const localData = GrantStorage.getGrant(caseNumber)
        if (localData) {
          // Create a simplified grant response object
          const localGrantResponse = {
            case_number: localData.caseNumber,
            status: localData.status || 'draft',
            created_at: localData.createdAt || new Date().toISOString(),
            updated_at: localData.updatedAt || new Date().toISOString()
          } as GrantCreateResponse

          currentGrant.value = localGrantResponse
          return localGrantResponse
        }

        // If neither source has data, re-throw the original error
        throw apiError
      }
    } catch (err) {
      handleError(err, 'loadGrant')
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Load data for a specific step
   * @param {string} caseNumber - The grant case number
   * @param {number} step - The step number
   * @returns {Promise<any>} The step data
   */
  const loadStepData = async (caseNumber: string, step: number) => {
    // Don't do anything if a load is already in progress
    if (isLoading.value) return null

    isLoading.value = true
    error.value = null
    currentStep.value = step

    try {
      let data: any = null

      // Step 1 loads from API, others from localStorage
      if (step === 1) {
        try {
          data = await getGrantStepData(caseNumber, step)
        } catch (apiError) {
          console.warn(`API error loading step ${step}, falling back to localStorage:`, apiError)

          // Try localStorage as fallback
          data = GrantStorage.getStepData(caseNumber, step) || {}
        }
      } else {
        // Steps 2-8 load from localStorage
        data = GrantStorage.getStepData(caseNumber, step) || {}
      }

      // Initialize form data with loaded data
      formData[step] = { ...data, valid: true }

      // Reset unsaved changes flag
      hasUnsavedChanges.value = false

      return data
    } catch (err) {
      handleError(err, 'loadStepData')

      // Initialize with empty object on error
      formData[step] = { valid: true }

      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Save data for a specific step
   * @param {number} step - The step number
   * @param {any} data - The step data to save
   * @returns {Promise<any>} The saved data
   */
  const saveStepData = async (step: number, data: any) => {
    if (!currentGrant.value?.case_number) {
      error.value = '無法儲存：尚未載入案件'
      return null
    }

    isSaving.value = true
    error.value = null
    const caseNumber = currentGrant.value.case_number

    try {
      let savedData: any = null

      // Step 1 saves to API, others to localStorage
      if (step === 1) {
        try {
          savedData = await updateGrantStepData(caseNumber, step, data)
        } catch (apiError) {
          console.warn(`API error saving step ${step}, falling back to localStorage:`, apiError)

          // Fallback to localStorage
          GrantStorage.saveStepData(caseNumber, step, data)
          savedData = data
        }
      } else {
        // Steps 2-8 save to localStorage
        GrantStorage.saveStepData(caseNumber, step, data)
        savedData = data
      }

      // Update form data
      formData[step] = { ...data, valid: true }

      // Update last saved timestamp
      lastSavedAt.value = new Date()

      // Reset unsaved changes flag
      hasUnsavedChanges.value = false

      return savedData
    } catch (err) {
      handleError(err, 'saveStepData')
      throw err
    } finally {
      isSaving.value = false
    }
  }

  /**
   * Update form data for a specific step
   * @param {number} step - The step number
   * @param {any} data - The form data to update
   */
  const updateFormData = (step: number, data: any) => {
    // Mark that we have unsaved changes
    hasUnsavedChanges.value = true

    // Update the form data
    formData[step] = { ...formData[step], ...data }
  }

  /**
   * Reset step data to last saved state
   * @param {number} step - The step number
   */
  const resetStepData = async (step: number) => {
    if (!currentGrant.value?.case_number) return

    const caseNumber = currentGrant.value.case_number

    try {
      isLoading.value = true

      // Reload data from storage
      await loadStepData(caseNumber, step)

      // Reset unsaved changes flag
      hasUnsavedChanges.value = false
    } catch (err) {
      handleError(err, 'resetStepData')
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Clear error message
   */
  const clearError = () => {
    error.value = null
  }

  /**
   * Clear current grant data
   */
  const clearCurrentGrant = () => {
    currentGrant.value = null
    currentStep.value = 1
    Object.keys(formData).forEach(key => {
      formData[Number(key)] = {}
    })
    hasUnsavedChanges.value = false
    lastSavedAt.value = null
  }

  /**
   * Save all unsaved changes
   * @returns {Promise<boolean>} Whether the save was successful
   */
  const saveAllChanges = async (): Promise<boolean> => {
    if (!currentGrant.value?.case_number || !hasUnsavedChanges.value) return true

    try {
      isSaving.value = true

      // Save the current step data
      await saveStepData(currentStep.value, formData[currentStep.value])

      // Reset unsaved changes flag
      hasUnsavedChanges.value = false

      return true
    } catch (err) {
      handleError(err, 'saveAllChanges')
      return false
    } finally {
      isSaving.value = false
    }
  }

  /**
   * Handle errors in a consistent way
   * @param {unknown} err - The error
   * @param {string} source - The source of the error
   */
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

  /**
   * Export grant application as a backup file
   * @returns {string} Backup data as JSON string
   */
  const exportGrantBackup = (): string => {
    if (!currentGrant.value?.case_number) return '';

    try {
      const caseNumber = currentGrant.value.case_number;
      return GrantStorage.createBackup();
    } catch (error) {
      console.error('Failed to export grant backup:', error);
      return '';
    }
  }

  /**
   * Import grant application from a backup file
   * @param {string} backupData - The backup data as JSON string
   * @returns {boolean} Whether the import was successful
   */
  const importGrantBackup = (backupData: string): boolean => {
    try {
      return GrantStorage.restoreFromBackup(backupData);
    } catch (error) {
      console.error('Failed to import grant backup:', error);
      return false;
    }
  }

  return {
    // State
    currentGrant,
    currentStep,
    isLoading,
    isSaving,
    error,
    formData,
    lastSavedAt,
    hasUnsavedChanges,

    // Getters
    isGrantLoaded,
    caseNumber,
    status,
    lastSavedTime,

    // Actions
    loadGrant,
    loadStepData,
    saveStepData,
    updateFormData,
    resetStepData,
    createProject,
    clearCurrentGrant,
    clearError,
    saveAllChanges,
    exportGrantBackup,
    importGrantBackup
  }
})
