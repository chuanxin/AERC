<template>
  <v-container
    fluid
    class="grants-query-container px-6 pb-0 pt-11"
    style="background-color: white"
  >
    <!-- 標題區域 -->
    <v-row justify="center">
      <v-col
        cols="10"
        lg="8"
        align-self="center"
        class="pt-0"
      >
        <div class="section-wrapper">
          <v-card
            class="mx-auto section-card pa-6"
            variant="outlined"
            rounded="lg"
          >
            <v-card-item class="custom-title">
              <v-card-title class="text-h5 font-weight-black">
                申請案件查詢與列印
              </v-card-title>
            </v-card-item>

            <v-card-text class="pa-2">
              <!-- 查詢條件區域 -->
              <div class="query-section">
                <div class="section-header">
                  <div class="section-line" />
                  <h3 class="section-title">
                    查詢條件
                  </h3>
                </div>

                <v-row class="query-fields">
                  <v-col
                    cols="12"
                    md="4"
                    class="query-field"
                  >
                    <div class="field-layout">
                      <div class="field-label">
                        查詢年度 *
                      </div>
                      <div class="field-control">
                        <v-combobox
                          v-model="searchFilters.year"
                          :items="yearOptions"
                          item-title="title"
                          item-value="value"
                          density="comfortable"
                          variant="outlined"
                          hide-details
                          placeholder="請選擇年度"
                          clearable
                          bg-color="white"
                          rounded="lg"
                          autocomplete="off"
                        />
                      </div>
                    </div>
                  </v-col>

                  <v-col
                    cols="12"
                    md="8"
                    class="query-field"
                  >
                    <div class="field-layout">
                      <div class="field-label-with-icon">
                        <span class="field-label">案件編號範圍</span>
                        <v-tooltip
                          location="top"
                          max-width="320"
                        >
                          <template #activator="{ props }">
                            <v-icon
                              v-bind="props"
                              icon="mdi-help-circle-outline"
                              size="18"
                              color="grey-darken-1"
                              class="ml-1"
                            />
                          </template>
                          <div class="case-number-tooltip">
                            <div class="tooltip-title">
                              案件編號格式說明
                            </div>
                            <div class="tooltip-section">
                              <strong>新系統格式：</strong>年度+單位代碼+流水號
                              <br>例：11401001, 11402015
                            </div>
                            <div class="tooltip-section">
                              <strong>舊系統格式：</strong>純流水號
                              <br>例：1, 100, 923
                            </div>
                            <div class="tooltip-note">
                              💡 系統使用數值區間查詢，純數字編號按數值大小排序
                            </div>
                          </div>
                        </v-tooltip>
                      </div>
                      <div class="field-control">
                        <div class="d-flex gap-2 align-center">
                          <v-text-field
                            v-model="searchFilters.caseNumberStart"
                            density="comfortable"
                            variant="outlined"
                            hide-details="auto"
                            placeholder="起始編號"
                            bg-color="white"
                            rounded="lg"
                            autocomplete="off"
                            :rules="caseNumberRules"
                          >
                            <template #append-inner>
                              <v-menu
                                v-model="showCaseNumberExamples"
                                :close-on-content-click="false"
                                location="bottom"
                              >
                                <template #activator="{ props }">
                                  <v-btn
                                    v-bind="props"
                                    icon="mdi-lightbulb-outline"
                                    size="small"
                                    variant="text"
                                    color="grey-darken-1"
                                  />
                                </template>
                                <v-card
                                  class="case-number-examples-card"
                                  max-width="280"
                                >
                                  <v-card-title class="text-subtitle-1 pa-3 pb-2">
                                    常見編號範例
                                  </v-card-title>
                                  <v-card-text class="pa-3 pt-0">
                                    <div class="examples-list">
                                      <div
                                        v-for="example in caseNumberExamples"
                                        :key="example.type"
                                        class="example-item"
                                        @click="applyCaseNumberExample(example)"
                                      >
                                        <div class="example-type">
                                          {{ example.type }}
                                        </div>
                                        <div class="example-range">
                                          {{ example.start }} ~ {{ example.end }}
                                        </div>
                                        <div class="example-desc">
                                          {{ example.description }}
                                        </div>
                                      </div>
                                    </div>
                                  </v-card-text>
                                </v-card>
                              </v-menu>
                            </template>
                          </v-text-field>
                          <span class="text-body-2 text-medium-emphasis">~</span>
                          <v-text-field
                            v-model="searchFilters.caseNumberEnd"
                            density="comfortable"
                            variant="outlined"
                            hide-details="auto"
                            placeholder="結束編號"
                            bg-color="white"
                            rounded="lg"
                            autocomplete="off"
                            :rules="caseNumberRules"
                          />
                        </div>

                        <!-- 範圍輸入提示 -->
                        <div
                          v-if="getCaseNumberFormatHint()"
                          class="case-number-hint mt-2"
                        >
                          <v-icon
                            icon="mdi-information-outline"
                            size="14"
                            :color="getCaseNumberHintColor()"
                            class="mr-1"
                          />
                          <span :class="getCaseNumberHintClass()">
                            {{ getCaseNumberFormatHint() }}
                          </span>
                        </div>
                      </div>
                    </div>
                  </v-col>
                </v-row>
              </div>

              <!-- 檔案選擇區域 -->
              <div class="download-section">
                <div class="section-header">
                  <div class="section-line" />
                  <h3 class="section-title">
                    選擇要下載的檔案類型
                  </h3>
                  <div class="text-caption text-medium ml-auto">
                    請選擇一種檔案類型，系統將收集所有符合條件的案件檔案
                  </div>
                  <v-btn
                    :icon="isFileSelectionExpanded ? 'mdi-fullscreen-exit' : 'mdi-fullscreen'"
                    size="small"
                    variant="text"
                    color="#3ea0a3"
                    class="ml-2"
                    @click="toggleFileSelectionExpansion"
                  />
                </div>

                <v-card
                  class="file-selection-card"
                  :class="{ 'expanded': isFileSelectionExpanded }"
                  variant="flat"
                  rounded="none"
                >
                  <div
                    class="file-selection-scroll-container"
                    :class="{ 'expanded': isFileSelectionExpanded }"
                  >
                    <v-radio-group
                      v-model="selectedFileType"
                      class="ma-0"
                    >
                      <template
                        v-for="category in fileCategories"
                        :key="category.name"
                      >
                        <!-- Vuetify Sticky 群組標題 -->
                        <v-sheet
                          class="category-sticky-header"
                          color="rgba(248, 249, 250, 0.95)"
                          elevation="0"
                        >
                          <div class="d-flex align-center pa-4">
                            <v-icon
                              :color="category.color"
                              size="22"
                              class="mr-3"
                            >
                              {{ category.icon }}
                            </v-icon>
                            <span class="text-subtitle-1 font-weight-bold text-grey-darken-2">
                              {{ category.name }}
                            </span>
                            <v-spacer />
                            <v-chip
                              size="small"
                              :color="category.color"
                              variant="tonal"
                              class="font-weight-medium"
                            >
                              {{ category.files.length }}
                            </v-chip>
                          </div>
                        </v-sheet>

                        <!-- Vuetify 檔案列表 -->
                        <v-list
                          class="file-list-container"
                          density="comfortable"
                          bg-color="transparent"
                        >
                          <v-list-item
                            v-for="file in category.files"
                            :key="file.id"
                            class="file-list-item"
                            @click="selectedFileType = file.id"
                          >
                            <template #prepend>
                              <v-radio
                                :model-value="selectedFileType"
                                :value="file.id"
                                color="#3ea0a3"
                                hide-details
                              />
                            </template>

                            <v-list-item-title class="file-item-title">
                              {{ file.title }}
                            </v-list-item-title>

                            <template #append>
                              <v-chip
                                size="x-small"
                                :color="file.formatColor"
                                variant="flat"
                                class="ml-2"
                              >
                                {{ file.format }}
                              </v-chip>
                            </template>
                          </v-list-item>
                        </v-list>
                      </template>
                    </v-radio-group>
                  </div>
                </v-card>
              </div>

              <!-- 操作按鈕區域 -->
              <div class="action-section pb-0">
                <div class="d-flex justify-center">
                  <v-btn
                    color="#3ea0a3"
                    size="x-large"
                    variant="flat"
                    rounded="lg"
                    min-width="160"
                    :disabled="isDownloadDisabled()"
                    :loading="downloading || checkingData"
                    @click="handleDownload"
                  >
                    <v-icon
                      left
                      class="mr-2"
                    >
                      mdi-download
                    </v-icon>
                    下載檔案
                  </v-btn>
                </div>

                <!-- 選取資訊提示 -->
                <div class="selection-info mt-4 text-center">
                  <div
                    v-if="selectedFileType && searchFilters.year"
                    class="text-body-2 text-medium-emphasis"
                  >
                    將下載：<strong>{{ getSelectedFileName() }}</strong>
                    <span>· {{ getYearDisplay(searchFilters.year) }}</span>
                    <span v-if="getCaseNumberRange()">· 案號範圍：{{ getCaseNumberRange() }}</span>
                  </div>
                  <div
                    v-else
                    class="text-body-2 text-medium-emphasis"
                  >
                    請選擇查詢年度和檔案類型
                  </div>

                  <!-- 資料可用性狀態 -->
                  <div
                    v-if="dataAvailability"
                    class="data-status mt-2"
                  >
                    <div
                      v-if="dataAvailability.has_data"
                      class="text-caption text-success"
                    >
                      ✓ 找到 {{ dataAvailability.total_count }} 筆符合條件的案件
                    </div>
                    <div
                      v-else
                      class="text-caption text-warning"
                    >
                      ⚠ {{ dataAvailability.message }}
                    </div>
                  </div>

                  <div
                    v-if="checkingData"
                    class="text-caption text-medium-emphasis mt-2"
                  >
                    <v-progress-circular
                      size="12"
                      width="2"
                      indeterminate
                      class="mr-1"
                    />
                    檢查資料中...
                  </div>
                </div>
              </div>
            </v-card-text>
          </v-card>
        </div>
      </v-col>
    </v-row>

    <!-- 下載進度對話框 -->
    <v-dialog
      v-model="downloadDialog"
      max-width="500px"
      :persistent="downloading"
    >
      <v-card rounded="lg">
        <v-card-title class="text-h6 pa-6 pb-2">
          <v-icon
            :icon="downloading ? 'mdi-download' : (downloadProgress === 100 ? 'mdi-check-circle' : 'mdi-alert-circle')"
            :color="downloading ? '#3ea0a3' : (downloadProgress === 100 ? 'success' : 'error')"
            class="mr-2"
          />
          {{ downloading ? '檔案下載中' : (downloadProgress === 100 ? '下載完成' : '下載失敗') }}
        </v-card-title>

        <v-card-text class="pa-6">
          <div class="text-center">
            <v-progress-circular
              v-if="downloading || downloadProgress === 100"
              :model-value="downloadProgress"
              size="64"
              width="4"
              :color="downloadProgress === 100 ? 'success' : '#3ea0a3'"
              class="mb-4"
            >
              {{ Math.round(downloadProgress) }}%
            </v-progress-circular>

            <v-icon
              v-else
              icon="mdi-alert-circle-outline"
              color="error"
              size="64"
              class="mb-4"
            />

            <div class="text-body-1 mb-2">
              {{ downloadStatus }}
            </div>

            <div
              v-if="downloading"
              class="text-caption text-medium-emphasis"
            >
              正在準備 {{ getSelectedFileName() }} 檔案...
            </div>
          </div>
        </v-card-text>

        <!-- 操作按鈕 -->
        <v-card-actions
          v-if="!downloading"
          class="pa-6 pt-0"
        >
          <v-spacer />
          <v-btn
            v-if="downloadProgress !== 100"
            color="#3ea0a3"
            variant="flat"
            @click="handleDownload"
          >
            重新下載
          </v-btn>
          <v-btn
            color="grey-darken-1"
            variant="text"
            @click="downloadDialog = false"
          >
            關閉
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script lang="ts" setup>
import { ref, onMounted, watch } from 'vue'
import { downloadsService } from '@/services/downloadsService'
import type { DownloadRequest, DataCheckResponse } from '@/services/downloadsService'
import { useUserStore } from '@/stores/users' //added by Joya
// 定義檔案項目介面
interface FileOption {
  id: string
  title: string
  category: string
  format: string
  formatColor: string
  apiEndpoint: string
}

// 響應式資料
const downloading = ref(false)
const downloadDialog = ref(false)
const downloadProgress = ref(0)
const downloadStatus = ref('')
const dataAvailability = ref<DataCheckResponse | null>(null)
const checkingData = ref(false)
const showCaseNumberExamples = ref(false)

// 檔案選擇區域展開狀態
const isFileSelectionExpanded = ref(false)

// 選中的檔案類型
const selectedFileType = ref<string | null>('photograph_carry_form')

// 搜尋篩選條件
const searchFilters = ref({
  year: null as string | null,
  caseNumberStart: '',
  caseNumberEnd: '',
  applicantName: '',
  status: null as string | null,
})

// 年度選項（97 年起到當前民國年，降序）
const yearOptions = computed(() => {
  const currentRocYear = new Date().getFullYear() - 1911
  const years = []
  for (let y = currentRocYear; y >= 97; y--) {
    years.push({ title: String(y), value: String(y) })
  }
  return years
})

const userStore = useUserStore(); //added by Joya
const currentOfficeId = computed(() => {
  return userStore.currentUser?.office?.id
})
// 案件編號範例
const caseNumberExamples = ref([
  {
    type: '新系統 - 全部',
    start: '115010001',
    end: '115999999',
    description: '115年度所有單位'
  },
  {
    type: '新系統 - 各管理處案件',
    start: '115010001',
    end: '115019999',
    description: '115年度宜蘭管理處案件'
  },
  {
    type: '舊系統 - 流水號表示方式',
    start: '1',
    end: '199999999',
    description: '編號1到199999999'
  }
])

// 案件編號驗證規則
const caseNumberRules = [
  (value: string) => {
    if (!value) return true // 允許空值
    // 基本格式檢查：允許數字、字母、連字號
    if (!/^[A-Za-z0-9-]+$/.test(value)) {
      return '案件編號只能包含英文字母、數字和連字號'
    }
    return true
  }
]

// 定義檔案分類介面
interface FileCategory {
  name: string
  color: string
  icon: string
  files: FileOption[]
}

// 所有檔案選項
const allFiles = ref<FileOption[]>([
  // A. 勘查審查類
  // { id: 'survey_record', title: '現場勘查紀錄表', category: 'A. 勘查審查類', format: 'XLS', formatColor: '#4CAF50', apiEndpoint: '/api/download/survey-record' },
  { id: 'photograph_carry_form', title: '外出拍攝照片攜帶表', category: 'A. 勘查審查類', format: 'XLSX', formatColor: '#4CAF50', apiEndpoint: '/api/download/photograph-carry-form' },
  { id: 'construction_photos', title: '施工前後照片', category: 'A. 勘查審查類', format: 'PDF', formatColor: '#f44336', apiEndpoint: '/api/download/construction-photos' },
  { id: 'review_form', title: '書面審查表', category: 'A. 勘查審查類', format: 'PDF', formatColor: '#f44336', apiEndpoint: '/api/download/review-form' },
  { id: 'site_investigation_report', title: '功能測試現地勘查報告書', category: 'A. 勘查審查類', format: 'PDF', formatColor: '#f44336', apiEndpoint: '/api/download/site-investigation-report' },

  // B. 經費與預算類
  { id: 'budget_book', title: '工程預算書', category: 'B. 經費與預算類', format: 'PDF', formatColor: '#f44336', apiEndpoint: '/api/download/budget-book' },
  { id: 'subsidy_details_list', title: '管路補助金額明細表', category: 'B. 經費與預算類', format: 'XLSX', formatColor: '#4CAF50', apiEndpoint: '/api/download/subsidy-details-list' },
  { id: 'subsidy_list', title: '印領清冊', category: 'B. 經費與預算類', format: 'XLSX', formatColor: '#4CAF50', apiEndpoint: '/api/download/subsidy-list' },
  { id: 'receipts', title: '領款收據', category: 'B. 經費與預算類', format: 'PDF', formatColor: '#f44336', apiEndpoint: '/api/download/receipts' },

  // C. 設計與地籍類
  { id: 'system_facility_design_drawings', title: '管路灌溉系統設施設計表', category: 'C. 設計與地籍類', format: 'XLSX', formatColor: '#4CAF50', apiEndpoint: '/api/download/system-facility-design-drawings' },
  { id: 'farm_lands_list', title: '土地清冊', category: 'C. 設計與地籍類', format: 'XLSX', formatColor: '#4CAF50', apiEndpoint: '/api/download/farm-lands-list' },

  // D. 其他
  { id: 'address_labels', title: '住址標籤', category: 'D. 其他', format: 'XLSX', formatColor: '#4CAF50', apiEndpoint: '/api/download/address-labels' },
  { id: 'cover_page', title: '封面', category: 'D. 其他', format: 'PDF', formatColor: '#f44336', apiEndpoint: '/api/download/cover-page' },
  { id: 'closing_docs', title: '切結書、收據、結案申報書', category: 'D. 其他', format: 'PDF', formatColor: '#f44336', apiEndpoint: '/api/download/closing-docs' }
])

// 按類別分組的檔案
const fileCategories = ref<FileCategory[]>([
  {
    name: 'A. 勘查審查類',
    color: '#2196F3',
    icon: 'mdi-clipboard-search',
    files: allFiles.value.filter(f => f.category === 'A. 勘查審查類')
  },
  {
    name: 'B. 經費與預算類',
    color: '#4CAF50',
    icon: 'mdi-calculator',
    files: allFiles.value.filter(f => f.category === 'B. 經費與預算類')
  },
  {
    name: 'C. 設計與地籍類',
    color: '#9C27B0',
    icon: 'mdi-drawing',
    files: allFiles.value.filter(f => f.category === 'C. 設計與地籍類')
  },
  {
    name: 'D. 其他',
    color: '#FF9800',
    icon: 'mdi-file-document',
    files: allFiles.value.filter(f => f.category === 'D. 其他')
  }
])

// 工具函數：取得年度顯示名稱
const getYearDisplay = (year: string | null) => {
  if (!year) return ''
  const yearOption = yearOptions.value.find((option: { title: string; value: string }) => option.value === year)
  return yearOption ? `${yearOption.title}年度` : year
}

// 工具函數：取得案件編號範圍顯示
const getCaseNumberRange = () => {
  const start = searchFilters.value.caseNumberStart
  const end = searchFilters.value.caseNumberEnd

  if (start && end) {
    return `${start} ~ ${end}`
  } else if (start) {
    return `${start} ~`
  } else if (end) {
    return `~ ${end}`
  }
  return ''
}

// 取得選中檔案名稱
const getSelectedFileName = () => {
  const selectedFile = allFiles.value.find(file => file.id === selectedFileType.value)
  return selectedFile?.title || ''
}

// 取得選中檔案的 API 端點
const getSelectedFileEndpoint = () => {
  const selectedFile = allFiles.value.find(file => file.id === selectedFileType.value)
  return selectedFile?.apiEndpoint || ''
}

// 切換檔案選擇區域展開狀態
const toggleFileSelectionExpansion = () => {
  isFileSelectionExpanded.value = !isFileSelectionExpanded.value
}

// 檢查資料可用性
const checkDataAvailability = async () => {
  if (!selectedFileType.value || !searchFilters.value.year) {
    dataAvailability.value = null
    return
  }

  checkingData.value = true
  try {
    const params = {
      year: searchFilters.value.year,
      case_number_start: searchFilters.value.caseNumberStart || null,
      case_number_end: searchFilters.value.caseNumberEnd || null,
      file_type: selectedFileType.value,
      office_id: currentOfficeId.value //added by Joya
    }

    console.log('檢查資料可用性 - 請求參數:', params)
    dataAvailability.value = await downloadsService.checkDataAvailability(params)
    console.log('檢查資料可用性 - 回應:', dataAvailability.value)
  } catch (error) {
    console.error('檢查資料可用性失敗 - 詳細錯誤:', error)
    console.error('錯誤類型:', typeof error)
    console.error('錯誤內容:', error)

    // 提供更詳細的錯誤訊息
    let errorMessage = '無法檢查資料狀態'
    if (error && typeof error === 'object') {
      if ('message' in error) {
        errorMessage = `檢查失敗: ${error.message}`
      } else if ('response' in error && error.response) {
        errorMessage = `API 錯誤: ${error.response.status} ${error.response.statusText || ''}`
      }
    }

    dataAvailability.value = {
      has_data: false,
      total_count: 0,
      message: errorMessage
    }
  } finally {
    checkingData.value = false
  }
}

// 計算下載按鈕是否應該禁用
const isDownloadDisabled = () => {
  if (!selectedFileType.value || !searchFilters.value.year) return true
  if (checkingData.value) return true
  if (dataAvailability.value === null) return true
  return !dataAvailability.value.has_data
}

// 應用案件編號範例
const applyCaseNumberExample = (example: typeof caseNumberExamples.value[0]) => {
  searchFilters.value.caseNumberStart = example.start
  searchFilters.value.caseNumberEnd = example.end
  showCaseNumberExamples.value = false
}

// 取得案件編號格式提示
const getCaseNumberFormatHint = () => {
  const start = searchFilters.value.caseNumberStart
  const end = searchFilters.value.caseNumberEnd

  if (!start && !end) return ''

  // 檢查格式一致性
  if (start && end) {
    const startIsNewFormat = /^\d{9}$/.test(start) // 9位數字格式
    const endIsNewFormat = /^\d{9}$/.test(end)

    if (startIsNewFormat && endIsNewFormat) {
      const startYear = start.substring(0, 3)
      const endYear = end.substring(0, 3)
      if (startYear !== endYear) {
        return '⚠️ 起始和結束編號的年度不一致'
      }
      return '✓ 新系統格式，將依案件編號範圍查詢'
    } else if (!startIsNewFormat && !endIsNewFormat) {
      return '✓ 舊系統格式，將依案件流水編號範圍查詢'
    } else {
      return '⚠️ 起始和結束編號格式不一致，建議使用相同格式'
    }
  } else if (start || end) {
    return '💡 請設置完整的起始和結束範圍'
  }

  return ''
}

// 取得案件編號提示顏色
const getCaseNumberHintColor = () => {
  const hint = getCaseNumberFormatHint()
  if (hint.includes('⚠️')) return '#ff9800' // 橙色警告
  if (hint.includes('✓')) return '#4caf50'   // 綠色成功
  if (hint.includes('💡')) return '#2196f3'  // 藍色資訊
  return '#666666' // 預設灰色
}

// 取得案件編號提示樣式類別
const getCaseNumberHintClass = () => {
  const hint = getCaseNumberFormatHint()
  if (hint.includes('⚠️')) return 'case-number-hint-warning'
  if (hint.includes('✓')) return 'case-number-hint-success'
  if (hint.includes('💡')) return 'case-number-hint-info'
  return 'case-number-hint-default'
}

// 事件處理：執行下載
const handleDownload = async () => {
  if (!selectedFileType.value || !searchFilters.value.year) {
    return
  }

  const fileName = getSelectedFileName()
  const apiEndpoint = getSelectedFileEndpoint()

  downloading.value = true
  downloadDialog.value = true
  downloadProgress.value = 0
  downloadStatus.value = '準備下載...'

  try {
    // 第一階段：準備工作（快速進度）
    downloadProgress.value = 20
    downloadStatus.value = '查詢案件資料...'
    await new Promise(resolve => setTimeout(resolve, 300))

    downloadProgress.value = 40
    downloadStatus.value = '篩選符合條件的案件...'
    await new Promise(resolve => setTimeout(resolve, 300))

    // 準備下載參數
    const downloadParams = {
      year: searchFilters.value.year,
      caseNumberStart: searchFilters.value.caseNumberStart || null,
      caseNumberEnd: searchFilters.value.caseNumberEnd || null,
      fileType: selectedFileType.value,
      office_id: currentOfficeId.value //added by Joya
    }

    console.log(`下載 ${fileName}:`, apiEndpoint, downloadParams)

    const downloadRequest: DownloadRequest = {
      year: downloadParams.year,
      case_number_start: downloadParams.caseNumberStart,
      case_number_end: downloadParams.caseNumberEnd,
      file_type: downloadParams.fileType,
      enable_pagination: true, // 預設啟用分頁
      office_id: downloadParams.office_id //added by Joya
    }

    // 第二階段：實際API調用
    downloadProgress.value = 60
    downloadStatus.value = `正在生成 ${fileName} 檔案...`

    // 根據檔案類型調用對應的服務方法
    switch (selectedFileType.value) {
      case 'photograph_carry_form':
        await downloadsService.downloadPhotographCarryForm(downloadRequest)
        break
      case 'budget_book':
        await downloadsService.downloadBudgetBook(downloadRequest)
        break
      case 'construction_photos':
        await downloadsService.downloadConstructionPhotos(downloadRequest)
        break
      case 'address_labels':
        await downloadsService.downloadAddressLabels(downloadRequest)
        break
      case 'receipts':
        await downloadsService.downloadReceipts(downloadRequest)
        break
      case 'site_investigation_report':
        await downloadsService.downloadTestReports(downloadRequest)
        break
      case 'review_form':
        await downloadsService.downloadReviewForm(downloadRequest)
        break
      case 'cover_page':
        await downloadsService.downloadCoverPage(downloadRequest)
        break
      case 'closing_docs':
        await downloadsService.downloadClosingDocs(downloadRequest)
        break
      default:
        throw new Error(`尚未支援的檔案類型: ${selectedFileType.value}`)
    }

    // 第三階段：檔案已生成並觸發瀏覽器下載
    downloadProgress.value = 90
    downloadStatus.value = '檔案已生成，正在啟動下載...'
    await new Promise(resolve => setTimeout(resolve, 500))

    // 第四階段：完成
    downloadProgress.value = 100
    downloadStatus.value = '檔案已送出，請查看瀏覽器的下載紀錄'

  } catch (error) {
    console.error('下載失敗:', error)
    downloadStatus.value = '下載失敗，請稍後再試'
    downloadProgress.value = 0
    // 不關閉對話框，讓用戶看到錯誤訊息
  } finally {
    downloading.value = false
  }
}

// 正規化 v-combobox 年度值：從選單選取時回傳物件，手動輸入時回傳字串，統一轉為字串
watch(() => searchFilters.value.year, (val) => {
  if (val && typeof val === 'object') {
    searchFilters.value.year = (val as { value: string }).value
  }
})

// 監聽查詢條件改變，自動檢查資料可用性
watch([selectedFileType, () => searchFilters.value.year, () => searchFilters.value.caseNumberStart, () => searchFilters.value.caseNumberEnd],
  () => {
    checkDataAvailability()
  },
  { immediate: true }
)

// 組件載入時初始化
onMounted(() => {
  console.log('申請案件查詢與列印頁面已載入')
  console.log('支援的檔案類型:', allFiles.value.length, '種')
  console.log('按類別分組:', fileCategories.value.length, '類')
  console.log('預設選中:', getSelectedFileName())
  console.log('當前 Office ID:', currentOfficeId.value)
})
</script>

<style scoped>
/* 添加背景圖片樣式 */
.grants-query-container {
  background-image: url('@/assets/bg_index.svg');
  background-size: cover;
  background-position: center bottom;
  background-repeat: no-repeat;
  background-attachment: fixed;
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
  background-color: rgba(255, 255, 255, 0.6) !important;
  backdrop-filter: blur(10px) !important;
  -webkit-backdrop-filter: blur(10px) !important;
  border: 1px solid rgba(255, 255, 255, 0.25) !important;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.05) !important;
}

.section-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08) !important;
  background-color: rgba(255, 255, 255, 0.85) !important;
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
  min-width: 250px;
  height: 50px;
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
}

/* 查詢條件區域樣式 */
.query-section {
  margin-bottom: 3rem;
}

.section-header {
  display: flex;
  align-items: center;
  margin-bottom: 2rem;
}

.section-line {
  width: 4px;
  height: 24px;
  background-color: #3ea0a3;
  margin-right: 12px;
  border-radius: 2px;
}

.section-title {
  color: #2c3e50;
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0;
}

/* 表單欄位佈局 */
.query-field {
  margin-bottom: 1rem;
}

.field-layout {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.field-label {
  min-width: 80px;
  color: #34495e;
  font-weight: 500;
  text-align: right;
}

.field-label-with-icon {
  min-width: 80px;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  text-align: right;
}

.field-control {
  flex: 1;
}

/* 案件編號相關樣式 */
.case-number-tooltip {
  padding: 12px;
}

.tooltip-title {
  font-weight: 600;
  font-size: 0.95rem;
  margin-bottom: 12px;
  color: #1a1a1a;
  border-bottom: 1px solid #e0e0e0;
  padding-bottom: 6px;
}

.tooltip-section {
  margin-bottom: 10px;
  line-height: 1.5;
  color: #424242;
  font-size: 0.9rem;
}

.tooltip-section strong {
  color: #2c3e50;
  font-weight: 600;
}

.tooltip-note {
  padding: 8px 12px;
  background-color: rgba(33, 150, 243, 0.12);
  border-left: 3px solid #2196f3;
  border-radius: 4px;
  font-size: 0.875rem;
  color: #1565c0;
  margin-top: 8px;
}

.case-number-examples-card {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
}

.examples-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.example-item {
  padding: 8px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.example-item:hover {
  background-color: rgba(62, 160, 163, 0.08);
  border-color: #3ea0a3;
}

.example-type {
  font-weight: 600;
  color: #2c3e50;
  font-size: 0.85rem;
}

.example-range {
  font-family: monospace;
  color: #3ea0a3;
  font-size: 0.9rem;
  margin: 2px 0;
}

.example-desc {
  color: #666;
  font-size: 0.8rem;
}

.case-number-hint {
  display: flex;
  align-items: center;
}

/* 案件編號提示文字樣式 */
.case-number-hint-success {
  color: #2e7d32 !important;
  font-weight: 500;
  font-size: 0.875rem;
}

.case-number-hint-warning {
  color: #f57c00 !important;
  font-weight: 500;
  font-size: 0.875rem;
}

.case-number-hint-info {
  color: #1976d2 !important;
  font-weight: 500;
  font-size: 0.875rem;
}

.case-number-hint-default {
  color: #424242 !important;
  font-weight: 500;
  font-size: 0.875rem;
}

.v-tooltip> ::v-deep(.v-overlay__content) {
  background: white;
  color: transparent;
}

/* 檔案下載區域樣式 */
.download-section {
  margin-bottom: 1rem;
}

.section-hint {
  font-style: italic;
}

/* Vuetify 檔案選擇卡片 */
.file-selection-card {
  margin-top: 1rem;
  background-color: rgba(255, 255, 255, 0.9) !important;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  overflow: hidden;
}

/* 滾動容器 - 預設固定高度模式 */
.file-selection-scroll-container {
  height: calc(100vh - 550px);
  min-height: 250px;
  max-height: 450px;
  overflow-y: auto;
  position: relative;
  transition: all 0.3s ease;
}

/* 展開模式 - 依內容高度自動調整 */
.file-selection-scroll-container.expanded {
  height: auto !important;
  min-height: auto !important;
  max-height: none !important;
  overflow-y: visible !important;
}

/* 展開模式下的卡片樣式 */
.file-selection-card.expanded {
  border: 1px solid #e9ecef !important;
  border-radius: 8px !important;
  background-color: rgba(255, 255, 255, 0.8) !important;
}

/* 自定義滾動條樣式 */
.file-selection-scroll-container::-webkit-scrollbar {
  width: 8px;
}

.file-selection-scroll-container::-webkit-scrollbar-track {
  background-color: rgba(248, 249, 250, 0.8);
  border-radius: 4px;
}

.file-selection-scroll-container::-webkit-scrollbar-thumb {
  background-color: rgba(62, 160, 163, 0.6);
  border-radius: 4px;
  transition: background-color 0.2s ease;
}

.file-selection-scroll-container::-webkit-scrollbar-thumb:hover {
  background-color: rgba(62, 160, 163, 0.8);
}

/* Sticky 群組標題 */
.category-sticky-header {
  position: sticky !important;
  top: 0 !important;
  z-index: 10 !important;
  backdrop-filter: blur(10px) !important;
  -webkit-backdrop-filter: blur(10px) !important;
  border-bottom: 2px solid #e9ecef !important;
  margin-bottom: 0 !important;
}

/* 展開模式下的群組標題樣式 */
.file-selection-scroll-container.expanded .category-sticky-header {
  position: relative !important;
  background-color: rgba(248, 249, 250, 0.95) !important;
  border-bottom: 1px solid #f1f3f4 !important;
}

/* 檔案列表容器 */
.file-list-container {
  background-color: transparent !important;
  padding: 0 !important;
}

/* 檔案列表項目 */
.file-list-item {
  border-bottom: 1px solid #f8f9fa !important;
  transition: background-color 0.2s ease;
  min-height: 56px !important;
  padding: 8px 16px !important;
}

.file-list-item:last-child {
  border-bottom: 1px solid #e9ecef !important;
}

.file-list-item:hover {
  background-color: rgba(62, 160, 163, 0.08) !important;
}

/* 展開模式下的檔案列表樣式 */
.file-selection-scroll-container.expanded .file-list-item {
  border-bottom: 1px solid #f8f9fa !important;
  border-radius: 6px !important;
  margin: 2px 8px !important;
  padding: 12px 16px !important;
}

.file-selection-scroll-container.expanded .file-list-item:hover {
  background-color: rgba(62, 160, 163, 0.05) !important;
}

.file-list-item:deep(.v-list-item__prepend) {
  margin-right: 16px !important;
}

.file-list-item:deep(.v-list-item__append) {
  margin-left: 16px !important;
}

/* 檔案標題樣式 */
.file-item-title {
  color: #2c3e50 !important;
  font-size: 0.9rem !important;
  font-weight: 500 !important;
  line-height: 1.4 !important;
}

/* 清理：舊的 HTML 結構樣式已被 Vuetify 組件取代 */

/* 操作按鈕區域樣式 */
/* .action-section {
  text-align: center;
  padding: 1rem 0;
  border-top: 1px solid #e9ecef;
} */

.selection-info {
  margin-top: 1rem;
}

/* 響應式設計 */
@media (max-width: 960px) {
  .field-layout {
    flex-direction: column;
    align-items: flex-start;
  }

  .field-label {
    min-width: auto;
    text-align: left;
    margin-bottom: 0.5rem;
  }

  .section-hint {
    margin-top: 0.5rem;
    text-align: center;
  }

  .category-section {
    margin-bottom: 1.5rem;
  }

  .file-label {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
  }
}

@media (max-width: 600px) {
  .section-card {
    padding: 1rem !important;
  }

  .custom-title {
    min-width: 200px;
  }

  .file-radio-group {
    gap: 0.5rem;
  }

  .category-section {
    padding: 0.75rem;
  }

  .category-title {
    font-size: 0.9rem;
  }

  .file-name {
    font-size: 0.85rem;
  }
}

/* 下載進度對話框樣式 */
.v-dialog .v-card {
  background-color: rgba(255, 255, 255, 0.95) !important;
  backdrop-filter: blur(10px) !important;
}
</style><style scoped>
/* 添加背景圖片樣式 */
.grants-query-container {
  background-image: url('@/assets/bg_index.svg');
  background-size: cover;
  background-position: center bottom;
  background-repeat: no-repeat;
  background-attachment: fixed;
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
  background-color: rgba(255, 255, 255, 0.6) !important;
  backdrop-filter: blur(10px) !important;
  -webkit-backdrop-filter: blur(10px) !important;
  border: 1px solid rgba(255, 255, 255, 0.25) !important;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.05) !important;
}

.section-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08) !important;
  background-color: rgba(255, 255, 255, 0.85) !important;
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
  min-width: 200px;
  height: 50px;
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
}

/* 表格區域樣式 */
.table-card {
  border-radius: 12px;
  overflow: hidden;
}

/* 表格樣式 */
.grants-query-table :deep(thead th) {
  background-color: #e3f4f4 !important;
  color: #333 !important;
  font-weight: 900 !important;
}

.grants-query-table :deep(.v-data-table__tr:hover) {
  background-color: rgba(98, 183, 187, 0.1) !important;
}

.grants-query-table :deep(.v-data-table__tr:nth-child(even)) {
  background-color: rgba(98, 183, 187, 0.05);
}

/* 案件編號晶片樣式 */
.case-number-chip {
  cursor: pointer;
  transition: all 0.2s ease;
}

.case-number-chip:hover {
  transform: scale(1.05);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

/* 按鈕樣式 */
.action-btn {
  background-color: white !important;
  font-weight: 500;
  transition: all 0.2s ease;
}

.action-btn:hover {
  background-color: #3ea0a3 !important;
  color: white !important;
}

/* 篩選區域樣式 */
.filter-select {
  max-width: 200px;
}

/* 下載預覽樣式 */
.download-preview {
  background-color: #fafafa;
  padding: 8px;
  border-radius: 4px;
}

@media (max-width: 600px) {
  .filter-select {
    min-width: 100%;
  }

  .d-flex.gap-2 {
    flex-direction: column;
    gap: 8px;
  }
}
</style>
