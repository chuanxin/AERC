import { defineStore } from 'pinia'
import { fetchAllCounties, fetchTownsByCounty, fetchVillagesByTown, type County, type Town, type Village } from '@/services/domicileService'
import { fetchLandSectionsByLandCodes, type LandSection } from '@/services/landSectionNlscService'
import { ApplicationError, wrapAsync } from '@/utils/asyncHelpers'


export const useDomicileStore = defineStore('domicile', () => {
  // State
  const counties = ref<County[]>([])
  const towns = ref<Town[]>([])
  const villages = ref<Village[]>([])
  const landSections = ref<LandSection[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Derived state for dropdowns
  const countyOptions = computed(() => {
    return counties.value.map(county => ({
      title: county.name,
      value: county.id,
      code: county.code,
      land_code: county.land_code,
      hasData: townsByCountyId.value.has(county.id)
    }))
  })

  // Create a map of county ID -> name for easy lookup
  const countyMap = computed(() => {
    const map = new Map<number, string>()
    counties.value.forEach(county => {
      map.set(county.id, county.name)
    })
    return map
  })

  const townsById = computed(() => {
    const map = new Map<number, Town>()
    towns.value.forEach(town => map.set(town.id, town))
    return map
  })

  const townsByCountyId = computed(() => {
    const map = new Map<number, Town[]>()
    towns.value.forEach(town => {
      if (!map.has(town.county_id)) {
        map.set(town.county_id, [])
      }
      map.get(town.county_id)?.push(town)
    })
    return map
  })

  const villagesByTownId = computed(() => {
    const map = new Map<number, Village[]>()
    villages.value.forEach(village => {
      if (!map.has(village.town_id)) {
        map.set(village.town_id, [])
      }
      map.get(village.town_id)?.push(village)
    })
    return map
  })

  const landSectionsByTownId = computed(() => {
    const map = new Map<number, LandSection[]>()
    // 使用 land_code 建立對應關係
    landSections.value.forEach(section => {
      // 從 town_land_code 找到對應的 town_id
      const town = towns.value.find(t =>
        t.land_code === section.town_land_code &&
        counties.value.find(c => c.id === t.county_id)?.land_code === section.county_land_code
      )
      if (town) {
        if (!map.has(town.id)) {
          map.set(town.id, [])
        }
        map.get(town.id)?.push(section)
      }
    })
    return map
  })

  // Create a map of county name -> array of towns for dropdowns
  const townsMap = computed(() => {
    const map: Record<string, {title: string, value: number}[]> = {}

    towns.value.forEach(town => {
      const countyName = town.county_name || countyMap.value.get(town.county_id) || ''

      if (!map[countyName]) {
        map[countyName] = []
      }

      map[countyName].push({
        title: town.name,
        value: town.id
      })
    })

    return map
  })

  // Create a nested map of county name -> town name -> array of villages for dropdowns
  const villagesMap = computed(() => {
    const map: Record<string, Record<string, {title: string, value: number}[]>> = {}

    villages.value.forEach(village => {
      const countyName = village.county_name || ''
      const townName = village.town_name || ''

      if (!map[countyName]) {
        map[countyName] = {}
      }

      if (!map[countyName][townName]) {
        map[countyName][townName] = []
      }

      map[countyName][townName].push({
        title: village.name,
        value: village.id
      })
    })

    return map
  })

  // Actions
  const loadCounties = wrapAsync(async () => {
    isLoading.value = true
    error.value = null

    try {
      counties.value = await fetchAllCounties()
    } catch (err: unknown) { // Must use unknown here
      if (err instanceof ApplicationError) {
        error.value = err.message || 'Failed to load counties'
      } else {
        error.value = 'Failed to load counties'
      }
      console.error('Error loading counties:', err)
    } finally {
      isLoading.value = false
    }
  })

  const loadTownsByCountyId = wrapAsync(async (countyId: number) => {
    isLoading.value = true
    error.value = null

    try {
      const newTowns = await fetchTownsByCounty(countyId)

      // Append instead of replace to build up the cache
      towns.value = [...towns.value.filter(t => t.county_id !== countyId), ...newTowns]
    } catch (err: unknown) {
      if (err instanceof ApplicationError) {
        error.value = err.message || `Failed to load towns for county ${countyId}`
      } else {
        error.value = `Failed to load towns for county ${countyId}`
      }
      console.error(`Error loading towns for county ${countyId}:`, err)
    } finally {
      isLoading.value = false
    }
  })

  const loadVillagesByTownId = wrapAsync(async (townId: number) => {
    isLoading.value = true
    error.value = null

    try {
      const newVillages = await fetchVillagesByTown(townId)

      // Append instead of replace to build up the cache
      villages.value = [...villages.value.filter(v => v.town_id !== townId), ...newVillages]
    } catch (err: unknown) {
      if (err instanceof ApplicationError) {
        error.value = err.message || `Failed to load villages for town ${townId}`
      } else {
        error.value = `Failed to load villages for town ${townId}`
      }
      console.error(`Error loading villages for town ${townId}:`, err)
    } finally {
      isLoading.value = false
    }
  })

  const loadLandSectionsByTownId = wrapAsync(async (townId: number) => {
    isLoading.value = true
    error.value = null

    try {
      // 從 town_id 查找對應的 land_code
      const town = townsById.value.get(townId)
      if (!town || !town.land_code) {
        throw new ApplicationError({
          message: `Town ${townId} not found or missing land_code`,
          status: 404,
          source: 'domicile.loadLandSectionsByTownId'
        })
      }

      const county = counties.value.find(c => c.id === town.county_id)
      if (!county || !county.land_code) {
        throw new ApplicationError({
          message: `County for town ${townId} not found or missing land_code`,
          status: 404,
          source: 'domicile.loadLandSectionsByTownId'
        })
      }

      // 使用新的 NLSC API
      const newLandSections = await fetchLandSectionsByLandCodes(
        county.land_code,
        town.land_code
      )

      // 更新快取（移除舊資料，添加新資料）
      landSections.value = [
        ...landSections.value.filter(s =>
          !(s.county_land_code === county.land_code && s.town_land_code === town.land_code)
        ),
        ...newLandSections
      ]
    } catch (err: unknown) {
      if (err instanceof ApplicationError) {
        error.value = err.message || `Failed to load land sections for town ${townId}`
      } else {
        error.value = `Failed to load land sections for town ${townId}`
      }
      console.error(`Error loading land sections for town ${townId}:`, err)
    } finally {
      isLoading.value = false
    }
  })

  // 直接使用 land_code 載入地段（用於特殊城市或跨區查詢）
  const loadLandSectionsByLandCodes = wrapAsync(async (countyLandCode: string, townLandCode: string) => {
    isLoading.value = true
    error.value = null

    try {
      const newLandSections = await fetchLandSectionsByLandCodes(
        countyLandCode,
        townLandCode
      )

      // 更新快取（移除舊資料，添加新資料）
      landSections.value = [
        ...landSections.value.filter(s =>
          !(s.county_land_code === countyLandCode && s.town_land_code === townLandCode)
        ),
        ...newLandSections
      ]
    } catch (err: unknown) {
      if (err instanceof ApplicationError) {
        error.value = err.message || `Failed to load land sections for ${countyLandCode}/${townLandCode}`
      } else {
        error.value = `Failed to load land sections for ${countyLandCode}/${townLandCode}`
      }
      console.error(`Error loading land sections for ${countyLandCode}/${townLandCode}:`, err)
    } finally {
      isLoading.value = false
    }
  })

  // Get towns for a specific county ID (more efficient)
  const getTownsForCounty = (countyId: number) => {
    return (townsByCountyId.value.get(countyId) || []).map(town => ({
      title: town.name,
      value: town.id,
      code: town.code,
      land_code: town.land_code,
      countyId: town.county_id,
      hasData: villagesByTownId.value.has(town.id)
    }))
  }

  // Get villages for a specific town ID (more efficient)
  const getVillagesForTown = (townId: number) => {
    return (villagesByTownId.value.get(townId) || []).map(village => ({
      title: village.name,
      value: village.id,
      code: village.code,
      townId: village.town_id
    }))
  }

  // Get land sections for a specific town ID (more efficient)
  const getLandSectionsForTown = (townId: number) => {
    return (landSectionsByTownId.value.get(townId) || []).map(section => ({
      title: section.name,
      value: section.code,  // 使用 code 作為 value（新資料沒有 id）
      code: section.code,
      county_land_code: section.county_land_code,
      town_land_code: section.town_land_code
    }))
  }

  // Convenience method to load towns by county name
  const loadTownsByCountyName = wrapAsync(async (countyName: string) => {
    const county = counties.value.find(c => c.name === countyName)
    if (county) {
      await loadTownsByCountyId(county.id)
    } else {
      console.error(`County not found: ${countyName}`)
    }
  })

  // Convenience method to load villages by town name and county name
  const loadVillagesByTownName = wrapAsync(async (countyName: string, townName: string) => {
    const county = counties.value.find(c => c.name === countyName)
    if (!county) {
      console.error(`County not found: ${countyName}`)
      return
    }

    // Make sure towns for this county are loaded
    if (!towns.value.some(t => t.county_id === county.id)) {
      await loadTownsByCountyId(county.id)
    }

    const town = towns.value.find(t => t.county_id === county.id && t.name === townName)
    if (town) {
      await loadVillagesByTownId(town.id)
    } else {
      console.error(`Town not found: ${townName} in county ${countyName}`)
    }
  })



  // Initialize store
  const initializeStore = async () => {
    await loadCounties()
  }

  return {
    // State
    counties,
    towns,
    villages,
    landSections,
    isLoading,
    error,

    // Computed properties
    countyOptions,
    countyMap,
    townsMap,
    villagesMap,
    townsById,
    townsByCountyId,
    villagesByTownId,
    landSectionsByTownId,

    // Actions
    loadCounties,
    loadTownsByCountyId,
    loadTownsByCountyName,
    loadVillagesByTownId,
    loadVillagesByTownName,
    loadLandSectionsByTownId,
    loadLandSectionsByLandCodes,
    initializeStore,

    // Add the helper methods
    getCountyById: (id: number) => counties.value.find(c => c.id === id),
    getTownById: (id: number) => townsById.value.get(id),
    getTownsForCountyId: (countyId: number) => getTownsForCounty(countyId),
    getVillagesForTownId: (townId: number) => getVillagesForTown(townId),
    getLandSectionsForTownId: (townId: number) => getLandSectionsForTown(townId)
  }
})
