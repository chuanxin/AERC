/**
 * Step4 材料計算相關的 TypeScript 類型定義
 */
import type { PipeFitting } from '@/types/pipeFittings'

// ============================================================================
// 基礎數據結構
// ============================================================================

/**
 * 前端表單輸入格式
 */
export interface FormInputs {
  Length?: number;
  width?: number;
  SL?: number; // 支管間距
  SS?: number; // 噴頭間距
  L1Len?: number;
  L1Material?: number;
  L1Spec?: number;
  L1Price?: number;
  L1MatAmt?: number;
  BranchSpec?: number;
  ChangeBranchSpec?: number;
  ddl_EndType?: number; // 灌溉系統類型
}

/**
 * 組件內部表單數據格式
 */
export interface LocalFormData {
  // 基本設施參數
  fieldLength?: number;
  fieldWidth?: number;
  branchPipeSpacing_SL?: number;
  sprinklerSpacing_SS?: number;

  // 主管1參數
  mainPipeLength?: number;
  mainPipeMaterialId?: number;
  mainPipeDiameterId?: number;
  mainPipeUnitPrice?: number;
  mainPipeQuantity?: number;

  // 主管2參數
  mainPipe2Enabled?: boolean;
  mainPipe2Length?: number;
  mainPipe2MaterialId?: number;
  mainPipe2DiameterId?: number;
  mainPipe2UnitPrice?: number;
  mainPipe2Quantity?: number;

  // 支管參數
  branchPipeDiameterId?: number;
  branchPipeChangeSpec?: number;

  // 灌溉系統類型
  irrigationTypeId?: number;
  sprinklerSubtypeId?: number;
  dripperSubtypeId?: number;
  perforatedPipeDirection?: number;

  // 豎管參數
  riserHeight_H?: number;
  riserPipeMaterialId?: number;
  riserPipeSpecId?: number;

  // 末端設施配置
  endFacilityPomno?: number;

  // 水源類型
  waterSourceId?: number;
}

/**
 * Legacy 格式的材料數據 (用於公式計算)
 */
export interface LegacyMaterialData {
  // 基本參數
  Length: number;
  width: number;
  SL: number;
  SS: number;

  // 主管相關
  L1Len: number;
  L1Material: number;
  L1Spec: number;
  L1Price: number;
  L1MatAmt: number;
  L1Bend: number;
  L1Receptacle: number;

  // 主管2相關
  L2Len: number;
  L2Material: number;
  L2Spec: number;
  L2Price: number;
  L2MatAmt: number;
  L2Bend: number;

  // 灌溉系統類型
  ddl_EndType: number;
  ddl_Sprinkler: number;
  ddl_Drop: number;
  PerforatedPipe: number;

  // 支管相關
  BranchAmt: number;
  BranchLength: number;
  BranchSpec: number;
  ChangeBranchSpec: number;

  // 末端設施數量
  NozzlePerBranch: number;
  TotalNozzles: number;

  // 末端設施配置
  endFacilityPomno?: number;

  // 豎管相關
  StandPipeLength?: number;
  StandPipeSpec?: number;
  StdpipeMat?: number;

  // 水源類型
  ddl_WtaerSrc: number;
}

// ============================================================================
// 材料相關數據結構
// ============================================================================

/**
 * 材料項目
 */
export interface MaterialItem {
  pomno: number | null;
  module: string;
  matname: string;
  module_id: number;
  mattype: string;
  spec1: string;
  spec2?: string;
  spec3?: string;
  itemunit: string;
  matprice: number | null;
  matamount: number;
  description: string;
  order: number;
  group: number;
  debugMatchData?: PipeFitting | null;
  isMainPipeMaterial?: boolean;
  customPrice?: number;
}

/**
 * 材料組
 */
export interface MaterialGroup {
  GroupNo: number;
  GroupName: string;
  List: MaterialItem[];
}

/**
 * 材料生成選項
 */
export interface MaterialGenerationOptions {
  version?: 'v1' | 'v2';
  excludeNoPriceMaterials?: boolean;
}

// ============================================================================
// 材料比對和選項數據
// ============================================================================

/**
 * 材料比對結果
 */
export interface MaterialMatchResult {
  pomno: number | null;
  matprice: number | null;
  matchedData: PipeFitting | null;
}

/**
 * 材料比對函數集合
 */
export interface MaterialMatchFunctions {
  matchMaterialFromStore: (
    moduleId: number,
    spec1: string,
    spec2?: string,
    spec3?: string,
    mattype?: string,
    matname?: string
  ) => MaterialMatchResult;

  matchMaterialByPomno: (pomno: string | number) => MaterialMatchResult;

  addMaterial: (
    materials: MaterialItem[],
    moduleId: number,
    spec1: string,
    spec2: string,
    mattype: string,
    config: Partial<MaterialItem>
  ) => boolean;

  addMainPipeMaterial: (
    materials: MaterialItem[],
    materialConfig: Partial<MaterialItem>,
    customPrice: number
  ) => boolean;

  calculateMaterialAmount: (amount: number, itemType: string) => number;
}

/**
 * 選項數據 (管材、口徑等)
 */
export interface OptionsData {
  pipeMaterialOptions: Array<{ id: number; name: string }>;
  pipeDiameterOptions: Array<{ id: number; name: string }>;
  irrigationTypeOptions: Array<{ id: number; name: string }>;
  sprinklerSubtypeOptions: Array<{ id: number; name: string }>;
  dripperSubtypeOptions: Array<{ id: number; name: string }>;
}

// ============================================================================
// 計算函數類型
// ============================================================================

/**
 * 材料生成器函數類型
 */
export type MaterialGenerator = (
  data: LegacyMaterialData,
  functions: MaterialMatchFunctions,
  options: OptionsData,
  groupId?: number,
  mainPipeSpec?: number
) => MaterialGroup;

/**
 * 公式計算函數類型
 */
export type FormulaCalculator = (
  formulaNumber: number,
  data: LegacyMaterialData,
  functions: MaterialMatchFunctions,
  options: OptionsData
) => MaterialGroup[];
