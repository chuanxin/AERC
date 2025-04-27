/**
 * Grant Storage - Data Persistence Layer
 *
 * This module provides a consistent interface for managing grant application data
 * with support for both localStorage and eventual API integration.
 */

// Store key for localStorage
const STORAGE_KEY = 'dry-farm-grants';

// Cache for grants data to minimize localStorage reads
let grantsCache: Record<string, GrantData> | null = null;

// Generic step data interface
export interface GrantStepData {
  [key: string]: any;
}

// Main grant data structure
export interface GrantData {
  caseNumber: string;
  status?: string;
  createdAt?: string;
  updatedAt?: string;
  steps: {
    [stepNumber: number]: GrantStepData;
  };
}

// Error type for storage operations
class StorageError extends Error {
  constructor(message: string, public cause?: unknown) {
    super(message);
    this.name = 'StorageError';
  }
}

/**
 * Grant Storage utility for managing grant data persistence
 * Provides abstracted access to both localStorage and API endpoints
 */
export const GrantStorage = {
  /**
   * Initialize the storage system
   * @returns {Promise<void>}
   */
  async initialize(): Promise<void> {
    try {
      // Initialize cache if needed
      if (!grantsCache) {
        this.refreshCache();
      }
      console.log('Grant storage system initialized');
    } catch (error) {
      console.error('Failed to initialize grant storage:', error);
      throw new StorageError('Storage initialization failed', error);
    }
  },

  /**
   * Refresh the grants cache from localStorage
   * @returns {Record<string, GrantData>} The refreshed cache
   */
  refreshCache(): Record<string, GrantData> {
    try {
      const storedData = localStorage.getItem(STORAGE_KEY);
      grantsCache = storedData ? JSON.parse(storedData) : {};
      return grantsCache;
    } catch (error) {
      console.error('Failed to refresh grants cache:', error);
      grantsCache = {};
      return grantsCache;
    }
  },

  /**
   * Get all stored grants
   * @param {boolean} [forceRefresh=false] Whether to force a refresh from localStorage
   * @returns {Record<string, GrantData>} All grants data
   */
  getAllGrants(forceRefresh = false): Record<string, GrantData> {
    if (forceRefresh || !grantsCache) {
      return this.refreshCache();
    }
    return grantsCache;
  },

  /**
   * Get a specific grant by case number
   * @param {string} caseNumber The case number of the grant
   * @returns {GrantData | null} The grant data or null if not found
   */
  getGrant(caseNumber: string): GrantData | null {
    try {
      if (!grantsCache) this.refreshCache();
      return grantsCache?.[caseNumber] || null;
    } catch (error) {
      console.error(`Failed to get grant ${caseNumber}:`, error);
      throw new StorageError(`Failed to retrieve grant ${caseNumber}`, error);
    }
  },

  /**
   * Get data for a specific step of a grant
   * @param {string} caseNumber The case number of the grant
   * @param {number} step The step number
   * @returns {GrantStepData | null} The step data or null if not found
   */
  getStepData(caseNumber: string, step: number): GrantStepData | null {
    try {
      const grant = this.getGrant(caseNumber);
      if (!grant || !grant.steps[step]) return null;
      return grant.steps[step];
    } catch (error) {
      console.error(`Failed to get step ${step} data for grant ${caseNumber}:`, error);
      throw new StorageError(`Failed to retrieve step ${step} data for grant ${caseNumber}`, error);
    }
  },

  /**
   * Save data for a step
   * @param {string} caseNumber The case number of the grant
   * @param {number} step The step number
   * @param {GrantStepData} data The step data to save
   * @returns {void}
   */
  saveStepData(caseNumber: string, step: number, data: GrantStepData): void {
    try {
      if (!grantsCache) this.refreshCache();

      // Initialize if not exists
      if (!grantsCache[caseNumber]) {
        grantsCache[caseNumber] = {
          caseNumber,
          createdAt: new Date().toISOString(),
          steps: {}
        };
      }

      // Update step data and timestamp
      grantsCache[caseNumber].steps[step] = data;
      grantsCache[caseNumber].updatedAt = new Date().toISOString();

      // Save back to localStorage
      this.persistToStorage();
    } catch (error) {
      console.error(`Failed to save step ${step} data for grant ${caseNumber}:`, error);
      throw new StorageError(`Failed to save step ${step} data for grant ${caseNumber}`, error);
    }
  },

  /**
   * Save entire grant data
   * @param {string} caseNumber The case number of the grant
   * @param {GrantData} data The grant data to save
   * @returns {void}
   */
  saveGrantData(caseNumber: string, data: GrantData): void {
    try {
      if (!grantsCache) this.refreshCache();

      // Ensure caseNumber consistency
      const saveData = { ...data, caseNumber };

      // Add timestamps
      if (!saveData.createdAt) {
        saveData.createdAt = new Date().toISOString();
      }
      saveData.updatedAt = new Date().toISOString();

      // Save to cache
      grantsCache[caseNumber] = saveData;

      // Persist to storage
      this.persistToStorage();
    } catch (error) {
      console.error(`Failed to save grant ${caseNumber}:`, error);
      throw new StorageError(`Failed to save grant ${caseNumber}`, error);
    }
  },

  /**
   * Delete a grant
   * @param {string} caseNumber The case number of the grant to delete
   * @returns {boolean} Whether the operation was successful
   */
  deleteGrant(caseNumber: string): boolean {
    try {
      if (!grantsCache) this.refreshCache();

      if (grantsCache[caseNumber]) {
        delete grantsCache[caseNumber];
        this.persistToStorage();
        return true;
      }
      return false;
    } catch (error) {
      console.error(`Failed to delete grant ${caseNumber}:`, error);
      throw new StorageError(`Failed to delete grant ${caseNumber}`, error);
    }
  },

  /**
   * Update grant status
   * @param {string} caseNumber The case number of the grant
   * @param {string} status The new status
   * @returns {void}
   */
  updateGrantStatus(caseNumber: string, status: string): void {
    try {
      const grant = this.getGrant(caseNumber);
      if (!grant) {
        throw new Error(`Grant ${caseNumber} not found`);
      }

      grant.status = status;
      grant.updatedAt = new Date().toISOString();

      grantsCache[caseNumber] = grant;
      this.persistToStorage();
    } catch (error) {
      console.error(`Failed to update status for grant ${caseNumber}:`, error);
      throw new StorageError(`Failed to update status for grant ${caseNumber}`, error);
    }
  },

  /**
   * Persist cache to localStorage
   * @private
   * @returns {void}
   */
  persistToStorage(): void {
    try {
      if (grantsCache) {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(grantsCache));
      }
    } catch (error) {
      console.error('Failed to persist grants to localStorage:', error);
      throw new StorageError('Failed to save data to localStorage', error);
    }
  },

  /**
   * Clear all grants data
   * @returns {void}
   */
  clearAllGrants(): void {
    try {
      localStorage.removeItem(STORAGE_KEY);
      grantsCache = {};
    } catch (error) {
      console.error('Failed to clear all grants:', error);
      throw new StorageError('Failed to clear all grants', error);
    }
  },

  /**
   * Check if storage is available and functioning
   * @returns {boolean} Whether storage is available
   */
  isStorageAvailable(): boolean {
    try {
      const testKey = `${STORAGE_KEY}-test`;
      localStorage.setItem(testKey, 'test');
      const result = localStorage.getItem(testKey) === 'test';
      localStorage.removeItem(testKey);
      return result;
    } catch (error) {
      console.error('Storage availability check failed:', error);
      return false;
    }
  },

  /**
   * Get the size of storage used by grants data
   * @returns {number} Size in bytes
   */
  getStorageSize(): number {
    try {
      const data = localStorage.getItem(STORAGE_KEY);
      return data ? new Blob([data]).size : 0;
    } catch (error) {
      console.error('Failed to calculate storage size:', error);
      return 0;
    }
  },

  /**
   * Create a backup of all grants data
   * @returns {string} JSON string of all grants data
   */
  createBackup(): string {
    try {
      if (!grantsCache) this.refreshCache();
      return JSON.stringify(grantsCache);
    } catch (error) {
      console.error('Failed to create backup:', error);
      throw new StorageError('Failed to create data backup', error);
    }
  },

  /**
   * Restore from a backup
   * @param {string} backupData JSON string of grants data
   * @returns {boolean} Whether restoration was successful
   */
  restoreFromBackup(backupData: string): boolean {
    try {
      const parsedData = JSON.parse(backupData);
      grantsCache = parsedData;
      this.persistToStorage();
      return true;
    } catch (error) {
      console.error('Failed to restore from backup:', error);
      throw new StorageError('Failed to restore from backup', error);
    }
  },

  /**
   * Generate a unique ID for a new grant
   * @param {number} [year] Optional year to include in the ID (defaults to current year)
   * @returns {string} A unique grant ID
   */
  generateGrantId(year?: number): string {
    const grants = this.getAllGrants();
    const currentYear = year || new Date().getFullYear();
    const taiwanYear = currentYear - 1911; // Convert to Taiwan calendar year

    // Find the highest existing ID for this year
    const yearPrefix = `${taiwanYear}`;
    let highestNumber = 0;

    Object.keys(grants).forEach(grantId => {
      if (grantId.startsWith(yearPrefix)) {
        const numberPart = parseInt(grantId.substring(yearPrefix.length), 10);
        if (!isNaN(numberPart) && numberPart > highestNumber) {
          highestNumber = numberPart;
        }
      }
    });

    // Generate new ID with incremented number
    const newNumber = highestNumber + 1;
    const paddedNumber = newNumber.toString().padStart(6, '0');
    return `${yearPrefix}${paddedNumber}`;
  },

  /**
   * Hybrid save function that can work with API in the future
   * Currently just saves to localStorage but provides a promise-based interface
   * for future API compatibility
   *
   * @param {string} caseNumber The case number of the grant
   * @param {number} step The step number
   * @param {GrantStepData} data The step data to save
   * @returns {Promise<GrantStepData>} The saved data
   */
  async saveStepDataAsync(caseNumber: string, step: number, data: GrantStepData): Promise<GrantStepData> {
    // For demo purposes, just use localStorage but return a promise
    this.saveStepData(caseNumber, step, data);
    return Promise.resolve(data);
  },

  /**
   * Hybrid get function that can work with API in the future
   * Currently just gets from localStorage but provides a promise-based interface
   * for future API compatibility
   *
   * @param {string} caseNumber The case number of the grant
   * @param {number} step The step number
   * @returns {Promise<GrantStepData | null>} The step data or null
   */
  async getStepDataAsync(caseNumber: string, step: number): Promise<GrantStepData | null> {
    // For demo purposes, just use localStorage but return a promise
    const data = this.getStepData(caseNumber, step);
    return Promise.resolve(data);
  }
};

// Initialize the cache on module load
(() => {
  try {
    GrantStorage.refreshCache();
  } catch (e) {
    console.warn('Failed to initialize grants cache:', e);
  }
})();

export default GrantStorage;
