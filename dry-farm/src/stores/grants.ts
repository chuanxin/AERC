import { defineStore } from 'pinia'
import {
  createGrant,
  getGrantByCaseNumber,
  getGrantStepData,
  updateGrantStepData,
  updateGrantStepDataWithTracking,
  updateCurrentStep as updateCurrentStepAPI,
  type GrantCreateResponse,
  type GrantStepDataUpdateRequest
} from '@/services/grantsService'
import { ApplicationError } from '@/utils/asyncHelpers'
import { GrantStorage } from '@/utils/grant-storage'
import type { GrantCreateRequest } from '@/types/grantForms'

// 🔧 同步特定字段到 localStorage 的工具函數
function syncFieldsToLocalStorage(caseNumber: string, stepData: Record<string, unknown>, functionName: string): void {
  const fieldsToSync = ['name', 'isDisasterCase', 'disasterCaseDescription', 'undertracker']
  const hasFieldsToSync = fieldsToSync.some(field => field in stepData)

  if (hasFieldsToSync) {
    const grantData = GrantStorage.getGrant(caseNumber)
    if (grantData) {
      // 更新對應的字段 (注意字段映射)
      if ('name' in stepData) grantData.applicantName = String(stepData.name || '')
      if ('isDisasterCase' in stepData) grantData.isDisasterCase = Boolean(stepData.isDisasterCase)
      if ('disasterCaseDescription' in stepData) grantData.disasterCaseDescription = String(stepData.disasterCaseDescription || '')
      if ('undertracker' in stepData) grantData.undertracker = String(stepData.undertracker || '')

      // 更新時間戳
      grantData.updatedAt = new Date().toISOString()

      // 保存回 localStorage
      GrantStorage.saveGrantData(caseNumber, grantData)
      console.log(`[grantsStore.${functionName}] Synced step1 fields to localStorage:`,
        fieldsToSync.filter(field => field in stepData))
    }
  }
}

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
  const formData = reactive<Record<number, Record<string, unknown>>>({
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
  const requestCache = reactive<Record<string, { data: GrantCreateResponse; timestamp: number }>>({})

  // Getters
  const isGrantLoaded = computed(() => !!currentGrant.value)
  const caseNumber = computed(() => currentGrant.value?.case_number || '')
  const status = computed(() => currentGrant.value?.status || '')
  const lastSavedTime = computed(() => lastSavedAt.value?.toLocaleTimeString() || '')

  // Form status
  const hasUnsavedChanges = ref(false)

  // 追蹤變更的詳細資訊
  const previousFormData = ref<Record<number, Record<string, unknown>>>({})
  const changedFields = ref<Record<number, string[]>>({})

  // 生成會話 ID
  const generateSessionId = (): string => {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  }

  // 追蹤欄位變更
  const trackFieldChanges = (step: number, newData: Record<string, unknown>) => {
    const oldData = previousFormData.value[step] || {}
    const changed: string[] = []

    // 檢查新增或修改的欄位
    Object.keys(newData).forEach(key => {
      if (key !== 'valid' && JSON.stringify(oldData[key]) !== JSON.stringify(newData[key])) {
        changed.push(key)
      }
    })

    // 檢查刪除的欄位
    Object.keys(oldData).forEach(key => {
      if (key !== 'valid' && !(key in newData)) {
        changed.push(key)
      }
    })

    changedFields.value[step] = changed
    return changed
  }

  /**
   * Create a new grant application
   * @param {GrantCreateRequest} projectData - Grant creation data
   * @returns {Promise<GrantCreateResponse>} The created grant
   */
  const createProject = async (projectData: GrantCreateRequest) => {
    isLoading.value = true;
    error.value = null;
    console.log('[grantsStore.createProject] Attempting to create project with data:', JSON.stringify(projectData, null, 2)); // Log 1

    try {
      console.log('[grantsStore.createProject] Calling createGrant API service...');
      const result = await createGrant(projectData);
      console.log('[grantsStore.createProject] API createGrant successful. Result:', JSON.stringify(result, null, 2)); // Log 2
      currentGrant.value = result;

      console.log(`[grantsStore.createProject] Attempting to save grant data to GrantStorage for case number: ${result.case_number}`); // Log 4

      // 💡 使用現有類型 + satisfies 操作符的優雅解決方案
      // 直接從 GrantCreateResponse 和 GrantCreateRequest 映射到 GrantData
      // 確保類型安全，同時保持 IntelliSense 和編譯時檢查
      const grantData = {
        // 從 GrantCreateResponse 映射
        caseNumber: result.case_number,
        applicantName: result.applicant_name,
        stepName: result.status,
        isDisasterCase: result.is_disaster_case ?? false,
        disasterCaseDescription: result.disaster_case_description ?? '',
        undertracker: result.undertracker ?? '',

        // 從 GrantCreateRequest 映射
        officeName: projectData.office,

        // 新案件的默認值
        // currentStep: 1,
        createdAt: new Date().toISOString(),
        // updatedAt: new Date().toISOString(),
        stepsData: {}
      } satisfies import('@/utils/grant-storage').GrantData; // 確保類型符合 grant-storage 的 GrantData 接口

      GrantStorage.saveGrantData(result.case_number, grantData);
      console.log(`[grantsStore.createProject] GrantStorage.saveGrantData successful with complete data for case number: ${result.case_number}`); // Log 5
      console.log(`[grantsStore.createProject] Mapped fields from existing types:`, Object.keys(grantData));

      return result;
    } catch (err: unknown) {
      console.error('[grantsStore.createProject] Error during project creation:', err); // Log for any error
      handleError(err, 'createProject');
      throw err;
    } finally {
      isLoading.value = false;
      console.log('[grantsStore.createProject] createProject finished.');
    }
  };

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

        // 從 localStorage 取得 currentStep，如果 API 資料中沒有的話
        const localData = GrantStorage.getGrant(caseNumber);
        if (localData && localData.currentStep) {
          currentStep.value = localData.currentStep;
          (data as GrantCreateResponse & { current_step: number }).current_step = localData.currentStep;
          console.log(`[grantsStore.loadGrant] Using currentStep ${localData.currentStep} from localStorage for API-loaded grant ${caseNumber}`);
        } else {
          // 預設為步驟 1
          currentStep.value = 1;
          (data as GrantCreateResponse & { current_step: number }).current_step = 1;
          console.log(`[grantsStore.loadGrant] No currentStep found, defaulting to 1 for API-loaded grant ${caseNumber}`);
        }

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
          // TODOCreate a simplified grant response object
          const localGrantResponse = {
            case_number: localData.caseNumber,
            status: localData.stepName || 'draft',
            created_at: localData.createdAt || new Date().toISOString(),
            updated_at: localData.updatedAt || new Date().toISOString(),
            current_step: localData.currentStep,
          } as Partial<GrantCreateResponse>

          // 同時設定當前步驟
          if (localData.currentStep) {
            currentStep.value = localData.currentStep;
            (localGrantResponse as GrantCreateResponse & { current_step: number }).current_step = localData.currentStep;
            console.log(`[grantsStore.loadGrant] Loaded currentStep ${localData.currentStep} from localStorage for grant ${caseNumber}`);
          } else {
            // 如果沒有 currentStep，預設為 1
            currentStep.value = 1;
            (localGrantResponse as GrantCreateResponse & { current_step: number }).current_step = 1;
            console.log(`[grantsStore.loadGrant] No currentStep found, defaulting to 1 for grant ${caseNumber}`);
          }

          currentGrant.value = localGrantResponse as GrantCreateResponse
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
      let data: Record<string, unknown> | null = null

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

      // 初始化 previousFormData 以便追蹤變更
      previousFormData.value[step] = { ...data, valid: true }

      // 清除變更追蹤
      changedFields.value[step] = []

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
   * Save data for a specific step with enhanced tracking
   * @param {number} step - The step number
   * @param {Record<string, unknown>} data - The step data to save
   * @returns {Promise<Record<string, unknown>>} The saved data
   */
  const saveStepData = async (step: number, data: Record<string, unknown>) => {
    if (!currentGrant.value?.case_number) {
      error.value = '無法儲存：尚未載入案件'
      return null
    }

    isSaving.value = true
    error.value = null
    const caseNumber = currentGrant.value.case_number

    try {
      // 準備追蹤資訊
      const sessionId = generateSessionId()
      const changed = changedFields.value[step] || trackFieldChanges(step, data)
      const oldData = previousFormData.value[step] || {}

      let savedData: Record<string, unknown> | null = null

      // Step 1 saves to API, others to localStorage
      if (step === 1) {
        try {
          if (changed.length > 0) {
            // 使用擴展的追蹤版本
            const updateRequest: GrantStepDataUpdateRequest = {
              data: data,
              action_type: 'manual_save',
              changed_fields: changed,
              old_value: oldData,
              session_id: sessionId,
              notes: `手動保存步驟 ${step} 資料，變更欄位: ${changed.join(', ')}`
            }

            savedData = await updateGrantStepDataWithTracking(caseNumber, step, updateRequest)
          } else {
            savedData = await updateGrantStepData(caseNumber, step, data)
          }

          // 🔧 同步特定字段到 localStorage
          syncFieldsToLocalStorage(caseNumber, data, 'saveStepData')
        } catch (apiError) {
          console.warn(`API error saving step ${step}, falling back to localStorage:`, apiError)

          // Fallback to localStorage
          GrantStorage.saveStepData(caseNumber, step, data)
          savedData = data
        }
      } else {
        // Steps 2-8 save to localStorage
        // console.log(`💾 Saving step ${step} to localStorage with data:`, JSON.stringify(data, null, 2));
        GrantStorage.saveStepData(caseNumber, step, data)
        // console.log('✅ GrantStorage.saveStepData completed');
        savedData = data
      }

      // Update form data
      formData[step] = { ...data, valid: true }
      // console.log(`📊 Updated formData[${step}] after save:`, JSON.stringify(formData[step], null, 2));

      // 更新 previousFormData 以便下次追蹤變更
      previousFormData.value[step] = { ...formData[step] }

      // 清除變更追蹤
      changedFields.value[step] = []

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
   * @param {Record<string, unknown>} data - The form data to update
   */
  const updateFormData = (step: number, data: Record<string, unknown>) => {
    // console.log(`🔄 grantsStore.updateFormData called for step ${step}`);
    // console.log('📥 Received data keys:', Object.keys(data));
    // console.log('📥 Current formData[' + step + '] before update:', JSON.stringify(formData[step], null, 2));

    // 保存當前數據作為 previousFormData 以便追蹤變更
    if (!previousFormData.value[step]) {
      previousFormData.value[step] = { ...formData[step] }
    }

    // Mark that we have unsaved changes
    hasUnsavedChanges.value = true
    // console.log('✅ hasUnsavedChanges set to true');

    // 追蹤變更的欄位
    trackFieldChanges(step, data)

    // Update the form data
    formData[step] = { ...formData[step], ...data }
    // console.log('📥 Updated formData[' + step + ']:', JSON.stringify(formData[step], null, 2));
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

    // 清理追蹤相關的狀態
    Object.keys(previousFormData.value).forEach(key => {
      previousFormData.value[Number(key)] = {}
    })
    Object.keys(changedFields.value).forEach(key => {
      changedFields.value[Number(key)] = []
    })

    hasUnsavedChanges.value = false
    lastSavedAt.value = null
  }

  /**
   * Save all unsaved changes with enhanced tracking
   * @returns {Promise<boolean>} Whether the save was successful
   */
  const saveAllChanges = async (): Promise<boolean> => {
    // console.log('💾 grantsStore.saveAllChanges called');
    // console.log('📊 currentGrant.case_number:', currentGrant.value?.case_number);
    // console.log('📊 hasUnsavedChanges:', hasUnsavedChanges.value);
    // console.log('📊 currentStep:', currentStep.value);

    if (!currentGrant.value?.case_number || !hasUnsavedChanges.value) {
      // console.log('⚠️ Skipping save - no case number or no unsaved changes');
      return true;
    }

    try {
      isSaving.value = true
      // console.log('💾 Starting to save step data...');

      const step = currentStep.value
      const stepData = formData[step]
      const caseNumber = currentGrant.value.case_number

      // 準備追蹤資訊
      const sessionId = generateSessionId()
      const changed = changedFields.value[step] || []
      const oldData = previousFormData.value[step] || {}

      // 根據步驟使用不同的保存方式
      if (step === 1) {
        // Step 1 使用 API 並支援詳細追蹤
        try {
          if (changed.length > 0) {
            // 使用擴展的追蹤版本
            const updateRequest: GrantStepDataUpdateRequest = {
              data: stepData,
              action_type: 'step_data_update',
              changed_fields: changed,
              old_value: oldData,
              session_id: sessionId,
              notes: `自動保存步驟 ${step} 資料，變更欄位: ${changed.join(', ')}`
            }

            await updateGrantStepDataWithTracking(caseNumber, step, updateRequest)
          } else {
            // 沒有變更，使用一般保存
            await updateGrantStepData(caseNumber, step, stepData)
          }

          // 🔧 同步特定字段到 localStorage
          syncFieldsToLocalStorage(caseNumber, stepData, 'saveAllChanges')
        } catch (apiError) {
          console.warn(`API error saving step ${step}, falling back to localStorage:`, apiError)

          // Fallback to localStorage
          GrantStorage.saveStepData(caseNumber, step, stepData)
        }
      } else {
        // Steps 2-8 保存到 localStorage
        // console.log(`💾 Saving step ${step} to localStorage with data:`, JSON.stringify(stepData, null, 2));
        GrantStorage.saveStepData(caseNumber, step, stepData)
        // console.log('✅ GrantStorage.saveStepData completed');
      }

      // Update form data
      formData[step] = { ...stepData, valid: true }
      // console.log(`📊 Updated formData[${step}] after save:`, JSON.stringify(formData[step], null, 2));

      // 更新 previousFormData 以便下次追蹤變更
      previousFormData.value[step] = { ...formData[step] }

      // 清除變更追蹤
      changedFields.value[step] = []

      // Update last saved timestamp
      lastSavedAt.value = new Date()

      // Reset unsaved changes flag
      hasUnsavedChanges.value = false
      // console.log('✅ hasUnsavedChanges reset to false');

      return true
    } catch (err) {
      // console.error('❌ Error in saveAllChanges:', err);
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

  const updateCurrentStep = async (step: number) => {
    // 驗證步驟數值有效性
    if (typeof step !== 'number' || isNaN(step) || step < 1 || step > 9) {
      console.warn(`[grantsStore.updateCurrentStep] Invalid step value: ${step}, defaulting to 1`);
      step = 1;
    }

    // 記錄步驟變更前的狀態以便追蹤
    const previousStep = currentStep.value;
    const sessionId = generateSessionId();

    // 更新 store 中的 currentStep
    currentStep.value = step;

    // 如果有 currentGrant，更新其 current_step 屬性
    if (currentGrant.value) {
      // 確保 currentGrant 有 current_step 屬性（TypeScript 可能需要轉型）
      (currentGrant.value as GrantCreateResponse & { current_step: number }).current_step = step;

      // 保存到 localStorage - 只更新當前案件的 current_step
      if (currentGrant.value.case_number) {
        const grantData = GrantStorage.getGrant(currentGrant.value.case_number);
        if (grantData) {
          // 只更新 currentStep，不影響其他數據
          grantData.currentStep = step;
          grantData.updatedAt = new Date().toISOString();
          // 保存回 localStorage
          GrantStorage.saveGrantData(currentGrant.value.case_number, grantData);
          console.log(`[grantsStore] Updated current_step to ${step} for grant ${currentGrant.value.case_number}`);

          // 同步到資料庫 - 如果有步驟變更，記錄追蹤資訊
          try {
            if (previousStep !== step) {
              // 有步驟變更，使用追蹤版本的 API
              const stepChangeData: GrantStepDataUpdateRequest = {
                data: { current_step: step },
                action_type: 'step_change',
                changed_fields: ['current_step'],
                old_value: { current_step: previousStep },
                session_id: sessionId,
                notes: `使用者從步驟 ${previousStep} 導航至步驟 ${step}`
              };

              // 這裡我們復用 updateGrantStepDataWithTracking，但只是更新 current_step
              await updateGrantStepDataWithTracking(currentGrant.value.case_number, step, stepChangeData);
              console.log(`[grantsStore] Successfully tracked step change from ${previousStep} to ${step}`);
            } else {
              // 沒有實際變更，使用一般 API
              await updateCurrentStepAPI(currentGrant.value.case_number, step);
            }
            console.log(`[grantsStore] Successfully synced current_step ${step} to database for grant ${currentGrant.value.case_number}`);
          } catch (error) {
            console.warn(`[grantsStore] Failed to sync current_step to database for grant ${currentGrant.value.case_number}:`, error);
            // 即使同步到資料庫失敗，localStorage 的更新依然有效，讓用戶能繼續操作
          }
        } else {
          console.warn(`[grantsStore] Grant data not found for case number: ${currentGrant.value.case_number}`);
        }
      }
    } else {
      console.warn(`[grantsStore.updateCurrentStep] No currentGrant loaded, step ${step} not saved to localStorage`);
    }

    return step;
  }

  /**
   * Track form validation events
   * @param step - Current step being validated
   * @param validationResult - Result of validation (success/failure)
   * @param errors - Array of validation errors if any
   */
  const trackFormValidation = async (step: number, validationResult: 'success' | 'failure', errors: string[] = []) => {
    if (!currentGrant.value?.case_number) return;

    try {
      const sessionId = generateSessionId();
      const validationData: GrantStepDataUpdateRequest = {
        data: {
          validation_result: validationResult,
          validation_errors: errors,
          validated_at: new Date().toISOString()
        },
        action_type: 'form_validation',
        changed_fields: ['validation_status'],
        old_value: {},
        session_id: sessionId,
        notes: `表單驗證${validationResult === 'success' ? '成功' : '失敗'} - 步驟 ${step}${errors.length > 0 ? `，錯誤: ${errors.join(', ')}` : ''}`
      };

      await updateGrantStepDataWithTracking(currentGrant.value.case_number, step, validationData);
      console.log(`[grantsStore] Successfully tracked form validation for step ${step}: ${validationResult}`);
    } catch (error) {
      console.warn(`[grantsStore] Failed to track form validation for step ${step}:`, error);
    }
  };

  /**
   * Track file upload/delete operations
   * @param step - Current step
   * @param operation - Type of file operation
   * @param fileName - Name of the file
   * @param fileType - Type/category of the file
   */
  const trackFileOperation = async (step: number, operation: 'upload' | 'delete', fileName: string, fileType?: string) => {
    if (!currentGrant.value?.case_number) return;

    try {
      const sessionId = generateSessionId();
      const fileData: GrantStepDataUpdateRequest = {
        data: {
          file_operation: operation,
          file_name: fileName,
          file_type: fileType,
          operation_time: new Date().toISOString()
        },
        action_type: 'file_operation',
        changed_fields: ['attachments'],
        old_value: {},
        session_id: sessionId,
        notes: `檔案${operation === 'upload' ? '上傳' : '刪除'} - 步驟 ${step}，檔案: ${fileName}${fileType ? `，類型: ${fileType}` : ''}`
      };

      await updateGrantStepDataWithTracking(currentGrant.value.case_number, step, fileData);
      console.log(`[grantsStore] Successfully tracked file ${operation} for step ${step}: ${fileName}`);
    } catch (error) {
      console.warn(`[grantsStore] Failed to track file ${operation} for step ${step}:`, error);
    }
  };

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
    importGrantBackup,
    updateCurrentStep,

    // Tracking functions
    trackFormValidation,
    trackFileOperation
  }
})
