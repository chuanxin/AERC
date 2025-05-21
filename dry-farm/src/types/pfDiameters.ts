// 口徑基本接口
export interface PFDiameterBase {
  value: number;
  name: string;
}

// 用於創建新口徑的接口
export interface PFDiameterCreate extends PFDiameterBase {
}

// 用於更新口徑的接口
export interface PFDiameterUpdate {
  value?: number;
  name?: string;
}

// 口徑響應接口
export interface PFDiameter {
  id: number;
  value: number;
  name: string;
}

// 分頁響應接口
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
}
