<template>
  <v-container
    fluid
    class="downloads-container px-6 pb-0 pt-0"
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
            <v-btn
              class="action-btn"
              color="#3ea0a3"
              prepend-icon="mdi-refresh"
              variant="outlined"
              rounded="lg"
              size="large"
              :loading="refreshing"
              @click="refreshDownloads"
            >
              重新整理
            </v-btn>
            <v-btn
              class="action-btn"
              color="#3ea0a3"
              prepend-icon="mdi-download-multiple"
              variant="outlined"
              rounded="lg"
              size="large"
              :disabled="selectedFiles.length === 0"
              :loading="batchDownloading"
              @click="batchDownload"
            >
              批量下載 {{ selectedFiles.length > 0 ? `(${selectedFiles.length})` : '' }}
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
                文件下載中心
              </v-card-title>
            </v-card-item>

            <v-card-text>
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
                      v-model="selectedCategory"
                      :items="categoryOptions"
                      label="文件類型"
                      density="comfortable"
                      variant="outlined"
                      hide-details
                      class="filter-select mr-2"
                      style="min-width: 150px"
                      clearable
                      bg-color="white"
                      rounded="lg"
                      @update:model-value="applyFilters"
                    />
                    <v-select
                      v-model="selectedFormat"
                      :items="formatOptions"
                      label="檔案格式"
                      density="comfortable"
                      variant="outlined"
                      hide-details
                      class="filter-select mr-2"
                      style="min-width: 120px"
                      clearable
                      bg-color="white"
                      rounded="lg"
                      @update:model-value="applyFilters"
                    />
                    <v-select
                      v-model="selectedDateRange"
                      :items="dateRangeOptions"
                      label="時間範圍"
                      density="comfortable"
                      variant="outlined"
                      hide-details
                      class="filter-select mr-2"
                      style="min-width: 120px"
                      clearable
                      bg-color="white"
                      rounded="lg"
                      @update:model-value="applyFilters"
                    />
                    <v-text-field
                      v-model="searchKeyword"
                      density="comfortable"
                      label="搜尋檔案名稱"
                      prepend-inner-icon="mdi-magnify"
                      variant="outlined"
                      hide-details
                      clearable
                      style="min-width: 200px"
                      bg-color="white"
                      rounded="lg"
                      @update:model-value="applyFilters"
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
                  v-model:selected="selectedFiles"
                  fixed-header
                  :headers="headers"
                  :items="filteredFiles"
                  :loading="loading"
                  :height="500"
                  density="comfortable"
                  item-value="id"
                  show-select
                  class="downloads-table rounded-lg"
                >
                  <!-- 自定義表頭：選取欄 -->
                  <template #[`header.data-table-select`]>
                    <div class="d-flex align-center">
                      <span class="ml-2 text-subtitle-2 font-weight-medium">選取</span>
                    </div>
                  </template>

                  <!-- 檔案名稱欄位 -->
                  <template #[`item.filename`]="{ item }">
                    <div class="d-flex align-center">
                      <v-icon
                        :icon="getFileIcon(item.format)"
                        :color="getFileIconColor(item.format)"
                        class="mr-2"
                        size="small"
                      />
                      <span class="text-body-2">{{ item.filename }}</span>
                    </div>
                  </template>

                  <!-- 文件類型欄位 -->
                  <template #[`item.category`]="{ item }">
                    <v-chip
                      :color="getCategoryColor(item.category)"
                      variant="flat"
                      size="small"
                      label
                      class="font-weight-medium"
                    >
                      {{ item.category }}
                    </v-chip>
                  </template>

                  <!-- 檔案大小欄位 -->
                  <template #[`item.size`]="{ item }">
                    <span class="text-body-2">{{ formatFileSize(item.size) }}</span>
                  </template>

                  <!-- 建立時間欄位 -->
                  <template #[`item.createdAt`]="{ item }">
                    <span class="text-body-2">{{ formatDateTime(item.createdAt) }}</span>
                  </template>

                  <!-- 狀態欄位 -->
                  <template #[`item.status`]="{ item }">
                    <v-chip
                      :color="getStatusColor(item.status)"
                      variant="flat"
                      size="small"
                      label
                      class="font-weight-medium"
                    >
                      {{ item.status }}
                    </v-chip>
                  </template>

                  <!-- 操作按鈕 -->
                  <template #[`item.actions`]="{ item }">
                    <div class="ma-0 pa-0 d-flex gap-2 justify-end">
                      <v-btn
                        icon="mdi-eye"
                        size="small"
                        color="#3ea0a3"
                        variant="text"
                        title="預覽檔案"
                        :disabled="!canPreview(item.format)"
                        @click="handlePreviewFile(item)"
                      />
                      <v-btn
                        icon="mdi-download"
                        size="small"
                        color="success"
                        variant="text"
                        title="下載檔案"
                        :loading="downloadingFiles.includes(item.id)"
                        @click="downloadFile(item)"
                      />
                      <v-btn
                        icon="mdi-delete"
                        size="small"
                        color="error"
                        variant="text"
                        title="刪除檔案"
                        @click="deleteFile(item)"
                      />
                    </div>
                  </template>

                  <!-- 表格底部 -->
                  <template #bottom>
                    <div class="d-flex align-center pa-3">
                      <span class="text-body-2 text-medium-emphasis">
                        共 {{ filteredFiles.length }} 筆檔案
                        <span v-if="selectedFiles.length > 0">
                          （已選取 {{ selectedFiles.length }} 筆）
                        </span>
                      </span>
                      <v-spacer />
                      <div
                        v-if="error"
                        class="text-error text-caption"
                      >
                        {{ error }}
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
                  點擊「預覽」按鈕可查看檔案內容（限支援格式），「下載」按鈕可下載單一檔案，「刪除」按鈕將永久移除檔案
                </span>
              </div>
            </v-card-text>
          </v-card>
        </div>
      </v-col>
    </v-row>

    <!-- 檔案預覽對話框 -->
    <v-dialog
      v-model="previewDialog"
      max-width="800px"
      persistent
    >
      <v-card rounded="lg">
        <v-card-title class="text-h5 pa-6 pb-2">
          <v-icon
            icon="mdi-eye"
            color="#3ea0a3"
            class="mr-2"
          />
          檔案預覽
          <v-spacer />
          <v-btn
            icon="mdi-close"
            variant="text"
            @click="previewDialog = false"
          />
        </v-card-title>

        <v-card-text class="pa-6">
          <div
            v-if="currentPreviewFile"
            class="mb-4"
          >
            <div class="d-flex align-center mb-3">
              <v-icon
                :icon="getFileIcon(currentPreviewFile.format)"
                :color="getFileIconColor(currentPreviewFile.format)"
                class="mr-2"
              />
              <div>
                <div class="text-subtitle-1 font-weight-bold">
                  {{ currentPreviewFile.filename }}
                </div>
                <div class="text-caption text-medium-emphasis">
                  {{ formatFileSize(currentPreviewFile.size) }} • {{ currentPreviewFile.format }} • {{ formatDateTime(currentPreviewFile.createdAt) }}
                </div>
              </div>
            </div>

            <!-- 預覽內容區域 -->
            <div
              class="preview-content"
              style="min-height: 300px; border: 1px solid #e0e0e0; border-radius: 4px; padding: 16px;"
            >
              <div
                v-if="previewLoading"
                class="d-flex justify-center align-center"
                style="height: 300px;"
              >
                <v-progress-circular
                  indeterminate
                  color="#3ea0a3"
                />
                <span class="ml-2">載入預覽中...</span>
              </div>
              <div
                v-else-if="previewError"
                class="d-flex justify-center align-center"
                style="height: 300px;"
              >
                <div class="text-center">
                  <v-icon
                    icon="mdi-alert-circle"
                    color="error"
                    size="large"
                    class="mb-2"
                  />
                  <div class="text-body-1">
                    無法預覽此檔案
                  </div>
                  <div class="text-caption text-medium-emphasis">
                    {{ previewError }}
                  </div>
                </div>
              </div>
              <div
                v-else
                class="preview-display"
              >
                <!-- 這裡可以根據檔案類型顯示不同的預覽內容 -->
                <div class="text-body-2">
                  預覽內容將在此顯示...
                </div>
              </div>
            </div>
          </div>
        </v-card-text>

        <v-card-actions class="pa-6 pt-0">
          <v-spacer />
          <v-btn
            variant="outlined"
            @click="previewDialog = false"
          >
            關閉
          </v-btn>
          <v-btn
            color="#3ea0a3"
            variant="flat"
            prepend-icon="mdi-download"
            @click="currentPreviewFile && downloadFile(currentPreviewFile)"
          >
            下載檔案
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script lang="ts" setup>
import { ref, computed, onMounted } from 'vue'

// 定義檔案資料介面
interface DownloadFile {
  id: string
  filename: string
  category: string
  format: string
  size: number
  createdAt: string
  status: string
  downloadUrl: string
  description?: string
}

// 響應式資料
const loading = ref(false)
const refreshing = ref(false)
const batchDownloading = ref(false)
const error = ref('')
const searchKeyword = ref('')
const selectedCategory = ref<string | null>(null)
const selectedFormat = ref<string | null>(null)
const selectedDateRange = ref<string | null>(null)
const selectedFiles = ref<string[]>([])
const downloadingFiles = ref<string[]>([])

// 預覽對話框相關
const previewDialog = ref(false)
const currentPreviewFile = ref<DownloadFile | null>(null)
const previewLoading = ref(false)
const previewError = ref('')

// 檔案清單資料
const files = ref<DownloadFile[]>([
  {
    id: '1',
    filename: '申請案件統計報表_113年.xlsx',
    category: '統計報表',
    format: 'xlsx',
    size: 1024000,
    createdAt: '2024-03-15 14:30:00',
    status: '可下載',
    downloadUrl: '/api/downloads/1'
  },
  {
    id: '2',
    filename: '管路灌溉材料清單.pdf',
    category: '材料清單',
    format: 'pdf',
    size: 512000,
    createdAt: '2024-03-14 10:15:00',
    status: '可下載',
    downloadUrl: '/api/downloads/2'
  },
  {
    id: '3',
    filename: '補助申請表單範本.doc',
    category: '表單範本',
    format: 'doc',
    size: 256000,
    createdAt: '2024-03-13 16:45:00',
    status: '可下載',
    downloadUrl: '/api/downloads/3'
  },
  {
    id: '4',
    filename: 'GIS圖層資料_北區.zip',
    category: 'GIS資料',
    format: 'zip',
    size: 5120000,
    createdAt: '2024-03-12 09:20:00',
    status: '處理中',
    downloadUrl: '/api/downloads/4'
  },
])

// 篩選選項
const categoryOptions = [
  { title: '統計報表', value: '統計報表' },
  { title: '材料清單', value: '材料清單' },
  { title: '表單範本', value: '表單範本' },
  { title: 'GIS資料', value: 'GIS資料' },
  { title: '系統文件', value: '系統文件' },
]

const formatOptions = [
  { title: 'PDF', value: 'pdf' },
  { title: 'Excel', value: 'xlsx' },
  { title: 'Word', value: 'doc' },
  { title: 'ZIP', value: 'zip' },
  { title: 'CSV', value: 'csv' },
]

const dateRangeOptions = [
  { title: '今天', value: 'today' },
  { title: '本週', value: 'week' },
  { title: '本月', value: 'month' },
  { title: '本季', value: 'quarter' },
  { title: '本年', value: 'year' },
]

// 表格標題
const headers = ref([
  { title: '檔案名稱', key: 'filename', align: 'start' as const },
  { title: '文件類型', key: 'category', align: 'center' as const },
  { title: '格式', key: 'format', align: 'center' as const },
  { title: '檔案大小', key: 'size', align: 'end' as const },
  { title: '建立時間', key: 'createdAt', align: 'center' as const },
  { title: '狀態', key: 'status', align: 'center' as const },
  { title: '操作', key: 'actions', align: 'center' as const, sortable: false },
])

// 計算屬性：過濾後的檔案清單
const filteredFiles = computed(() => {
  let result = files.value

  // 依類型篩選
  if (selectedCategory.value) {
    result = result.filter(file => file.category === selectedCategory.value)
  }

  // 依格式篩選
  if (selectedFormat.value) {
    result = result.filter(file => file.format === selectedFormat.value)
  }

  // 依時間範圍篩選
  if (selectedDateRange.value) {
    // TODO: 實作時間範圍篩選邏輯
    // 這裡可以實作具體的時間範圍篩選邏輯
    result = result.filter(() => {
      return true
    })
  }

  // 依關鍵字搜尋
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(file =>
      file.filename.toLowerCase().includes(keyword) ||
      file.category.toLowerCase().includes(keyword) ||
      file.description?.toLowerCase().includes(keyword)
    )
  }

  return result
})

// 工具函數：取得檔案圖示
const getFileIcon = (format: string) => {
  const iconMap: Record<string, string> = {
    'pdf': 'mdi-file-pdf-box',
    'xlsx': 'mdi-file-excel',
    'xls': 'mdi-file-excel',
    'doc': 'mdi-file-word',
    'docx': 'mdi-file-word',
    'zip': 'mdi-folder-zip',
    'csv': 'mdi-file-delimited',
    'txt': 'mdi-file-document',
    'jpg': 'mdi-file-image',
    'jpeg': 'mdi-file-image',
    'png': 'mdi-file-image',
  }
  return iconMap[format.toLowerCase()] || 'mdi-file'
}

// 工具函數：取得檔案圖示顏色
const getFileIconColor = (format: string) => {
  const colorMap: Record<string, string> = {
    'pdf': 'red',
    'xlsx': 'green',
    'xls': 'green',
    'doc': 'blue',
    'docx': 'blue',
    'zip': 'orange',
    'csv': 'teal',
    'txt': 'grey',
    'jpg': 'purple',
    'jpeg': 'purple',
    'png': 'purple',
  }
  return colorMap[format.toLowerCase()] || 'grey'
}

// 工具函數：取得類型顏色
const getCategoryColor = (category: string) => {
  const colorMap: Record<string, string> = {
    '統計報表': 'blue-lighten-4',
    '材料清單': 'green-lighten-4',
    '表單範本': 'orange-lighten-4',
    'GIS資料': 'purple-lighten-4',
    '系統文件': 'grey-lighten-4',
  }
  return colorMap[category] || 'grey-lighten-4'
}

// 工具函數：取得狀態顏色
const getStatusColor = (status: string) => {
  const colorMap: Record<string, string> = {
    '可下載': 'green-lighten-4',
    '處理中': 'orange-lighten-4',
    '已過期': 'red-lighten-4',
    '暫停下載': 'grey-lighten-4',
  }
  return colorMap[status] || 'grey-lighten-4'
}

// 工具函數：格式化檔案大小
const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 工具函數：格式化日期時間
const formatDateTime = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleString('zh-TW', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 工具函數：檢查是否可預覽
const canPreview = (format: string) => {
  const previewableFormats = ['pdf', 'txt', 'csv', 'jpg', 'jpeg', 'png']
  return previewableFormats.includes(format.toLowerCase())
}

// 事件處理：重新整理
const refreshDownloads = async () => {
  refreshing.value = true
  try {
    // TODO: 實際呼叫 API 重新載入檔案清單
    await new Promise(resolve => setTimeout(resolve, 1000))
    console.log('重新整理檔案清單')
  } catch (refreshError) {
    error.value = '重新整理失敗，請稍後再試'
    console.error('重新整理失敗:', refreshError)
  } finally {
    refreshing.value = false
  }
}

// 事件處理：批量下載
const batchDownload = async () => {
  if (selectedFiles.value.length === 0) return

  batchDownloading.value = true
  try {
    // TODO: 實際呼叫批量下載 API
    await new Promise(resolve => setTimeout(resolve, 2000))
    console.log('批量下載檔案:', selectedFiles.value)

    // 清除選取狀態
    selectedFiles.value = []
  } catch (batchError) {
    error.value = '批量下載失敗，請稍後再試'
    console.error('批量下載失敗:', batchError)
  } finally {
    batchDownloading.value = false
  }
}

// 事件處理：套用篩選
const applyFilters = () => {
  // 篩選邏輯已在 computed 中處理
  console.log('套用篩選條件')
}

// 事件處理：預覽檔案
const handlePreviewFile = async (file: DownloadFile) => {
  if (!canPreview(file.format)) return

  currentPreviewFile.value = file
  previewDialog.value = true
  previewLoading.value = true
  previewError.value = ''

  try {
    // TODO: 實際呼叫 API 獲取預覽內容
    await new Promise(resolve => setTimeout(resolve, 1000))
    console.log('預覽檔案:', file.filename)
  } catch (error) {
    previewError.value = '無法載入檔案預覽'
    console.error('預覽檔案失敗:', error)
  } finally {
    previewLoading.value = false
  }
}

// 事件處理：下載檔案
const downloadFile = async (file: DownloadFile) => {
  if (downloadingFiles.value.includes(file.id)) return

  downloadingFiles.value.push(file.id)
  try {
    // TODO: 實際下載檔案邏輯
    console.log('下載檔案:', file.filename)

    // 模擬下載
    const link = document.createElement('a')
    link.href = file.downloadUrl
    link.download = file.filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)

  } catch (downloadError) {
    error.value = `下載檔案 ${file.filename} 失敗`
    console.error('下載檔案失敗:', downloadError)
  } finally {
    downloadingFiles.value = downloadingFiles.value.filter(id => id !== file.id)
  }
}

// 事件處理：刪除檔案
const deleteFile = async (file: DownloadFile) => {
  const confirmMessage = `確定要刪除檔案「${file.filename}」嗎？此操作無法撤銷。`

  if (confirm(confirmMessage)) {
    try {
      // TODO: 實際呼叫刪除 API
      console.log('刪除檔案:', file.filename)

      // 從清單中移除
      const index = files.value.findIndex(f => f.id === file.id)
      if (index > -1) {
        files.value.splice(index, 1)
      }
    } catch (deleteError) {
      error.value = `刪除檔案 ${file.filename} 失敗`
      console.error('刪除檔案失敗:', deleteError)
    }
  }
}

// 組件載入時初始化
onMounted(async () => {
  loading.value = true
  try {
    // TODO: 實際載入檔案清單 API
    await new Promise(resolve => setTimeout(resolve, 500))
    console.log('載入檔案清單完成')
  } catch (loadError) {
    error.value = '載入檔案清單失敗'
    console.error('載入檔案清單失敗:', loadError)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
/* 添加背景圖片樣式 */
.downloads-container {
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
  min-width: 130px;
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
.downloads-table :deep(thead th) {
  background-color: #e3f4f4 !important;
  color: #333 !important;
  font-weight: 900 !important;
}

.downloads-table :deep(.v-data-table__tr:hover) {
  background-color: rgba(98, 183, 187, 0.1) !important;
}

.downloads-table :deep(.v-data-table__tr:nth-child(even)) {
  background-color: rgba(98, 183, 187, 0.05);
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

@media (max-width: 600px) {
  .filter-select {
    min-width: 100%;
  }
}

/* 預覽內容樣式 */
.preview-content {
  background-color: #fafafa;
}

.preview-display {
  font-family: monospace;
  white-space: pre-wrap;
  overflow-y: auto;
  max-height: 400px;
}
</style>
