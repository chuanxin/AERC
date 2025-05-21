import { apiService } from './api/http';
import { PF_ANNUAL_PRICES } from './api/endpoints';
import type {
  PFAnnualPrice,
  PFAnnualPriceCreate,
  PFAnnualPriceUpdate,
  PaginatedResponse,
} from '@/types/pfAnnualPrices';

export const pfAnnualPricesService = {
  createAnnualPrice: async (data: PFAnnualPriceCreate): Promise<PFAnnualPrice> => {
    return apiService.post<PFAnnualPrice>(PF_ANNUAL_PRICES.CREATE, data);
  },

  getAnnualPrices: async (params?: { skip?: number; limit?: number }): Promise<PaginatedResponse<PFAnnualPrice>> => {
    return apiService.get<PaginatedResponse<PFAnnualPrice>>(PF_ANNUAL_PRICES.LIST, { params });
  },

  getAnnualPriceById: async (id: number | string): Promise<PFAnnualPrice> => {
    return apiService.get<PFAnnualPrice>(PF_ANNUAL_PRICES.DETAIL(id));
  },

  getAnnualPricesByPipeFitting: async (
    pipeFittingId: number | string,
    params?: { office_id?: number; skip?: number; limit?: number }
  ): Promise<PaginatedResponse<PFAnnualPrice>> => {
    return apiService.get<PaginatedResponse<PFAnnualPrice>>(
      PF_ANNUAL_PRICES.BY_PIPE_FITTING(pipeFittingId),
      { params }
    );
  },

  getCurrentPriceByPipeFitting: async (
    pipeFittingId: number | string,
    params?: { office_id?: number }
  ): Promise<PFAnnualPrice> => {
    return apiService.get<PFAnnualPrice>(
      PF_ANNUAL_PRICES.CURRENT_PRICE(pipeFittingId),
      { params }
    );
  },

  updateAnnualPrice: async (id: number | string, data: PFAnnualPriceUpdate): Promise<PFAnnualPrice> => {
    return apiService.put<PFAnnualPrice>(PF_ANNUAL_PRICES.UPDATE(id), data);
  },

  deleteAnnualPrice: async (id: number | string): Promise<void> => {
    await apiService.delete(PF_ANNUAL_PRICES.DELETE(id));
  },
};
