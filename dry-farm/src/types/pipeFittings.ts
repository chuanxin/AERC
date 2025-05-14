// Minimal example, expand based on your actual backend schemas

export interface PFMaterialResponseMin {
  id: number;
  name: string;
}

export interface PFModuleResponseMin {
  id: number;
  name: string;
}

export interface PFDiameterResponseMin {
  id: number;
  value: number; // Assuming value is a number
  name: string;
}

export interface OfficeResponseMin {
  id: number;
  name: string;
}

export interface UserResponseMin {
  id: int;
  username: string;
}

export interface PipeFitting {
  pomno: number;
  name: string;
  material_id: number;
  module_id: number;
  diameter1_id?: number | null;
  diameter2_id?: number | null;
  diameter3_id?: number | null;
  unit?: string | null;
  description?: string | null;
  office_id?: number | null;
  length?: number | null;
  compatibility_group?: any[] | null; // Or a more specific type if known
  typical_location?: string | null;
  is_active: boolean;
  is_terminal: boolean;
  year?: number | null;
  created_at: string; // Consider using Date if you parse it
  modified_at: string; // Consider using Date if you parse it
  created_by_id?: number | null;
  modified_by_id?: number | null;

  // Related objects (optional, based on prefetch_related in backend)
  material?: PFMaterialResponseMin | null;
  module?: PFModuleResponseMin | null;
  diameter1?: PFDiameterResponseMin | null;
  diameter2?: PFDiameterResponseMin | null;
  diameter3?: PFDiameterResponseMin | null;
  office?: OfficeResponseMin | null;
  created_by?: UserResponseMin | null;
  modified_by?: UserResponseMin | null;
}

export interface PipeFittingCreate {
  name: string;
  material_id: number;
  module_id: number;
  diameter1_id?: number | null;
  diameter2_id?: number | null;
  diameter3_id?: number | null;
  unit?: string | null;
  description?: string | null;
  office_id?: number | null;
  length?: number | null;
  compatibility_group?: any[] | null;
  typical_location?: string | null;
  is_active?: boolean;
  is_terminal?: boolean;
  year?: number | null;
  created_by_id?: number | null; // Usually set by backend based on authenticated user
}

export interface PipeFittingUpdate {
  name?: string;
  material_id?: number;
  module_id?: number;
  diameter1_id?: number | null;
  diameter2_id?: number | null;
  diameter3_id?: number | null;
  unit?: string | null;
  description?: string | null;
  office_id?: number | null;
  length?: number | null;
  compatibility_group?: any[] | null;
  typical_location?: string | null;
  is_active?: boolean;
  is_terminal?: boolean;
  year?: number | null;
  modified_by_id?: number | null; // Usually set by backend
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  // Add these if your backend includes them and you need them
  // page?: number;
  // limit?: number;
  // pages?: number;
}
