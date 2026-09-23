<template>
  <v-container
    fluid
    class="px-6 py-4 pb-0 dashboard-container"
    :class="{ 'dashboard-container--full-height': canViewReports }"
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
                    <tr v-if="announcementsLoading">
                      <td colspan="3" class="text-center py-8">
                        <v-progress-circular indeterminate color="#3ea0a3" size="32" />
                      </td>
                    </tr>
                    <tr v-else-if="announcementsError">
                      <td colspan="3" class="text-center py-8 text-error">
                        {{ announcementsError }}
                      </td>
                    </tr>
                    <tr v-else-if="announcements.length === 0">
                      <td colspan="3" class="text-center py-8 text-grey text-subtitle-1">
                        目前沒有最新消息
                      </td>
                    </tr>
                    <tr
                      v-for="(item, index) in announcements"
                      v-else
                      :key="item.id"
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
                          {{ toRocDate(item.publish_date) }}
                        </v-chip>
                      </td>
                      <td class="type-cell text-center">
                        <v-chip
                          :color="item.type.color"
                          variant="outlined"
                          size="small"
                          label
                          class="font-weight-medium text-subtitle-1"
                        >
                          {{ item.type.name }}
                        </v-chip>
                      </td>
                      <td
                        class="content-cell px-2"
                      >
                        {{ item.title }}
                      </td>
                    </tr>
                  </tbody>
                </v-table>
              </v-card>

              <!-- 更多連結 -->
              <div class="d-flex justify-end pa-0 ma-0">
                <!--
                  FR-020：首頁不得存在任何指向不存在頁面的操作入口，此條在
                  **每一個上線階段**皆須成立。公告列表頁（US5）完成後將
                  ANNOUNCEMENT_LIST_READY 改為 true 即可顯示。
                -->
                <v-btn
                  v-if="ANNOUNCEMENT_LIST_READY"
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
    <v-row
      v-if="canViewReports"
      justify="center"
    >
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
                      :items="budgetRowGroups"
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
                      <!-- 以 #item slot 覆寫整列渲染：每個管理處一組，組內來源行 + 小計行各自
                           成一個 <tr>，「管理處」儲存格用 rowspan 跨越整組（客戶設計稿樣式）。
                           組 A 五欄（核定執行面積/預算、未編列補助款、兩個執行率）無來源維度，
                           只在小計行有值，來源行留空——留空而非顯示 0/-，避免誤導成「該來源為零」。 -->
                      <template #item="{ item }">
                        <tr
                          v-for="(line, idx) in item.lines"
                          :key="`${item.office.office_id}-${line.key}`"
                          :class="[
                            `budget-line--${line.variant}`,
                            idx === item.lines.length - 1 ? 'budget-line--group-end' : ''
                          ]"
                        >
                          <td
                            v-if="idx === 0"
                            :rowspan="item.lines.length"
                            class="text-center budget-office-cell"
                          >
                            {{ item.office.office_name }}
                          </td>
                          <td class="text-center budget-source-cell">{{ line.label }}</td>
                          <td class="text-end">
                            {{ line.planned_area === undefined ? '' : (line.planned_area === 0 ? '-' : Math.round(line.planned_area)) }}
                          </td>
                          <td class="text-end">
                            {{ line.planned_budget === undefined ? '' : formatCurrency(line.planned_budget) }}
                          </td>
                          <td class="text-end">{{ formatCount(line.budgeted_cases) }}</td>
                          <td class="text-end">{{ formatArea(line.budgeted_area) }}</td>
                          <td class="text-end">{{ formatCurrency(line.budgeted_subsidy) }}</td>
                          <td class="text-end" :class="{ 'text-error': (line.unbudgeted_subsidy ?? 0) < 0 }">
                            {{ line.unbudgeted_subsidy === undefined ? '' : formatCurrency(line.unbudgeted_subsidy) }}
                          </td>
                          <td class="text-end">{{ formatCount(line.verified_cases) }}</td>
                          <td class="text-end">{{ formatArea(line.verified_area) }}</td>
                          <td class="text-end">{{ formatCurrency(line.verified_amount) }}</td>
                          <td class="text-center">
                            <template v-if="line.area_execution_rate !== undefined">
                              <v-chip
                                v-if="line.area_execution_rate > 0"
                                :color="line.area_execution_rate >= 80 ? 'success' : line.area_execution_rate >= 50 ? 'warning' : 'error'"
                                size="small"
                                label
                              >
                                {{ formatPercentage(line.area_execution_rate) }}
                              </v-chip>
                              <span v-else>-</span>
                            </template>
                          </td>
                          <td class="text-center">
                            <template v-if="line.budget_execution_rate !== undefined">
                              <v-chip
                                v-if="line.budget_execution_rate > 0"
                                :color="line.budget_execution_rate >= 80 ? 'success' : line.budget_execution_rate >= 50 ? 'warning' : 'error'"
                                size="small"
                                label
                              >
                                {{ formatPercentage(line.budget_execution_rate) }}
                              </v-chip>
                              <span v-else>-</span>
                            </template>
                          </td>
                        </tr>
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
import { announcementsService } from '@/services/announcementsService'
import { useStatisticsStore } from '@/stores/statistics'
import { useUserStore } from '@/stores/users'
import type { AnnouncementListItem } from '@/types/announcements'
import type { OfficeBudgetStats } from '@/services/statisticsService'
import { toRocDate } from '@/utils/rocDate'

const router = useRouter()
const statisticsStore = useStatisticsStore()
const userStore = useUserStore()

const canViewReports = computed(() => userStore.can('reports', 'view'))

// 當前年度（民國年）
const currentYear = new Date().getFullYear() - 1911

// ── 最新消息（040：改由 API 供應，不再寫死於程式碼）────────────────────
//
// 原本此處有三則硬編碼公告、一個 getTypeColor() 的 switch、以及一個只做
// console.log 的 viewAnnouncementDetail()。三者皆已移除：
//   - 公告資料改由後端統一管理（SC-013：同一則公告的資料來源數量為 1）
//   - 類型顏色改用後端回傳的類型資料，新增類型不再需要改程式
//   - 點擊改為真正導向明細頁

/** 公告列表頁（US5）已建立，「更多」按鈕導向 /announcements。
 *  保留此旗標是為了讓 FR-020「每一個上線階段皆不得有失效入口」這條規則
 *  在文件與程式碼之間有一個對得上的落點——若日後列表頁被移除，改回 false
 *  即可，不需要再去範本裡找那顆按鈕。 */
const ANNOUNCEMENT_LIST_READY = true

/** 首頁顯示的公告則數 */
const ANNOUNCEMENT_LIMIT = 5

const announcements = ref<AnnouncementListItem[]>([])
const announcementsLoading = ref(true)
const announcementsError = ref('')

async function loadAnnouncements () {
  announcementsLoading.value = true
  announcementsError.value = ''
  try {
    const res = await announcementsService.fetchLatest(ANNOUNCEMENT_LIMIT)
    announcements.value = res.items
  } catch {
    announcementsError.value = '無法載入最新消息，請稍後再試'
  } finally {
    announcementsLoading.value = false
  }
}

/** 查看公告詳細內容 */
const viewAnnouncementDetail = (item: AnnouncementListItem) => {
  router.push(`/announcements/${item.id}`)
}

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
// sortable 全數關閉：表格是「管理處 → 來源子列 → 小計」的階層結構，
// 任何欄位排序都會把子列與所屬小計打散，使表格失去意義
const budgetHeaders = [
  { title: '管理處', key: 'office_name', align: 'center' as const, sortable: false },
  { title: '預算來源', key: 'label', align: 'center' as const, sortable: false },
  { title: '預定執行面積(公頃)', key: 'planned_area', align: 'center' as const, sortable: false },
  { title: '預定執行預算(元)', key: 'planned_budget', align: 'center' as const, sortable: false },
  { title: '已編預算案件數', key: 'budgeted_cases', align: 'center' as const, sortable: false },
  { title: '已編預算面積(公頃)', key: 'budgeted_area', align: 'center' as const, sortable: false },
  { title: '已編列補助款(元)', key: 'budgeted_subsidy', align: 'center' as const, sortable: false },
  { title: '未編列補助款(元)', key: 'unbudgeted_subsidy', align: 'center' as const, sortable: false },
  { title: '已驗收案件數', key: 'verified_cases', align: 'center' as const, sortable: false },
  { title: '已驗收面積(公頃)', key: 'verified_area', align: 'center' as const, sortable: false },
  { title: '已驗收金額(元)', key: 'verified_amount', align: 'center' as const, sortable: false },
  { title: '面積執行率%', key: 'area_execution_rate', align: 'center' as const, sortable: false },
  { title: '預算執行率%', key: 'budget_execution_rate', align: 'center' as const, sortable: false }
]

/** 來源在視覺上的區辨鍵（決定文字顏色，不只靠文字分辨） */
const SOURCE_VARIANTS: Record<string, string> = {
  農水署: 'ia',
  作業基金: 'advance',
  其他: 'other'
}

/** 管理處列內的一行（來源行或小計行）；組 A 五欄只有小計行有值 */
interface BudgetLine {
  key: string
  label: string
  variant: string
  budgeted_cases: number
  budgeted_area: number
  budgeted_subsidy: number
  verified_cases: number
  verified_area: number
  verified_amount: number
  planned_area?: number
  planned_budget?: number
  unbudgeted_subsidy?: number
  area_execution_rate?: number
  budget_execution_rate?: number
}

/**
 * 把單一管理處展開成該列內「垂直分格」的行
 *
 * 一個管理處維持一個 table row，來源與小計在列內堆疊；每欄的行數一致，
 * 橫向才對得齊。組 A 五欄（核定執行面積/預算、未編列補助款、兩個執行率）
 * 無來源維度，只在「小計」那一行有值，來源行留 undefined。
 */
const budgetLinesOf = (office: OfficeBudgetStats): BudgetLine[] => {
  const lines = (office.sources || []).map(source => ({
    key: source.source_name,
    label: source.source_name,
    variant: SOURCE_VARIANTS[source.source_name] || 'other',
    budgeted_cases: source.budgeted_cases,
    budgeted_area: source.budgeted_area,
    budgeted_subsidy: source.budgeted_subsidy,
    verified_cases: source.verified_cases,
    verified_area: source.verified_area,
    verified_amount: source.verified_amount,
    planned_area: undefined as number | undefined,
    planned_budget: undefined as number | undefined,
    unbudgeted_subsidy: undefined as number | undefined,
    area_execution_rate: undefined as number | undefined,
    budget_execution_rate: undefined as number | undefined
  }))

  lines.push({
    key: '小計',
    label: '小計',
    variant: 'subtotal',
    budgeted_cases: office.budgeted_cases,
    budgeted_area: office.budgeted_area,
    budgeted_subsidy: office.budgeted_subsidy,
    verified_cases: office.verified_cases,
    verified_area: office.verified_area,
    verified_amount: office.verified_amount,
    planned_area: office.planned_area,
    planned_budget: office.planned_budget,
    unbudgeted_subsidy: office.unbudgeted_subsidy,
    area_execution_rate: office.area_execution_rate,
    budget_execution_rate: office.budget_execution_rate
  })

  return lines
}

/**
 * 表格資料：每個管理處一組，組內含該管理處的來源行 + 小計行
 *
 * 以 v-data-table 的 #item slot 覆寫整列渲染，「管理處」儲存格用 rowspan 跨越組內所有行，
 * 其餘欄位逐行各自成格——這是客戶設計稿的樣式，也是 HTML 表格處理「同一實體多行」的原生做法。
 * 這裡先算好 lines，避免在 template 內重複呼叫 budgetLinesOf()。
 */
const budgetRowGroups = computed(() =>
  (statisticsStore.budgetAnalysis?.offices || []).map(office => ({
    office,
    lines: budgetLinesOf(office)
  }))
)

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
  // 最新消息與統計資料互不依賴，平行載入；公告失敗不影響統計呈現
  await Promise.all([
    loadAnnouncements(),
    statisticsStore.fetchAllStatistics(currentYear),
  ])
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
}

.dashboard-container--full-height {
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

/* ========== 經費統計表：管理處 rowspan + 來源/小計逐行（客戶設計稿樣式） ==========
 * 以 v-data-table 的 #item slot 輸出多個 <tr>，「管理處」儲存格 rowspan 跨越整組。
 * 來源以文字顏色區辨，使用者不需要只靠文字內容分辨（V3：差異用最小標記表達）。
 */
.statistics-table :deep(.budget-office-cell) {
  font-weight: 600;
  vertical-align: middle;
  background-color: #fff;
  border-right: 1px solid #e0e0e0;
}

.statistics-table :deep(.budget-source-cell) {
  font-weight: 600;
  white-space: nowrap;
}

/* 來源別配色 */
.statistics-table :deep(.budget-line--ia .budget-source-cell) {
  color: #1565c0;
}

.statistics-table :deep(.budget-line--advance .budget-source-cell) {
  color: #e65100;
}

.statistics-table :deep(.budget-line--other .budget-source-cell) {
  color: #6a1b9a;
}

/* 來源行之間用細虛線分隔，屬同一個管理處 */
.statistics-table :deep(.budget-line--ia td),
.statistics-table :deep(.budget-line--advance td),
.statistics-table :deep(.budget-line--other td) {
  border-bottom: 1px dashed #eceff1 !important;
}

/* 小計行：整行淡灰底 + 加粗，橫向可一眼掃到 */
.statistics-table :deep(.budget-line--subtotal td) {
  background-color: #f5f5f5;
  font-weight: 700;
  color: #263238;
}

.statistics-table :deep(.budget-line--subtotal .budget-source-cell) {
  color: #546e7a;
}

/* 每個管理處群組結束處加實線，與下一個管理處明確分開 */
.statistics-table :deep(.budget-line--group-end td) {
  border-bottom: 1px solid #cfd8dc !important;
}

/* hover 只作用在整個管理處群組視覺上不跳動：關閉逐行 hover 變色 */
.statistics-table :deep(tbody tr:hover > td) {
  background-color: inherit;
}

/* 「預算來源」欄需容納「作業基金」四字不換行 */
.statistics-table :deep(thead th:nth-child(2)) {
  min-width: 86px;
  width: 86px;
}
/* ========== 經費統計表樣式結束 ========== */

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
