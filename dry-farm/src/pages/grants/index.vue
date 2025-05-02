<template>
  <v-container fluid class="grants-container px-6 py-4" style="background-color: white">
    <!-- 標題區域 -->
    <v-row justify="center">
      <v-col cols="10" lg="10" align-self="center" class="pt-0">
        <!-- 功能按鈕區 -->
        <div class="d-flex flex-wrap align-center pr-2">
          <v-spacer />
          <div class="d-flex gap-2">
            <v-btn
              class="action-btn mr-2"
              color="#3ea0a3"
              prepend-icon="mdi-content-copy"
              to="/grants/edit"
              variant="outlined"
              rounded="lg"
              size="large"
            >
              批次跨年度
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
              <!-- 篩選卡片 -->
              <v-card
                class="table-card mb-4"
                rounded="lg"
                elevation="0"
              >
                <div class="d-flex flex-wrap align-center gap-3 pa-4" style="background-color: #e3f4f4;">
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
                      v-model="selectedYear"
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
                    />
                    <v-select
                      v-model="selectedOffice"
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
                  fixed-header
                  :headers="headers"
                  :items="filteredItems"
                  :loading="loading"
                  :height="500"
                  density="comfortable"
                  item-value="name"
                  v-model:selected="selected"
                  show-select
                  :item-selectable="item => item.iron !== '0'"
                  class="grants-table rounded-lg"
                >
                  <!-- 選取欄位標題 -->
                  <template #['header.data-table-select']>
                    <span class="ml-2 font-weight-medium">選取</span>
                  </template>

                  <!-- 案件狀態欄位 -->
                  <template #[`item.carbs`]="{ item }">
                    <v-chip
                      :color="getStatusColor(item.carbs)"
                      variant="flat"
                      size="small"
                      label
                      class="font-weight-medium"
                    >
                      {{ item.carbs }}
                    </v-chip>
                  </template>

                  <!-- 公告狀態欄位 -->
                  <template #[`item.card`]="{ item }">
                    <v-chip
                      :color="getCardStatusColor(item.card)"
                      variant="outlined"
                      size="small"
                      label
                      class="font-weight-medium"
                    >
                      {{ item.card }}
                    </v-chip>
                  </template>

                  <!-- 操作按鈕 -->
                  <template #[`item.protein`]="{ item }">
                    <div class="ma-0 pa-0 d-flex gap-2 justify-end">
                      <v-btn
                        icon="mdi-pencil"
                        size="small"
                        color="#3ea0a3"
                        variant="text"
                        @click="editItem(item.value)"
                      />
                      <v-btn
                        icon="mdi-delete"
                        size="small"
                        color="error"
                        variant="text"
                        @click="deleteItem(item.value)"
                      />
                    </div>
                  </template>

                  <!-- 表格底部分頁與合計 -->
                  <template #bottom>
                    <div class="d-flex align-center pa-3">
                      <span class="text-body-2 text-medium-emphasis">
                        共 {{ filteredItems.length }} 筆資料
                      </span>
                      <v-spacer />
                      <v-pagination
                        v-model="page"
                        :length="Math.ceil(filteredItems.length / itemsPerPage)"
                        :total-visible="5"
                        density="comfortable"
                        color="#3ea0a3"
                      />
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
  </v-container>
</template>

<script lang="ts" setup>
import { useDisplay } from 'vuetify'
import { GrantStorage } from '@/utils/grant-storage' // Import GrantStorage utility

const allItems = ref<any[]>([])
const loading = ref(true)
const search = ref('')
const selected = ref<string[]>([])
const router = useRouter()

// 分頁
const page = ref(1)
const itemsPerPage = ref(10)

// 篩選選項
const selectedYear = ref(null)
const selectedOffice = ref(null)

// 年度選項 - 動態生成近5年的選項（台灣年號）
const currentYear = new Date().getFullYear() - 1911
const yearOptions = Array.from({ length: 5 }, (_, i) => {
  const year = currentYear - i
  return { title: `${year}年`, value: year }
})

// 管理處選項
const officeOptions = [
  { title: '瑠公管理處', value: '瑠公管理處' },
  { title: '七星管理處', value: '七星管理處' },
  { title: '北基管理處', value: '北基管理處' },
  { title: '石門管理處', value: '石門管理處' },
  { title: '臺中管理處', value: '臺中管理處' },
  { title: '嘉南管理處', value: '嘉南管理處' },
  { title: '高雄管理處', value: '高雄管理處' },
  { title: '屏東管理處', value: '屏東管理處' },
  { title: '花蓮管理處', value: '花蓮管理處' },
  { title: '台東管理處', value: '台東管理處' }
]

const headers = ref([
  { title: '申請年度', key: 'year', align: 'start' },
  { title: '案號', key: 'id', align: 'start' },
  { title: '申請人姓名', key: 'name', align: 'start' },
  { title: '管理處', key: 'office', align: 'start' },
  { title: '末端形式', key: 'calories', align: 'end' },
  { title: '施作面積 (m²)', key: 'fat', align: 'end' },
  { title: '案件狀態', key: 'carbs', align: 'end' },
  { title: '公告狀態（農民卡）', key: 'card', align: 'end' },
  { title: '操作', key: 'protein', align: 'end' },
])

const { name } = useDisplay()
const isSmallScreen = computed(() => name.value === 'xs' || name.value === 'sm')

// 根據案件狀態返回對應的顏色
const getStatusColor = (status: string) => {
  if (status.includes('完成申請人資料') || status.includes('完成土地資料')) {
    return 'blue-lighten-5';
  } else if (status.includes('完成灌溉調控設施') || status.includes('完成田間管路')) {
    return 'amber-lighten-5';
  } else if (status.includes('完成現場勘查') || status.includes('完成補助申請資料')) {
    return 'light-green-lighten-5';
  } else if (status.includes('完成變更設計') || status.includes('完成上傳佐證文件')) {
    return 'light-blue-lighten-5';
  }
  return 'grey-lighten-4';
}

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

// Sample data
const apply = [
  {
    name: '許大利',
    calories: '滴灌',  // 更新末端類型
    fat: 1900,        // 施作面積
    carbs: '完成申請人資料', // 案件狀態
    card: '已受理',    // 農民卡狀態
    protein: 4,
    iron: '1',
    year: 113,        // 申請年度
    id: '11301001',   // 案號
    office: '瑠公管理處', // 新增管理處
  },
  {
    name: '陳大明',
    calories: '穿孔管',
    fat: 4000,
    carbs: '完成灌溉調控設施',
    card: '審查中',
    protein: 4,
    iron: '1',
    year: 113,
    id: '11301002',
    office: '七星管理處',
  },
  {
    name: '劉台北',
    calories: '其他',  // 更新末端類型
    fat: 2800,
    carbs: '完成田間管路',
    card: '審查中',
    protein: 4,
    iron: '1',
    year: 113,
    id: '11301003',
    office: '北基管理處',
  },
  {
    name: '彭大吉',
    calories: '噴灌',  // 更新末端類型
    fat: 4000,
    carbs: '完成現場勘查',
    card: '審查通過',  // 隨機分配
    protein: 4,
    iron: '1',
    year: 113,
    id: '11301004',
    office: '瑠公管理處',
  },
  {
    name: '林正雄',
    calories: '滴灌',
    fat: 3500,
    carbs: '完成申請人資料',
    card: '已受理',
    protein: 4,
    iron: '1',
    year: 112,
    id: '11201042',
    office: '臺中管理處',
  },
  {
    name: '王美蓮',
    calories: '噴灌',  // 更新末端類型
    fat: 2600,
    carbs: '完成土地資料',
    card: '審查中',
    protein: 4,
    iron: '1',
    year: 112,
    id: '11201085',
    office: '嘉南管理處',
  },
  {
    name: '張水源',
    calories: '微噴',
    fat: 3200,
    carbs: '完成現場勘查',
    card: '結案流程',  // 隨機分配
    protein: 4,
    iron: '2',
    year: 111,
    id: '11101126',
    office: '高雄管理處',
  },
  {
    name: '李農田',
    calories: '其他',
    fat: 1800,
    carbs: '完成現場勘查',
    card: '撥款作業',  // 隨機分配
    protein: 4,
    iron: '0',
    year: 111,
    id: '11101152',
    office: '屏東管理處',
  },
  {
    name: '黃水利',
    calories: '滴灌',
    fat: 5200,
    carbs: '完成田間管路',
    card: '審查中',
    protein: 4,
    iron: '1',
    year: 111,
    id: '11101023',
    office: '花蓮管理處',
  },
  {
    name: '吳田野',
    calories: '微噴',  // 更新末端類型，原先為霧化器
    fat: 4800,
    carbs: '完成田間管路',
    card: '審查中',
    protein: 4,
    iron: '1',
    year: 110,
    id: '11001078',
    office: '台東管理處',
  }
]

// Status mapping based on current step
const statusMapping = {
  1: '完成申請人資料',
  2: '完成土地資料',
  3: '完成灌溉調控設施',
  4: '完成田間管路',
  5: '完成現場勘查',
  6: '完成補助申請資料',
  7: '完成變更設計及結案申報',
  8: '完成上傳佐證文件',
}

// Card status options (random assignment for demo)
const cardStatusOptions = ['已受理', '審查中', '審查通過', '撥款作業', '結案流程']

// Filter items based on search and selected filters
const filteredItems = computed(() => {
  let result = allItems.value

  // 過濾年度
  if (selectedYear.value) {
    result = result.filter(item => item.year === selectedYear.value)
  }

  // 過濾管理處
  if (selectedOffice.value) {
    result = result.filter(item => item.office === selectedOffice.value)
  }

  // 搜尋過濾
  if (search.value) {
    const searchTerm = search.value.toLowerCase()
    result = result.filter(item => {
      return (
        (item.name && item.name.toLowerCase().includes(searchTerm)) ||
        (item.id && item.id.toLowerCase().includes(searchTerm)) ||
        (String(item.year) && String(item.year).includes(searchTerm))
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
  const transformedData = Object.entries(grants).map(([caseNumber, grantData]) => {
    // Extract applicant name from step 1
    const step1Data = grantData.steps?.[1] || {}
    const name = step1Data.name || step1Data.applicantName || '未填寫'

    // Extract year from case number (first 3 digits)
    const year = parseInt(caseNumber.substring(0, 3)) || 113

    // Extract land area from step 2
    const step2Data = grantData.steps?.[2] || {}
    const areaHa = parseFloat(step2Data.facilityAreaHa || step2Data.landAreaHa || '0')
    const areaM2 = Math.round(areaHa * 10000) // Convert hectares to square meters

    // Extract irrigation type from step 4
    const step4Data = grantData.steps?.[4] || {}
    let irrigationType = '未設定'

    if (step4Data.irrigationType) {
      // Map from irrigation type to display name
      const typeMap = {
        '穿孔管系統': '穿孔管',
        '噴頭式系統': '噴灌',
        '微噴系統': '微噴',
        '滴灌系統': '滴灌',
        '其他': '其他'
      }
      irrigationType = typeMap[step4Data.irrigationType] || step4Data.irrigationType
    }

    // Extract office from store data or default
    const office = step1Data.department || '瑠公管理處'

    // Determine current step and status
    const currentStep = grantData.current_step || 1
    const status = statusMapping[currentStep] || '處理中'

    // Generate random card status for demo
    const cardStatusIndex = Math.floor(Math.random() * cardStatusOptions.length)
    const cardStatus = cardStatusOptions[cardStatusIndex]

    return {
      name: name,
      calories: irrigationType,
      fat: areaM2,
      carbs: status,
      card: cardStatus,
      protein: 4, // For action buttons
      iron: '1',  // For selection
      year: Number(year),
      id: caseNumber,
      office: office,
      value: caseNumber // Needed for editItem and deleteItem functions
    }
  })

  // If no data in localStorage, use sample data
  if (transformedData.length === 0) {
    allItems.value = apply
  } else {
    // Combine sample data with transformed data for demo purposes
    allItems.value = [...transformedData, ...apply]
  }

  loading.value = false
}

const editItem = (itemId: string) => {
  router.push(`/grants/edit?id=${itemId}`)
}

const deleteItem = (itemId: string) => {
  if (confirm(`確定要刪除案號 ${itemId} 的申請案件嗎？`)) {
    try {
      // Remove from localStorage
      GrantStorage.removeGrant(itemId)
      // Also remove from UI
      allItems.value = allItems.value.filter(item => item.id !== itemId)
    } catch (error) {
      console.error('Failed to delete grant:', error)
    }
  }
}

// Load data when component is mounted
onMounted(() => {
  loadAllItems()
})
</script>

<style scoped>
/* 添加背景圖片樣式 */
.grants-container {
  background-image: url('@/assets/bg_index.png');
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
  padding: 0 16px !important;
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
  padding-left: 16px;
}

/* 表格區域樣式 */
.table-card {
  border-radius: 12px;
  overflow: hidden;
}

/* 表格樣式 */
.grants-table :deep(thead th) {
  background-color: #62b7bb30 !important;
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
