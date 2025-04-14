<template>
  <v-container :fluid="isFluid" class="pt-0">
    <v-card class="pa-0 mb-6">
      <v-card-title class="bg-light-blue-lighten-4 d-flex align-center py-2 px-4">
        <v-icon class="me-2" size="small">mdi-currency-usd</v-icon>
        <span class="text-subtitle-1 font-weight-medium">本年度預算執行即時資訊</span>
        <v-spacer></v-spacer>
        <v-btn
          icon
          variant="text"
          size="small"
          @click="toggleFluid"
          :title="isFluid ? '切換為固定寬度' : '切換為全寬模式'"
        >
          <v-icon>{{ isFluid ? 'mdi-arrow-collapse-horizontal' : 'mdi-arrow-expand-horizontal' }}</v-icon>
        </v-btn>
        <v-btn
          icon
          variant="text"
          size="small"
          @click="exportToExcel"
          title="匯出為Excel"
        >
          <v-icon>mdi-microsoft-excel</v-icon>
        </v-btn>
        <v-btn
          icon
          variant="text"
          size="small"
          @click="printTable"
          title="列印"
        >
          <v-icon>mdi-printer</v-icon>
        </v-btn>
      </v-card-title>

      <!-- 查詢條件區域 -->
      <v-card-text class="pa-3">
        <v-row dense>
          <v-col cols="12" sm="6" md="3">
            <v-select
              v-model="selectedYear"
              :items="yearOptions"
              label="年度"
              variant="outlined"
              density="compact"
              hide-details
              class="mb-2"
            ></v-select>
          </v-col>
          <v-col cols="12" sm="6" md="3">
            <v-select
              v-model="selectedMonth"
              :items="monthOptions"
              label="月份"
              variant="outlined"
              density="compact"
              hide-details
              class="mb-2"
            ></v-select>
          </v-col>
          <v-col cols="12" sm="6" md="3">
            <v-btn
              color="primary"
              variant="elevated"
              size="small"
              @click="fetchBudgetData"
              :loading="isLoading"
              class="mb-2"
            >
              <v-icon size="small" class="me-1">mdi-magnify</v-icon>
              查詢
            </v-btn>
          </v-col>
        </v-row>
      </v-card-text>

      <!-- Budget Data Table -->
      <div class="table-container" ref="tableContainer">
        <v-data-table
          :headers="headers"
          :items="budgetItems"
          :loading="isLoading"
          class="elevation-0 budget-table"
          density="compact"
          fixed-header
        >
          <!-- Custom header formatting -->
          <template v-slot:header="{ columns }">
            <tr>
              <th
                v-for="(column, i) in columns"
                :key="i"
                :class="getHeaderClass(column)"
              >
                {{ column.title }}
              </th>
            </tr>
            <tr class="formula-row">
              <th>受理單位</th>
              <th>(公頃)(a)</th>
              <th>(元)(b)</th>
              <th>(c)</th>
              <th>(公頃)(d)</th>
              <th>(元)(e)</th>
              <th>(元)(f)</th>
              <th>(g)</th>
              <th>(公頃)(h)</th>
              <th>(元)(i)</th>
              <th>(j=h/a)</th>
              <th>(k=i/b)</th>
            </tr>
          </template>

          <!-- Custom cell formatting -->
          <template v-slot:item="{ item, index }">
            <td v-for="(column, colIndex) in headers" :key="colIndex" :class="column.key === 'unit' ? getUnitCellClass(index) : 'text-right'">
              <span v-if="column.key === 'unit'">{{ item.unit }}</span>
              <span v-else-if="column.key === 'executionArea'">{{ formatNumber(item.executionArea) }}</span>
              <span v-else-if="column.key === 'executionBudget'">{{ formatCurrency(item.executionBudget) }}</span>
              <span v-else-if="column.key === 'households'">{{ formatNumber(item.households) }}</span>
              <span v-else-if="column.key === 'area'">{{ formatNumber(item.area, 4) }}</span>
              <span v-else-if="column.key === 'subsidy'">{{ formatCurrency(item.subsidy) }}</span>
              <span v-else-if="column.key === 'remainingSubsidy'" :class="{'negative-value': item.remainingSubsidy < 0}">{{ formatCurrency(item.remainingSubsidy) }}</span>
              <span v-else-if="column.key === 'acceptedHouseholds'">{{ formatNumber(item.acceptedHouseholds) }}</span>
              <span v-else-if="column.key === 'acceptedArea'">{{ formatNumber(item.acceptedArea, 4) }}</span>
              <span v-else-if="column.key === 'acceptedAmount'">{{ formatCurrency(item.acceptedAmount) }}</span>
              <span v-else-if="column.key === 'areaExecutionRate'">{{ item.areaExecutionRate }}</span>
              <span v-else-if="column.key === 'budgetExecutionRate'">{{ item.budgetExecutionRate }}</span>
              <span v-else>{{ item[column.key as keyof typeof item] }}</span>
            </td>
          </template>

          <!-- Custom footer for totals -->
          <template v-slot:bottom>
            <tr class="total-row">
              <td class="font-weight-bold">合計</td>
              <td class="text-right">{{ formatNumber(totalExecutionArea) }}</td>
              <td class="text-right">{{ formatCurrency(totalExecutionBudget) }}</td>
              <td class="text-right">{{ formatNumber(totalHouseholds) }}</td>
              <td class="text-right">{{ formatNumber(totalArea, 4) }}</td>
              <td class="text-right">{{ formatCurrency(totalSubsidy) }}</td>
              <td class="text-right" :class="{'negative-value': totalRemainingSubsidy < 0}">{{ formatCurrency(totalRemainingSubsidy) }}</td>
              <td class="text-right">{{ formatNumber(totalAcceptedHouseholds) }}</td>
              <td class="text-right">{{ formatNumber(totalAcceptedArea, 4) }}</td>
              <td class="text-right">{{ formatCurrency(totalAcceptedAmount) }}</td>
              <td class="text-right">{{ totalAreaExecutionRate }}</td>
              <td class="text-right">{{ totalBudgetExecutionRate }}</td>
            </tr>
          </template>
        </v-data-table>
        <div v-if="isOverflowing" class="scroll-hint">
          滑動下方捲軸以查看完整表格內容
        </div>
      </div>
    </v-card>
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';

const isFluid = ref(true);
const isLoading = ref(false);
const selectedYear = ref('113');
const selectedMonth = ref('4');

// 查詢選項
const yearOptions = [
  { title: '113年', value: '113' },
  { title: '112年', value: '112' },
  { title: '111年', value: '111' },
  { title: '110年', value: '110' }
];

const monthOptions = [
  { title: '1月', value: '1' },
  { title: '2月', value: '2' },
  { title: '3月', value: '3' },
  { title: '4月', value: '4' },
  { title: '5月', value: '5' },
  { title: '6月', value: '6' },
  { title: '7月', value: '7' },
  { title: '8月', value: '8' },
  { title: '9月', value: '9' },
  { title: '10月', value: '10' },
  { title: '11月', value: '11' },
  { title: '12月', value: '12' }
];

// 切換 fluid 狀態的方法
const toggleFluid = () => {
  isFluid.value = !isFluid.value;
  localStorage.setItem('preferFluid', String(isFluid.value));
  // 延遲檢查溢出狀態，以確保 DOM 已更新
  setTimeout(checkOverflow, 100);
};

// 匯出為Excel
const exportToExcel = () => {
  // 實際應用時，這裡會實現真正的匯出功能
  console.log('匯出為Excel');
};

// 列印表格
const printTable = () => {
  // 實際應用時，這裡會實現真正的列印功能
  console.log('列印表格');
};

// Table headers
const headers = [
  { title: '受理單位', key: 'unit', align: 'start' as const, width: '120px', sortable: false },
  { title: '預定執行面積', key: 'executionArea', align: 'end' as const, width: '100px', sortable: false },
  { title: '預定執行預算', key: 'executionBudget', align: 'end' as const, width: '120px', sortable: false },
  { title: '已編預算戶數', key: 'households', align: 'end' as const, width: '100px', sortable: false },
  { title: '已編預算面積', key: 'area', align: 'end' as const, width: '120px', sortable: false },
  { title: '已編列補助款', key: 'subsidy', align: 'end' as const, width: '120px', sortable: false },
  { title: '未編列補助款', key: 'remainingSubsidy', align: 'end' as const, width: '120px', sortable: false },
  { title: '已驗收戶數', key: 'acceptedHouseholds', align: 'end' as const, width: '100px', sortable: false },
  { title: '已驗收面積', key: 'acceptedArea', align: 'end' as const, width: '120px', sortable: false },
  { title: '已驗收金額', key: 'acceptedAmount', align: 'end' as const, width: '120px', sortable: false },
  { title: '面積執行率%', key: 'areaExecutionRate', align: 'end' as const, width: '100px', sortable: false },
  { title: '經費執行率%', key: 'budgetExecutionRate', align: 'end' as const, width: '100px', sortable: false },
];

// 根據圖片數據更新的樣本數據
const budgetItems = ref([
  { unit: '宜蘭管理處', executionArea: 10, executionBudget: 2680000, households: 18, area: 11.5354, subsidy: 2161320, remainingSubsidy: 518680, acceptedHouseholds: 8, acceptedArea: 4.3867, acceptedAmount: 965991, areaExecutionRate: '115.35%', budgetExecutionRate: '80.65%' },
  { unit: '北基管理處', executionArea: 5, executionBudget: 550000, households: 8, area: 3.0636, subsidy: 1009902, remainingSubsidy: -459902, acceptedHouseholds: 2, acceptedArea: 0.39, acceptedAmount: 159040, areaExecutionRate: '0.6127%', budgetExecutionRate: '1.8362%' },
  { unit: '桃園管理處', executionArea: 10, executionBudget: 3450000, households: 26, area: 17.3613, subsidy: 6172848, remainingSubsidy: -2722848, acceptedHouseholds: 9, acceptedArea: 5.5495, acceptedAmount: 1806603, areaExecutionRate: '1.7361%', budgetExecutionRate: '1.7892%' },
  { unit: '石門管理處', executionArea: 15, executionBudget: 2730000, households: 20, area: 9.2582, subsidy: 3630667, remainingSubsidy: -900667, acceptedHouseholds: 0, acceptedArea: 0, acceptedAmount: 0, areaExecutionRate: '0.6172%', budgetExecutionRate: '1.3299%' },
  { unit: '新竹管理處', executionArea: 20, executionBudget: 2270000, households: 28, area: 17.8373, subsidy: 1979291, remainingSubsidy: 290709, acceptedHouseholds: 9, acceptedArea: 4.3668, acceptedAmount: 462000, areaExecutionRate: '0.8919%', budgetExecutionRate: '0.8719%' },
  { unit: '苗栗管理處', executionArea: 90, executionBudget: 45450000, households: 571, area: 153.3909, subsidy: 65302600, remainingSubsidy: -19852600, acceptedHouseholds: 49, acceptedArea: 12.2276, acceptedAmount: 5836500, areaExecutionRate: '1.7043%', budgetExecutionRate: '1.4368%' },
  { unit: '臺中管理處', executionArea: 150, executionBudget: 86450000, households: 552, area: 308.3238, subsidy: 89234557, remainingSubsidy: -2784557, acceptedHouseholds: 158, acceptedArea: 80.9542, acceptedAmount: 23273031, areaExecutionRate: '2.0555%', budgetExecutionRate: '1.0322%' },
  { unit: '南投管理處', executionArea: 90, executionBudget: 33010000, households: 324, area: 125.7879, subsidy: 38124976, remainingSubsidy: -5114976, acceptedHouseholds: 151, acceptedArea: 54.7455, acceptedAmount: 14866146, areaExecutionRate: '1.3976%', budgetExecutionRate: '1.155%' },
  { unit: '彰化管理處', executionArea: 185, executionBudget: 24540000, households: 309, area: 261.3744, subsidy: 22384578, remainingSubsidy: 2155422, acceptedHouseholds: 117, acceptedArea: 199.0833, acceptedAmount: 10454585, areaExecutionRate: '1.4128%', budgetExecutionRate: '0.9122%' },
  { unit: '雲林管理處', executionArea: 260, executionBudget: 27540000, households: 307, area: 371.9595, subsidy: 27770116, remainingSubsidy: -230116, acceptedHouseholds: 0, acceptedArea: 0, acceptedAmount: 0, areaExecutionRate: '1.4306%', budgetExecutionRate: '1.0084%' },
  { unit: '嘉南管理處', executionArea: 350, executionBudget: 41820000, households: 619, area: 349.7016, subsidy: 42364761, remainingSubsidy: -544761, acceptedHouseholds: 151, acceptedArea: 118.8712, acceptedAmount: 10917018, areaExecutionRate: '0.9991%', budgetExecutionRate: '1.013%' },
  { unit: '高雄管理處', executionArea: 50, executionBudget: 12160000, households: 109, area: 137.28, subsidy: 9722233, remainingSubsidy: 2437767, acceptedHouseholds: 52, acceptedArea: 54.79, acceptedAmount: 4207046, areaExecutionRate: '2.7456%', budgetExecutionRate: '0.7995%' },
  { unit: '屏東管理處', executionArea: 230, executionBudget: 25000000, households: 314, area: 248.019, subsidy: 23619680, remainingSubsidy: 1380320, acceptedHouseholds: 187, acceptedArea: 152.7799, acceptedAmount: 15110436, areaExecutionRate: '1.0783%', budgetExecutionRate: '0.9448%' },
  { unit: '臺東管理處', executionArea: 125, executionBudget: 26000000, households: 202, area: 176.9975, subsidy: 25442217, remainingSubsidy: 557783, acceptedHouseholds: 107, acceptedArea: 104.4135, acceptedAmount: 16261980, areaExecutionRate: '1.416%', budgetExecutionRate: '0.9785%' },
  { unit: '花蓮管理處', executionArea: 70, executionBudget: 6820000, households: 57, area: 71.0195, subsidy: 6616183, remainingSubsidy: 203817, acceptedHouseholds: 21, acceptedArea: 25.3541, acceptedAmount: 1841446, areaExecutionRate: '1.0146%', budgetExecutionRate: '0.9701%' },
  { unit: '七星管理處', executionArea: 3, executionBudget: 0, households: 16, area: 5.5837, subsidy: 1892927, remainingSubsidy: -1892927, acceptedHouseholds: 7, acceptedArea: 2.318, acceptedAmount: 948317, areaExecutionRate: '1.8612%', budgetExecutionRate: '0%' },
  { unit: '瑠公管理處', executionArea: 3, executionBudget: 0, households: 30, area: 9.6373, subsidy: 3550749, remainingSubsidy: -3550749, acceptedHouseholds: 10, acceptedArea: 3.5067, acceptedAmount: 1341724, areaExecutionRate: '3.2124%', budgetExecutionRate: '0%' },
  { unit: '農工中心', executionArea: 0, executionBudget: 0, households: 0, area: 0, subsidy: 0, remainingSubsidy: 0, acceptedHouseholds: 0, acceptedArea: 0, acceptedAmount: 0, areaExecutionRate: '0%', budgetExecutionRate: '0%' },
  { unit: '高雄市政府農業局', executionArea: 35, executionBudget: 2730000, households: 17, area: 10.6758, subsidy: 1078120, remainingSubsidy: 1651880, acceptedHouseholds: 0, acceptedArea: 0, acceptedAmount: 0, areaExecutionRate: '0.305%', budgetExecutionRate: '0.3949%' }
]);

// Computed totals
const totalExecutionArea = computed(() => budgetItems.value.reduce((sum, item) => sum + item.executionArea, 0));
const totalExecutionBudget = computed(() => budgetItems.value.reduce((sum, item) => sum + item.executionBudget, 0));
const totalHouseholds = computed(() => budgetItems.value.reduce((sum, item) => sum + item.households, 0));
const totalArea = computed(() => budgetItems.value.reduce((sum, item) => sum + item.area, 0));
const totalSubsidy = computed(() => budgetItems.value.reduce((sum, item) => sum + item.subsidy, 0));
const totalRemainingSubsidy = computed(() => budgetItems.value.reduce((sum, item) => sum + item.remainingSubsidy, 0));
const totalAcceptedHouseholds = computed(() => budgetItems.value.reduce((sum, item) => sum + item.acceptedHouseholds, 0));
const totalAcceptedArea = computed(() => budgetItems.value.reduce((sum, item) => sum + item.acceptedArea, 0));
const totalAcceptedAmount = computed(() => budgetItems.value.reduce((sum, item) => sum + item.acceptedAmount, 0));

// 面積執行率和經費執行率的計算
const totalAreaExecutionRate = computed(() => {
  const rate = totalAcceptedArea.value / totalExecutionArea.value * 100;
  return rate.toFixed(4) + '%';
});

const totalBudgetExecutionRate = computed(() => {
  const rate = totalAcceptedAmount.value / totalExecutionBudget.value * 100;
  return rate.toFixed(4) + '%';
});

// 格式化數字
const formatNumber = (value: number, decimals: number = 0) => {
  if (value === 0) return '0';
  if (!value) return '';
  return decimals > 0
    ? value.toLocaleString('zh-TW', { minimumFractionDigits: decimals, maximumFractionDigits: decimals })
    : value.toLocaleString('zh-TW');
};

// 格式化貨幣
const formatCurrency = (value: number) => {
  if (value === 0) return '0';
  if (!value) return '';
  return value.toLocaleString('zh-TW');
};

// 設置單位欄格式
const getUnitCellClass = (index: number) => {
  // 最後一行特殊處理（合計行）
  if (index === budgetItems.value.length - 1) {
    return 'text-left font-weight-bold';
  }
  return 'text-left';
};

// 設置表頭樣式
const getHeaderClass = (column: any) => {
  return `text-center ${column.key === 'unit' ? 'text-left' : ''}`;
};

// 查詢預算資料
const fetchBudgetData = () => {
  isLoading.value = true;

  // 模擬 API 請求
  setTimeout(() => {
    // 這裡實際上應該是從 API 獲取數據
    console.log(`查詢 ${selectedYear.value} 年 ${selectedMonth.value} 月的預算執行資料`);

    // 完成載入
    isLoading.value = false;

    // 檢查表格是否需要水平滾動提示
    checkOverflow();
  }, 800);
};

// Detect horizontal overflow
const tableContainer = ref<HTMLElement | null>(null);
const isOverflowing = ref(false);

const checkOverflow = () => {
  if (tableContainer.value) {
    isOverflowing.value = tableContainer.value.scrollWidth > tableContainer.value.offsetWidth;
  }
};

onMounted(() => {
  // 從 localStorage 恢復用戶偏好
  const preferFluid = localStorage.getItem('preferFluid');
  if (preferFluid !== null) {
    isFluid.value = preferFluid === 'true';
  }

  // 初始化載入數據
  fetchBudgetData();

  // 添加監聽器檢查溢出
  checkOverflow();
  window.addEventListener('resize', checkOverflow);
});

// 監聽數據變化，更新溢出狀態
watch(budgetItems, () => {
  checkOverflow();
});
</script>

<style scoped>
/* 表頭樣式 */
.budget-table :deep(th) {
  white-space: nowrap;
  background-color: #f5f5f5;
  font-weight: 600;
  border-bottom: 1px solid rgba(0, 0, 0, 0.12);
  padding: 8px;
  height: auto !important;
}

/* 公式行樣式 */
.budget-table :deep(.formula-row th) {
  background-color: #e8f5e9;
  font-size: 0.8rem;
  font-weight: normal;
  padding: 4px 8px;
  text-align: center;
}

.budget-table :deep(.formula-row th:first-child) {
  text-align: left;
}

/* 表格行樣式 */
.budget-table :deep(tr:nth-child(even) td) {
  background-color: #f9f9f9;
}

.budget-table :deep(tr:hover td) {
  background-color: #f0f8ff !important;
}

/* 單元格樣式 */
.budget-table :deep(td) {
  padding: 6px 8px;
  white-space: nowrap;
  border-bottom: 1px solid rgba(0, 0, 0, 0.12);
}

/* 負值樣式 */
.budget-table :deep(.negative-value) {
  color: #d32f2f;
}

/* 合計行樣式 */
.budget-table :deep(.total-row td) {
  background-color: #e3f2fd !important;
  font-weight: 500;
  border-top: 2px solid rgba(0, 0, 0, 0.2);
  border-bottom: none;
}

/* 表格容器樣式 */
.table-container {
  position: relative;
  overflow-x: auto;
  box-shadow: none;
  border: 1px solid rgba(0, 0, 0, 0.12);
  border-radius: 4px;
}

.scroll-hint {
  position: absolute;
  bottom: 8px;
  right: 8px;
  background-color: rgba(255, 255, 255, 0.9);
  padding: 4px 8px;
  font-size: 0.75rem;
  color: rgba(0, 0, 0, 0.6);
  border-radius: 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  z-index: 1;
}

/* 卡片標題樣式 */
.bg-light-blue-lighten-4 {
  background-color: #B3E5FC !important; /* 使用與補助申請頁面一致的顏色 */
}

.font-weight-medium {
  font-weight: 500 !important;
}

/* 查詢區域樣式 */
.v-card-text {
  padding: 12px !important;
}
</style>
