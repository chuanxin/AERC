export interface GrantStepData {
  [key: string]: any;
}

export interface GrantData {
  caseNumber: string;
  steps: {
    [stepNumber: number]: GrantStepData;
  };
}

const STORAGE_KEY = 'dry-farm-grants';

export const GrantStorage = {
  // Get all stored grants
  getAllGrants(): Record<string, GrantData> {
    const storedData = localStorage.getItem(STORAGE_KEY);
    return storedData ? JSON.parse(storedData) : {};
  },

  // Get a specific grant by case number
  getGrant(caseNumber: string): GrantData | null {
    const grants = this.getAllGrants();
    return grants[caseNumber] || null;
  },

  // Get data for a specific step of a grant
  getStepData(caseNumber: string, step: number): GrantStepData | null {
    const grant = this.getGrant(caseNumber);
    if (!grant || !grant.steps[step]) return null;
    return grant.steps[step];
  },

  // Save data for a step
  saveStepData(caseNumber: string, step: number, data: GrantStepData): void {
    const grants = this.getAllGrants();

    // Initialize if not exists
    if (!grants[caseNumber]) {
      grants[caseNumber] = {
        caseNumber,
        steps: {}
      };
    }

    // Update step data
    grants[caseNumber].steps[step] = data;

    // Save back to localStorage
    localStorage.setItem(STORAGE_KEY, JSON.stringify(grants));
  }
};
