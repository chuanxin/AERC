import { defineStore } from 'pinia';
import { pfModulesService } from '@/services/pfModulesService'; // Adjust path
import type { PFModule, PaginatedResponse } from '@/types/pfModules'; // Adjust path

interface PFModulesState {
  modules: PFModule[];
  totalModules: number;
  isLoading: boolean;
  error: string | null;
}

export const usePFModulesStore = defineStore('pfModules', {
  state: (): PFModulesState => ({
    modules: [],
    totalModules: 0,
    isLoading: false,
    error: null,
  }),
  getters: {
    allModules: (state): PFModule[] => state.modules,
    moduleCount: (state): number => state.totalModules,
    hasModules: (state): boolean => state.modules.length > 0,
  },
  actions: {
    async fetchModules(params?: { skip?: number; limit?: number }) {
      this.isLoading = true;
      this.error = null;
      try {
        // To fetch all modules, you might pass limit: 0 or a very large number
        // depending on your backend API design for "get all".
        // The backend route for pf_modules has limit=0 for all.
        const effectiveParams = { skip: params?.skip || 0, limit: params?.limit === undefined ? 0 : params.limit };

        const response: PaginatedResponse<PFModule> = await pfModulesService.getModules(effectiveParams);
        this.modules = response.items;
        this.totalModules = response.total;
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'Failed to fetch modules';
        this.modules = [];
        this.totalModules = 0;
        console.error('[STORE FETCH PFModules] Error:', err);
      } finally {
        this.isLoading = false;
      }
    },

    async fetchModuleById(id: number | string) {
      this.isLoading = true;
      this.error = null;
      try {
        const module = await pfModulesService.getModuleById(id);
        // Handle how you want to store/use a single fetched module
        // For now, just returning it, or you could add it to the list if not present
        return module;
      } catch (err) {
        this.error = err instanceof Error ? err.message : `Failed to fetch module ${id}`;
        console.error(`[STORE FETCH PFModule ${id}] Error:`, err);
        throw err; // Rethrow so the caller can handle it
      } finally {
        this.isLoading = false;
      }
    },

    async createModule(moduleData: Omit<PFModule, 'id' | 'created_at' | 'modified_at'>) {
      this.isLoading = true;
      this.error = null;
      try {
        const newModule = await pfModulesService.createModule(moduleData);
        // Optionally refetch all modules or add to the list
        await this.fetchModules(); // Easiest way to keep list updated
        return newModule;
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'Failed to create module';
        console.error('[STORE CREATE PFModule] Error:', err);
        throw err;
      } finally {
        this.isLoading = false;
      }
    },

    async updateModule(id: number | string, moduleData: Partial<Omit<PFModule, 'id' | 'created_at' | 'modified_at'>>) {
      this.isLoading = true;
      this.error = null;
      try {
        const updatedModule = await pfModulesService.updateModule(id, moduleData);
        // Optionally refetch all modules or update the specific item in the list
        await this.fetchModules();
        return updatedModule;
      } catch (err) {
        this.error = err instanceof Error ? err.message : `Failed to update module ${id}`;
        console.error(`[STORE UPDATE PFModule ${id}] Error:`, err);
        throw err;
      } finally {
        this.isLoading = false;
      }
    },

    async deleteModule(id: number | string) {
      this.isLoading = true;
      this.error = null;
      try {
        await pfModulesService.deleteModule(id);
        // Optionally refetch all modules or remove from the list
        await this.fetchModules();
      } catch (err) {
        this.error = err instanceof Error ? err.message : `Failed to delete module ${id}`;
        console.error(`[STORE DELETE PFModule ${id}] Error:`, err);
        throw err;
      } finally {
        this.isLoading = false;
      }
    },

    // Action to specifically fetch all modules for dropdowns, etc.
    async ensureAllModulesLoaded() {
      if (this.modules.length === 0 || this.modules.length < this.totalModules && !this.isLoading) {
         // Assuming limit=0 fetches all, as per your backend.
        await this.fetchModules({ skip: 0, limit: 0 });
      }
    }
  },
});
