import { defineStore } from 'pinia'
import {
  fetchAllCropCategories,
  fetchCropNamesByCategory,
  fetchCropsGrouped,
  type CropCategory,
  type CropName,
  type CropCategoryWithNames
} from '@/services/cropsService'
import { ApplicationError, wrapAsync } from '@/utils/asyncHelpers'

export const useCropsStore = defineStore('crops', () => {
  // State
  const categories = ref<CropCategory[]>([])
  const cropNames = ref<CropName[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const isInitialized = ref(false)

  // Computed: 作物類別選項（下拉選單用）
  const categoryOptions = computed(() => {
    return categories.value
      .slice() // 避免修改原始陣列
      .sort((a, b) => b.id - a.id) // 依 id 降冪排序
      .map(category => ({
        title: category.name,
        value: category.name, // step2.vue 使用名稱作為 value
        id: category.id
      }))
  })

  // Computed: 作物類別名稱列表
  const categoryNames = computed(() => {
    return categories.value
      .slice() // 避免修改原始陣列
      .sort((a, b) => b.id - a.id) // 依 id 降冪排序
      .map(c => c.name)
  })

  // Computed: 根據類別 ID 建立作物名稱映射
  const cropNamesByCategoryId = computed(() => {
    const map = new Map<number, CropName[]>()
    cropNames.value.forEach(crop => {
      if (!map.has(crop.category_id)) {
        map.set(crop.category_id, [])
      }
      map.get(crop.category_id)?.push(crop)
    })
    return map
  })

  // Computed: 根據類別名稱建立作物名稱映射（與前端現有格式相容）
  const cropNamesByCategoryName = computed(() => {
    const map: Record<string, string[]> = {}
    categories.value.forEach(category => {
      const names = cropNamesByCategoryId.value.get(category.id) || []
      map[category.name] = names
        .slice() // 避免修改原始陣列
        .sort((a, b) => b.id - a.id) // 依 id 降冪排序
        .map(n => n.name)
    })
    return map
  })

  // Actions: 載入所有作物類別
  const loadCategories = wrapAsync(async () => {
    isLoading.value = true
    error.value = null

    try {
      categories.value = await fetchAllCropCategories()
    } catch (err: unknown) {
      if (err instanceof ApplicationError) {
        error.value = err.message || 'Failed to load crop categories'
      } else {
        error.value = 'Failed to load crop categories'
      }
      console.error('Error loading crop categories:', err)
    } finally {
      isLoading.value = false
    }
  })

  // Actions: 載入指定類別的作物名稱
  const loadCropNamesByCategory = wrapAsync(async (categoryId: number) => {
    isLoading.value = true
    error.value = null

    try {
      const newCropNames = await fetchCropNamesByCategory(categoryId)

      // 合併資料，避免重複
      cropNames.value = [
        ...cropNames.value.filter(c => c.category_id !== categoryId),
        ...newCropNames
      ]
    } catch (err: unknown) {
      if (err instanceof ApplicationError) {
        error.value = err.message || `Failed to load crop names for category ${categoryId}`
      } else {
        error.value = `Failed to load crop names for category ${categoryId}`
      }
      console.error(`Error loading crop names for category ${categoryId}:`, err)
    } finally {
      isLoading.value = false
    }
  })

  // Actions: 一次性載入所有作物資料（層級結構）
  const loadAllCropsGrouped = wrapAsync(async () => {
    isLoading.value = true
    error.value = null

    try {
      const groupedData = await fetchCropsGrouped()

      // 解構並儲存
      categories.value = groupedData.map(item => ({
        id: item.id,
        name: item.name
      }))

      cropNames.value = groupedData.flatMap(category =>
        category.crop_names.map(crop => ({
          ...crop,
          category_id: category.id
        }))
      )

      isInitialized.value = true
    } catch (err: unknown) {
      if (err instanceof ApplicationError) {
        error.value = err.message || 'Failed to load crops data'
      } else {
        error.value = 'Failed to load crops data'
      }
      console.error('Error loading crops data:', err)
    } finally {
      isLoading.value = false
    }
  })

  // Helper: 根據類別名稱取得作物名稱列表
  const getCropNamesForCategory = (categoryName: string): string[] => {
    return cropNamesByCategoryName.value[categoryName] || []
  }

  // Helper: 根據類別 ID 取得類別資訊
  const getCategoryById = (id: number): CropCategory | undefined => {
    return categories.value.find(c => c.id === id)
  }

  // Helper: 根據類別名稱取得類別資訊
  const getCategoryByName = (name: string): CropCategory | undefined => {
    return categories.value.find(c => c.name === name)
  }

  // Initialize store: 載入所有作物資料
  const initializeStore = async () => {
    if (!isInitialized.value) {
      await loadAllCropsGrouped()
    }
  }

  return {
    // State
    categories,
    cropNames,
    isLoading,
    error,
    isInitialized,

    // Computed
    categoryOptions,
    categoryNames,
    cropNamesByCategoryId,
    cropNamesByCategoryName,

    // Actions
    loadCategories,
    loadCropNamesByCategory,
    loadAllCropsGrouped,
    initializeStore,

    // Helpers
    getCropNamesForCategory,
    getCategoryById,
    getCategoryByName
  }
})
