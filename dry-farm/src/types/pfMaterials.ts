// 材質基本接口
export interface PFMaterialBase {
  name: string;
}

// 用於創建新材質的接口
export interface PFMaterialCreate extends PFMaterialBase {
}

// 用於更新材質的接口
export interface PFMaterialUpdate {
  name?: string;
}

// 材質響應接口
export interface PFMaterial {
  id: number;
  name: string;
}

// 分頁響應接口
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
}
