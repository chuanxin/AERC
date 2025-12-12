import { apiService } from './api/http'
import { DOMICILE } from './api/endpoints'
import { ApplicationError } from '@/utils/asyncHelpers'

// Types for land section data
export interface LandSection {
  id: number
  name: string
  code: string
  town_id: number
  town_name?: string
  county_id?: number
  county_name?: string
}

// Mock data for land sections
const MOCK_LAND_SECTIONS: LandSection[] = [
  {
    id: 1,
    name: '內埔子段',
    code: '0001',
    town_id: 286,
    town_name: '竹崎鄉',
    county_id: 10,
    county_name: '嘉義縣'
  },
  {
    id: 2,
    name: '瓦厝埔段',
    code: '0002',
    town_id: 286,
    town_name: '竹崎鄉',
    county_id: 10,
    county_name: '嘉義縣'
  },
  {
    id: 3,
    name: '龍山段',
    code: '0003',
    town_id: 286,
    town_name: '竹崎鄉',
    county_id: 10,
    county_name: '嘉義縣'
  },
  {
    id: 4,
    name: '灣橋段',
    code: '0004',
    town_id: 286,
    town_name: '竹崎鄉',
    county_id: 10,
    county_name: '嘉義縣'
  }
]

/**
 * Fetch land sections by town ID with mock data support
 * @param townId - The town ID to filter sections by
 * @returns Promise<LandSection[]> - Array of land sections
 */
export const fetchLandSectionsByTown = async (townId: number): Promise<LandSection[]> => {
  try {
    try {
      const response = await apiService.get<LandSection[]>(`${DOMICILE.SECTIONS_LIST}?town_id=${townId}`)
      return response
    } catch (apiError) {
      console.warn(`API call failed for townId ${townId}, falling back to empty array:`, apiError)

      // If API fails, return empty array instead of throwing error
      // This provides graceful degradation
      return []
    }
  } catch (error: unknown) {
    // Handle errors properly
    if (error instanceof Error) {
      const status = (error as { response?: { status?: number } })?.response?.status || 0
      const message = (error as { response?: { data?: { detail?: string } } })?.response?.data?.detail || error.message || 'Failed to load land sections'

      throw new ApplicationError({
        message,
        status,
        source: 'landSectionService.fetchLandSectionsByTown',
        originalError: error
      })
    } else {
      throw new ApplicationError({
        message: 'An unknown error occurred while loading land sections',
        status: 500,
        source: 'landSectionService.fetchLandSectionsByTown',
        originalError: error
      })
    }
  }
}

/**
 * Get all available land sections (for admin purposes)
 * @returns Promise<LandSection[]> - All land sections
 */
export const fetchAllLandSections = async (): Promise<LandSection[]> => {
  try {
    const response = await apiService.get<LandSection[]>(DOMICILE.SECTIONS_LIST)
    return response
  } catch (error: unknown) {
    // Fall back to mock data if API fails
    console.warn('API call failed for all land sections, falling back to mock data:', error)
    return MOCK_LAND_SECTIONS
  }
}

/**
 * Get land section by ID
 * @param sectionId - The section ID
 * @returns Promise<LandSection | null> - The land section or null if not found
 */
export const fetchLandSectionById = async (sectionId: number): Promise<LandSection | null> => {
  try {
    // Check mock data first
    const mockSection = MOCK_LAND_SECTIONS.find(section => section.id === sectionId)
    if (mockSection) {
      return mockSection
    }

    // Try API call
    const response = await apiService.get<LandSection>(`${DOMICILE.SECTIONS_LIST}/${sectionId}`)
    return response
  } catch (error: unknown) {
    console.warn(`Failed to fetch land section ${sectionId}:`, error)
    return null
  }
}
