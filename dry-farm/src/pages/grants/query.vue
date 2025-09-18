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

            <v-card-text class="pa-8">
              <!-- 查詢條件區域 -->
              <div class="query-section mb-8">
                <div class="section-header mb-6">
                  <div class="section-line" />
                  <h3 class="section-title">
                    查詢條件
                  </h3>
                </div>

                <v-row class="query-fields">
                  <v-col
                    cols="12"
                    md="6"
                    class="query-field"
                  >
                    <div class="field-layout">
                      <div class="field-label">
                        查詢年度 *
                      </div>
                      <div class="field-control">
                        <v-select
                          v-model="searchFilters.year"
                          :items="yearOptions"
                          density="comfortable"
                          variant="outlined"
                          hide-details
                          placeholder="請選擇年度"
                          clearable
                          bg-color="white"
                          rounded="lg"
                        />
                      </div>
                    </div>
                  </v-col>

                  <v-col
                    cols="12"
                    md="6"
                    class="query-field"
                  >
                    <div class="field-layout">
                      <div class="field-label">
                        案件編號範圍
                      </div>
                      <div class="field-control">
                        <div class="d-flex gap-2 align-center">
                          <v-text-field
                            v-model="searchFilters.caseNumberStart"
                            density="comfortable"
                            variant="outlined"
                            hide-details
                            placeholder="起始編號"
                            bg-color="white"
                            rounded="lg"
                          />
                          <span class="text-body-2 text-medium-emphasis">~</span>
                          <v-text-field
                            v-model="searchFilters.caseNumberEnd"
                            density="comfortable"
                            variant="outlined"
                            hide-details
                            placeholder="結束編號"
                            bg-color="white"
                            rounded="lg"
                          />
                        </div>
                      </div>
                    </div>
                  </v-col>
                </v-row>
              </div>

              <!-- 檔案選擇區域 -->
              <div class="download-section">
                <div class="section-header mb-6">
                  <div class="section-line" />
                  <h3 class="section-title">
                    選擇要下載的檔案類型
                  </h3>
                  <div class="section-hint text-caption text-medium-emphasis ml-auto">
                    請選擇一種檔案類型，系統將收集所有符合條件的案件檔案
                  </div>
                </div>

                <!-- 優雅的檔案選擇區域 -->
                <v-radio-group
                  v-model="selectedFileType"
                  class="elegant-file-selection"
                >
                  <v-row
                    class="file-categories-row"
                    no-gutters
                  >
                    <v-col
                      v-for="category in fileCategories"
                      :key="category.name"
                      cols="12"
                      sm="6"
                      md="3"
                    >
                      <div class="category-card-elegant">
                        <!-- 類別標題 -->
                        <div class="category-header-elegant">
                          <div class="category-title-elegant">
                            {{ category.name }}
                          </div>
                        </div>

                        <!-- 檔案選項 -->
                        <div class="file-options-elegant">
                          <div
                            v-for="file in category.files"
                            :key="file.id"
                            :class="['file-tile-elegant', { 'selected': selectedFileType === file.id }]"
                            @click="selectedFileType = file.id"
                          >
                            <v-radio
                              :value="file.id"
                              color="#3ea0a3"
                              class="file-radio-hidden"
                              hide-details
                            />
                            <div class="file-content-tile">
                              <div class="file-name-tile">
                                {{ file.title }}
                              </div>
                              <div class="file-badge-tile">
                                <span
                                  class="format-tag-tile"
                                  :class="file.format.toLowerCase()"
                                >
                                  {{ file.format }}
                                </span>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </v-col>
                  </v-row>
                </v-radio-group>
              </div>

              <!-- 操作按鈕區域 -->
              <div class="action-section mt-8 pb-0">
                <div class="d-flex justify-center gap-4">
                  <v-btn
                    color="#3ea0a3"
                    size="x-large"
                    variant="flat"
                    rounded="lg"
                    min-width="160"
                    :disabled="!selectedFileType || !searchFilters.year"
                    :loading="downloading"
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
      persistent
    >
      <v-card rounded="lg">
        <v-card-title class="text-h6 pa-6 pb-2">
          <v-icon
            icon="mdi-download"
            color="#3ea0a3"
            class="mr-2"
          />
          檔案下載中
        </v-card-title>

        <v-card-text class="pa-6">
          <div class="text-center">
            <v-progress-circular
              :model-value="downloadProgress"
              size="64"
              width="4"
              color="#3ea0a3"
              class="mb-4"
            >
              {{ Math.round(downloadProgress) }}%
            </v-progress-circular>
            <div class="text-body-1 mb-2">
              {{ downloadStatus }}
            </div>
            <div class="text-caption text-medium-emphasis">
              正在準備 {{ getSelectedFileName() }} 檔案...
            </div>
          </div>
        </v-card-text>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script lang="ts" setup>
import { ref, onMounted } from 'vue'

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

// 選中的檔案類型
const selectedFileType = ref<string | null>('survey_record')

// 搜尋篩選條件
const searchFilters = ref({
  year: '114' as string | null, // 預設選取114年度
  caseNumberStart: '',
  caseNumberEnd: '',
  applicantName: '',
  status: null as string | null,
})

// 年度選項
const yearOptions = [
  { title: '114', value: '114' },
  { title: '113', value: '113' },
  { title: '112', value: '112' },
  { title: '111', value: '111' },
  { title: '110', value: '110' },
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
  // { id: 'survey_record', title: '現場勘查紀錄表', category: 'A. 勘查審查類', format: 'XLS', formatColor: '#4CAF50', apiEndpoint: '/api/files/survey-record' },
  { id: 'photograph_carry_form', title: '外出拍攝照片攜帶表', category: 'A. 勘查審查類', format: 'XLS', formatColor: '#4CAF50', apiEndpoint: '/api/files/photograph-carry-form' },
  { id: 'construction_photos', title: '施工前後照片', category: 'A. 勘查審查類', format: 'PDF', formatColor: '#f44336', apiEndpoint: '/api/files/construction-photos' },
  { id: 'review_form', title: '書面審查表', category: 'A. 勘查審查類', format: 'PDF', formatColor: '#f44336', apiEndpoint: '/api/files/review-form' },
  { id: 'site_investigation_report', title: '功能測試現地勘查報告書', category: 'A. 勘查審查類', format: 'PDF', formatColor: '#f44336', apiEndpoint: '/api/files/site-investigation-report' },

  // B. 經費與預算類
  { id: 'budget_book', title: '工程預算書', category: 'B. 經費與預算類', format: 'PDF', formatColor: '#f44336', apiEndpoint: '/api/files/budget-book' },
  { id: 'subsidy_details_list', title: '管路補助金額明細表', category: 'B. 經費與預算類', format: 'XLS', formatColor: '#4CAF50', apiEndpoint: '/api/files/subsidy-details-list' },
  { id: 'subsidy_list', title: '印領清冊', category: 'B. 經費與預算類', format: 'PDF', formatColor: '#f44336', apiEndpoint: '/api/files/subsidy-list' },
  { id: 'payment_receipt', title: '領款收據', category: 'B. 經費與預算類', format: 'PDF', formatColor: '#f44336', apiEndpoint: '/api/files/payment-receipt' },

  // C. 設計與地籍類
  { id: 'system_facility_design_drawings', title: '管路灌溉系統設施設計表', category: 'C. 設計與地籍類', format: 'XLS', formatColor: '#4CAF50', apiEndpoint: '/api/files/system-facility-design-drawings' },
  { id: 'farm_lands_list', title: '土地清冊', category: 'C. 設計與地籍類', format: 'XLS', formatColor: '#4CAF50', apiEndpoint: '/api/files/farm-lands-list' },

  // D. 其他
  { id: 'address_labels', title: '住址標籤', category: 'D. 其他', format: 'XLS', formatColor: '#4CAF50', apiEndpoint: '/api/files/address-labels' },
  { id: 'cover_page', title: '封面', category: 'D. 其他', format: 'PDF', formatColor: '#f44336', apiEndpoint: '/api/files/cover-page' },
  { id: 'documents_package', title: '切結書、收據、結案申報書', category: 'D. 其他', format: 'PDF', formatColor: '#f44336', apiEndpoint: '/api/files/documents-package' }
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
  const yearOption = yearOptions.find(option => option.value === year)
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
    const progressSteps = [
      { progress: 20, status: '查詢案件資料...' },
      { progress: 40, status: '篩選符合條件的案件...' },
      { progress: 60, status: `收集 ${fileName} 檔案...` },
      { progress: 80, status: '產生下載檔案...' },
      { progress: 100, status: '下載完成！' }
    ]

    for (const step of progressSteps) {
      await new Promise(resolve => setTimeout(resolve, 800))
      downloadProgress.value = step.progress
      downloadStatus.value = step.status
    }

    // 呼叫專屬 API 端點
    const downloadParams = {
      year: searchFilters.value.year,
      caseNumberStart: searchFilters.value.caseNumberStart || null,
      caseNumberEnd: searchFilters.value.caseNumberEnd || null,
      fileType: selectedFileType.value
    }

    console.log(`下載 ${fileName}:`, apiEndpoint, downloadParams)

    // TODO: 實際 API 呼叫
    // const response = await fetch(apiEndpoint, {
    //   method: 'POST',
    //   headers: { 'Content-Type': 'application/json' },
    //   body: JSON.stringify(downloadParams)
    // })
    // 處理下載響應...

    await new Promise(resolve => setTimeout(resolve, 1000))

  } catch (error) {
    console.error('下載失敗:', error)
    downloadStatus.value = '下載失敗，請稍後再試'
  } finally {
    downloading.value = false
    downloadDialog.value = false
  }
}

// 組件載入時初始化
onMounted(() => {
  console.log('申請案件查詢與列印頁面已載入')
})

// 組件載入時初始化
onMounted(() => {
  console.log('申請案件查詢與列印頁面已載入')
  console.log('支援的檔案類型:', allFiles.value.length, '種')
  console.log('按類別分組:', fileCategories.value.length, '類')
  console.log('預設選中:', getSelectedFileName())
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

.field-control {
  flex: 1;
}

/* 檔案下載區域樣式 */
.download-section {
  margin-bottom: 3rem;
}

.section-hint {
  font-style: italic;
}

/* 優雅檔案選擇設計 */
.elegant-file-selection {
  margin-top: 1.5rem;
}

.file-categories-row {
  gap: 1rem;
  margin: 0;
}

.category-card-elegant {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: linear-gradient(145deg, #ffffff 0%, #f8f9fa 100%);
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  overflow: hidden;
  margin: 0.5rem;
}

.category-card-elegant:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(62, 160, 163, 0.15);
}

/* 類別標題區域 */
.category-header-elegant {
  background: linear-gradient(135deg, #3ea0a3 0%, #2d8c8f 100%);
  color: white;
  padding: 1rem;
  text-align: center;
  position: relative;
}

.category-title-elegant {
  font-size: 0.9rem;
  font-weight: 600;
  margin: 0;
  letter-spacing: 0.5px;
}

/* 檔案選項區域 */
.file-options-elegant {
  padding: 1rem;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

/* 檔案瓷磚設計 */
.file-tile-elegant {
  position: relative;
  padding: 0.75rem;
  border-radius: 8px;
  border: 2px solid transparent;
  background-color: rgba(248, 249, 250, 0.6);
  cursor: pointer;
  transition: all 0.25s ease;
  min-height: 70px;
  display: flex;
  align-items: center;
}

.file-tile-elegant:hover {
  background-color: rgba(62, 160, 163, 0.08);
  border-color: rgba(62, 160, 163, 0.3);
  transform: translateX(2px);
  box-shadow: 0 2px 8px rgba(62, 160, 163, 0.15);
}

.file-tile-elegant.selected {
  background: linear-gradient(135deg, rgba(62, 160, 163, 0.1) 0%, rgba(62, 160, 163, 0.05) 100%);
  border-color: #3ea0a3;
  box-shadow: 0 2px 12px rgba(62, 160, 163, 0.2);
}

.file-tile-elegant.selected::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  background: linear-gradient(to bottom, #3ea0a3, #2d8c8f);
  border-radius: 0 4px 4px 0;
}

/* 隱藏的 radio 按鈕 */
.file-radio-hidden {
  position: absolute;
  opacity: 0;
  pointer-events: none;
}

/* 檔案內容 */
.file-content-tile {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  padding-left: 1rem;
}

.file-name-tile {
  color: #2c3e50;
  font-size: 0.85rem;
  line-height: 1.3;
  font-weight: 500;
  flex: 1;
}

.file-badge-tile {
  margin-left: 0.5rem;
}

.format-tag-tile {
  display: inline-block;
  padding: 3px 8px;
  border-radius: 6px;
  font-size: 0.7rem;
  font-weight: 600;
  letter-spacing: 0.5px;
  text-transform: uppercase;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.format-tag-tile.xls {
  background: linear-gradient(135deg, #4CAF50, #45a049);
  color: white;
}

.format-tag-tile.pdf {
  background: linear-gradient(135deg, #f44336, #e53935);
  color: white;
}

.file-info {
  min-height: 80px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.file-title {
  color: #2c3e50;
  line-height: 1.3;
  margin-bottom: 4px;
}

.file-category {
  color: #6c757d;
  margin-bottom: 8px;
  font-weight: 500;
}

.file-format {
  margin-top: auto;
}

/* 操作按鈕區域樣式 */
.action-section {
  text-align: center;
  padding: 2rem 0;
  border-top: 1px solid #e9ecef;
}

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

  .file-categories-row {
    gap: 0.5rem;
  }

  .category-card-elegant {
    margin: 0.25rem;
  }

  .category-header-elegant {
    padding: 0.75rem;
  }

  .file-options-elegant {
    padding: 0.75rem;
    gap: 0.4rem;
  }

  .file-tile-elegant {
    padding: 0.6rem;
    min-height: 60px;
  }

  .file-content-tile {
    padding-left: 0.5rem;
  }
}

@media (max-width: 600px) {
  .section-card {
    padding: 1rem !important;
  }

  .custom-title {
    min-width: 200px;
  }

  .elegant-file-selection {
    margin-top: 1rem;
  }

  .category-card-elegant {
    margin: 0.125rem;
  }

  .category-title-elegant {
    font-size: 0.8rem;
  }

  .file-name-elegant {
    font-size: 0.75rem;
    line-height: 1.3;
  }

  .file-options-elegant {
    padding: 0.5rem;
    gap: 0.3rem;
  }

  .file-tile-elegant {
    padding: 0.5rem;
    min-height: 50px;
  }

  .file-name-tile {
    font-size: 0.75rem;
  }

  .format-tag-tile {
    font-size: 0.6rem;
    padding: 2px 6px;
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
