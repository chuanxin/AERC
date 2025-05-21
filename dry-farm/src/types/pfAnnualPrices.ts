export interface PFAnnualPrice {
  id: number;
  pipe_fitting_id: number;
  office_id?: number | null;
  year: number;
  price: number;
  is_active: boolean;
  created_at: string;
  modified_at: string;
  created_by_id?: number | null;
  modified_by_id?: number | null;
}

export interface PFAnnualPriceCreate {
  pipe_fitting_id: number;
  office_id?: number | null;
  year: number;
  price: number;
  is_active?: boolean;
  created_by_id?: number | null;
}

export interface PFAnnualPriceUpdate {
  pipe_fitting_id?: number;
  office_id?: number | null;
  year?: number;
  price?: number;
  is_active?: boolean;
  modified_by_id?: number | null;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
}
