import { apiService } from './api/http'
import { OFFICES } from './api/endpoints'

export interface Office {
  id: number
  name: string
  short_name: string
  code: string
  classification: number
}

// Response interfaces for listing
export interface ListResponse<T> {
  items: T[]
  total: number
}

// Query parameters for filtering
export interface LocationQueryParams {
  page?: number
  size?: number
  search?: string
  county_id?: number
  town_id?: number
}

/**
 * Service for handling Office-related API calls
 */
export const officeService = {
  /**
   * Get all offices
   */
  async getAll(): Promise<ListResponse<Office>> {
    const response = await apiService.get<ListResponse<Office>>(OFFICES.LIST)
    return response
    // return await apiService.get<ListResponse<Office>>(OFFICES.LIST)
  },

  /**
   * Get office by ID
   */
  // async getById(id: number): Promise<Office> {
  //   return await apiService.get<Office>(OFFICES.DETAIL(id));
  // },

  /**
   * Create a new office
   */
  async create(data: Omit<Office, 'id'>): Promise<Office> {
    return await apiService.post<Office>(
      OFFICES.CREATE,
      data as Record<string, unknown>
    )
  },

  /**
   * Update an existing office
   */
  async update(id: number, data: Partial<Office>): Promise<Office> {
    return await apiService.put<Office>(
      OFFICES.UPDATE(id),
      data as Record<string, unknown>
    )
  },

  /**
   * Delete an office
   */
  async delete(id: number): Promise<void> {
    await apiService.delete(OFFICES.DELETE(id))
  }
}
