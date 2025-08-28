import { defineStore } from 'pinia'
import {
  createGrant,
  getGrantByCaseNumber,
  getGrantStepData,
  updateGrantStepData,
  updateGrantStepDataWithTracking,
  updateCurrentStep as updateCurrentStepAPI,
  hybridGrantService,
  grantCacheService,
  type GrantCreateResponse,
  type GrantStepDataUpdateRequest,
  type GrantListItem,
  type GrantListParams,
  type ServiceStatus,
} from '@/services/grantsService'
import { ApplicationError } from '@/utils/asyncHelpers'
import { GrantStorage } from '@/utils/grant-storage'
import type { GrantCreateRequest } from '@/types/grantForms'
import { debounce } from 'lodash-es'

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
    // 🚫 移除 step9，變更設計功能不使用傳統的步驟流程
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
      // 🔥 Linus式修復：在創建新案件前先清空所有資料，確保乾淨的狀態
      console.log('[grantsStore.createProject] 清空前一個案件的資料，準備建立新案件...');
      clearCurrentGrant();

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

      // 🆕 Step 1 從 API 讀取，Steps 2-8 優先從 API (grant_versions) 讀取，失敗時回退到 localStorage
      if (step === 1) {
        try {
          data = await getGrantStepData(caseNumber, step)
        } catch (apiError) {
          console.warn(`API error loading step ${step}, falling back to localStorage:`, apiError)

          // Try localStorage as fallback
          data = GrantStorage.getStepData(caseNumber, step) || {}
        }
      } else if (step >= 2 && step <= 8) {
        // 🆕 Steps 2-8 優先從 API (grant_versions.all_steps_data.steps[step]) 讀取
        try {
          console.log(`🎯 Loading step ${step} from grant_versions API...`)
          data = await getGrantStepData(caseNumber, step)
          console.log(`✅ Successfully loaded step ${step} from API:`, Object.keys(data || {}))
        } catch (apiError) {
          console.warn(`❌ API error loading step ${step}, falling back to localStorage:`, apiError)

          // Try localStorage as fallback
          data = GrantStorage.getStepData(caseNumber, step) || {}
          console.log(`💾 Using localStorage data for step ${step}:`, Object.keys(data || {}))
        }
      } else {
        // Invalid step number
        console.warn(`Invalid step number: ${step}`)
        data = {}
      }

      // Initialize form data with loaded data and case number tracking
      formData[step] = { ...data, valid: true, _caseNumber: caseNumber }

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
      } else if (step >= 2 && step <= 8) {
        // 🆕 Steps 2-8 使用現有 API 儲存到 grant_versions.all_steps_data.steps[step]
        console.log(`🎯 Step ${step} detected: Using existing API to save to grant_versions`);

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

          console.log(`✅ Step ${step} data saved to grant_versions via existing API`);

          // 同時更新 localStorage 作為本地備份
          GrantStorage.saveStepData(caseNumber, step, data);
          console.log(`✅ localStorage backup saved for step ${step}`);

        } catch (apiError) {
          console.warn(`❌ API error saving step ${step}, falling back to localStorage:`, apiError);

          // API 失敗時回退到僅 localStorage 儲存
          GrantStorage.saveStepData(caseNumber, step, data);
          savedData = data;
        }
      } else {
        // Invalid step number
        console.warn(`Invalid step number: ${step}`);
        GrantStorage.saveStepData(caseNumber, step, data);
        savedData = data;
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
    // Preserve case number when updating form data
    const currentCaseNumber = formData[step]?._caseNumber || (currentGrant.value?.case_number as string);
    formData[step] = { ...formData[step], ...data, _caseNumber: currentCaseNumber }
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
    console.log('[grantsStore.clearCurrentGrant] 清理當前案件資料...')
    
    currentGrant.value = null
    currentStep.value = 1
    
    // 🔥 Linus式修復：徹底清空所有步驟資料，避免資料污染
    Object.keys(formData).forEach(key => {
      const stepNum = Number(key)
      formData[stepNum] = { valid: true } // 重置為初始狀態
      console.log(`[grantsStore.clearCurrentGrant] 清空 formData[${stepNum}]`)
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
    
    console.log('[grantsStore.clearCurrentGrant] 案件資料清理完成')
  }

  /**
   * Save all unsaved changes with enhanced tracking and grant_versions support
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

      // 🆕 根據步驟使用不同的保存方式，step2 優先使用 grant_versions API
      if (step === 1) {
        // Step 1 使用原有的 API 並支援詳細追蹤
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

          // 同步特定字段到 localStorage (step1 案件基本資料的特有處理方式)
          // TODO:個資相關資料不存放於 localStorage 需要特別處理遮罩問題
          syncFieldsToLocalStorage(caseNumber, stepData, 'saveAllChanges')
        } catch (apiError) {
          console.warn(`API error saving step ${step}, falling back to localStorage:`, apiError)

          // Fallback to localStorage
          GrantStorage.saveStepData(caseNumber, step, stepData)
        }
      } else if (step >= 2 && step <= 8) {
        // 🆕 Steps 2-8 使用現有的 API 儲存到 grant_versions.all_steps_data.steps[step]
        console.log(`🎯 Step ${step} detected: Using existing API to save to grant_versions`);
        console.log(`📦 Step ${step} data to save:`, JSON.stringify(stepData, null, 2));

        try {
          // 🆕 使用現有的 updateGrantStepDataWithTracking API 儲存到 grant_versions
          if (changed.length > 0) {
            // 使用擴展的追蹤版本
            const updateRequest: GrantStepDataUpdateRequest = {
              data: stepData,
              action_type: 'step_data_update',
              changed_fields: changed,
              old_value: oldData,
              session_id: sessionId,
              notes: `Step ${step} 資料更新: 變更欄位 ${changed.join(', ')}`
            }

            await updateGrantStepDataWithTracking(caseNumber, step, updateRequest)
          } else {
            // 沒有變更，使用一般保存
            await updateGrantStepData(caseNumber, step, stepData)
          }

          console.log(`✅ Step ${step} data saved to grant_versions via existing API`);

          // 後端儲存成功後，同時更新 localStorage 作為本地備份
          GrantStorage.saveStepData(caseNumber, step, stepData);
          console.log(`✅ localStorage backup saved for step ${step}`);

        } catch (apiError) {
          console.warn(`❌ API error for step ${step}, falling back to localStorage only:`, apiError);

          // API 失敗時回退到僅 localStorage 儲存
          GrantStorage.saveStepData(caseNumber, step, stepData);
        }
      } else {
        // Invalid step number
        console.warn(`Invalid step number: ${step}`);
        GrantStorage.saveStepData(caseNumber, step, stepData);
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

          // 🔥 修復：只使用專門的 updateCurrentStepAPI，不要用 updateGrantStepDataWithTracking
          // updateGrantStepDataWithTracking 會覆蓋目標步驟的資料，導致資料丟失
          try {
            await updateCurrentStepAPI(currentGrant.value.case_number, step);
            console.log(`[grantsStore] Successfully synced current_step ${step} to database for grant ${currentGrant.value.case_number}`);

            // 🆕 如果需要追蹤步驟變更，可以使用單獨的追蹤邏輯，不影響步驟資料
            if (previousStep !== step) {
              console.log(`[grantsStore] Step change tracked: ${previousStep} → ${step} (sessionId: ${sessionId})`);
            }
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

  // =============================================================================
  // 列表管理功能
  // =============================================================================

  // 列表相關狀態
  const grantsList = ref<GrantListItem[]>([])
  const listLoading = ref(false)
  const listError = ref<string | null>(null)
  const serviceStatus = ref<ServiceStatus>(hybridGrantService.getServiceStatus())

  // 篩選與搜尋 - 移除預設的數量限制
  const listFilters = reactive<GrantListParams>({
    year: undefined,
    office_id: undefined,
    search: '',
    skip: 0,
    limit: undefined // 預設不限制數量
  })

  // 選取的案件
  const selectedGrants = ref<string[]>([])

  // 分頁資訊
  const pagination = reactive({
    page: 1,
    itemsPerPage: 50,
    totalItems: 0
  })

  // 列表相關的 getters
  const filteredGrantsList = computed(() => {
    let result = grantsList.value

    // 本地篩選（如果需要的話）
    if (listFilters.search && listFilters.search.length > 0) {
      const searchTerm = listFilters.search.toLowerCase()
      result = result.filter(grant =>
        grant.applicant_name.toLowerCase().includes(searchTerm) ||
        grant.case_number.toLowerCase().includes(searchTerm) ||
        (grant.applicant_id && grant.applicant_id.toLowerCase().includes(searchTerm))
      )
    }

    return result
  })

  const isUsingApi = computed(() => serviceStatus.value.apiAvailable && !serviceStatus.value.fallbackMode)

  // 列表相關的 actions

  /**
   * 載入案件列表
   */
  const loadGrantsList = async (params?: Partial<GrantListParams>) => {
    listLoading.value = true
    listError.value = null

    try {
      // 合併參數
      const queryParams = { ...listFilters, ...params }

      // 使用混合服務載入資料
      const grants = await hybridGrantService.getGrants(queryParams)
      grantsList.value = grants

      // 更新服務狀態
      serviceStatus.value = hybridGrantService.getServiceStatus()

      // 更新分頁資訊
      pagination.totalItems = grants.length

      console.log(`📋 [loadGrantsList] Loaded ${grants.length} grants`)

    } catch (err) {
      listError.value = err instanceof Error ? err.message : '載入案件列表失敗'
      console.error('📋 [loadGrantsList] Error:', err)
    } finally {
      listLoading.value = false
    }
  }

  /**
   * 防抖搜尋
   */
  const debouncedSearch = debounce(async (searchTerm: string) => {
    listFilters.search = searchTerm
    await loadGrantsList()
  }, 500)

  /**
   * 更新篩選條件
   */
  const updateFilters = async (newFilters: Partial<GrantListParams>) => {
    // 使用 Object.assign 並特別處理 undefined 值
    Object.assign(listFilters, newFilters)

    console.log('🔍 [updateFilters] Updated filters:', listFilters)
    await loadGrantsList()
  }

  /**
   * 重置篩選條件
   */
  const resetFilters = async () => {
    Object.assign(listFilters, {
      year: undefined,
      office_id: undefined,
      search: '',
      skip: 0,
      limit: undefined // 重置時也不限制數量
    })
    await loadGrantsList()
  }

  /**
   * 刪除案件
   */
  const deleteGrantFromList = async (item: GrantListItem) => {
    try {
      await hybridGrantService.deleteGrant(item)

      // 從列表中移除
      const index = grantsList.value.findIndex(grant => grant.case_number === item.case_number)
      if (index >= 0) {
        grantsList.value.splice(index, 1)
      }

      console.log(`📋 [deleteGrantFromList] Deleted grant ${item.case_number}`)

    } catch (err) {
      console.error(`📋 [deleteGrantFromList] Error deleting grant ${item.case_number}:`, err)
      throw err
    }
  }

  /**
   * 批次刪除案件
   */
  const deleteSelectedGrants = async () => {
    if (selectedGrants.value.length === 0) return

    const deletePromises = selectedGrants.value.map(async (caseNumber) => {
      const item = grantsList.value.find(grant => grant.case_number === caseNumber)
      if (item) {
        await deleteGrantFromList(item)
      }
    })

    try {
      await Promise.all(deletePromises)
      selectedGrants.value = []
      console.log(`📋 [deleteSelectedGrants] Deleted ${deletePromises.length} grants`)
    } catch (err) {
      console.error('📋 [deleteSelectedGrants] Error in batch delete:', err)
      throw err
    }
  }

  /**
   * 重新整理列表
   */
  const refreshGrantsList = async () => {
    // 清除快取
    grantCacheService.clear('grants-list')

    // 清除選取狀態
    selectedGrants.value = []

    // 重新載入
    await loadGrantsList()
  }

  /**
   * 清除選取狀態
   */
  const clearSelectedGrants = () => {
    selectedGrants.value = []
    console.log('🔄 [grantsStore] 清除選取狀態')
  }

  /**
   * 嘗試重新連接 API
   */
  const tryReconnectApi = async () => {
    try {
      const success = await hybridGrantService.tryReconnectApi()
      serviceStatus.value = hybridGrantService.getServiceStatus()

      if (success) {
        // 重新載入列表
        await loadGrantsList()
      }

      return success
    } catch (err) {
      console.error('📋 [tryReconnectApi] Error:', err)
      return false
    }
  }

  // =============================================================================
  // 網路狀態監控
  // =============================================================================

  /**
   * 監聽網路狀態變化
   */
  const setupNetworkMonitoring = () => {
    if (typeof window !== 'undefined') {
      window.addEventListener('online', async () => {
        console.log('📋 [NetworkMonitor] Back online, attempting to reconnect...')
        await tryReconnectApi()
      })

      window.addEventListener('offline', () => {
        console.log('📋 [NetworkMonitor] Gone offline, switching to fallback mode')
        serviceStatus.value.apiAvailable = false
        serviceStatus.value.fallbackMode = true
      })
    }
  }

  // 初始化網路監控
  setupNetworkMonitoring()

  return {
    // State - 原有的
    currentGrant,
    currentStep,
    isLoading,
    isSaving,
    error,
    formData,
    lastSavedAt,
    hasUnsavedChanges,

    // State - 新增的列表功能
    grantsList,
    listLoading,
    listError,
    serviceStatus,
    listFilters,
    selectedGrants,
    pagination,

    // Getters - 原有的
    isGrantLoaded,
    caseNumber,
    status,
    lastSavedTime,

    // Getters - 新增的
    filteredGrantsList,
    isUsingApi,

    // Actions - 原有的
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

    // Actions - 新增的列表功能
    loadGrantsList,
    debouncedSearch,
    updateFilters,
    resetFilters,
    deleteGrantFromList,
    deleteSelectedGrants,
    refreshGrantsList,
    tryReconnectApi,
    clearSelectedGrants,

    // Tracking functions - 原有的
    trackFormValidation,
    trackFileOperation,
  }
})
