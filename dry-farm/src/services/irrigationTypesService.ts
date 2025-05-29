import { apiService } from './api/http'
import { IRRIGATION_TYPES } from './api/endpoints'

export interface IrrigationType {
  id: number
  name: string
  code: string
  description?: string
  is_active: boolean
  parent_id?: number | null
}

export interface IrrigationTypeOptions extends IrrigationType {
  option?: IrrigationTypeOptions[]
}

export const irrigationTypesService = {
  getAll: async (params?: { skip?: number; limit?: number }): Promise<IrrigationType[]> => {
    try {
      const response = await apiService.get<IrrigationType[]>(IRRIGATION_TYPES.LIST, { params })
      return response
    } catch (error) {
      console.error('Error fetching irrigation types:', error)
      throw error
    }
  },

  getOptions: async (): Promise<IrrigationTypeOptions[]> => {
    try {
      const response = await apiService.get<IrrigationTypeOptions[]>(IRRIGATION_TYPES.OPTIONS)
      return response
    } catch (error) {
      console.error('Error fetching irrigation type options:', error)
      throw error
    }
  },

  getById: async (id: number): Promise<IrrigationType> => {
    try {
      const response = await apiService.get<IrrigationType>(IRRIGATION_TYPES.DETAIL(id))
      return response
    } catch (error) {
      console.error(`Error fetching irrigation type ${id}:`, error)
      throw error
    }
  }
}
