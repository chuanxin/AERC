import { defineStore } from 'pinia'
import { officeService, type Office } from '@/services/officelistService'
import { wrapAsync } from '@/utils/asyncHelpers'

/**
 * Store for managing Office data
 */
export const useOfficesStore = defineStore('offices', () => {
  // State
  const offices = ref<Office[]>([])
  const currentOffice = ref<Office | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const totalCount = ref(0)
  const currentPage = ref(1)
  const pageSize = ref(20)
  const totalPages = ref(0)

  // Computed properties
  const isOfficesLoaded = computed(() => offices.value.length > 0)

  // Map for quick access to office by ID
  const officesMap = computed(() => {
    const map = new Map<number, Office>()
    offices.value.forEach(office => {
      map.set(office.id, office)
    })
    return map
  })

  // Sorted offices for UI display
  const sortedOffices = computed(() => {
    return [...offices.value].sort((a, b) => a.name.localeCompare(b.name, 'zh-TW'))
  })

  // Office select options for dropdowns - Updated for Vuetify compatibility
  const officeOptions = computed(() => {
    return sortedOffices.value.map(office => ({
      text: office.name,  // Changed from 'title' to 'text' for Vuetify
      value: office.id,
    }))
  })

  // For newer Vuetify versions that support 'title' instead of 'text'
  const officeSelectItems = computed(() => {
    return sortedOffices.value.map(office => ({
      title: office.name,
      value: office.id,
      classification: office.classification,
    }))
  })

  // Async options
  const asyncOptions = {
    loadingRef: isLoading,
    errorRef: error
  }

  /**
   * Fetch all offices with optional filtering
   */
  const fetchOffices = wrapAsync(async () => {
    const response = await officeService.getAll()

    // Check if response has the expected structure
    if (Array.isArray(response)) {
      // API returned a direct array of offices
      offices.value = response
      totalCount.value = response.length
    } else if (response && 'items' in response) {
      // API returned a paginated response
      offices.value = response.items
      totalCount.value = response.total
    } else {
      console.error('Unexpected API response format', response)
      offices.value = []
      totalCount.value = 0
    }

    return response
  }, asyncOptions)


  /**
   * Create a new office
   */
  const createOffice = wrapAsync(async (data: Omit<Office, 'id'>) => {
    const newOffice = await officeService.create(data)

    // Add to local state
    offices.value.push(newOffice)

    // Refresh list to ensure accurate data
    await fetchOffices()

    return newOffice
  }, asyncOptions)

  /**
   * Update an existing office
   */
  const updateOffice = wrapAsync(async (id: number, data: Partial<Office>) => {
    const updatedOffice = await officeService.update(id, data)

    // Update in local state
    const index = offices.value.findIndex(o => o.id === id)
    if (index !== -1) {
      offices.value[index] = updatedOffice
    }

    // If this is the currently selected office, update it
    if (currentOffice.value?.id === id) {
      currentOffice.value = updatedOffice
    }

    return updatedOffice
  }, asyncOptions)

  /**
   * Delete an office
   */
  const deleteOffice = wrapAsync(async (id: number) => {
    await officeService.delete(id)

    // Remove from local state
    offices.value = offices.value.filter(o => o.id !== id)

    // If this was the currently selected office, clear it
    if (currentOffice.value?.id === id) {
      currentOffice.value = null
    }

    return true
  }, asyncOptions)

  /**
   * Set pagination parameters
   */
  const setPagination = (page: number, size: number) => {
    currentPage.value = page
    pageSize.value = size
  }

  /**
   * Reset the store state
   */
  const resetState = () => {
    offices.value = []
    currentOffice.value = null
    isLoading.value = false
    error.value = null
    totalCount.value = 0
    currentPage.value = 1
    pageSize.value = 20
    totalPages.value = 0
  }

  const items = computed(() => {
    // return sortedOffices.value.map(office => ({
    //   title: office.name,
    //   value: office.id,
    // }))
    return [...offices.value].map(office => ({
      title: office.name,
      value: office.id,
      classification: office.classification
    }))
  })

  // Initialize store - preload commonly used data
  const initializeStore = async () => {
    if (!isOfficesLoaded.value) {
      await fetchOffices()
    }
  }

  return {
    // State
    offices,
    currentOffice,
    isLoading,
    error,
    totalCount,
    currentPage,
    pageSize,
    totalPages,

    // Computed
    isOfficesLoaded,
    officesMap,
    sortedOffices,
    officeOptions,
    officeSelectItems,
    items,

    // Actions
    fetchOffices,
    createOffice,
    updateOffice,
    deleteOffice,
    setPagination,
    resetState,
    initializeStore,
  }
})
