import { apiService } from './api/http'
import { PIPE_FITTINGS } from './api/endpoints'
import type {
  PipeFitting,
  PipeFittingCreate,
  PipeFittingUpdate,
  PaginatedResponse,
  // Assuming you have or will create these types/interfaces
  // based on your backend Pydantic schemas.
  // Example:
  // export interface PipeFitting {
  //   pomno: number;
  //   name: string;
  //   material_id: number;
  //   module_id: number;
  //   diameter1_id?: number | null;
  //   diameter2_id?: number | null;
  //   diameter3_id?: number | null;
  //   unit?: string | null;
  //   description?: string | null;
  //   office_id?: number | null;
  //   length?: number | null;
  //   compatibility_group?: any[] | null; // Adjust based on actual structure
  //   typical_location?: string | null;
  //   is_active: boolean;
  //   is_terminal: boolean;
  //   year?: number | null;
  //   created_at: string; // Or Date
  //   modified_at: string; // Or Date
  //   created_by_id?: number | null;
  //   modified_by_id?: number | null;
  //   // Include related objects if they are part of the response
  //   material?: { id: number; name: string };
  //   module?: { id: number; name: string };
  //   // ... other related objects
  // }
  //
  // export interface PipeFittingCreate {
  //   name: string;
  //   material_id: number;
  //   module_id: number;
  //   diameter1_id?: number | null;
  //   // ... other fields from PipeFittingCreate schema
  //   created_by_id?: number | null;
  // }
  //
  // export interface PipeFittingUpdate {
  //   name?: string;
  //   material_id?: number;
  //   // ... other fields from PipeFittingUpdate schema
  //   modified_by_id?: number | null;
  // }
  //
  // export interface PaginatedResponse<T> {
  //   items: T[];
  //   total: number;
  //   // page?: number; // if your backend returns these
  //   // size?: number; // if your backend returns these
  // }
} from '@/types/pipeFittings' // Adjust path as needed for your type definitions

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
    params?: { skip?: number; limit?: number }
  ): Promise<PaginatedResponse<PipeFitting>> => {
    try {

      const configForApiService = { params }; // 這是傳遞給 apiService.get 的配置對象
      console.log('[Service] Config for apiService.get:', JSON.stringify(configForApiService));
      const apiClientResponse = await apiService.get<PaginatedResponse<PipeFitting>>(
        PIPE_FITTINGS.BY_OFFICE_ID(officeId),
        configForApiService
      );
      // const apiClientResponse = await apiService.get<PaginatedResponse<PipeFitting>>(
      //   PIPE_FITTINGS.BY_OFFICE_ID(officeId),
      //   { params }
      // );
      // console.log('[Service] getPipeFittingsByOfficeId apiClientResponse.data:', apiClientResponse);
      return apiClientResponse; // This is correct if no error occurs HERE
    } catch (error) {
      console.error('[Service] Error in getPipeFittingsByOfficeId:', error);
      // WHAT HAPPENS HERE?
      // If you just log the error and don't explicitly return anything or rethrow,
      // the function will implicitly return 'undefined'.
      // The promise will then resolve with 'undefined'.

      // Option 1: Rethrow the error (often preferred for services)
      // throw error;

      // Option 2: Return a specific error structure or a default PaginatedResponse
      // return { items: [], total: 0, error: "Service error message" }; // Example
      // Or, if the function signature doesn't allow for an error property, you must throw.
    }
  },
}
