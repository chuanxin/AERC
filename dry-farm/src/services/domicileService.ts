import { apiService } from './api/http'
import { DOMICILE } from './api/endpoints'
import { ApplicationError } from '@/utils/asyncHelpers'

// Types for domicile data
export interface County {
  id: number
  name: string
  code: string
}

export interface Town {
  id: number
  name: string
  code: string
  is_indigenous: boolean
  indigenous_type?: string
  county_id: number
  county_name?: string
}

export interface Village {
  id: number
  name: string
  code: string
  town_id: number
  town_name?: string
  county_id?: number
  county_name?: string
}

// // API service functions
// export const fetchAllCounties = async (): Promise<County[]> => {
//   const response = await apiService.get<County[]>(DOMICILE.COUNTIES_LIST)
//   return response
// }

export const fetchAllCounties = async (): Promise<County[]> => {
  try {
    const response = await apiService.get<County[]>(DOMICILE.COUNTIES_LIST)
    return response
  } catch (error: unknown) {
    // Handle technical aspects of the error
    if (error instanceof Error) {
      const status = (error as { response?: { status?: number } })?.response?.status || 0
      const message = (error as { response?: { data?: { detail?: string } } })?.response?.data?.detail || error.message || 'Failed to load counties'

      // Transform into a standardized application error
      throw new ApplicationError({
        message,
        status,
        source: 'domicileService.fetchAllCounties',
        originalError: error
      })
    } else {
      throw new ApplicationError({
        message: 'An unknown error occurred',
        status: 500,
        source: 'domicileService.fetchAllCounties',
        originalError: error
      })
    }
  }
}

// export const fetchTownsByCounty = async (countyId: number): Promise<Town[]> => {
//   const response = await apiService.get<Town[]>(`${DOMICILE.TOWNS_LIST}?county_id=${countyId}`)
//   return response
// }

export const fetchTownsByCounty = async (countyId: number): Promise<Town[]> => {
  try {
    // Use a simple query parameter approach
    const response = await apiService.get<Town[]>(`${DOMICILE.TOWNS_LIST}?county_id=${countyId}`)
    return response
  } catch (error: unknown) {
    // Error handling...
    throw new ApplicationError({
      message: 'Failed to load towns',
      source: 'domicileService.fetchTownsByCounty',
      originalError: error
    })
  }
}

export const fetchVillagesByTown = async (townId: number): Promise<Village[]> => {
  const response = await apiService.get<Village[]>(`${DOMICILE.VILLAGES_LIST}?town_id=${townId}`)
  return response
}
