<template>
  <v-container :fluid="isFluid" class="pt-0">
    <v-card class="pa-0 mb-6">
      <v-card-title class="d-flex align-center">
        <v-icon icon="mdi-currency-usd" class="pe-2" />
        本年度預算執行即時資訊
        <v-btn
          icon
          variant="text"
          @click="toggleFluid"
          :title="isFluid ? '切換為固定寬度' : '切換為全寬模式'"
        >
          <v-icon>{{ isFluid ? 'mdi-arrow-collapse-horizontal' : 'mdi-arrow-expand-horizontal' }}</v-icon>
        </v-btn>
      </v-card-title>
      <v-divider />

      <!-- Budget Data Table -->
      <div class="table-container" ref="tableContainer">
        <v-data-table-server
          :headers="headers"
          :items="items"
          :items-length="items.length"
          fixed-header
          fixed-footer
          class="elevation-1"
          density="compact"
          hide-default-footer
        >
          <!-- Custom footer for totals -->
          <template #body.append>
            <tr>
              <td class="text-end font-weight-bold">合計</td>
              <td class="text-end">{{ totalExecutionArea }}</td>
              <td class="text-end">{{ totalExecutionBudget }}</td>
              <td class="text-end">{{ totalHouseholds }}</td>
              <td class="text-end">{{ totalArea }}</td>
              <td class="text-end">{{ totalSubsidy }}</td>
              <td class="text-end">{{ totalRemainingSubsidy }}</td>
              <td class="text-end">{{ totalAcceptedHouseholds }}</td>
              <td class="text-end">{{ totalAcceptedArea }}</td>
              <td class="text-end">{{ totalAcceptedAmount }}</td>
              <td class="text-end">{{ totalAreaExecutionRate }}</td>
              <td class="text-end">{{ totalBudgetExecutionRate }}</td>
            </tr>
          </template>
        </v-data-table-server>
        <div v-if="isOverflowing" class="scroll-hint">
          滑動下方捲軸以查看完整表格內容
        </div>
      </div>
    </v-card>
  </v-container>
</template>

<script lang="ts" setup>
const isFluid = ref(false)

// 切換 fluid 狀態的方法
const toggleFluid = () => {
  isFluid.value = !isFluid.value
  // 可選：保存用戶偏好到 localStorage
  localStorage.setItem('preferFluid', String(isFluid.value))
}

// Table headers
const headers = [
  { title: '受理單位', key: 'unit', align: 'start' as const, width: '110', fixed: true },
  { title: '預定執行面積 (公頃) [a]', key: 'executionArea', align: 'end' as const, width: '90' },
  { title: '預定執行預算 (元) [b]', key: 'executionBudget', align: 'end' as const },
  { title: '已編預算戶數 [c]', key: 'households', align: 'end' as const },
  { title: '已編預算面積 (公頃) [d]', key: 'area', align: 'end' as const },
  { title: '已編列補助款 (元) [e]', key: 'subsidy', align: 'end' as const },
  { title: '未編列補助款 (元) [f]', key: 'remainingSubsidy', align: 'end' as const },
  { title: '已驗收戶數 [g]', key: 'acceptedHouseholds', align: 'end' as const },
  { title: '已驗收面積 (公頃) [h]', key: 'acceptedArea', align: 'end' as const },
  { title: '已驗收金額 (元) [i]', key: 'acceptedAmount', align: 'end' as const },
  { title: '面積執行率 (%) [j=d/a]', key: 'areaExecutionRate', align: 'end' as const },
  { title: '經費執行率 (%) [k=e/b]', key: 'budgetExecutionRate', align: 'end' as const },
]

// Sample data
const items = [
  { unit: '宜蘭管理處', executionArea: 10, executionBudget: 2680000, households: 0, area: 0, subsidy: 2161320, remainingSubsidy: 518680, acceptedHouseholds: 0, acceptedArea: 4.3867, acceptedAmount: 965991, areaExecutionRate: '115.35%', budgetExecutionRate: '80.65%' },
  { unit: '北基管理處', executionArea: 5, executionBudget: 550000, households: 0, area: 0, subsidy: 1009602, remainingSubsidy: -459902, acceptedHouseholds: 0, acceptedArea: 0.6127, acceptedAmount: 159000, areaExecutionRate: '1.7361%', budgetExecutionRate: '1.7892%' },
  { unit: '桃園管理處', executionArea: 10, executionBudget: 3450000, households: 0, area: 0, subsidy: 6172848, remainingSubsidy: -2722848, acceptedHouseholds: 0, acceptedArea: 5.5495, acceptedAmount: 1806603, areaExecutionRate: '17.3613%', budgetExecutionRate: '1.7892%' },
  { unit: '石門管理處', executionArea: 20, executionBudget: 2270000, households: 0, area: 0, subsidy: 3630667, remainingSubsidy: -900667, acceptedHouseholds: 0, acceptedArea: 9.2582, acceptedAmount: 0, areaExecutionRate: '0.6172%', budgetExecutionRate: '1.3299%' },
  { unit: '新竹管理處', executionArea: 20, executionBudget: 2270000, households: 0, area: 0, subsidy: 1979291, remainingSubsidy: 290709, acceptedHouseholds: 0, acceptedArea: 4.3668, acceptedAmount: 462000, areaExecutionRate: '0.8919%', budgetExecutionRate: '0.8719%' },
  // Add more rows as needed
]

// Computed totals
const totalExecutionArea = computed(() => items.reduce((sum, item) => sum + item.executionArea, 0))
const totalExecutionBudget = computed(() => items.reduce((sum, item) => sum + item.executionBudget, 0))
const totalHouseholds = computed(() => items.reduce((sum, item) => sum + item.households, 0))
const totalArea = computed(() => items.reduce((sum, item) => sum + item.area, 0))
const totalSubsidy = computed(() => items.reduce((sum, item) => sum + item.subsidy, 0))
const totalRemainingSubsidy = computed(() => items.reduce((sum, item) => sum + item.remainingSubsidy, 0))
const totalAcceptedHouseholds = computed(() => items.reduce((sum, item) => sum + item.acceptedHouseholds, 0))
const totalAcceptedArea = computed(() => items.reduce((sum, item) => sum + item.acceptedArea, 0))
const totalAcceptedAmount = computed(() => items.reduce((sum, item) => sum + item.acceptedAmount, 0))
const totalAreaExecutionRate = computed(() => `${(totalAcceptedArea.value / totalExecutionArea.value * 100).toFixed(2)}%`)
const totalBudgetExecutionRate = computed(() => `${(totalAcceptedAmount.value / totalExecutionBudget.value * 100).toFixed(2)}%`)

// Detect horizontal overflow
const tableContainer = ref<HTMLElement | null>(null)
const isOverflowing = ref(false)

const checkOverflow = () => {
  if (tableContainer.value) {
    console.log('Checking overflow:', tableContainer.value.scrollWidth, tableContainer.value.offsetWidth)
    isOverflowing.value = tableContainer.value.scrollWidth > tableContainer.value.offsetWidth
  }
}

onMounted(() => {
  checkOverflow()
  window.addEventListener('resize', checkOverflow)
})

watch(items, () => {
  checkOverflow()
})
</script>

<style scoped>
/* Prevent word-wrap in headers */
.v-data-table th {
  white-space: nowrap;
  text-align: center;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Optional: Add horizontal scrolling for large tables */
.v-data-table {
  overflow-x: auto;
}

.table-container {
  position: relative;
  overflow-x: auto;
}

.scroll-hint {
  position: absolute;
  bottom: 0;
  right: 0;
  background-color: rgba(255, 255, 255, 0.8);
  padding: 4px 8px;
  font-size: 0.875rem;
  color: var(--v-theme-on-surface);
  border-radius: 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  z-index: 1;
}
</style>
