/**
 * AERC 灌溉設施補助標準配置
 * 基於 PDF 附表規範建立正確的補助金額計算標準
 */

export interface SubsidyStandards {
  powerEquipment: {
    general: Record<string, number>;
    indigenous: Record<string, number>;
  };
  storageEquipment: {
    general: Record<string, Record<number, number>>;
    indigenous: Record<string, Record<number, number>>;
  };
  controlEquipment: {
    general: number; // 元/公頃
    indigenous: number; // 元/公頃
  };
}

/**
 * 官方補助標準 - 完全對應 PDF 附表規範
 */
export const SUBSIDY_STANDARDS: SubsidyStandards = {
  // 動力設備補助上限（元/臺）
  powerEquipment: {
    general: {
      '馬達（含抽水機）': 4500,
      '汽油引擎': 7000,
      '柴油引擎': 12000,
      '柱塞式泵': 7000
    },
    indigenous: {
      '馬達（含抽水機）': 4950,
      '汽油引擎': 7700,
      '柴油引擎': 13200,
      '柱塞式泵': 7700
    }
  },

  // 調蓄設施(蓄水槽)補助上限（元）
  storageEquipment: {
    general: {
      '鋁合金': {
        10: 24000, 20: 32000, 30: 40000, 40: 48000, 50: 56000,
        60: 64000, 70: 73000, 80: 91000, 90: 99000, 100: 104000
      },
      '塑膠類': {
        10: 24000, 20: 32000, 30: 40000, 40: 48000, 50: 56000,
        60: 64000, 70: 73000, 80: 91000, 90: 99000, 100: 104000
      },
      '不鏽鋼': {
        10: 40000, 20: 84000, 30: 108000, 40: 124000, 50: 144000,
        60: 157000, 70: 176000, 80: 190000, 90: 216000, 100: 244000
      }
    },
    indigenous: {
      '鋁合金': {
        10: 26400, 20: 35200, 30: 44000, 40: 52800, 50: 61600,
        60: 70400, 70: 80300, 80: 100100, 90: 108900, 100: 114400
      },
      '塑膠類': {
        10: 26400, 20: 35200, 30: 44000, 40: 52800, 50: 61600,
        60: 70400, 70: 80300, 80: 100100, 90: 108900, 100: 114400
      },
      '不鏽鋼': {
        10: 44000, 20: 92400, 30: 118800, 40: 136400, 50: 158400,
        60: 172700, 70: 193600, 80: 209000, 90: 237600, 100: 268400
      }
    }
  },

  // 調蓄控制設施補助上限（元/公頃）
  controlEquipment: {
    general: 230000,
    indigenous: 253000
  }
};

/**
 * 根據設施類型、設備、地區計算正確補助金額
 */
export const calculateSubsidyAmount = (
  facilityType: 'power' | 'storage' | 'control',
  equipment: string,
  region: 'general' | 'indigenous',
  quantity: number = 1,
  tonnage?: number,
  area?: number
): number => {
  
  switch (facilityType) {
    case 'power': {
      const unitSubsidy = SUBSIDY_STANDARDS.powerEquipment[region][equipment];
      if (!unitSubsidy) {
        console.warn(`未找到動力設備 "${equipment}" 在 ${region} 地區的補助標準`);
        return 0;
      }
      return unitSubsidy * quantity;
    }

    case 'storage': {
      const [material] = equipment.split('-');
      const materialStandards = SUBSIDY_STANDARDS.storageEquipment[region][material];
      
      if (!materialStandards || !tonnage) {
        console.warn(`未找到調蓄設施 "${material}-${tonnage}噸" 在 ${region} 地區的補助標準`);
        return 0;
      }

      // 找到對應噸數的補助金額
      const subsidyAmount = materialStandards[tonnage];
      if (!subsidyAmount) {
        console.warn(`調蓄設施噸數 ${tonnage} 不在補助範圍內（10-100噸）`);
        return 0;
      }

      return subsidyAmount * quantity;
    }

    case 'control': {
      const unitSubsidy = SUBSIDY_STANDARDS.controlEquipment[region];
      if (!area) {
        console.warn(`調節控制設施需要提供設施面積進行計算`);
        return 0;
      }
      return unitSubsidy * area;
    }

    default:
      console.warn(`未知的設施類型: ${facilityType}`);
      return 0;
  }
};

/**
 * 判斷地區類型（需要從 step2 的土地資料中取得）
 */
export const determineRegionType = (aboriginalArea?: boolean): 'general' | 'indigenous' => {
  return aboriginalArea ? 'indigenous' : 'general';
};

/**
 * 驗證調蓄設施參數 - 修正邏輯錯誤
 */
export const validateStorageFacility = (material: string, tonnage: number, area?: number): boolean => {
  // 檢查材料是否合法
  if (!['鋁合金', '不鏽鋼', '塑膠類'].includes(material)) {
    console.warn(`調蓄設施材料不合法: ${material}`);
    return false;
  }

  // 檢查噸數範圍
  if (tonnage < 10 || tonnage > 100) {
    console.warn(`調蓄設施噸數不在範圍內: ${tonnage}（應為10-100噸）`);
    return false;
  }

  // 檢查面積限制（根據PDF附表規範）
  if (area !== undefined) {
    // 核定面積未達0.1公頃者，不予補助
    if (area < 0.1) {
      console.warn(`調蓄設施面積不足: ${area}公頃（最低要求0.1公頃）`);
      return false;
    }
    
    // 檢查容量限制：面積0.1-0.3公頃最大50噸，0.3公頃以上最大100噸
    const maxCapacity = getStorageCapacityLimit(area);
    if (tonnage > maxCapacity) {
      console.warn(`調蓄設施噸數超過面積限制: ${tonnage}噸 > ${maxCapacity}噸（面積${area}公頃）`);
      return false;
    }
  }

  console.log(`調蓄設施參數驗證通過: ${material}-${tonnage}噸，面積${area}公頃`);
  return true;
};

/**
 * 取得調蓄設施的最大容量限制
 */
export const getStorageCapacityLimit = (area: number): number => {
  if (area >= 0.3) {
    return 100; // 0.3公頃以上：最大容量100噸
  } else if (area >= 0.1) {
    return 50;  // 0.1公頃以上未達0.3公頃：最大容量50噸
  } else {
    return 0;   // 未達0.1公頃：不予補助
  }
};

/**
 * 計算已新增設施列表中的調蓄設施總容量
 */
export const calculateExistingStorageCapacity = (facilities: Array<{
  type: string;
  name: string;
  quantity: number;
}>): number => {
  return facilities
    .filter(facility => facility.type === 'storage')
    .reduce((totalCapacity, facility) => {
      // 從設施名稱中提取噸數，格式: "材料-噸數噸"
      const match = facility.name.match(/-(\d+)噸/);
      if (match) {
        const tonnage = parseInt(match[1], 10);
        const quantity = facility.quantity || 1;
        return totalCapacity + (tonnage * quantity);
      }
      return totalCapacity;
    }, 0);
};

/**
 * 根據面積和已有容量計算剩餘可申請容量
 */
export const getAvailableStorageCapacity = (area: number, existingCapacity: number): number => {
  const maxCapacity = getStorageCapacityLimit(area);
  return Math.max(0, maxCapacity - existingCapacity);
};

/**
 * 檢查指定噸數的調蓄設施是否可以加入
 */
export const canAddStorageFacility = (
  area: number,
  existingCapacity: number,
  newTonnage: number,
  newQuantity: number = 1
): boolean => {
  const availableCapacity = getAvailableStorageCapacity(area, existingCapacity);
  const requiredCapacity = newTonnage * newQuantity;
  
  console.log(`[容量檢查] 面積:${area}公頃, 已用:${existingCapacity}噸, 可用:${availableCapacity}噸, 需要:${requiredCapacity}噸`);
  
  return requiredCapacity <= availableCapacity;
};

/**
 * 計算已新增設施列表中的調蓄控制設施累積補助金額
 */
export const calculateExistingControlSubsidy = (facilities: Array<{
  type: string;
  subsidyAmount?: number;
}>): number => {
  return facilities
    .filter(facility => facility.type === 'control')
    .reduce((totalSubsidy, facility) => {
      return totalSubsidy + (facility.subsidyAmount || 0);
    }, 0);
};

/**
 * 根據面積和地區類型計算調蓄控制設施的總補助上限
 */
export const getControlSubsidyLimit = (area: number, region: 'general' | 'indigenous'): number => {
  const unitSubsidy = SUBSIDY_STANDARDS.controlEquipment[region];
  return unitSubsidy * area;
};

/**
 * 根據面積和已有補助金額計算剩餘可申請補助額度
 */
export const getAvailableControlSubsidy = (
  area: number, 
  region: 'general' | 'indigenous',
  existingSubsidy: number
): number => {
  const totalLimit = getControlSubsidyLimit(area, region);
  return Math.max(0, totalLimit - existingSubsidy);
};

/**
 * 計算調蓄控制設施的實際可獲得補助金額
 * 需要考慮已有設施的累積補助金額，確保不超過每公頃補助上限
 */
export const calculateControlActualSubsidy = (
  area: number,
  region: 'general' | 'indigenous',
  existingSubsidy: number,
  newFacilityCost: number
): number => {
  const availableSubsidy = getAvailableControlSubsidy(area, region, existingSubsidy);
  const actualSubsidy = Math.min(newFacilityCost, availableSubsidy);
  
  console.log(`[調蓄控制設施補助計算] 面積:${area}公頃, 地區:${region}, 已用補助:${existingSubsidy}, 剩餘額度:${availableSubsidy}, 設施成本:${newFacilityCost}, 實際補助:${actualSubsidy}`);
  
  return actualSubsidy;
};

/**
 * 調蓄控制設施整體分配結果介面
 */
export interface ControlSubsidyAllocation {
  facilityIndex: number;
  totalCost: number;
  subsidyAmount: number;
  selfPaidAmount: number;
  subsidyRatio: number; // 補助比例 (0-1)
}

/**
 * 🔥 Linus式修復：調蓄控制設施整體性補助分配
 * 計算所有調蓄控制設施的總成本，然後按比例分配補助金額
 */
export const calculateControlFacilitiesAllocation = (
  area: number,
  region: 'general' | 'indigenous',
  controlFacilities: Array<{
    totalPrice: number;
    quantity: number;
  }>
): ControlSubsidyAllocation[] => {
  // 1. 計算所有調蓄控制設施的總成本
  const totalCost = controlFacilities.reduce((sum, facility) => sum + (facility.totalPrice || 0), 0);
  
  // 2. 計算補助上限
  const subsidyLimit = getControlSubsidyLimit(area, region);
  
  // 3. 計算實際總補助金額（不超過上限）
  const totalActualSubsidy = Math.min(totalCost, subsidyLimit);
  
  // 4. 計算整體補助比例
  const overallSubsidyRatio = totalCost > 0 ? totalActualSubsidy / totalCost : 0;
  
  // 5. 按比例分配給每個設施
  const allocations: ControlSubsidyAllocation[] = controlFacilities.map((facility, index) => {
    const facilityCost = facility.totalPrice || 0;
    const facilitySubsidy = facilityCost * overallSubsidyRatio;
    const facilitySelfPaid = facilityCost - facilitySubsidy;
    
    return {
      facilityIndex: index,
      totalCost: facilityCost,
      subsidyAmount: Math.round(facilitySubsidy), // 四捨五入到整數
      selfPaidAmount: Math.round(facilitySelfPaid), // 四捨五入到整數
      subsidyRatio: overallSubsidyRatio
    };
  });
  
  console.log(`[調蓄控制設施整體分配] 面積:${area}公頃, 地區:${region}, 總成本:${totalCost}, 補助上限:${subsidyLimit}, 實際補助:${totalActualSubsidy}, 補助比例:${(overallSubsidyRatio * 100).toFixed(1)}%`);
  
  return allocations;
};

/**
 * 計算調蓄控制設施的總成本（包括預覽中的新設施）
 */
export const calculateControlTotalCost = (
  facilities: Array<{
    type: string;
    totalPrice?: number;
  }>,
  previewCost?: number
): number => {
  const existingCost = facilities
    .filter(facility => facility.type === 'control')
    .reduce((sum, facility) => sum + (facility.totalPrice || 0), 0);
  
  return existingCost + (previewCost || 0);
};
