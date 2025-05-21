import { defineStore } from 'pinia';
import { pfDiametersService } from '@/services/pfDiametersService';
import type { PFDiameter, PaginatedResponse } from '@/types/pfDiameters'; // 假設 types 在此路徑

interface PFDiametersState {
  diameters: PFDiameter[];
  totalDiameters: number;
  isLoading: boolean;
  error: string | null;
}

export const usePFDiametersStore = defineStore('pfDiameters', {
  state: (): PFDiametersState => ({
    diameters: [],
    totalDiameters: 0,
    isLoading: false,
    error: null,
  }),

  getters: {
    allDiameters: (state): PFDiameter[] => state.diameters,
    diameterCount: (state): number => state.totalDiameters,
    hasDiameters: (state): boolean => state.diameters.length > 0,

    // 獲取格式化的口徑選項 (用於下拉菜單)
    diameterOptions: (state): { title: string; value: number }[] => {
      return state.diameters.map(diameter => ({
        title: `${diameter.name} (${diameter.value})`,
        value: diameter.id
      }));
    },

    // 根據口徑ID獲取口徑對象
    getDiameterById: (state) => (id: number | string) => {
      return state.diameters.find(d => d.id === Number(id)) || null;
    }
  },

  actions: {
    async fetchDiameters(params?: { skip?: number; limit?: number }) {
      this.isLoading = true;
      this.error = null;
      try {
        // 使用 limit: 0 獲取所有口徑項目 (根據後端 API 設計)
        const effectiveParams = { skip: params?.skip || 0, limit: params?.limit === undefined ? 0 : params.limit };

        const response: PaginatedResponse<PFDiameter> = await pfDiametersService.getDiameters(effectiveParams);
        this.diameters = response.items;
        this.totalDiameters = response.total;
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'Failed to fetch diameters';
        this.diameters = [];
        this.totalDiameters = 0;
        console.error('[STORE FETCH PFDiameters] Error:', err);
      } finally {
        this.isLoading = false;
      }
    },

    async fetchDiameterById(id: number | string) {
      this.isLoading = true;
      this.error = null;
      try {
        const diameter = await pfDiametersService.getDiameterById(id);
        return diameter;
      } catch (err) {
        this.error = err instanceof Error ? err.message : `Failed to fetch diameter ${id}`;
        console.error(`[STORE FETCH PFDiameter ${id}] Error:`, err);
        throw err;
      } finally {
        this.isLoading = false;
      }
    },

    async createDiameter(diameterData: Omit<PFDiameter, 'id'>) {
      this.isLoading = true;
      this.error = null;
      try {
        const newDiameter = await pfDiametersService.createDiameter(diameterData);
        await this.fetchDiameters();
        return newDiameter;
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'Failed to create diameter';
        console.error('[STORE CREATE PFDiameter] Error:', err);
        throw err;
      } finally {
        this.isLoading = false;
      }
    },

    async updateDiameter(id: number | string, diameterData: Partial<Omit<PFDiameter, 'id'>>) {
      this.isLoading = true;
      this.error = null;
      try {
        const updatedDiameter = await pfDiametersService.updateDiameter(id, diameterData);
        await this.fetchDiameters();
        return updatedDiameter;
      } catch (err) {
        this.error = err instanceof Error ? err.message : `Failed to update diameter ${id}`;
        console.error(`[STORE UPDATE PFDiameter ${id}] Error:`, err);
        throw err;
      } finally {
        this.isLoading = false;
      }
    },

    async deleteDiameter(id: number | string) {
      this.isLoading = true;
      this.error = null;
      try {
        await pfDiametersService.deleteDiameter(id);
        await this.fetchDiameters();
      } catch (err) {
        this.error = err instanceof Error ? err.message : `Failed to delete diameter ${id}`;
        console.error(`[STORE DELETE PFDiameter ${id}] Error:`, err);
        throw err;
      } finally {
        this.isLoading = false;
      }
    },

    // 確保口徑數據已加載 (用於下拉選單)
    async ensureAllDiametersLoaded() {
      if (this.diameters.length === 0 || (this.diameters.length < this.totalDiameters && !this.isLoading)) {
        await this.fetchDiameters({ skip: 0, limit: 0 });
      }
    }
  },
});
