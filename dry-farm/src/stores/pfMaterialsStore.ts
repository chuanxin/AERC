import { defineStore } from 'pinia';
import { pfMaterialsService } from '@/services/pfMaterialsService';
import type { PFMaterial, PaginatedResponse } from '@/types/pfMaterials'; // 假設 types 在此路徑

interface PFMaterialsState {
  materials: PFMaterial[];
  totalMaterials: number;
  isLoading: boolean;
  error: string | null;
}

export const usePFMaterialsStore = defineStore('pfMaterials', {
  state: (): PFMaterialsState => ({
    materials: [],
    totalMaterials: 0,
    isLoading: false,
    error: null,
  }),

  getters: {
    allMaterials: (state): PFMaterial[] => state.materials,
    materialCount: (state): number => state.totalMaterials,
    hasMaterials: (state): boolean => state.materials.length > 0,
  },

  actions: {
    async fetchMaterials(params?: { skip?: number; limit?: number }) {
      this.isLoading = true;
      this.error = null;
      try {
        // 使用 limit: 0 獲取所有材質項目 (根據後端 API 設計)
        const effectiveParams = { skip: params?.skip || 0, limit: params?.limit === undefined ? 0 : params.limit };

        const response: PaginatedResponse<PFMaterial> = await pfMaterialsService.getMaterials(effectiveParams);
        this.materials = response.items;
        this.totalMaterials = response.total;
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'Failed to fetch materials';
        this.materials = [];
        this.totalMaterials = 0;
        console.error('[STORE FETCH PFMaterials] Error:', err);
      } finally {
        this.isLoading = false;
      }
    },

    async fetchMaterialById(id: number | string) {
      this.isLoading = true;
      this.error = null;
      try {
        const material = await pfMaterialsService.getMaterialById(id);
        // 只返回獲取的材質，不保存到狀態中
        return material;
      } catch (err) {
        this.error = err instanceof Error ? err.message : `Failed to fetch material ${id}`;
        console.error(`[STORE FETCH PFMaterial ${id}] Error:`, err);
        throw err; // 重拋異常，讓調用者處理
      } finally {
        this.isLoading = false;
      }
    },

    async createMaterial(materialData: Omit<PFMaterial, 'id'>) {
      this.isLoading = true;
      this.error = null;
      try {
        const newMaterial = await pfMaterialsService.createMaterial(materialData);
        // 重新獲取所有材質以保持列表更新
        await this.fetchMaterials();
        return newMaterial;
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'Failed to create material';
        console.error('[STORE CREATE PFMaterial] Error:', err);
        throw err;
      } finally {
        this.isLoading = false;
      }
    },

    async updateMaterial(id: number | string, materialData: Partial<Omit<PFMaterial, 'id'>>) {
      this.isLoading = true;
      this.error = null;
      try {
        const updatedMaterial = await pfMaterialsService.updateMaterial(id, materialData);
        // 重新獲取所有材質以保持列表更新
        await this.fetchMaterials();
        return updatedMaterial;
      } catch (err) {
        this.error = err instanceof Error ? err.message : `Failed to update material ${id}`;
        console.error(`[STORE UPDATE PFMaterial ${id}] Error:`, err);
        throw err;
      } finally {
        this.isLoading = false;
      }
    },

    async deleteMaterial(id: number | string) {
      this.isLoading = true;
      this.error = null;
      try {
        await pfMaterialsService.deleteMaterial(id);
        // 重新獲取所有材質以保持列表更新
        await this.fetchMaterials();
      } catch (err) {
        this.error = err instanceof Error ? err.message : `Failed to delete material ${id}`;
        console.error(`[STORE DELETE PFMaterial ${id}] Error:`, err);
        throw err;
      } finally {
        this.isLoading = false;
      }
    },

    // 確保材質數據已加載 (用於下拉選單)
    async ensureAllMaterialsLoaded() {
      if (this.materials.length === 0 || (this.materials.length < this.totalMaterials && !this.isLoading)) {
        // 假設 limit=0 獲取所有，根據後端設計
        await this.fetchMaterials({ skip: 0, limit: 0 });
      }
    }
  },
});
