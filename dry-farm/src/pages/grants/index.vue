<template>
  <v-container
    fluid
    class="grants-container px-6 pb-0 pt-0"
    style="background-color: white"
  >
    <!-- 標題區域 -->
    <v-row justify="center">
      <v-col
        cols="10"
        lg="10"
        align-self="center"
        class="pt-0"
      >
        <!-- 功能按鈕區 -->
        <div class="d-flex flex-wrap align-center pr-2">
          <v-spacer />
          <div class="d-flex gap-2">
            <!-- 重新連接 API 按鈕 -->
            <v-btn
              v-if="!isUsingApi"
              class="action-btn mr-2"
              color="orange"
              prepend-icon="mdi-wifi"
              variant="outlined"
              rounded="lg"
              size="large"
              :loading="reconnecting"
              @click="tryReconnect"
            >
              重新連接
            </v-btn>

            <v-btn
              class="action-btn mr-2"
              color="#3ea0a3"
              prepend-icon="mdi-content-copy"
              variant="outlined"
              rounded="lg"
              size="large"
              :disabled="isBatchButtonDisabled"
              :loading="batchProcessing"
              @click="showBatchCrossYearDialog = true"
            >
              批次跨年度 {{ selectedCount > 0 ? `(${selectedCount})` : '' }}
            </v-btn>

            <v-btn
              class="action-btn"
              color="#3ea0a3"
              prepend-icon="mdi-plus"
              to="/grants/new"
              variant="outlined"
              rounded="lg"
              size="large"
            >
              建立新案件
            </v-btn>
          </div>
        </div>
        <div class="section-wrapper">
          <v-card
            class="mx-auto section-card pa-4"
            variant="outlined"
            rounded="lg"
          >
            <v-card-item class="custom-title">
              <v-card-title class="text-h5 font-weight-black">
                申請案件列表
              </v-card-title>
            </v-card-item>

            <v-card-text>
              <!-- 服務狀態指示器 -->
              <v-alert
                v-if="!isUsingApi"
                type="warning"
                variant="outlined"
                class="mb-4"
              >
                <div class="d-flex align-center">
                  <v-icon
                    icon="mdi-wifi-off"
                    class="mr-2"
                  />
                  <div>
                    <div>目前使用本地資料模式</div>
                    <div class="text-caption">
                      上次 API 檢查：{{ formatTime(serviceStatus.lastApiCheck) }}
                    </div>
                  </div>
                  <v-spacer />
                  <v-btn
                    variant="text"
                    size="small"
                    :loading="reconnecting"
                    @click="tryReconnect"
                  >
                    重試連接
                  </v-btn>
                </div>
              </v-alert>

              <!-- 偵錯資訊 -->
              <!-- <v-alert
                type="info"
                variant="outlined"
                class="mb-4"
              >
                <div class="text-caption">
                  <div><strong>🔍 偵錯資訊：</strong></div>
                  <div>當前年度：{{ getCurrentYear() }}</div>
                  <div>使用者：{{ userStore.currentUser?.username || '未登入' }} ({{ userStore.currentUser?.office?.name || '無管理處' }})</div>
                  <div>使用者管理處ID：{{ getUserOfficeId() ?? '未偵測到' }}</div>
                  <div>篩選條件：年度={{ filters.year || '無' }}, 管理處={{ filters.office_id || '無' }}</div>
                  <div>已載入案件數：{{ filteredGrantsList.length }}</div>
                  <div>API狀態：{{ isUsingApi ? '正常' : '離線模式' }}</div>
                </div>
              </v-alert> -->

              <!-- 篩選卡片 -->
              <v-card
                class="table-card mb-4"
                rounded="lg"
                elevation="0"
              >
                <div
                  class="d-flex flex-wrap align-center gap-3 pa-4"
                  style="background-color: #e3f4f4;"
                >
                  <v-icon
                    icon="mdi-filter-variant"
                    color="#3ea0a3"
                    class="me-2"
                  />
                  <span class="text-subtitle-1 font-weight-medium">篩選條件</span>
                  <v-spacer />

                  <!-- 篩選區域 -->
                  <div class="d-flex flex-wrap">
                    <v-select
                      v-model="filters.year"
                      :items="yearOptions"
                      label="年度"
                      density="comfortable"
                      variant="outlined"
                      hide-details
                      class="filter-select mr-2"
                      style="min-width: 120px"
                      clearable
                      bg-color="white"
                      rounded="lg"
                      @update:model-value="updateFilters"
                    />
                    <v-select
                      v-model="filters.office_id"
                      :items="officeOptions"
                      label="管理處"
                      density="comfortable"
                      variant="outlined"
                      hide-details
                      class="filter-select mr-2"
                      style="min-width: 150px"
                      clearable
                      bg-color="white"
                      rounded="lg"
                      @update:model-value="updateFilters"
                    />
                    <v-text-field
                      v-model="search"
                      density="comfortable"
                      label="搜尋"
                      prepend-inner-icon="mdi-magnify"
                      variant="outlined"
                      hide-details
                      clearable
                      style="min-width: 200px"
                      bg-color="white"
                      rounded="lg"
                    />
                    <v-btn
                      title="重新整理"
                      icon="mdi-refresh"
                      variant="text"
                      :loading="listLoading"
                      @click="refreshList"
                    />
                  </div>
                </div>
              </v-card>

              <!-- 表格區域 -->
              <v-card
                class="table-card"
                rounded="lg"
                elevation="0"
              >
                <v-data-table-virtual
                  v-model:selected="selectedGrants"
                  fixed-header
                  :headers="headers"
                  :items="filteredGrantsList"
                  :loading="listLoading"
                  :height="500"
                  :search="search"
                  density="comfortable"
                  item-value="case_number"
                  show-select
                  class="grants-table rounded-lg"
                >
                  <!-- 自定義表頭：選取欄 -->
                  <template #[`header.data-table-select`]>
                    <div class="d-flex align-center">
                      <span class="ml-2 text-subtitle-2 font-weight-medium">選取</span>
                    </div>
                  </template>
                  <!-- 案件狀態欄位 -->
                  <template #[`item.status`]="{ item }">
                    <v-chip
                      :color="getStatusColor(item.current_step, item.status)"
                      variant="flat"
                      size="small"
                      label
                      class="font-weight-medium"
                    >
                      {{ getStatusText(item.current_step, item.is_legacy, item.status) }}
                    </v-chip>
                  </template>

                  <!-- 公告狀態欄位 -->
                  <!-- <template #[`item.card`]="{ item }">
                    <v-chip
                      :color="getCardStatusColor(item.card)"
                      variant="outlined"
                      size="small"
                      label
                      class="font-weight-medium"
                    >
                      {{ item.card }}
                    </v-chip>
                  </template> -->
                  <!-- 設施面積欄位 -->
                  <template #[`item.facility_area_m2`]="{ item }">
                    {{ item.facility_area_m2 ? item.facility_area_m2.toLocaleString() : '-' }}
                  </template>

                  <!-- 操作按鈕 -->
                  <template #[`item.actions`]="{ item }">
                    <div class="ma-0 pa-0 d-flex gap-2 justify-end">
                      <!-- 歷史案件：顯示查看按鈕和查看歷史按鈕 -->
                      <template v-if="item.is_legacy">
                        <v-btn
                          icon="mdi-eye"
                          size="small"
                          color="#3ea0a3"
                          variant="text"
                          title="查看歷史案件"
                          @click="editItem(item)"
                        />
                        <v-btn
                          icon="mdi-file-pdf-box"
                          size="small"
                          color="#ff9800"
                          variant="text"
                          title="查看歷史 - 生成工程預算書封面PDF"
                          :loading="pdfGenerating === item.case_number"
                          @click="generateHistoryPdf(item)"
                        />
                      </template>
                      <!-- 一般案件：顯示編輯和刪除按鈕 -->
                      <template v-else>
                        <v-btn
                          icon="mdi-pencil"
                          size="small"
                          color="#3ea0a3"
                          variant="text"
                          title="編輯案件"
                          @click="editItem(item)"
                        />
                        <v-btn
                          icon="mdi-delete"
                          size="small"
                          color="error"
                          variant="text"
                          title="刪除案件"
                          @click="deleteItem(item)"
                        />
                      </template>
                    </div>
                  </template>

                  <!-- 表格底部 -->
                  <template #bottom>
                    <div class="d-flex align-center pa-3">
                      <span class="text-body-2 text-medium-emphasis">
                        共 {{ filteredGrantsList.length }} 筆資料
                        <span
                          v-if="!isUsingApi"
                          class="text-warning"
                        >（本地資料）</span>
                      </span>
                      <v-spacer />
                      <div
                        v-if="listError"
                        class="text-error text-caption"
                      >
                        {{ listError }}
                      </div>
                    </div>
                  </template>
                </v-data-table-virtual>
              </v-card>

              <!-- 提示說明 -->
              <div class="d-flex align-center mt-4">
                <v-icon
                  icon="mdi-information-outline"
                  color="#3ea0a3"
                  class="me-2"
                  size="small"
                />
                <span class="text-caption text-medium-emphasis">
                  點擊「編輯」按鈕可查看或修改案件內容，「刪除」按鈕將永久移除該案件資料
                </span>
              </div>
            </v-card-text>
          </v-card>
        </div>
      </v-col>
    </v-row>

    <!-- 批次跨年度確認對話框 -->
    <v-dialog
      v-model="showBatchCrossYearDialog"
      max-width="600px"
      persistent
    >
      <v-card rounded="lg">
        <v-card-title class="text-h5 pa-6 pb-2">
          <v-icon
            icon="mdi-content-copy"
            color="#3ea0a3"
            class="mr-2"
          />
          批次跨年度確認
        </v-card-title>

        <v-card-text class="pa-6">
          <v-alert
            type="info"
            variant="outlined"
            class="mb-4"
          >
            <div>
              <strong>批次跨年度處理說明：</strong>
            </div>
            <div class="mt-2">
              • 被選取的案件將被複製為新案件，並調整為次年度<br>
              • 原案件狀態將變更為「跨年度案件」<br>
              • 原案件說明將標示為「預算用罄，移至次年度撥款」<br>
              • 新案件將建立初始版本，並在版本註解中記錄來源案件資訊
            </div>
          </v-alert>

          <div class="text-body-1 mb-3">
            <strong>已選取案件數量：</strong> {{ selectedCount }} 筆
          </div>

          <div class="text-body-2 text-medium-emphasis">
            選取的案件編號：{{ selectedGrants.join(', ') }}
          </div>
        </v-card-text>

        <v-card-actions class="pa-6 pt-0">
          <v-spacer />
          <v-btn
            variant="outlined"
            :disabled="batchProcessing"
            @click="showBatchCrossYearDialog = false"
          >
            取消
          </v-btn>
          <v-btn
            color="#3ea0a3"
            variant="flat"
            :loading="batchProcessing"
            @click="confirmBatchCrossYear"
          >
            確認執行
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script lang="ts" setup>
import { storeToRefs } from 'pinia';
import { useRouter } from 'vue-router'
import type { GrantListItem } from '@/services/grantsService'
import { generateKaiuPdf, downloadPdfBlob, batchCrossYearGrants } from '@/services/grantsService'
import { useGrantsStore } from '@/stores/grants'
import { useUserStore } from '@/stores/users'
import { GrantStorage, type GrantData } from '@/utils/grant-storage'

const router = useRouter()
const grantsStore = useGrantsStore()
const userStore = useUserStore()

// 取得當前使用者資訊和設定預設篩選條件
const getCurrentYear = () => new Date().getFullYear() - 1911 // 民國年
const getUserOfficeId = () => {
  // 優先從 userStore 取得當前使用者的管理處ID
  const officeId = userStore.currentUser?.office?.id || null
  console.log('🏢 [getUserOfficeId] 從 userStore 取得管理處ID:', officeId)
  console.log('👤 [getUserOfficeId] 當前使用者:', userStore.currentUser?.username)
  console.log('🏢 [getUserOfficeId] 管理處名稱:', userStore.currentUser?.office?.name)

  return officeId
}

interface Step2Data {
  facilityAreaHa?: string
  landAreaHa?: string
  [key: string]: unknown
}

interface Step4Data {
  irrigationType?: string
  [key: string]: unknown
}

// 擴展 GrantData 類型以包含 currentStep
interface ExtendedGrantData extends GrantData {
  currentStep?: number,
  is_legacy?: boolean // 是否為舊版案件
}

interface GrantItem {
  applicantName: string
  irrigationName: string
  facilityArea: number
  stepName: string
  card: string
  actions: number
  selectable: boolean
  caseYear: number
  caseNumber: string
  officeName: string
}

// 響應式資料
const searchInput = ref('')
const reconnecting = ref(false)
const deleting = ref(false)
const showDeleteConfirmDialog = ref(false)
const pdfGenerating = ref<string | null>(null) // 追蹤正在生成PDF的案件編號
const batchProcessing = ref(false) // 批次處理狀態
const showBatchCrossYearDialog = ref(false) // 批次跨年度確認對話框

// 篩選條件 - 設置預設值
const filters = reactive({
  year: getCurrentYear(), // 預設為當年度
  office_id: getUserOfficeId() // 預設為使用者所屬管理處
})

// 從 store 取得狀態
const {
  grantsList,
  filteredGrantsList,
  listLoading,
  listError,
  serviceStatus,
  selectedGrants,
  // migrationInProgress,
  // migrationResult,
  isUsingApi
} = storeToRefs(grantsStore)

// 計算選取案件數量，確保響應式更新
const selectedCount = computed(() => selectedGrants.value.length)
const isBatchButtonDisabled = computed(() => selectedCount.value === 0)

// 監聽選取變化，用於調試
watch(selectedGrants, (newVal) => {
  console.log('🔍 [selectedGrants] 變化:', newVal)
  console.log('🔍 [selectedCount] 數量:', selectedCount.value)
}, { deep: true })

const allItems = ref<GrantItem[]>([])
const loading = ref(true)
const search = ref('')
const selected = ref<string[]>([])

// 篩選選項
const selectedYear = ref(null)
const selectedOffice = ref(null)

// 年度選項
const currentYear = new Date().getFullYear() - 1911
const startYear = 97 // 民國 97 年
const yearOptions = Array.from({ length: currentYear - startYear + 1 }, (_, i) => {
  const year = currentYear - i // 從最新年度開始，向前遞減
  return { title: `${year}年`, value: year }
})

// 管理處選項 - 根據實際資料庫資料更新對應關係
const officeOptions = [
  { title: '農業部農田水利署', value: 0 },
  { title: '宜蘭管理處', value: 1 },
  { title: '北基管理處', value: 2 },
  { title: '桃園管理處', value: 3 },
  { title: '石門管理處', value: 4 },
  { title: '新竹管理處', value: 5 },
  { title: '苗栗管理處', value: 6 },
  { title: '臺中管理處', value: 7 },
  { title: '南投管理處', value: 8 },
  { title: '彰化管理處', value: 9 },
  { title: '雲林管理處', value: 10 },
  { title: '嘉南管理處', value: 11 },
  { title: '高雄管理處', value: 12 },
  { title: '屏東管理處', value: 13 },
  { title: '臺東管理處', value: 14 },
  { title: '花蓮管理處', value: 15 },
  { title: '七星管理處', value: 16 },
  { title: '瑠公管理處', value: 17 },
  { title: '金門縣農會', value: 18 },
  { title: '澎湖縣農會', value: 19 },
  { title: '農田水利人力發展中心', value: 20 },
  { title: '茶葉改良場', value: 21 },
  { title: '財團法人農業工程研究中心', value: 22 },
  { title: '高雄市政府農業局', value: 23 },
  { title: '農工中心', value: 99 },
  { title: '農業部', value: 100 }
]

// 表格標題
const headers = ref([
  { title: '申請年度', key: 'year', align: 'start' as const, width: '110px' },
  { title: '案號', key: 'case_number', align: 'start' as const },
  { title: '申請人姓名', key: 'applicant_name', align: 'start' as const },
  { title: '管理處', key: 'office', align: 'start' as const },
  { title: '末端形式', key: 'facility_type', align: 'end' as const },
  { title: '施作面積 (m²)', key: 'facility_area_m2', align: 'end' as const },
  { title: '案件狀態', key: 'status', align: 'end' as const },
  // { title: '公告狀態（農民卡）', key: 'card', align: 'end' as const },
  { title: '操作', key: 'actions', align: 'end' as const, sortable: false },
])

// 根據公告狀態返回對應的顏色
const getCardStatusColor = (status: string) => {
  switch (status) {
    case '已受理':
      return 'blue';
    case '審查中':
      return 'amber';
    case '審查通過':
      return 'light-green';
    case '撥款作業':
      return 'purple';
    case '結案流程':
      return 'green';
    default:
      return 'grey';
  }
}

// Status mapping based on current step
const statusMapping = {
  1: '處理中',
  2: '完成申請人資料',
  3: '完成土地資料',
  4: '完成現場勘查',
  5: '完成灌溉調控設施',
  6: '完成田間管路',
  7: '完成補助申請資料',
  8: '完成結案申報',
}

// 整合後端 GrantStatus 枚舉的狀態映射表
const grantStatusMapping = {
  'draft': '草稿',
  'submitted': '已提交',
  'under_review': '審查中',
  'approved': '核准',
  'rejected': '駁回',
  'withdrawn': '撤銷',
  'cross_year': '跨年度案件',
  'completed': '已結案',
  'deleted': '已刪除'
} as const

const getStatusText = (currentStep: number, isLegacy?: boolean, status?: string): string => {
  // 處理特殊狀態 - 優先使用後端 GrantStatus 枚舉
  if (isLegacy) {
    return '歷史案件'
  }

  // TODO：使用後端 GrantStatus 枚舉狀態
  // if (status && status in grantStatusMapping) {
  //   return grantStatusMapping[status as keyof typeof grantStatusMapping]
  // }

  // 預設使用基於步驟的狀態映射
  return statusMapping[currentStep as keyof typeof statusMapping] || '處理中'
}

// 整合後端 GrantStatus 枚舉的顏色映射表
const grantStatusColorMapping = {
  'draft': 'grey-lighten-4',           // 草稿 - 灰色
  'submitted': 'blue-lighten-4',       // 已提交 - 藍色
  'under_review': 'amber-lighten-4',   // 審查中 - 琥珀色
  'approved': 'green-lighten-4',       // 核准 - 綠色
  'rejected': 'red-lighten-4',         // 駁回 - 紅色
  'withdrawn': 'purple-lighten-4',     // 撤銷 - 紫色
  'cross_year': 'orange-lighten-4',    // 跨年度案件 - 橙色
  'completed': 'green-lighten-4',      // 已結案 - 綠色
  'deleted': 'red-lighten-5'           // 已刪除 - 淡紅色
} as const

const getStatusColor = (currentStep: number, status?: string) => {
  // TODO：優先使用後端 GrantStatus 枚舉狀態顏色
  // if (status && status in grantStatusColorMapping) {
  //   return grantStatusColorMapping[status as keyof typeof grantStatusColorMapping]
  // }

  // 預設根據步驟返回顏色
  if (currentStep <= 2) return 'blue-lighten-5'
  if (currentStep <= 4) return 'amber-lighten-5'
  if (currentStep <= 6) return 'light-green-lighten-5'
  if (currentStep <= 8) return 'light-blue-lighten-5'
  return 'grey-lighten-4'
}

const formatTime = (date: Date) => {
  return new Intl.DateTimeFormat('zh-TW', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  }).format(date)
}

const handleSearch = () => {
  grantsStore.debouncedSearch(searchInput.value)
}

const updateFilters = async () => {
  // 篩選條件變更時清除選取狀態
  grantsStore.clearSelectedGrants()

  // 明確設定篩選參數，包括移除數量限制
  const filterParams = {
    year: filters.year || undefined,
    office_id: filters.office_id || undefined,
    limit: undefined, // 明確移除數量限制
    skip: 0
  }

  console.log('🔍 [index.vue] Updating filters with params:', filterParams)
  await grantsStore.updateFilters(filterParams)

  // 篩選條件變更時重新載入案件清單，確保不限制數量
  await grantsStore.loadGrantsList(filterParams)
}

const refreshList = async () => {
  // refreshGrantsList 內部會自動清除選取狀態
  await grantsStore.refreshGrantsList()
}

const tryReconnect = async () => {
  reconnecting.value = true
  try {
    const success = await grantsStore.tryReconnectApi()
    if (success) {
      console.log('📡 API 重新連接成功')
    }
  } catch (error) {
    console.error('📡 API 重新連接失敗:', error)
  } finally {
    reconnecting.value = false
  }
}

const confirmBatchDelete = async () => {
  showDeleteConfirmDialog.value = false
  deleting.value = true

  try {
    await grantsStore.deleteSelectedGrants()
  } catch (error) {
    console.error('批次刪除失敗:', error)
    alert('批次刪除失敗，請稍後再試')
  } finally {
    deleting.value = false
  }
}

// Card status options (random assignment for demo)
const cardStatusOptions = ['已受理', '審查中', '審查通過', '撥款作業', '結案流程']

// Filter items based on search and selected filters
const filteredItems = computed(() => {
  let result = allItems.value

  // 過濾年度
  if (selectedYear.value) {
    result = result.filter(item => item.caseYear === selectedYear.value)
  }

  // 過濾管理處
  if (selectedOffice.value) {
    result = result.filter(item => item.officeName === selectedOffice.value)
  }

  // 搜尋過濾
  if (search.value) {
    const searchTerm = search.value.toLowerCase()
    result = result.filter(item => {
      return (
        (item.applicantName && item.applicantName.toLowerCase().includes(searchTerm)) ||
        (item.caseNumber && item.caseNumber.toLowerCase().includes(searchTerm)) ||
        (String(item.caseYear) && String(item.caseYear).includes(searchTerm)) ||
        (item.officeName && item.officeName.toLowerCase().includes(searchTerm)) ||
        (item.irrigationName && item.irrigationName.toLowerCase().includes(searchTerm)) ||
        (item.stepName && item.stepName.toLowerCase().includes(searchTerm))
      )
    })
  }

  return result
})

// Load all data from localStorage and sample data
const loadAllItems = () => {
  loading.value = true

  // Get all grants from localStorage
  const grants = GrantStorage.getAllGrants()

  // Transform grant data to table format
  const transformedData = Object.entries(grants).map(([caseNumber, grantData]: [string, ExtendedGrantData]) => {
    // Extract applicant name from step 1
    // const step1Data = grantData.stepsData?.[1] as Step1Data || {}
    // console.log(`[loadAllItems] Processing case: ${caseNumber}`, grantData)
    const name = grantData.applicantName || '未填寫'

    // Extract year from case number (first 3 digits)
    const year = parseInt(caseNumber.substring(0, 3))

    // Extract land area from step 2
    const step2Data = grantData.stepsData?.[2] as Step2Data || {}
    const areaHa = parseFloat(step2Data.facilityAreaHa || step2Data.landAreaHa || '0')
    const areaM2 = Math.round(areaHa * 10000) // Convert hectares to square meters

    // Extract irrigation type from step 4
    const step4Data = grantData.stepsData?.[4] as Step4Data || {}
    let irrigationType = '未設定'

    if (step4Data.irrigationType) {
      // Map from irrigation type to display name
      const typeMap: Record<string, string> = {
        '穿孔管系統': '穿孔管',
        '噴頭式系統': '噴灌',
        '微噴系統': '微噴',
        '滴灌系統': '滴灌',
        '其他': '其他'
      }
      irrigationType = typeMap[step4Data.irrigationType] || step4Data.irrigationType
    }

    // Extract office from store data or default
    const office = grantData.officeName || '未設定'

    // Determine current step and status - safely access currentStep
    const currentStep = grantData.currentStep
    const status = statusMapping[currentStep as keyof typeof statusMapping] || '處理中'

    // Generate random card status for demo
    const cardStatusIndex = Math.floor(Math.random() * cardStatusOptions.length)
    const cardStatus = cardStatusOptions[cardStatusIndex]

    return {
      applicantName: name,
      irrigationName: irrigationType,
      facilityArea: areaM2,
      stepName: status,
      card: cardStatus,
      actions: 4, // For action buttons
      selectable: true,  // All items are selectable
      caseYear: Number(year),
      caseNumber: caseNumber,
      officeName: office
    }
  })

  // 只使用 localStorage 中的實際申請案件資料
  allItems.value = transformedData

  loading.value = false
}

// const editItem = (itemId: string) => {
//   const grantData = GrantStorage.getGrant(itemId) as ExtendedGrantData | null;
//   if (grantData) {
//     // 取得案件的 currentStep，如果沒有則預設為 0
//     const currentStep = grantData.currentStep || 0;

//     console.log(`[editItem] Navigating to edit grant ${itemId} at step ${currentStep}`);

//     // 直接導航到編輯頁面，讓 edit.vue 自己處理案件載入和步驟設置
//     router.push(`/grants/edit?id=${itemId}&step=${currentStep}`);
//   } else {
//     // 如果找不到數據，只帶 ID 參數導航
//     console.warn(`Grant data not found for ID: ${itemId}, navigating with ID only`);
//     router.push(`/grants/edit?id=${itemId}`);
//   }
// }
const editItem = (item: GrantListItem) => {
  if (item.is_legacy) {
    // 如果是歷史案件，在新分頁中開啟查看頁面，包含 grants_id 參數以區分重複案件編號
    const url = router.resolve(`/grants/statements?case=${item.case_number}&grants_id=${item.id}`).href
    window.open(url, '_blank')
    return
  }
  router.push(`/grants/edit?id=${item.case_number}&step=${item.current_step}`)
}

// const deleteItem = (itemId: string) => {
//   if (confirm(`確定要刪除案號 ${itemId} 的申請案件嗎？`)) {
//     try {
//       // Remove from localStorage
//       GrantStorage.deleteGrant(itemId)
//       // Also remove from UI
//       allItems.value = allItems.value.filter(item => item.caseNumber !== itemId)
//     } catch (error) {
//       console.error('Failed to delete grant:', error)
//     }
//   }
// }
const deleteItem = async (item: GrantListItem) => {
  // 🔥 Linus式修復：提供清晰的確認對話框，說明邏輯刪除的含義
  const confirmMessage = [
    `確定要刪除以下申請案件嗎？`,
    ``,
    `案件編號：${item.case_number}`,
    `申請者：${item.applicant_name || '未填寫'}`,
    `管理處：${item.office || '未指定'}`,
    ``,
    `注意：此操作將案件狀態設為「已刪除」，`,
    `案件資料將保留在資料庫中以供審計追蹤。`
  ].join('\n')

  if (confirm(confirmMessage)) {
    try {
      console.log(`📋 [deleteItem] 開始刪除案件: ${item.case_number} (ID: ${item.id})`)

      await grantsStore.deleteGrantFromList(item)

      console.log(`📋 [deleteItem] 案件 ${item.case_number} 已成功刪除`)
      alert(`案件 ${item.case_number} 已成功刪除`)

    } catch (error) {
      console.error(`📋 [deleteItem] 刪除案件 ${item.case_number} 失敗:`, error)

      // 提供更詳細的錯誤信息
      let errorMessage = '刪除案件失敗'
      if (error instanceof Error) {
        if (error.message.includes('已經被刪除')) {
          errorMessage = '此案件已經被刪除'
        } else if (error.message.includes('不存在')) {
          errorMessage = '案件不存在，可能已被其他人刪除'
        } else if (error.message.includes('權限')) {
          errorMessage = '沒有權限刪除此案件'
        } else {
          errorMessage = `刪除失敗：${error.message}`
        }
      }

      alert(errorMessage)
    }
  }
}

// 新增：生成歷史案件PDF
const generateHistoryPdf = async (item: GrantListItem) => {
  if (!item.is_legacy) {
    console.warn('只有歷史案件才能生成PDF')
    return
  }

  try {
    console.log('🖨️ 開始生成PDF，案件:', item.case_number)
    pdfGenerating.value = item.case_number

    // 調用PDF生成服務
    const pdfBlob = await generateKaiuPdf(item)

    // 生成檔案名稱
    const timestamp = new Date().toISOString().slice(0, 19).replace(/[:]/g, '-')
    const filename = `${item.case_number}_工程預算書封面_${timestamp}.pdf`

    // 下載PDF
    downloadPdfBlob(pdfBlob, filename)

    console.log('🖨️ PDF生成並下載完成')

  } catch (error) {
    console.error('🖨️ PDF生成失敗:', error)
    alert('PDF生成失敗，請稍後再試')
  } finally {
    pdfGenerating.value = null
  }
}

// 新增：批次跨年度處理
const confirmBatchCrossYear = async () => {
  showBatchCrossYearDialog.value = false
  batchProcessing.value = true

  try {
    console.log('🔄 開始批次跨年度處理，選取案件:', selectedGrants.value)

    // 獲取選取案件的詳細資料
    const selectedItems = selectedGrants.value.map(caseNumber =>
      grantsList.value.find(grant => grant.case_number === caseNumber)
    ).filter(Boolean) as GrantListItem[]

    // 調用批次跨年度服務
    const results = await batchCrossYearGrants(selectedItems)

    console.log('✅ 批次跨年度處理完成:', results)

    // 使用 grantsStore 的方法清除選取狀態
    grantsStore.clearSelectedGrants()

    // 重新載入案件列表以顯示更新
    await refreshList()

    // 顯示成功訊息
    const successCount = results.filter(r => r.success).length
    const failCount = results.length - successCount
    let message = `批次跨年度處理完成！成功處理 ${successCount} 筆案件`
    if (failCount > 0) {
      message += `，失敗 ${failCount} 筆案件`
    }

    // 使用瀏覽器原生 alert，後續可改為 Vuetify 的 snackbar
    alert(message)

  } catch (error) {
    console.error('🔄 批次跨年度處理失敗:', error)
    alert('批次跨年度處理失敗，請稍後再試')
  } finally {
    batchProcessing.value = false
  }
}

// Load data when component is mounted
onMounted(async () => {
  console.log('🚀 [grants/index] 頁面載入開始')

  // 確保使用者資料已載入
  if (!userStore.currentUser && userStore.token) {
    console.log('👤 [grants/index] 等待使用者資料載入...')
    await userStore.fetchCurrentUser()
  }

  // 重新取得預設篩選條件（使用者資料載入後）
  filters.year = getCurrentYear()
  filters.office_id = getUserOfficeId()

  console.log('📊 [grants/index] 設定預設篩選條件:', {
    year: filters.year,
    office_id: filters.office_id,
    user: userStore.currentUser?.username,
    officeName: userStore.currentUser?.office?.name
  })

  // 明確設定篩選參數,包括移除數量限制
  const filterParams = {
    year: filters.year || undefined,
    office_id: filters.office_id || undefined,
    limit: undefined, // 明確移除數量限制
    skip: 0
  }

  console.log('🔍 [grants/index] 使用篩選參數載入案件列表:', filterParams)

  // 直接載入案件清單（含預設篩選條件），避免重複調用updateFilters
  await grantsStore.loadGrantsList(filterParams)

  console.log('✅ [grants/index] 頁面載入完成，共載入', filteredGrantsList.value.length, '筆案件')
})

// Watch for changes in grantsStore currentStep to update status
watch(() => grantsStore.currentStep, (newStep) => {
  if (newStep && grantsStore.currentGrant) {
    // 更新對應案件的狀態
    const caseNumber = grantsStore.currentGrant.case_number
    const item = allItems.value.find(item => item.caseNumber === caseNumber)
    if (item) {
      item.stepName = statusMapping[newStep as keyof typeof statusMapping]
    }
  }
})
</script>

<style scoped>
/* 添加背景圖片樣式 */
.grants-container {
  background-image: url('@/assets/bg_index.svg');
  background-size: cover;
  background-position: center bottom;
  background-repeat: no-repeat;
  background-attachment: fixed;
  /* min-height: 100vh; */
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
  /* padding: 0 16px !important; */
  background-color: #3ea0a3 !important;
  border-radius: 8px 8px 0 0;
  z-index: 1;
  transition: all 0.3s ease;
}

.v-card-title {
  color: white !important;
  display: flex;
  justify-content: flex-start;
  align-items: center;
  width: 100%;
  height: 100%;
  /* padding-left: 16px; */
}

/* 表格區域樣式 */
.table-card {
  border-radius: 12px;
  overflow: hidden;
}

/* 表格樣式 */
.grants-table :deep(thead th) {
  background-color: #e3f4f4 !important;
  color: #333 !important;
  font-weight: 900 !important;
}

.grants-table :deep(.v-data-table__tr:hover) {
  background-color: rgba(98, 183, 187, 0.1) !important;
}

.grants-table :deep(.v-data-table__tr:nth-child(even)) {
  background-color: rgba(98, 183, 187, 0.05);
}

/* 按鈕樣式 */
.action-btn {
  background-color: white !important;
  font-weight: 500;
  transition: all 0.2s ease;
}

.action-btn:hover {
  /* transform: translateY(-2px); */
  /* box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1); */
  background-color: #3ea0a3 !important;
  color: white !important;
}

/* 篩選區域樣式 */
.filter-select {
  max-width: 200px;
}

@media (max-width: 600px) {
  .filter-select {
    min-width: 100%;
  }
}
</style>
