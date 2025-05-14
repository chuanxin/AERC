import { defineStore } from 'pinia'
import { pipeFittingsService } from '@/services/pipeFittingsService'
import type {
  PipeFitting,
  PipeFittingCreate,
  PipeFittingUpdate,
  PaginatedResponse,
} from '@/types/pipeFittings' // Adjust path as needed

interface PipeFittingsState {
  pipeFittings: PipeFitting[]
  currentPipeFitting: PipeFitting | null
  totalPipeFittings: number // 總項目數，由 API 提供
  isLoading: boolean // 初始加載狀態
  isLoadingMore: boolean // 加載更多數據的狀態
  error: string | null
}

export const usePipeFittingsStore = defineStore('pipeFittings', {
  state: (): PipeFittingsState => ({
    pipeFittings: [],
    currentPipeFitting: null,
    totalPipeFittings: 0,
    isLoading: false,
    isLoadingMore: false, // 新增狀態
    error: null,
  }),

  actions: {
    async createPipeFitting(data: PipeFittingCreate) {
      this.isLoading = true
      this.error = null
      try {
        const newPipeFitting = await pipeFittingsService.createPipeFitting(data)
        // Optionally, add to state or refetch list
        // this.pipeFittings.push(newPipeFitting);
        // this.totalPipeFittings++;
        return newPipeFitting // Return for immediate use if needed
      } catch (err: any) {
        this.error = err.response?.data?.detail || err.message || 'Failed to create pipe fitting'
        throw err
      } finally {
        this.isLoading = false
      }
    },

    async fetchPipeFittings(params?: { skip?: number; limit?: number }) {
      this.isLoading = true
      this.error = null
      try {
        const response: PaginatedResponse<PipeFitting> = await pipeFittingsService.getPipeFittings(params)
        this.pipeFittings = response.items
        this.totalPipeFittings = response.total
      } catch (err: any) {
        console.error('[Store Action] Error fetching pipe fittings:', err);
        this.error = err.response?.data?.detail || err.message || 'Failed to fetch pipe fittings';
        this.pipeFittings = [];
        this.totalPipeFittings = 0;
      } finally {
        this.isLoading = false
      }
    },

    async fetchPipeFittingById(pomno: number | string) {
      this.isLoading = true
      this.error = null
      try {
        this.currentPipeFitting = await pipeFittingsService.getPipeFittingById(pomno)
      } catch (err: any) {
        this.currentPipeFitting = null
        this.error = err.response?.data?.detail || err.message || `Failed to fetch pipe fitting with POMNO ${pomno}`
        // console.error(`Error fetching pipe fitting ${pomno}:`, err);
      } finally {
        this.isLoading = false
      }
    },

    async updatePipeFitting(pomno: number | string, data: PipeFittingUpdate) {
      this.isLoading = true
      this.error = null
      try {
        const updatedPipeFitting = await pipeFittingsService.updatePipeFitting(pomno, data)
        // Update in local state if it exists
        const index = this.pipeFittings.findIndex(pf => pf.pomno === updatedPipeFitting.pomno)
        if (index !== -1) {
          this.pipeFittings[index] = updatedPipeFitting
        }
        if (this.currentPipeFitting?.pomno === updatedPipeFitting.pomno) {
          this.currentPipeFitting = updatedPipeFitting
        }
        return updatedPipeFitting // Return for immediate use if needed
      } catch (err: any) {
        this.error = err.response?.data?.detail || err.message || 'Failed to update pipe fitting'
        throw err
      } finally {
        this.isLoading = false
      }
    },

    async deletePipeFitting(pomno: number | string) {
      this.isLoading = true
      this.error = null
      try {
        await pipeFittingsService.deletePipeFitting(pomno)
        this.pipeFittings = this.pipeFittings.filter(pf => pf.pomno !== pomno)
        this.totalPipeFittings = Math.max(0, this.totalPipeFittings - 1)
        if (this.currentPipeFitting?.pomno === pomno) {
          this.currentPipeFitting = null
        }
      } catch (err: any) {
        this.error = err.response?.data?.detail || err.message || 'Failed to delete pipe fitting'
        throw err
      } finally {
        this.isLoading = false
      }
    },

    async fetchPipeFittingsByOfficeId(
      officeId: number | string,
      options: { skip?: number; limit?: number; append?: boolean } = {}
    ) {
      const { skip = 0, limit = 50, append = false } = options; // 默認每次加載50條

      console.log(`[STORE FETCH] Requesting: officeId=${officeId}, skip=${skip}, limit=${limit}, append=${append}. Current loaded: ${this.pipeFittings.length}, current total: ${this.totalPipeFittings}`);

      if (!append) {
        this.isLoading = true;
        // For initial load, we might want to clear previous items,
        // or ensure skip is 0 if not appending.
        // If skip is explicitly passed for a non-append, respect it.
        if (skip === 0) {
            this.pipeFittings = [];
        }
      } else {
        this.isLoadingMore = true;
      }
      this.error = null;

      try {
        // console.log(`[Store] Fetching office ${officeId}, skip: ${skip}, limit: ${limit}, append: ${append}`);
        const response: PaginatedResponse<PipeFitting> = await pipeFittingsService.getPipeFittingsByOfficeId(
          officeId,
          { skip, limit }
        );

        console.log(`[STORE FETCH] API Response: items_length=${response?.items?.length}, total=${response?.total}`);

        if (response && response.items) {
          const newItemsPomnos = response.items.map(item => item.pomno).join(',');
          console.log(`[STORE FETCH] New items pomnos: ${newItemsPomnos.substring(0, 100)}...`);

          if (append) {
            // 檢查是否有重複項 (可選，用於調試)
            const existingPomnos = new Set(this.pipeFittings.map(p => p.pomno));
            const uniqueNewItems = response.items.filter(newItem => !existingPomnos.has(newItem.pomno));
            if (uniqueNewItems.length < response.items.length) {
              console.warn(`[STORE FETCH] Potential duplicate items being added. Original new: ${response.items.length}, Unique new: ${uniqueNewItems.length}`);
            }
            this.pipeFittings = [...this.pipeFittings, ...response.items];
          } else {
            this.pipeFittings = response.items;
          }
          this.totalPipeFittings = response.total; // API 應返回總數
          console.log(`[STORE FETCH] After update: loaded=${this.pipeFittings.length}, total=${this.totalPipeFittings}`);
        } else {
          console.error('[Store Action] Invalid response or no items:', response);
          if (!append && skip === 0) this.pipeFittings = [];
        }
      } catch (err: any) {
        console.error('[Store Action] Error fetching pipe fittings by office ID:', err);
        this.error = err.response?.data?.detail || err.message || `Failed to fetch pipe fittings`;
        if (!append && skip === 0) this.pipeFittings = [];
      } finally {
        if (!append) {
          this.isLoading = false;
        } else {
          this.isLoadingMore = false;
        }
        console.log(`[STORE FETCH] Finished: isLoading=${this.isLoading}, isLoadingMore=${this.isLoadingMore}`);
      }
    },

    clearCurrentPipeFitting() {
      this.currentPipeFitting = null
    },
  },

  getters: {
    getFittingById: (state) => {
      return (pomno: number | string) => state.pipeFittings.find(pf => pf.pomno === pomno) || state.currentPipeFitting?.pomno === pomno ? state.currentPipeFitting : null
    },
  },
})
