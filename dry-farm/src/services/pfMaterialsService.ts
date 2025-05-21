import { apiService } from './api/http';
import { PF_MATERIALS } from './api/endpoints';
import type {
  PFMaterial,
  PFMaterialCreate,
  PFMaterialUpdate,
  PaginatedResponse,
} from '@/types/pfMaterials'; // 假設 types 在此路徑

export const pfMaterialsService = {
  createMaterial: async (data: PFMaterialCreate): Promise<PFMaterial> => {
    return apiService.post<PFMaterial>(PF_MATERIALS.CREATE, data);
  },

  getMaterials: async (params?: { skip?: number; limit?: number }): Promise<PaginatedResponse<PFMaterial>> => {
    // Backend 使用 limit=0 表示獲取所有項目
    // 如果後端特別需要 limit=0 來獲取所有數據，保留此設計
    return apiService.get<PaginatedResponse<PFMaterial>>(PF_MATERIALS.LIST, { params });
  },

  getMaterialById: async (id: number | string): Promise<PFMaterial> => {
    return apiService.get<PFMaterial>(PF_MATERIALS.DETAIL(id));
  },

  updateMaterial: async (id: number | string, data: PFMaterialUpdate): Promise<PFMaterial> => {
    return apiService.put<PFMaterial>(PF_MATERIALS.UPDATE(id), data);
  },

  deleteMaterial: async (id: number | string): Promise<void> => {
    await apiService.delete(PF_MATERIALS.DELETE(id));
  },
};
