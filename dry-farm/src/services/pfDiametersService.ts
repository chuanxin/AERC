import { apiService } from './api/http';
import { PF_DIAMETERS } from './api/endpoints';
import type {
  PFDiameter,
  PFDiameterCreate,
  PFDiameterUpdate,
  PaginatedResponse,
} from '@/types/pfDiameters'; // 假設 types 在此路徑

export const pfDiametersService = {
  createDiameter: async (data: PFDiameterCreate): Promise<PFDiameter> => {
    return apiService.post<PFDiameter>(PF_DIAMETERS.CREATE, data);
  },

  getDiameters: async (params?: { skip?: number; limit?: number }): Promise<PaginatedResponse<PFDiameter>> => {
    // Backend 使用 limit=0 表示獲取所有項目
    // 如果後端特別需要 limit=0 來獲取所有數據，保留此設計
    return apiService.get<PaginatedResponse<PFDiameter>>(PF_DIAMETERS.LIST, { params });
  },

  getDiameterById: async (id: number | string): Promise<PFDiameter> => {
    return apiService.get<PFDiameter>(PF_DIAMETERS.DETAIL(id));
  },

  updateDiameter: async (id: number | string, data: PFDiameterUpdate): Promise<PFDiameter> => {
    return apiService.put<PFDiameter>(PF_DIAMETERS.UPDATE(id), data);
  },

  deleteDiameter: async (id: number | string): Promise<void> => {
    await apiService.delete(PF_DIAMETERS.DELETE(id));
  },
};
