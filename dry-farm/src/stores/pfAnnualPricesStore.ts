import { defineStore } from 'pinia';
import { pfAnnualPricesService } from '@/services/pfAnnualPricesService';
import type { PFAnnualPrice, PaginatedResponse } from '@/types/pfAnnualPrices';

interface PFAnnualPricesState {
  annualPrices: PFAnnualPrice[];
  currentPipeFittingPrices: Record<number, PFAnnualPrice[]>; // 以 pipe_fitting_id 為鍵
  currentPrices: Record<number, PFAnnualPrice>; // 以 pipe_fitting_id 為鍵，儲存當前價格
  totalPrices: number;
  isLoading: boolean;
  error: string | null;
}

export const usePFAnnualPricesStore = defineStore('pfAnnualPrices', {
  state: (): PFAnnualPricesState => ({
    annualPrices: [],
    currentPipeFittingPrices: {},
    currentPrices: {},
    totalPrices: 0,
    isLoading: false,
    error: null,
  }),

  getters: {
    getAnnualPricesByPipeFittingId: (state) => (pipeFittingId: number) => {
      return state.currentPipeFittingPrices[pipeFittingId] || [];
    },
    getCurrentPriceByPipeFittingId: (state) => (pipeFittingId: number) => {
      return state.currentPrices[pipeFittingId] || null;
    },
    hasAnnualPrices: (state) => (pipeFittingId: number) => {
      return !!state.currentPipeFittingPrices[pipeFittingId] && state.currentPipeFittingPrices[pipeFittingId].length > 0;
    },
  },

  actions: {
    async fetchAnnualPrices(params?: { skip?: number; limit?: number }) {
      this.isLoading = true;
      this.error = null;
      try {
        const response = await pfAnnualPricesService.getAnnualPrices(params);
        this.annualPrices = response.items;
        this.totalPrices = response.total;
      } catch (err: any) {
        console.error('Error fetching annual prices:', err);
        this.error = err.message || 'Failed to fetch annual prices';
        this.annualPrices = [];
        this.totalPrices = 0;
      } finally {
        this.isLoading = false;
      }
    },

    async fetchAnnualPricesByPipeFitting(
      pipeFittingId: number,
      params?: { office_id?: number; skip?: number; limit?: number }
    ) {
      this.isLoading = true;
      this.error = null;
      try {
        const response = await pfAnnualPricesService.getAnnualPricesByPipeFitting(
          pipeFittingId,
          params
        );
        this.currentPipeFittingPrices[pipeFittingId] = response.items;
        return response.items;
      } catch (err: any) {
        console.error(`Error fetching annual prices for pipe fitting ${pipeFittingId}:`, err);
        this.error = err.message || `Failed to fetch annual prices for pipe fitting ${pipeFittingId}`;
        this.currentPipeFittingPrices[pipeFittingId] = [];
        return [];
      } finally {
        this.isLoading = false;
      }
    },

    async fetchCurrentPriceByPipeFitting(
      pipeFittingId: number,
      params?: { office_id?: number }
    ) {
      this.isLoading = true;
      this.error = null;
      try {
        const currentPrice = await pfAnnualPricesService.getCurrentPriceByPipeFitting(
          pipeFittingId,
          params
        );
        this.currentPrices[pipeFittingId] = currentPrice;
        return currentPrice;
      } catch (err: any) {
        console.error(`Error fetching current price for pipe fitting ${pipeFittingId}:`, err);
        this.error = err.message || `Failed to fetch current price for pipe fitting ${pipeFittingId}`;
        delete this.currentPrices[pipeFittingId];
        return null;
      } finally {
        this.isLoading = false;
      }
    },

    async createAnnualPrice(data: {
      pipe_fitting_id: number;
      office_id?: number | null;
      year: number;
      price: number;
      is_active?: boolean;
      created_by_id?: number | null;
    }) {
      this.isLoading = true;
      this.error = null;
      try {
        const newPrice = await pfAnnualPricesService.createAnnualPrice(data);

        // 如果已加載該管件的價格歷史，則更新本地狀態
        if (this.currentPipeFittingPrices[data.pipe_fitting_id]) {
          this.currentPipeFittingPrices[data.pipe_fitting_id].push(newPrice);
          // 根據年份排序，最新年份在前
          this.currentPipeFittingPrices[data.pipe_fitting_id].sort((a, b) => b.year - a.year);
        }

        // 更新當前價格（如果新增的是最新年份）
        if (
          this.currentPrices[data.pipe_fitting_id] &&
          newPrice.year >= this.currentPrices[data.pipe_fitting_id].year &&
          newPrice.is_active
        ) {
          this.currentPrices[data.pipe_fitting_id] = newPrice;
        } else if (!this.currentPrices[data.pipe_fitting_id] && newPrice.is_active) {
          this.currentPrices[data.pipe_fitting_id] = newPrice;
        }

        return newPrice;
      } catch (err: any) {
        console.error('Error creating annual price:', err);
        this.error = err.message || 'Failed to create annual price';
        throw err;
      } finally {
        this.isLoading = false;
      }
    },

    async updateAnnualPrice(
      priceId: number,
      data: {
        pipe_fitting_id?: number;
        office_id?: number | null;
        year?: number;
        price?: number;
        is_active?: boolean;
        modified_by_id?: number | null;
      }
    ) {
      this.isLoading = true;
      this.error = null;
      try {
        const updatedPrice = await pfAnnualPricesService.updateAnnualPrice(priceId, data);

        // 更新本地狀態
        if (this.currentPipeFittingPrices[updatedPrice.pipe_fitting_id]) {
          const index = this.currentPipeFittingPrices[updatedPrice.pipe_fitting_id].findIndex(p => p.id === priceId);
          if (index !== -1) {
            this.currentPipeFittingPrices[updatedPrice.pipe_fitting_id][index] = updatedPrice;
            // 重新排序
            this.currentPipeFittingPrices[updatedPrice.pipe_fitting_id].sort((a, b) => b.year - a.year);
          }
        }

        // 更新當前價格
        if (
          this.currentPrices[updatedPrice.pipe_fitting_id] &&
          this.currentPrices[updatedPrice.pipe_fitting_id].id === priceId
        ) {
          this.currentPrices[updatedPrice.pipe_fitting_id] = updatedPrice;
        }

        return updatedPrice;
      } catch (err: any) {
        console.error(`Error updating annual price ${priceId}:`, err);
        this.error = err.message || `Failed to update annual price ${priceId}`;
        throw err;
      } finally {
        this.isLoading = false;
      }
    },

    async deleteAnnualPrice(priceId: number, pipeFittingId: number) {
      this.isLoading = true;
      this.error = null;
      try {
        await pfAnnualPricesService.deleteAnnualPrice(priceId);

        // 從本地狀態中刪除
        if (this.currentPipeFittingPrices[pipeFittingId]) {
          this.currentPipeFittingPrices[pipeFittingId] = this.currentPipeFittingPrices[pipeFittingId].filter(
            p => p.id !== priceId
          );
        }

        // 如果刪除的是當前價格，則需要更新當前價格
        if (
          this.currentPrices[pipeFittingId] &&
          this.currentPrices[pipeFittingId].id === priceId
        ) {
          // 如果還有其他價格記錄，設置最新年份的價格為當前價格
          if (this.currentPipeFittingPrices[pipeFittingId] && this.currentPipeFittingPrices[pipeFittingId].length > 0) {
            // 已按年份排序，最新年份在前
            this.currentPrices[pipeFittingId] = this.currentPipeFittingPrices[pipeFittingId][0];
          } else {
            // 如果沒有其他價格記錄，刪除當前價格
            delete this.currentPrices[pipeFittingId];
          }
        }
      } catch (err: any) {
        console.error(`Error deleting annual price ${priceId}:`, err);
        this.error = err.message || `Failed to delete annual price ${priceId}`;
        throw err;
      } finally {
        this.isLoading = false;
      }
    },

    // 清理特定管件的價格數據
    clearPipeFittingPrices(pipeFittingId: number) {
      delete this.currentPipeFittingPrices[pipeFittingId];
      delete this.currentPrices[pipeFittingId];
    },

    // 全部清理
    clearAllPrices() {
      this.annualPrices = [];
      this.currentPipeFittingPrices = {};
      this.currentPrices = {};
      this.totalPrices = 0;
    }
  }
});
