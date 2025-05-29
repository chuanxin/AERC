import { defineStore } from 'pinia'
import { irrigationTypesService, type IrrigationType, type IrrigationTypeOptions } from '@/services/irrigationTypesService'

export const useIrrigationTypesStore = defineStore('irrigationTypes', () => {
  // State
  const irrigationTypes = ref<IrrigationType[]>([])
  const irrigationTypeOptions = ref<IrrigationTypeOptions[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const getIrrigationTypeById = computed(() => {
    return (id: number): IrrigationType | undefined => {
      return irrigationTypes.value.find(type => type.id === id)
    }
  })

  const getActiveIrrigationTypes = computed(() => {
    return irrigationTypes.value.filter(type => type.is_active)
  })

  // 從階層式選項中提取只有父節點的選項
  const getParentIrrigationTypeOptions = computed(() => {
    return irrigationTypeOptions.value
    .filter(option => {
      // 條件1: parent_id 為 null（頂層節點）
      // 條件2: 有 option 陣列且長度大於0（有子選項的節點）
      return (option.parent_id === null || (option.option && option.option.length > 0))
             && option.is_active
    })
    .map(option => ({
      id: option.id,
      name: option.name,
      code: option.code,
      description: option.description,
      value: option.id,
      title: option.name
    }))
  })

  // 取得特定父類型的子選項
  const getChildOptions = computed(() => {
    return (parentId: number) => {
      const parentOption = irrigationTypeOptions.value.find(option => option.id === parentId)
      if (!parentOption || !parentOption.option) return []

      return parentOption.option
        .filter(child => child.is_active)
        .map(child => ({
          id: child.id,
          name: child.name,
          code: child.code,
          description: child.description,
          value: child.id,
          title: child.name,
          parent_id: child.parent_id
        }))
    }
  })

  // 用於 v-select 的格式化選項 (只包含父節點)
  const getIrrigationTypeSelectOptions = computed(() => {
    return getParentIrrigationTypeOptions.value
  })

  // 取得噴頭子類型選項 (parent_id = 2)
  const getSprinklerTypeOptions = computed(() => {
    return getChildOptions.value(2)
  })

  // 取得滴灌子類型選項 (parent_id = 4)
  const getDripperTypeOptions = computed(() => {
    return getChildOptions.value(4)
  })

  // Actions
  const fetchIrrigationTypes = async (params?: { skip?: number; limit?: number }) => {
    try {
      loading.value = true
      error.value = null

      console.log('[IrrigationTypesStore] Fetching irrigation types...', params)
      const data = await irrigationTypesService.getAll(params)
      irrigationTypes.value = data
      console.log(`[IrrigationTypesStore] Successfully fetched ${data.length} irrigation types`)

    } catch (err) {
      console.error('[IrrigationTypesStore] Error fetching irrigation types:', err)
      error.value = err instanceof Error ? err.message : 'Failed to fetch irrigation types'

      // 提供備用的預設值
      irrigationTypes.value = [
        {
          id: 1,
          name: '穿孔管系統',
          code: '1',
          description: '穿孔管灌溉系統',
          is_active: true,
          parent_id: null
        },
        {
          id: 2,
          name: '噴頭式系統',
          code: '2',
          description: '噴頭式灌溉系統',
          is_active: true,
          parent_id: null
        },
        {
          id: 3,
          name: '微噴系統',
          code: '3',
          description: '微噴灌溉系統',
          is_active: true,
          parent_id: null
        },
        {
          id: 4,
          name: '滴灌系統',
          code: '4',
          description: '滴灌灌溉系統',
          is_active: true,
          parent_id: null
        }
      ]
      console.log('[IrrigationTypesStore] Using fallback irrigation types data')
    } finally {
      loading.value = false
    }
  }

  const fetchIrrigationTypeOptions = async () => {
    try {
      loading.value = true
      error.value = null

      console.log('[IrrigationTypesStore] Fetching irrigation type options...')
      const data = await irrigationTypesService.getOptions()
      irrigationTypeOptions.value = data
      console.log(`[IrrigationTypesStore] Successfully fetched ${data.length} irrigation type options`)

    } catch (err) {
      console.error('[IrrigationTypesStore] Error fetching irrigation type options:', err)
      error.value = err instanceof Error ? err.message : 'Failed to fetch irrigation type options'

      // 備用資料結構
      irrigationTypeOptions.value = [
        {
          id: 1,
          name: '穿孔管系統',
          code: '1',
          description: '穿孔管系統',
          is_active: true,
          parent_id: null,
          option: []
        },
        {
          id: 2,
          name: '噴頭式系統',
          code: '2',
          description: '噴頭式系統',
          is_active: true,
          parent_id: null,
          option: [
            {
              id: 2,
              name: '一般',
              code: '2',
              description: '噴頭式系統',
              is_active: true,
              parent_id: 2,
              option: []
            },
            {
              id: 6,
              name: '高壓大型噴頭系統',
              code: '6',
              description: '噴頭式系統子系統',
              is_active: true,
              parent_id: 2,
              option: []
            }
          ]
        },
        {
          id: 3,
          name: '微噴系統',
          code: '3',
          description: '微噴系統',
          is_active: true,
          parent_id: null,
          option: []
        },
        {
          id: 4,
          name: '滴灌系統',
          code: '4',
          description: '滴灌系統',
          is_active: true,
          parent_id: null,
          option: [
            {
              id: 7,
              name: '滴嘴滴灌系統',
              code: '7',
              description: '滴灌系統子系統',
              is_active: true,
              parent_id: 4,
              option: []
            },
            {
              id: 8,
              name: '滴水管滴灌系統',
              code: '8',
              description: '滴灌系統子系統',
              is_active: true,
              parent_id: 4,
              option: []
            }
          ]
        }
      ]
      console.log('[IrrigationTypesStore] Using fallback options data')
    } finally {
      loading.value = false
    }
  }

  const fetchIrrigationTypeById = async (id: number): Promise<IrrigationType | null> => {
    try {
      // 首先檢查 store 中是否已有此資料
      const cached = getIrrigationTypeById.value(id)
      if (cached) {
        return cached
      }

      console.log(`[IrrigationTypesStore] Fetching irrigation type by ID: ${id}`)
      const data = await irrigationTypesService.getById(id)

      // 更新 store 中的資料
      const existingIndex = irrigationTypes.value.findIndex(type => type.id === id)
      if (existingIndex >= 0) {
        irrigationTypes.value[existingIndex] = data
      } else {
        irrigationTypes.value.push(data)
      }

      console.log(`[IrrigationTypesStore] Successfully fetched irrigation type: ${data.name}`)
      return data

    } catch (err) {
      console.error(`[IrrigationTypesStore] Error fetching irrigation type ${id}:`, err)
      error.value = err instanceof Error ? err.message : `Failed to fetch irrigation type ${id}`
      return null
    }
  }

  const clearError = () => {
    error.value = null
  }

  const reset = () => {
    irrigationTypes.value = []
    irrigationTypeOptions.value = []
    error.value = null
    loading.value = false
  }

  return {
    // State
    irrigationTypes,
    irrigationTypeOptions,
    loading,
    error,

    // Getters
    getIrrigationTypeById,
    getActiveIrrigationTypes,
    getParentIrrigationTypeOptions,
    getChildOptions,
    getIrrigationTypeSelectOptions,
    getSprinklerTypeOptions,
    getDripperTypeOptions,

    // Actions
    fetchIrrigationTypes,
    fetchIrrigationTypeOptions,
    fetchIrrigationTypeById,
    clearError,
    reset
  }
})
