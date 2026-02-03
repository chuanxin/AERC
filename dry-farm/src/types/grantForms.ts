// 基礎申請人資料類型 - 包含所有共同的基本欄位
export interface BaseGrantData {
  name: string;
  id: string;
  phone: string;
  phone2: string | null;
  county: string;
  countyId: number | null;
  town: string;
  townId: number | null;
  village: string;
  villageId: number | null;
  address: string;
  office: string;
  officeId: number | null;
  valid: boolean | null; // 允許 null 值，後端會自動轉換為 false
}

export interface GrantCreateRequest extends BaseGrantData {
  undertracker: string; // 只定義新增的欄位
  isDisasterCase: boolean; // 是否為災害案件
  disasterCaseDescription: string; // 災害案件說明
}

export interface Step1Data extends GrantCreateRequest {
  caseNumber: string;
  receivedDate: string;
  receivedTime: string;
}

// 方法 2: 使用交集類型 (type alias + intersection)
export type GrantCreateRequestAlt = BaseGrantData & {
  undertracker: string;
}

export type Step1DataAlt = BaseGrantData & {
  caseNumber: string;
  receivedDate: string;
  receivedTime: string;
}

// 方法 3: 使用 Omit 創建變體類型
export type GrantCreateWithoutTracker = Omit<GrantCreateRequest, 'undertracker'>

// 方法 4: 使用 Pick 選擇部分欄位
export type BasicApplicantInfo = Pick<BaseGrantData, 'name' | 'id' | 'phone' | 'phone2' | 'county' | 'town' | 'village'>

// 保持向後兼容的舊名稱 (使用 type alias)
export type step1Data = Step1Data; // 映射到新的命名規範

// ================================
// 更多進階的類型繼承範例
// ================================

// 方法 5: 條件類型擴展
export type GrantDataWithOptionalFields<T extends keyof BaseGrantData> = BaseGrantData & {
  [K in T]?: BaseGrantData[K]; // 將指定欄位變為可選
}

// 方法 6: 部分覆蓋類型
export type GrantDataWithStringIds = Omit<BaseGrantData, 'countyId' | 'townId' | 'villageId' | 'officeId'> & {
  countyId: string;  // 覆蓋為 string 類型
  townId: string;
  villageId: string;
  officeId: string;
}

// 方法 7: 遞迴擴展 (用於多層資料結構)
export interface GrantWithSteps extends BaseGrantData {
  step1?: Step1Data;
  step2?: Record<string, unknown>; // 可以進一步定義 Step2Data
  step3?: Record<string, unknown>;
}

// 方法 8: 聯合類型 (Union Types)
export type GrantStatus = 'pending' | 'approved' | 'rejected' | 'in_review';

export interface GrantWithStatus extends BaseGrantData {
  status: GrantStatus;
  statusHistory?: Array<{
    status: GrantStatus;
    timestamp: string;
    operator: string;
  }>;
}

// 方法 9: 泛型接口
export interface ApiResponse<T = Record<string, unknown>> {
  success: boolean;
  data: T;
  message?: string;
  error?: string;
}

// 使用泛型的具體類型
export type GrantCreateResponse = ApiResponse<GrantCreateRequest>;
export type Step1Response = ApiResponse<Step1Data>;

// 方法 10: 映射類型 (Mapped Types)
export type PartialGrant = Partial<BaseGrantData>; // 所有欄位變為可選
export type RequiredGrant = Required<BaseGrantData>; // 所有欄位變為必填
export type ReadonlyGrant = Readonly<BaseGrantData>; // 所有欄位變為唯讀

// ================================
// 使用範例說明
// ================================

/*
使用繼承的優點：
1. 代碼重用 - 避免重複定義相同欄位
2. 維護性 - 修改基礎類型會自動影響所有繼承的類型
3. 類型安全 - TypeScript 會檢查類型相容性
4. 擴展性 - 可以輕鬆添加新欄位而不影響現有代碼

使用範例：

// 創建基礎資料
const baseData: BaseGrantData = {
  name: "張三",
  id: "A123456789",
  // ... 其他欄位
};

// 擴展為申請資料
const createRequest: GrantCreateRequest = {
  ...baseData,
  undertracker: "李四" // 只需要添加新欄位
};

// 使用交集類型
const altRequest: GrantCreateRequestAlt = {
  ...baseData,
  undertracker: "王五"
};

// 使用 Pick 選擇部分欄位
const basicInfo: BasicApplicantInfo = {
  name: baseData.name,
  id: baseData.id,
  phone: baseData.phone,
  county: baseData.county,
  town: baseData.town,
  village: baseData.village
};

*/
