import { apiService } from './api/http';
import { PF_MODULES } from './api/endpoints';
import type {
  PFModule,
  PFModuleCreate,
  PFModuleUpdate,
  PaginatedResponse,
} from '@/types/pfModules'; // Adjust path if your types are elsewhere

export const pfModulesService = {
  createModule: async (data: PFModuleCreate): Promise<PFModule> => {
    return apiService.post<PFModule>(PF_MODULES.CREATE, data);
  },

  getModules: async (params?: { skip?: number; limit?: number }): Promise<PaginatedResponse<PFModule>> => {
    // Backend uses limit=0 for all, frontend might send undefined or a large number.
    // Adjust if your backend expects limit=0 explicitly for "all items".
    // If limit is 0, it means "all", so we might not need to pass it or pass a specific value
    // if the backend handles limit=0 as "all".
    // For now, just passing params as is.
    return apiService.get<PaginatedResponse<PFModule>>(PF_MODULES.LIST, { params });
  },

  getModuleById: async (id: number | string): Promise<PFModule> => {
    return apiService.get<PFModule>(PF_MODULES.DETAIL(id));
  },

  updateModule: async (id: number | string, data: PFModuleUpdate): Promise<PFModule> => {
    return apiService.put<PFModule>(PF_MODULES.UPDATE(id), data);
  },

  deleteModule: async (id: number | string): Promise<void> => {
    await apiService.delete(PF_MODULES.DELETE(id));
  },
};
