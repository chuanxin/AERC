// Mirrors your backend Pydantic schemas for PFModules

export interface PFModuleBase {
  name: string;
  // description?: string | null; // If you have this field
}

export interface PFModuleCreate extends PFModuleBase {}

export interface PFModuleUpdate {
  name?: string;
  // description?: string | null;
}

export interface PFModule extends PFModuleBase {
  id: number;
  created_at: string; // Or Date, depending on how you handle dates
  modified_at: string; // Or Date
}

// You can reuse the generic PaginatedResponse if it's defined globally
// or redefine it here if specific adjustments are needed.
// For now, assuming it's similar to the one used by pipeFittings
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
}
