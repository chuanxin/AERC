import { defineStore } from 'pinia'
import { officeService, type Office } from '@/services/officelistService'
import { wrapAsync } from '@/utils/asyncHelpers'

// offices 離線快取：`grantsService` 的 localStorage 降級路徑只在 API 失敗時觸發，
// 而 office name→id 對映改為 SSOT 後同樣依賴 API。沒有快取的話，離線時 map 為空 →
// 每筆離線案件 office_id 為 undefined → 管理處篩選結果恆為 0 筆（原硬編碼版本可離線運作）。
const OFFICES_CACHE_KEY = 'aerc_offices_cache'

function readOfficesCache(): Office[] {
  try {
    const raw = localStorage.getItem(OFFICES_CACHE_KEY)
    if (!raw) return []
    const parsed = JSON.parse(raw)
    return Array.isArray(parsed) ? parsed as Office[] : []
  } catch (e) {
    console.warn('[offices] 讀取 offices 快取失敗，將以空清單處理:', e)
    return []
  }
}

function writeOfficesCache(list: Office[]): void {
  try {
    localStorage.setItem(OFFICES_CACHE_KEY, JSON.stringify(list))
  } catch (e) {
    console.warn('[offices] 寫入 offices 快取失敗（不影響線上功能）:', e)
  }
}

/**
 * Store for managing Office data
 */
export const useOfficesStore = defineStore('offices', () => {
  // State
  const offices = ref<Office[]>([])
  // 上次成功取得的 offices（localStorage 快取），僅在 API 尚未回應/失敗時作為降級來源
  const cachedOffices = ref<Office[]>(readOfficesCache())
  const currentOffice = ref<Office | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const totalCount = ref(0)
  const currentPage = ref(1)
  const pageSize = ref(20)
  const totalPages = ref(0)

  // 快取的唯一寫入入口：記憶體與 localStorage 一起更新，避免呼叫點各做一半
  const syncOfficesCache = (list: Office[]) => {
    cachedOffices.value = [...list]
    writeOfficesCache(list)
  }

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

  // Sorted offices for UI display (sorted by ID in ascending order)
  const sortedOffices = computed(() => {
    return [...offices.value].sort((a, b) => a.id - b.id)
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
      syncOfficesCache(response)
    } else if (response && 'items' in response) {
      // API returned a paginated response
      offices.value = response.items
      totalCount.value = response.total
      syncOfficesCache(response.items)
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

    // 同步離線快取，否則快取會停留在變更前的內容直到下次 fetchOffices
    // （createOffice 結尾呼叫 fetchOffices 已隱含刷新，此處與 delete 需自行處理）
    syncOfficesCache(offices.value)

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

    // 同步離線快取（理由同 updateOffice）：不同步的話，刪掉的單位會在
    // 下次「API 掛掉、改讀快取」時重新出現在下拉選單裡
    syncOfficesCache(offices.value)

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

  // Add this computed property
  const managementOffices = computed(() => {
    return [...offices.value]
      .filter(office => office.classification === 1)
      .map(office => ({
        title: office.name,
        value: office.id,
        classification: office.classification
      }))
  })

  // API 尚未回應或失敗時退回上次成功結果的快取，讓下拉選單與 name→id 對映在離線仍可用
  const effectiveOffices = computed(() =>
    offices.value.length > 0 ? offices.value : cachedOffices.value
  )

  // name -> id 對映（SSOT）：供離線資料轉換等需要 name↔id 之處統一取用，
  // 避免各處（如 grantsService）各自硬編碼 office 清單而漂移。以 offices 表為唯一來源。
  // 排除 API 附加的合成「作業基金」(id=-1)：它不是真實 office 記錄，
  // 不應成為離線案件 officeName 的解析目標（原硬編碼 map 亦無此項）
  const officeNameToIdMap = computed(() => {
    const map: Record<string, number> = {}
    effectiveOffices.value.forEach(office => {
      if (office.name && office.id >= 0) map[office.name] = office.id
    })
    return map
  })

  // 管理處下拉選單 SSOT：offices 表中正式的部門記錄（排除 API 附加的合成「作業基金」id<0）。
  // 「申請案件列表」「使用者帳號列表」兩處下拉共用此來源，內容一致且含 id=0 農業部農田水利署。
  const managementAreaSelectItems = computed(() =>
    [...effectiveOffices.value]
      .sort((a, b) => a.id - b.id)
      .filter(office => office.id >= 0)
      .map(office => ({
        title: office.name,
        value: office.id,
        classification: office.classification
      }))
  )

  // 下拉選單是否有可用來源（含離線快取）：呼叫端據此判斷是否需要提示操作者
  const hasOfficeOptions = computed(() => effectiveOffices.value.length > 0)

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
    managementOffices,
    officeNameToIdMap,
    managementAreaSelectItems,
    hasOfficeOptions,

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
