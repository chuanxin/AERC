<template>
  <v-container
    fluid
    class="px-6 py-4 pb-0 dashboard-container"
    style="background-color: white"
  >
    <!-- 最新消息區塊 -->
    <v-row justify="center">
      <v-col
        cols="10"
        lg="10"
        align-self="center"
        class="pt-10"
      >
        <div class="section-wrapper">
          <v-card
            class="mx-auto section-card pa-4 pb-0"
            variant="outlined"
            rounded="lg"
          >
            <v-card-item
              class="custom-title"
              color="#3ea0a3"
            >
              <v-card-title class="text-h5 font-weight-black px-4">
                <v-img
                  src="@/assets/icons/news.svg"
                  alt="news icon"
                  width="24"
                  height="24"
                  class="me-2"
                />
                最新消息
              </v-card-title>
            </v-card-item>
            <v-card-text>
              <v-card
                class="table-card mb-4"

                elevation="0"
              >
                <v-table
                  class="news-table rounded-table pt-4 pb-0"
                  hover
                >
                  <thead class="table-header-bold">
                    <tr>
                      <th class="text-left px-2 text-center font-weight-black">
                        發布日期
                      </th>
                      <th class="text-left text-center font-weight-black">
                        類型
                      </th>
                      <th class="text-left text-center font-weight-black">
                        標題
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr
                      v-for="(item, index) in announcements"
                      :key="index"
                      class="news-row text-subtitle-1"
                      :style="index % 2 === 1 ? { backgroundColor: '#62b7bb30' } : {}"
                      @click="viewAnnouncementDetail(item)"
                    >
                      <td class="date-cell text-left py-3 px-3 text-grey text-subtitle-1 text-center">
                        <v-chip
                          color="#FFF8DE"
                          variant="elevated"
                          elevation="0"
                          rounded="lg"
                          class="date-chip"
                          density="comfortable"
                        >
                          {{ item.date }}
                        </v-chip>
                      </td>
                      <td class="type-cell text-center">
                        <v-chip
                          :color="getTypeColor(item.type)"
                          variant="outlined"
                          size="small"
                          label
                          class="font-weight-medium text-subtitle-1"
                        >
                          {{ item.type }}
                        </v-chip>
                      </td>
                      <td
                        class="content-cell px-2"
                      >
                        {{ item.content }}
                      </td>
                    </tr>
                  </tbody>
                </v-table>
              </v-card>

              <!-- 更多連結 -->
              <div class="d-flex justify-end pa-0 ma-0">
                <v-btn
                  class="more-btn"
                  variant="outlined"
                  rounded="lg"
                  color="#3ea0a3"
                  to="/announcements"
                  size="large"
                  append-icon="mdi-chevron-right-circle"
                >
                  更多
                </v-btn>
              </div>
            </v-card-text>
          </v-card>
        </div>
      </v-col>
    </v-row>

    <!-- 預算執行區塊 -->
    <v-row justify="center">
      <v-col
        cols="10"
        lg="10"
        align-self="center"
      >
        <div class="section-wrapper">
          <v-card
            class="mx-auto section-card pa-4 pb-0"
            variant="outlined"
            rounded="lg"
            color="#3ea0a3"
          >
            <v-card-item class="custom-title">
              <v-card-title class="text-h5 font-weight-black pr-4">
                <v-img
                  src="@/assets/icons/budget.svg"
                  alt="news icon"
                  width="24"
                  height="24"
                  class="mb-1"
                />
                預算
              </v-card-title>
            </v-card-item>
            <v-card-text>
              <!-- 管理處執行進度表格 -->
              <v-card
                class="table-card mb-6"
                rounded="lg"
                elevation="0"
              >
                <div class="pa-4">
                  <h3 class="text-h6 font-weight-bold mb-4" style="color: #3ea0a3;">
                    管理處執行進度
                  </h3>

                  <v-sheet
                    border
                    rounded="lg"
                  >
                    <v-data-table
                      :headers="executionHeaders"
                      :items="statisticsStore.executionProgress?.offices || []"
                      :loading="statisticsStore.isLoading"
                      loading-text="載入中..."
                      no-data-text="暫無資料"
                      class="statistics-table"
                      density="comfortable"
                      :items-per-page="-1"
                      hide-default-footer
                      hover
                      max-height="400"
                      fixed-header
                    >
                    <!-- 自訂欄位格式 - 直接顯示後端已計算的值，不進行前端計算 -->
                    <template #item.approved_budget="{ value }">
                      {{ formatCurrency(value) }}
                    </template>
                    <template #item.completed_cases="{ value }">
                      {{ formatCount(value) }}
                    </template>
                    <template #item.total_area="{ value }">
                      {{ formatArea(value) }}
                    </template>
                    <!-- total_subsidy: ✓ 後端已驗證包含三組件（A項田間管路+B項調控設施+設計費） -->
                    <template #item.total_subsidy="{ value }">
                      {{ formatCurrency(value) }}
                    </template>
                    <template #item.execution_rate="{ value }">
                      <v-chip
                        v-if="value > 0"
                        :color="value >= 80 ? 'success' : value >= 50 ? 'warning' : 'error'"
                        size="small"
                        label
                      >
                        {{ formatPercentage(value) }}
                      </v-chip>
                      <span v-else>-</span>
                    </template>

                    <!-- 總計列 -->
                    <template #bottom>
                      <div v-if="(statisticsStore.executionProgress?.offices || []).length > 1">
                        <v-divider />
                        <div class="d-flex align-center pa-4 bg-grey-lighten-4">
                          <div class="text-subtitle-1 font-weight-bold" style="min-width: 120px;">
                            總計
                          </div>
                          <v-spacer />
                          <div class="d-flex flex-wrap ga-6">
                            <div class="text-caption">
                              <span class="text-medium-emphasis">總核定預算：</span>
                              <span class="font-weight-bold">{{ formatCurrency(statisticsStore.executionProgress?.total_approved_budget || 0) }}{{ statisticsStore.executionProgress?.total_approved_budget ? ' 元' : '' }}</span>
                            </div>
                          <div class="text-caption">
                            <span class="text-medium-emphasis">總已結案案件：</span>
                            <span class="font-weight-bold">{{ formatCount(statisticsStore.executionProgress?.total_completed_cases || 0) }}{{ statisticsStore.executionProgress?.total_completed_cases ? ' 件' : '' }}</span>
                          </div>
                          <div class="text-caption">
                            <span class="text-medium-emphasis">總補助面積：</span>
                            <span class="font-weight-bold">{{ formatArea(statisticsStore.executionProgress?.total_area || 0) }}{{ statisticsStore.executionProgress?.total_area ? ' 公頃' : '' }}</span>
                          </div>
                          <div class="text-caption">
                            <span class="text-medium-emphasis">整體執行率：</span>
                            <v-chip
                              v-if="(statisticsStore.executionProgress?.overall_execution_rate || 0) > 0"
                              :color="(statisticsStore.executionProgress?.overall_execution_rate || 0) >= 80 ? 'success' : 'warning'"
                              size="x-small"
                              label
                            >
                              {{ formatPercentage(statisticsStore.executionProgress?.overall_execution_rate || 0) }}
                            </v-chip>
                            <span v-else>-</span>
                          </div>
                        </div>
                        </div>
                      </div>
                    </template>
                    </v-data-table>
                  </v-sheet>
                </div>
              </v-card>

              <!-- 管理處經費統計表格 -->
              <v-card
                class="table-card mb-4"
                rounded="lg"
                elevation="0"
              >
                <div class="pa-4">
                  <h3 class="text-h6 font-weight-bold mb-2" style="color: #3ea0a3;">
                    管理處經費統計表
                  </h3>
                  <div class="text-caption text-grey-darken-1 mb-3">
                    <!-- 💡 數據已按類別整合顯示，提升可讀性 -->
                  </div>

                  <v-sheet border rounded class="overflow-hidden">
                    <v-data-table
                      :headers="budgetHeaders"
                      :items="statisticsStore.budgetAnalysis?.offices || []"
                      :loading="statisticsStore.isLoading"
                      loading-text="載入中..."
                      no-data-text="暫無資料"
                      class="statistics-table"
                      density="compact"
                      :items-per-page="-1"
                      hide-default-footer
                      hover
                      :mobile-breakpoint="0"
                      max-height="450"
                      fixed-header
                    >
                    <!-- 自訂欄位格式 - 直接顯示後端已計算的值，不進行前端計算 -->
                    <template #item.planned_area="{ value }">
                      {{ value === 0 ? '-' : Math.round(value) }}
                    </template>
                    <template #item.planned_budget="{ value }">
                      {{ formatCurrency(value) }}
                    </template>
                    <template #item.budgeted_cases="{ value }">
                      {{ formatCount(value) }}
                    </template>
                    <template #item.budgeted_area="{ value }">
                      {{ formatArea(value) }}
                    </template>
                    <!-- budgeted_subsidy: ✓ 後端已驗證包含三組件（A項+B項+設計費，排除 rejected/withdrawn/deleted） -->
                    <template #item.budgeted_subsidy="{ value }">
                      {{ formatCurrency(value) }}
                    </template>
                    <!-- unbudgeted_subsidy: 後端已計算（planned_budget - budgeted_subsidy，允許負值顯示超支） -->
                    <template #item.unbudgeted_subsidy="{ value }">
                      {{ formatCurrency(value) }}
                    </template>
                    <template #item.verified_cases="{ value }">
                      {{ formatCount(value) }}
                    </template>
                    <template #item.verified_area="{ value }">
                      {{ formatArea(value) }}
                    </template>
                    <!-- verified_amount: ✓ 後端已驗證包含三組件（A項+B項+設計費，completed + submitted 狀態） -->
                    <template #item.verified_amount="{ value }">
                      {{ formatCurrency(value) }}
                    </template>
                    <template #item.area_execution_rate="{ value }">
                      <v-chip
                        v-if="value > 0"
                        :color="value >= 80 ? 'success' : value >= 50 ? 'warning' : 'error'"
                        size="small"
                        label
                      >
                        {{ formatPercentage(value) }}
                      </v-chip>
                      <span v-else>-</span>
                    </template>
                    <template #item.budget_execution_rate="{ value }">
                      <v-chip
                        v-if="value > 0"
                        :color="value >= 80 ? 'success' : value >= 50 ? 'warning' : 'error'"
                        size="small"
                        label
                      >
                        {{ formatPercentage(value) }}
                      </v-chip>
                      <span v-else>-</span>
                    </template>

                    <!-- 總計列 -->
                    <template #bottom>
                      <div v-if="(statisticsStore.budgetAnalysis?.offices || []).length > 1">
                        <v-divider />
                        <div class="d-flex align-center pa-4 bg-grey-lighten-4">
                          <div class="text-subtitle-1 font-weight-bold" style="min-width: 120px;">
                            總計
                          </div>
                          <v-spacer />
                          <div class="d-flex flex-wrap ga-6">
                            <div class="text-caption">
                              <span class="text-medium-emphasis">總預定執行預算：</span>
                              <span class="font-weight-bold">{{ formatCurrency(statisticsStore.budgetAnalysis?.total_planned_budget || 0) }}{{ statisticsStore.budgetAnalysis?.total_planned_budget ? ' 元' : '' }}</span>
                            </div>
                          <div class="text-caption">
                            <span class="text-medium-emphasis">總已編列補助款：</span>
                            <span class="font-weight-bold">{{ formatCurrency(statisticsStore.budgetAnalysis?.total_budgeted_subsidy || 0) }}{{ statisticsStore.budgetAnalysis?.total_budgeted_subsidy ? ' 元' : '' }}</span>
                          </div>
                          <div class="text-caption">
                            <span class="text-medium-emphasis">整體面積執行率：</span>
                            <v-chip
                              v-if="(statisticsStore.budgetAnalysis?.overall_area_execution_rate || 0) > 0"
                              :color="(statisticsStore.budgetAnalysis?.overall_area_execution_rate || 0) >= 80 ? 'success' : 'warning'"
                              size="x-small"
                              label
                            >
                              {{ formatPercentage(statisticsStore.budgetAnalysis?.overall_area_execution_rate || 0) }}
                            </v-chip>
                            <span v-else>-</span>
                          </div>
                          <div class="text-caption">
                            <span class="text-medium-emphasis">整體計畫執行率：</span>
                            <v-chip
                              v-if="(statisticsStore.budgetAnalysis?.overall_budget_execution_rate || 0) > 0"
                              :color="(statisticsStore.budgetAnalysis?.overall_budget_execution_rate || 0) >= 80 ? 'success' : 'warning'"
                              size="x-small"
                              label
                            >
                              {{ formatPercentage(statisticsStore.budgetAnalysis?.overall_budget_execution_rate || 0) }}
                            </v-chip>
                            <span v-else>-</span>
                          </div>
                        </div>
                        </div>
                      </div>
                    </template>
                    </v-data-table>
                  </v-sheet>
                </div>
              </v-card>
            </v-card-text>
          </v-card>
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { useStatisticsStore } from '@/stores/statistics'

// Joya added
import { announcementsData } from '@/data/announcement'
const router = useRouter()
const statisticsStore = useStatisticsStore()
const announcements = ref(announcementsData);
// 當前年度（民國年）
const currentYear = new Date().getFullYear() - 1911


// 根據公告類型返回對應的顏色
const getTypeColor = (type: string) => {
  switch (type) {
    case '系統公告':
      return 'blue'
    case '停機公告':
      return 'deep-orange'
    default:
      return 'grey'
  }
}

// 查看公告詳細內容
/*const viewAnnouncementDetail = (item: any) => {
  console.log('查看公告詳情:', item)
}*/

// Joya added
// 查看公告詳細內容 
const viewAnnouncementDetail = (item: { id: number; date: string; type: string; content: string }) => {
  // 導航到公告詳細頁面，將公告的 ID 作為路由參數傳遞
  router.push({ path: `/announcements/${item.id}` }); // 使用具名路由 '/announcements/[id]'
  // 或者使用路徑:
  // router.push(`/announcements/${item.id}`);
};

// 格式化金額（加上千分位，0 顯示為 -）
const formatCurrency = (value: number) => {
  if (value === 0) return '-'
  return new Intl.NumberFormat('zh-TW').format(value)
}

// 格式化百分比（0 顯示為 -）
const formatPercentage = (value: number) => {
  if (value === 0) return '-'
  return `${value.toFixed(2)}%`
}

// 格式化面積（0 顯示為 -）
const formatArea = (value: number) => {
  if (value === 0) return '-'
  return value.toFixed(4)
}

// 格式化數量（0 顯示為 -）
const formatCount = (value: number) => {
  if (value === 0) return '-'
  return value.toString()
}

// 執行進度表格欄位定義
const executionHeaders = [
  { title: '管理處', key: 'office_name', align: 'center' as const },
  { title: '核定金額(元)', key: 'approved_budget', align: 'end' as const },
  { title: '補助案件數(已結案)', key: 'completed_cases', align: 'center' as const },
  { title: '補助面積(公頃)', key: 'total_area', align: 'end' as const },
  { title: '補助總額(元)', key: 'total_subsidy', align: 'end' as const },
  { title: '補助款執行率%', key: 'execution_rate', align: 'end' as const }
]

// 經費統計表格欄位定義（分開版 - 客戶偏好）
const budgetHeaders = [
  { title: '管理處', key: 'office_name', align: 'center' as const, sortable: true },
  { title: '預定執行面積(公頃)', key: 'planned_area', align: 'center' as const, sortable: true },
  { title: '預定執行預算(元)', key: 'planned_budget', align: 'center' as const, sortable: true },
  { title: '已編預算案件數', key: 'budgeted_cases', align: 'center' as const, sortable: true },
  { title: '已編預算面積(公頃)', key: 'budgeted_area', align: 'center' as const, sortable: true },
  { title: '已編列補助款(元)', key: 'budgeted_subsidy', align: 'center' as const, sortable: true },
  { title: '未編列補助款(元)', key: 'unbudgeted_subsidy', align: 'center' as const, sortable: true },
  { title: '已驗收案件數', key: 'verified_cases', align: 'center' as const, sortable: true },
  { title: '已驗收面積(公頃)', key: 'verified_area', align: 'center' as const, sortable: true },
  { title: '已驗收金額(元)', key: 'verified_amount', align: 'center' as const, sortable: true },
  { title: '面積執行率%', key: 'area_execution_rate', align: 'center' as const, sortable: true },
  { title: '預算執行率%', key: 'budget_execution_rate', align: 'center' as const, sortable: true }
]

/* ========== 整合版本（備用，供未來參考） ==========
 * 設計思路：將相關數據合併到單一欄位，節省橫向空間
 * 從 12 欄優化為 7 欄，合併規則：
 *   - 預定執行 = 預定面積 + 預定預算
 *   - 已編列 = 編預案件 + 編預面積 + 編列補助
 *   - 已驗收 = 驗收件數 + 驗收面積 + 驗收金額
 *
 * const budgetHeadersMerged = [
 *   { title: '管理處', key: 'office_name', align: 'center' as const, sortable: true, width: '110px' },
 *   { title: '預定執行', key: 'planned', align: 'center' as const, sortable: false, width: '140px', cellProps: { class: 'text-left' } },
 *   { title: '已編列', key: 'budgeted', align: 'center' as const, sortable: false, width: '160px', cellProps: { class: 'text-left' } },
 *   { title: '未編列補助款', key: 'unbudgeted_subsidy', align: 'center' as const, sortable: true, width: '120px', cellProps: { class: 'text-right' } },
 *   { title: '已驗收', key: 'verified', align: 'center' as const, sortable: false, width: '160px', cellProps: { class: 'text-left' } },
 *   { title: '面積執行率', key: 'area_execution_rate', align: 'center' as const, sortable: true, width: '100px' },
 *   { title: '預算執行率', key: 'budget_execution_rate', align: 'center' as const, sortable: true, width: '100px' }
 * ]
 *
 * 對應的 template（需搭配使用）：
 *   <template #item.planned="{ item }">
 *     <div class="merged-cell">
 *       <div class="cell-line">面積 {{ Math.round(item.planned_area) }} 公頃</div>
 *       <div class="cell-line">預算 {{ formatCurrency(item.planned_budget) }} 元</div>
 *     </div>
 *   </template>
 *   <template #item.budgeted="{ item }">
 *     <div class="merged-cell">
 *       <div class="cell-line">案件 {{ item.budgeted_cases }} 件</div>
 *       <div class="cell-line">面積 {{ item.budgeted_area.toFixed(4) }} 公頃</div>
 *       <div class="cell-line">補助 {{ formatCurrency(item.budgeted_subsidy) }} 元</div>
 *     </div>
 *   </template>
 *   <template #item.verified="{ item }">
 *     <div class="merged-cell">
 *       <div class="cell-line">案件 {{ item.verified_cases }} 件</div>
 *       <div class="cell-line">面積 {{ item.verified_area.toFixed(4) }} 公頃</div>
 *       <div class="cell-line">金額 {{ formatCurrency(item.verified_amount) }} 元</div>
 *     </div>
 *   </template>
 * ========== 整合版本結束 ========== */

onMounted(async () => {
  // 載入統計資料
  await statisticsStore.fetchAllStatistics(currentYear)
})
</script>

<style scoped>
/* 添加背景圖片樣式 */
.dashboard-container {
  background-image: url('@/assets/bg_index.svg');
  background-size: cover;
  background-position: center bottom;
  background-repeat: no-repeat;
  background-attachment: fixed;
  min-height: 100vh;
}

/* 區塊共通容器 */
.section-wrapper {
  padding: 8px 4px 0px 4px;
}

/* 卡片與標題樣式 */
.section-card {
  position: relative;
  margin: 24px 0;
  overflow: visible !important;
  border-top-left-radius: 0 !important;
  transition: all 0.3s ease;

  /* 毛玻璃效果 */
  background-color: rgba(255, 255, 255, 0.6) !important; /* 半透明白色背景 */
  backdrop-filter: blur(10px) !important; /* 背景模糊效果 */
  -webkit-backdrop-filter: blur(10px) !important; /* Safari 支持 */
  border: 1px solid rgba(255, 255, 255, 0.25) !important; /* 細微邊框增強玻璃感 */
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.05) !important; /* 柔和陰影增強玻璃感 */
}

.section-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08) !important;
  background-color: rgba(255, 255, 255, 0.85) !important; /* 懸停時略微增加不透明度 */
}

.section-card:hover .custom-title {
  background-color: #2d8c8f !important;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.08);
}

.custom-title {
  position: absolute;
  top: -50px;
  left: -1px;
  width: auto !important;
  min-width: 130px;
  height: 50px;
  padding: 0 0px !important;
  background-color: #3ea0a3 !important;
  border-radius: 8px 8px 0 0;
  z-index: 1;
  transition: all 0.3s ease;
}

.custom-title:not(.full-width-title) .v-card-title {
  justify-content: center;
}

.v-card-title {
  color: white !important;
  display: flex;
  justify-content: flex-start;
  align-items: center;
  width: 100%;
  height: 100%;
  padding-left: 0px;
}

/* 表格樣式 */
/* .news-table, .files-table { */
  /* border-collapse: separate; */
  /* border-spacing: 0; */
/* } */

.table-card, .rounded-table {
  border-radius: 6px;
  overflow: hidden;
}

/* 表頭樣式 */
.table-header-bold th {
  font-weight: 900 !important;
  background-color: #62b7bb30 !important;
  padding-top: 8px !important;
  padding-bottom: 8px !important;
  line-height: 2 !important;
  height: 40px !important;
}

/* 表格單元格樣式 */
.news-row td, .file-row td {
  padding-top: 8px;
  padding-bottom: 8px;
}

.news-table thead tr th {
  font-size: 1.1rem !important;
}

.news-row, .file-row {
  cursor: pointer;
  transition: background-color 0.2s;
}

.news-table tbody tr:hover {
  background-color: rgba(98, 183, 187, 0.2) !important;
}

/* 日期chip專用樣式 */
.date-chip {
  font-weight: 500 !important;
  color: #6b5e2e !important;
  min-width: 85px;
  justify-content: center;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.08) !important;
  /* border: 1px solid rgba(232, 218, 157, 0.5) !important; */
}

/* 日期單元格樣式 */
.date-cell {
  width: 200px;
  white-space: nowrap;
  background-color: transparent !important;
  padding: 8px 12px !important;
  position: relative;
  z-index: 1;
}

.type-cell {
  width: 200px;
  padding-right: 10px;
}

.content-cell, .name-cell {
  font-weight: 500;
}

/* 按鈕樣式 */
.more-btn {
  font-weight: 500;
  /* margin: 8px 0 12px 0; */
  transition: all 0.2s ease;
}

.more-btn:hover {
  background-color: #3ea0a3 !important;
  color: white !important;
}

/* 預算區塊樣式 */
.budget-data-group {
  min-width: 120px;
}

.budget-panels {
  border: 1px solid rgba(62, 160, 163, 0.15);
  border-radius: 8px;
}

.budget-panel :deep(.v-expansion-panel-title) {
  min-height: 48px;
}

.budget-panel :deep(.v-expansion-panel-title:hover) {
  background-color: rgba(62, 160, 163, 0.05);
}

.budget-table {
  margin-top: 8px;
}

.budget-table th {
  color: #3ea0a3;
  font-weight: 700;
  background-color: rgba(62, 160, 163, 0.08);
}

/* 表格區域樣式 - 添加圓角 */
/* .table-card {
  border-radius: 12px;
  overflow: hidden;
} */

/* 統計表格樣式 - 與申請案件列表保持一致 */
/* .statistics-table {
  border-radius: 12px;
  overflow: hidden;
}

.statistics-table :deep(.v-table__wrapper) {
  border-radius: 12px;
  overflow: hidden;
}*/

.statistics-table :deep(thead th) {
  background-color: #e3f4f4 !important;
  color: #333 !important;
  font-weight: 900 !important;
}

/* ========== 整合版本 CSS（備用，供未來參考） ==========
 * 用於顯示多行數據的合併單元格
 *
 * .merged-cell {
 *   display: flex;
 *   flex-direction: column;
 *   gap: 4px;
 *   padding: 4px 0;
 * }
 *
 * .merged-cell .cell-line {
 *   font-size: 0.8rem;
 *   line-height: 1.4;
 *   color: #333;
 * }
 *
 * .merged-cell .cell-line:not(:last-child) {
 *   border-bottom: 1px solid #e0e0e0;
 *   padding-bottom: 4px;
 * }
 * ========== 整合版本 CSS 結束 ========== */

/* .statistics-table :deep(thead th:first-child) {
  border-top-left-radius: 12px;
}

.statistics-table :deep(thead th:last-child) {
  border-top-right-radius: 12px;
} */

.statistics-table :deep(tbody td) {
  padding: 12px 16px !important;
}

.statistics-table :deep(.v-data-table__tr:hover) {
  background-color: rgba(98, 183, 187, 0.1) !important;
}

.statistics-table :deep(.v-data-table__tr:nth-child(even)) {
  background-color: rgba(98, 183, 187, 0.05);
}

/* 輔助樣式 */
.position-relative {
  position: relative;
}

.position-absolute {
  position: absolute;
}
</style>
