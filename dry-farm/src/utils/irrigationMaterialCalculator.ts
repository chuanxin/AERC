/**
 * 灌溉材料計算器
 * 
 * 基於14種公式條件的動態材料計算工具庫
 * 負責將前端灌溉系統配置參數轉換為所需材料清單
 * 
 * 核心功能：
 * 1. 前端欄位映射到Legacy系統欄位
 * 2. 根據灌溉型式和配置決定計算公式
 * 3. 生成對應的材料組和物料清單
 * 4. 支援版本控制和價格過濾
 */

// ===== 型別定義 =====

export interface FormInputs {
  Length?: number;
  width?: number;
  SL?: number;  // 支管行距
  SS?: number;  // 噴頭間距
  L1Len?: number;
  L1Material?: number;
  L1Spec?: number;
  L1Price?: number;
  L1MatAmt?: number;
  BranchSpec?: number;
  BranchMaterial?: number;
  NozzleMaterial?: number;
  ddl_EndType?: number;
}

export interface MaterialData {
  // 基本參數
  Length: number;
  width: number;
  SL: number;
  SS: number;

  // 主管1相關
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
  BranchMaterial: number;

  // 末端設施相關
  NozzleAmt: number;
  NozzleMaterial: number;
  EndFacilityPomno?: string;

  // 豎管相關
  StandPipeSpec: number;
  StandPipeLength: number;
  StdpipeMat: number;

  // 變更相關
  ChangeBranchSpec: number;
  NewBranchSpec: number | null;

  // 設施類型
  ddl_FacType: number;
  ddl_WtaerSrc: number;
}

export interface MaterialItem {
  pomno: string;
  groupId: number;
  groupName: string;
  mattype: string;
  matname: string;
  matunit: string;
  matqty: number;
  matprice: number;
  totalPrice: number;
  spec1: string;
  description: string;
  order: number;
  debugMatchData?: any;
}

export interface MaterialGroup {
  GroupNo: number;
  GroupName: string;
  List: MaterialItem[];
}

export interface MaterialGenerationOptions {
  excludeNoPriceMaterials?: boolean;
  version?: 'v1' | 'v2';
}

// ===== 工具函數 =====

/**
 * 獲取物料編號 (模擬)
 */
export const getPOMNo = (moduleType: string, name: string): string => {
  return (Math.floor(Math.random() * 10000) + 10000).toString();
};

/**
 * 計算總價格
 */
export const calculateTotalPrice = (materials: MaterialItem[]): number => {
  return materials.reduce((sum, material) => sum + material.totalPrice, 0);
};

// ===== 核心計算函數 =====

/**
 * 主要材料計算入口函數
 * 
 * @param formInputs 前端表單輸入數據
 * @param localFormData 本地表單數據 (需要從外部傳入)
 * @param options 材料生成選項
 * @returns 材料組陣列
 */
export const calculateIrrigationMaterials = (
  formInputs: FormInputs,
  localFormData: any,
  options: MaterialGenerationOptions = {}
): MaterialGroup[] => {
  const { excludeNoPriceMaterials = false, version = 'v1' } = options;
  
  console.log(`[calculateIrrigationMaterials] 使用版本: ${version}, 排除無單價材料: ${excludeNoPriceMaterials}`);

  // 映射前端欄位到legacy欄位名稱
  const legacyData = mapFormDataToLegacyFields(formInputs, localFormData);

  // 決定使用哪個公式
  const formulaNumber = determineCalculationFormula(legacyData);
  console.log(`[calculateIrrigationMaterials] 使用公式 ${formulaNumber} 進行材料計算 (版本: ${version})`);

  // 根據公式生成材料列表
  const materialGroups = generateMaterialsByFormula(formulaNumber, legacyData, localFormData);
  
  // 版本 v2 過濾邏輯
  if (version === 'v2' || excludeNoPriceMaterials) {
    return filterMaterialGroupsByPrice(materialGroups);
  }
  
  return materialGroups;
};

/**
 * 過濾沒有單價的材料（版本 v2 專用）
 */
export const filterMaterialGroupsByPrice = (materialGroups: MaterialGroup[]): MaterialGroup[] => {
  const filteredGroups = materialGroups.map(group => {
    const filteredList = group.List.filter((material: MaterialItem) => {
      const hasValidPrice = material.matprice !== null && 
                           material.matprice !== undefined && 
                           material.matprice > 0;
      
      if (!hasValidPrice) {
        console.log(`[filterMaterialGroupsByPrice] 排除無單價材料: ${material.matname} (${material.description})`);
      }
      
      return hasValidPrice;
    });
    
    return {
      ...group,
      List: filteredList
    };
  }).filter(group => group.List.length > 0);

  const originalCount = materialGroups.reduce((sum, group) => sum + group.List.length, 0);
  const filteredCount = filteredGroups.reduce((sum, group) => sum + group.List.length, 0);
  
  console.log(`[filterMaterialGroupsByPrice] 過濾結果: ${originalCount} -> ${filteredCount} 項材料 (移除 ${originalCount - filteredCount} 項無單價材料)`);
  
  return filteredGroups;
};

/**
 * 映射前端欄位到Legacy系統欄位
 */
export const mapFormDataToLegacyFields = (formInputs: FormInputs, localFormData: any): MaterialData => {
  const fieldLength = localFormData.fieldLength || formInputs.Length || 0;
  const fieldWidth = localFormData.fieldWidth || formInputs.width || 0;
  const branchPipeSpacing = localFormData.branchPipeSpacing_SL || formInputs.SL || 0;
  const sprinklerSpacing = localFormData.sprinklerSpacing_SS || formInputs.SS || 0;

  // 計算支管數量和末端設施數量
  const branchAmt = branchPipeSpacing > 0 ? Math.floor(fieldLength / branchPipeSpacing) : 0;
  const branchLength = fieldWidth;
  const nozzlePerBranch = sprinklerSpacing > 0 ? Math.ceil(fieldWidth / sprinklerSpacing) : 0;
  const totalNozzles = branchAmt * nozzlePerBranch;

  return {
    // 基本參數
    Length: fieldLength,
    width: fieldWidth,
    SL: branchPipeSpacing,
    SS: sprinklerSpacing,

    // 主管相關
    L1Len: formInputs.L1Len || localFormData.mainPipeLength || 0,
    L1Material: formInputs.L1Material || localFormData.mainPipeMaterialId || 1,
    L1Spec: formInputs.L1Spec || localFormData.mainPipeDiameterId || 1,
    L1Price: formInputs.L1Price || localFormData.mainPipeUnitPrice || 0,
    L1MatAmt: formInputs.L1MatAmt || localFormData.mainPipeQuantity || 0,
    L1Bend: 3,
    L1Receptacle: (localFormData.mainPipe2Enabled &&
                   localFormData.mainPipeDiameterId &&
                   localFormData.mainPipe2DiameterId &&
                   localFormData.mainPipeDiameterId === localFormData.mainPipe2DiameterId) ? 2 : 1,

    // 主管2相關
    L2Len: localFormData.mainPipe2Enabled ? (localFormData.mainPipe2Length || 0) : 0,
    L2Material: localFormData.mainPipe2Enabled ? (localFormData.mainPipe2MaterialId || 0) : 0,
    L2Spec: localFormData.mainPipe2Enabled ? (localFormData.mainPipe2DiameterId || 0) : 0,
    L2Price: localFormData.mainPipe2Enabled ? (localFormData.mainPipe2UnitPrice || 0) : 0,
    L2MatAmt: localFormData.mainPipe2Enabled ? (localFormData.mainPipe2Quantity || 0) : 0,
    L2Bend: localFormData.mainPipe2Enabled ? 3 : 0,

    // 灌溉系統類型
    ddl_EndType: formInputs.ddl_EndType || localFormData.irrigationTypeId || 1,
    ddl_Sprinkler: localFormData.sprinklerSubtypeId || 2,
    ddl_Drop: localFormData.dripperSubtypeId || 7,
    PerforatedPipe: localFormData.perforatedPipeDirection || 1,

    // 支管相關
    BranchAmt: branchAmt,
    BranchLength: branchLength,
    BranchSpec: localFormData.branchPipeDiameterId || formInputs.BranchSpec || 3,
    BranchMaterial: localFormData.branchPipeMaterialId || formInputs.BranchMaterial || 1,

    // 末端設施相關
    NozzleAmt: totalNozzles,
    NozzleMaterial: localFormData.endFacilitySpecId || formInputs.NozzleMaterial || 1,
    EndFacilityPomno: localFormData.endFacilityPomno,

    // 豎管相關
    StandPipeSpec: localFormData.riserPipeSpecId || 2,
    StandPipeLength: localFormData.riserHeight_H || 1,
    StdpipeMat: localFormData.riserPipeMaterialId || 1,

    // 變更相關
    ChangeBranchSpec: 0,
    NewBranchSpec: null,

    // 設施類型
    ddl_FacType: localFormData.facilityTypeId || 1,
    ddl_WtaerSrc: localFormData.waterSourceId || 1
  };
};

/**
 * 決定使用哪個計算公式 (14種公式條件)
 */
export const determineCalculationFormula = (data: MaterialData): number => {
  const endType = data.ddl_EndType;
  const hasL2 = data.L2MatAmt > 0;
  const hasSpecChange = data.ChangeBranchSpec !== 0;
  const dropType = data.ddl_Drop;

  if (endType === 1) { // 穿孔管系統
    if (!hasL2) return 1;
    return 2;
  }

  if (endType === 2) { // 噴頭式系統
    if (!hasSpecChange && !hasL2) return 3;
    if (!hasSpecChange && hasL2) return 4;
    if (hasSpecChange && !hasL2) return 5;
    if (hasSpecChange && hasL2) return 6;
  }

  if (endType === 3) { // 微噴系統
    if (!hasSpecChange && !hasL2) return 7;
    if (!hasSpecChange && hasL2) return 8;
    if (hasSpecChange && !hasL2) return 9;
    if (hasSpecChange && hasL2) return 10;
  }

  if (endType === 4) { // 滴灌系統
    if (dropType === 7) { // 滴灌帶
      if (!hasL2) return 11;
      return 12;
    }
    if (dropType === 8) { // 滴灌管
      if (!hasL2) return 13;
      return 14;
    }
  }

  // 預設返回公式1
  return 1;
};

/**
 * 根據公式生成材料列表
 * 
 * 注意：此函數需要依賴外部的材料生成函數，這裡僅提供架構
 * 實際的材料生成邏輯需要在使用時注入相關依賴
 * 
 * @param formulaNumber 公式編號
 * @param data 映射後的材料數據
 * @param localFormData 原始表單數據
 * @param materialGenerators 材料生成函數集合
 */
export const generateMaterialsByFormula = (
  formulaNumber: number, 
  data: MaterialData,
  localFormData: any,
  materialGenerators?: any
): MaterialGroup[] => {
  console.log(`[generateMaterialsByFormula] 開始生成材料，公式: ${formulaNumber}`);
  
  // 如果沒有提供材料生成器，返回空數組
  // 實際應用中應該從組件注入材料生成函數
  if (!materialGenerators) {
    console.warn(`[generateMaterialsByFormula] 缺少材料生成器，返回空數組`);
    return [];
  }
  
  const materialGroups: MaterialGroup[] = [];

  // 所有公式都包含主管1材料
  materialGroups.push(materialGenerators.generateL1MainPipeLine(data));

  // 當主管材質為鍍鋅鋼時，添加制水閥到滴水管組
  materialGroups.push(materialGenerators.generateGalvanizedSteelValveGroup(data));

  // 根據公式添加特定材料組
  switch (formulaNumber) {
    case 1:
      materialGroups.push(materialGenerators.generatePerforatedPipe(data, data.L1Spec));
      break;
    case 2:
      materialGroups.push(materialGenerators.generatePerforatedPipe(data, data.L1Spec));
      materialGroups.push(materialGenerators.generateL2MainPipeLine(data));
      break;
    case 3:
      materialGroups.push(materialGenerators.generateBranchPipeGroup(data, data.L1Spec));
      materialGroups.push(materialGenerators.generateStandPipeGroup(data));
      materialGroups.push(materialGenerators.generateSprinklerHeadsGroup(data));
      break;
    case 4:
      materialGroups.push(materialGenerators.generateBranchPipeGroup(data, data.L1Spec));
      materialGroups.push(materialGenerators.generateStandPipeGroup(data));
      materialGroups.push(materialGenerators.generateSprinklerHeadsGroup(data));
      materialGroups.push(materialGenerators.generateL2MainPipeLine(data));
      break;
    case 5:
      materialGroups.push(materialGenerators.generateNozzleChangeSystem(data, data.L1Spec));
      break;
    case 6:
      materialGroups.push(materialGenerators.generateNozzleChangeSystem(data, data.L1Spec));
      materialGroups.push(materialGenerators.generateL2MainPipeLine(data));
      break;
    case 7:
      materialGroups.push(materialGenerators.generateBranchPipeGroup(data, data.L1Spec));
      materialGroups.push(materialGenerators.generateStandPipeGroup(data));
      materialGroups.push(materialGenerators.generateMicroSprinklerHeadsGroup(data));
      break;
    case 8:
      materialGroups.push(materialGenerators.generateBranchPipeGroup(data, data.L1Spec));
      materialGroups.push(materialGenerators.generateStandPipeGroup(data));
      materialGroups.push(materialGenerators.generateMicroSprinklerHeadsGroup(data));
      materialGroups.push(materialGenerators.generateL2MainPipeLine(data));
      break;
    case 9:
      materialGroups.push(materialGenerators.generateMicroSprinklerChangeSystem(data, data.L1Spec));
      break;
    case 10:
      materialGroups.push(materialGenerators.generateMicroSprinklerChangeSystem(data, data.L1Spec));
      materialGroups.push(materialGenerators.generateL2MainPipeLine(data));
      break;
    case 11:
      materialGroups.push(materialGenerators.generateDripTapeSystem(data, data.L1Spec));
      break;
    case 12:
      materialGroups.push(materialGenerators.generateDripTapeSystem(data, data.L1Spec));
      materialGroups.push(materialGenerators.generateL2MainPipeLine(data));
      break;
    case 13:
      materialGroups.push(materialGenerators.generateDripPipeSystem(data, data.L1Spec));
      break;
    case 14:
      materialGroups.push(materialGenerators.generateDripPipeSystem(data, data.L1Spec));
      materialGroups.push(materialGenerators.generateL2MainPipeLine(data));
      break;
    default:
      console.warn(`[generateMaterialsByFormula] 未知的公式編號: ${formulaNumber}`);
  }

  return materialGroups.filter(group => group && group.List && group.List.length > 0);
};

/**
 * 驗證自動帶入材料的條件
 */
export const validateAutoFillConditions = (localFormData: any): boolean => {
  const basicConditions =
    !!localFormData.fieldLength &&
    !!localFormData.fieldWidth &&
    !!localFormData.mainPipeLength &&
    !!localFormData.mainPipeMaterialId &&
    !!localFormData.mainPipeDiameterId &&
    !!localFormData.irrigationTypeId;

  const mainPipe2Conditions = !localFormData.mainPipe2Enabled || (
    !!localFormData.mainPipe2Length &&
    !!localFormData.mainPipe2MaterialId &&
    !!localFormData.mainPipe2DiameterId
  );

  let irrigationTypeSpecificConditions = true;
  
  if (localFormData.irrigationTypeId === 1) { // 穿孔管
    irrigationTypeSpecificConditions = !!localFormData.perforatedPipeDirection;
  } else if ([2, 3].includes(localFormData.irrigationTypeId)) { // 噴頭式或微噴
    irrigationTypeSpecificConditions = 
      !!localFormData.branchPipeSpacing_SL &&
      !!localFormData.sprinklerSpacing_SS &&
      !!localFormData.branchPipeMaterialId &&
      !!localFormData.branchPipeDiameterId &&
      !!localFormData.riserHeight_H &&
      !!localFormData.riserPipeMaterialId &&
      !!localFormData.riserPipeSpecId &&
      !!localFormData.endFacilitySpecId;
  } else if (localFormData.irrigationTypeId === 4) { // 滴灌
    irrigationTypeSpecificConditions = 
      !!localFormData.branchPipeSpacing_SL &&
      !!localFormData.sprinklerSpacing_SS &&
      !!localFormData.branchPipeMaterialId &&
      !!localFormData.branchPipeDiameterId &&
      !!localFormData.dripperSubtypeId;
  }

  return basicConditions && mainPipe2Conditions && irrigationTypeSpecificConditions;
};

/**
 * 獲取欄位中文名稱映射
 */
export const getFieldChineseName = (fieldName: string): string => {
  const fieldNameMap: Record<string, string> = {
    'fieldLength': '田間坵塊長度',
    'fieldWidth': '田間坵塊寬度',
    'fundingSourceId': '補助單位',
    'irrigationTypeId': '灌溉型式',
    'waterSourceId': '灌溉水源',
    'mainPipeLength': '主管1長度',
    'mainPipeMaterialId': '主管1材質',
    'mainPipeDiameterId': '主管1管徑',
    'mainPipe2Length': '主管2長度',
    'mainPipe2MaterialId': '主管2材質',
    'mainPipe2DiameterId': '主管2管徑',
    'perforatedPipeDirection': '穿孔管出水方向',
    'branchPipeSpacing_SL': '支管行距(SL)',
    'sprinklerSpacing_SS': '噴頭間距(SS)',
    'branchPipeMaterialId': '支管材質',
    'branchPipeDiameterId': '支管規格',
    'facilityTypeId': '設施型式',
    'sprinklerSubtypeId': '噴頭類型',
    'dripperSubtypeId': '滴灌類型',
    'riserHeight_H': '豎管高度',
    'riserPipeMaterialId': '豎管材質',
    'riserPipeSpecId': '豎管規格',
    'endFacilitySpecId': '末端設施規格',
    'endFacilityPomno': '末端設施名稱'
  };

  return fieldNameMap[fieldName] || fieldName;
};