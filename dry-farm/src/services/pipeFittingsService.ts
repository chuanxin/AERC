import { apiService } from './api/http'
import { PIPE_FITTINGS } from './api/endpoints'
import type {
  PipeFitting,
  PipeFittingCreate,
  PipeFittingUpdate,
  PaginatedResponse,
} from '@/types/pipeFittings'

export const pipeFittingsService = {
  createPipeFitting: async (data: PipeFittingCreate): Promise<PipeFitting> => {
    const response = await apiService.post<PipeFitting>(PIPE_FITTINGS.CREATE, data)
    return response
  },

  getPipeFittings: async (params?: { skip?: number; limit?: number }): Promise<PaginatedResponse<PipeFitting>> => {
    const response = await apiService.get<PaginatedResponse<PipeFitting>>(PIPE_FITTINGS.LIST, { params })
    return response
  },

  getPipeFittingById: async (pomno: number | string): Promise<PipeFitting> => {
    const response = await apiService.get<PipeFitting>(PIPE_FITTINGS.DETAIL(pomno))
    return response
  },

  updatePipeFitting: async (pomno: number | string, data: PipeFittingUpdate): Promise<PipeFitting> => {
    const response = await apiService.put<PipeFitting>(PIPE_FITTINGS.UPDATE(pomno), data)
    return response
  },

  deletePipeFitting: async (pomno: number | string): Promise<void> => {
    await apiService.delete(PIPE_FITTINGS.DELETE(pomno))
  },

  getPipeFittingsByOfficeId: async (
    officeId: number | string,
    params?: { skip?: number; limit?: number; include_inactive?: boolean }
  ): Promise<PaginatedResponse<PipeFitting>> => {
    try {

      const configForApiService = { params }; // 這是傳遞給 apiService.get 的配置對象
      console.log('[Service] Config for apiService.get:', JSON.stringify(configForApiService));
      const apiClientResponse = await apiService.get<PaginatedResponse<PipeFitting>>(
        PIPE_FITTINGS.BY_OFFICE_ID(officeId),
        configForApiService
      );
      return apiClientResponse; // This is correct if no error occurs HERE
    } catch (error) {
      console.error('[Service] Error in getPipeFittingsByOfficeId:', error);
      throw error; // Rethrow to let caller handle the error
    }
  },
}
