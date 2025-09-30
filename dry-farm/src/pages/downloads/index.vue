<template>
  <v-container
    fluid
    class="downloads-container px-6 pb-0 pt-11"
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
            <!-- <v-btn
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
            </v-btn> -->
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
                文件清單
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
                    <!-- <v-select
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
                    /> -->
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
                      autocomplete="off"
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
                  fixed-header
                  :headers="headers"
                  :items="filteredFiles"
                  :loading="loading"
                  :height="500"
                  density="comfortable"
                  item-value="id"
                  class="downloads-table rounded-lg"
                >
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

                  <!-- 可用格式欄位 (可點擊下載) -->
                  <template #[`item.formats`]="{ item }">
                    <div class="d-flex flex-wrap justify-center">
                      <v-chip
                        v-for="format in (item.availableFormats || [])"
                        :key="format.id"
                        variant="outlined"
                        label
                        class="font-weight-medium format-chip mx-2"
                        :color="getFileIconColor(format.format)"
                        :loading="downloadingFiles.includes(format.id)"
                        :disabled="downloadingFiles.includes(format.id)"
                        @click="downloadFile({...item, id: format.id, filename: format.filename, format: format.format})"
                      >
                        <v-icon
                          :icon="getFileIcon(format.format)"
                          size="x-small"
                          class="mr-1"
                        />
                        {{ format.format.toUpperCase() }}
                        <span class="text-caption ml-1">({{ formatFileSize(format.size) }})</span>
                      </v-chip>
                    </div>
                  </template>

                  <!-- 最後更新時間欄位 -->
                  <template #[`item.createdAt`]="{ item }">
                    <span class="text-body-2">{{ formatDateTime(item.createdAt) }}</span>
                  </template>


                  <!-- 表格底部 -->
                  <template #bottom>
                    <div class="d-flex align-center pa-3">
                      <span class="text-body-2 text-medium-emphasis">
                        共 {{ filteredFiles.length }} 個檔案
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
                  直接點擊格式標籤進行下載
                </span>
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
              v-if="downloading && currentDownloadFile"
              class="text-caption text-medium-emphasis"
            >
              正在準備 {{ currentDownloadFile.filename }} 檔案...
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
            @click="retryDownload"
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
import { ref, computed, onMounted } from 'vue'

// 引入整合的下載服務
import downloadsService, {
  type FileGroup,
  type StaticFileInfo,
  type StaticDownloadsFilterRequest
} from '@/services/downloadsService'

// 定義檔案資料介面（適配前端顯示）
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
  // 新增格式相關欄位
  baseFileName: string
  availableFormats?: StaticFileInfo[]
  fileGroup?: FileGroup
}

// 響應式資料
const loading = ref(false)
const error = ref('')
const searchKeyword = ref('')
const downloadingFiles = ref<string[]>([])

// 下載進度對話框相關變數
const downloading = ref(false)
const downloadDialog = ref(false)
const downloadProgress = ref(0)
const downloadStatus = ref('')
const currentDownloadFile = ref<DownloadFile | null>(null)

// 檔案清單資料
const files = ref<DownloadFile[]>([])
const fileGroups = ref<FileGroup[]>([])
const availableCategories = ref<string[]>([])

// 靜態下載篩選請求
const filterRequest = ref<StaticDownloadsFilterRequest>({
  category: null,
  format: null,
  search_keyword: null,
  date_range: null
})

// 移除不再使用的篩選選項

// 表格標題
const headers = ref([
  { title: '檔案名稱', key: 'filename', align: 'start' as const },
  { title: '下載格式', key: 'formats', align: 'center' as const },
  { title: '最後更新', key: 'createdAt', align: 'center' as const },
])

// 計算屬性：過濾後的檔案清單（主要是關鍵字搜尋）
const filteredFiles = computed(() => {
  let result = files.value

  // 依關鍵字搜尋
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(file =>
      file.filename.toLowerCase().includes(keyword) ||
      file.baseFileName.toLowerCase().includes(keyword) ||
      file.category?.toLowerCase().includes(keyword) ||
      file.description?.toLowerCase().includes(keyword)
    )
  }

  return result
})

// 資料轉換：將 FileGroup 轉換為前端顯示格式（每個群組只產生一筆記錄）
const convertFileGroupsToFiles = (groups: FileGroup[]): DownloadFile[] => {
  const convertedFiles: DownloadFile[] = []

  // 定義格式優先級順序（與後端保持一致）
  const FORMAT_PRIORITY: Record<string, number> = {
    'csv': 1, 'doc': 2, 'docx': 3, 'odt': 19, 'ods': 20, 'pdf': 5, 'ppt': 6, 'pptx': 7,
    'txt': 8, 'xls': 9, 'xlsx': 10, 'zip': 11, 'rar': 12, 'jpg': 13,
    'jpeg': 14, 'png': 15, 'gif': 16, 'mp4': 17, 'avi': 18
  }

  groups.forEach(group => {
    // 取最新的檔案作為主要檔案資訊
    const latestFile = group.formats.sort((a, b) =>
      new Date(b.modified_at).getTime() - new Date(a.modified_at).getTime()
    )[0]

    // 對格式進行統一排序
    const sortedFormats = [...group.formats].sort((a, b) => {
      const priorityA = FORMAT_PRIORITY[a.format.toLowerCase()] || 999
      const priorityB = FORMAT_PRIORITY[b.format.toLowerCase()] || 999
      return priorityA - priorityB
    })

    convertedFiles.push({
      id: group.base_name, // 使用 base_name 作為 ID
      filename: group.display_name || group.base_name,
      category: group.category || '未分類',
      format: group.formats.map(f => f.format).join(', '), // 顯示所有格式
      size: 0, // 不再使用檔案大小欄位
      createdAt: group.latest_modified,
      status: '可下載',
      downloadUrl: latestFile.download_url,
      description: group.description || undefined,
      baseFileName: group.base_name,
      availableFormats: sortedFormats,
      fileGroup: group
    })
  })

  return convertedFiles
}

// 工具函數：使用整合的下載服務
const getFileIcon = downloadsService.getFileIcon.bind(downloadsService)
const getFileIconColor = downloadsService.getFileIconColor.bind(downloadsService)
const formatFileSize = downloadsService.formatFileSize.bind(downloadsService)
const formatDateTime = downloadsService.formatDateTime.bind(downloadsService)

// 移除不再使用的工具函數

// 載入靜態檔案清單
const loadStaticFiles = async () => {
  try {
    loading.value = true
    error.value = ''

    // 同步篩選條件
    filterRequest.value = {
      category: null,
      format: null,
      search_keyword: searchKeyword.value,
      date_range: null
    }

    const response = await downloadsService.getStaticFilesList(filterRequest.value)
    fileGroups.value = response.file_groups
    availableCategories.value = response.categories
    files.value = convertFileGroupsToFiles(response.file_groups)

    console.log(`載入 ${response.total_groups} 個檔案群組，${response.total_files} 個檔案`)
  } catch (loadError) {
    error.value = '載入檔案清單失敗，請稍後再試'
    console.error('載入靜態檔案失敗:', loadError)
  } finally {
    loading.value = false
  }
}

// 移除不再使用的批量下載功能

// 事件處理：套用篩選
const applyFilters = async () => {
  // 重新載入資料以套用篩選
  await loadStaticFiles()
  console.log('套用篩選條件')
}

// 移除預覽相關函數

// 事件處理：下載檔案
const downloadFile = async (file: DownloadFile) => {
  if (downloadingFiles.value.includes(file.id)) return

  // 設定當前下載檔案和開啟對話框
  currentDownloadFile.value = file
  downloading.value = true
  downloadDialog.value = true
  downloadProgress.value = 0
  downloadStatus.value = '準備下載...'

  downloadingFiles.value.push(file.id)

  try {
    // 第一階段：準備工作
    downloadProgress.value = 20
    downloadStatus.value = '正在驗證檔案...'
    await new Promise(resolve => setTimeout(resolve, 300))

    downloadProgress.value = 40
    downloadStatus.value = '建立下載連線...'
    await new Promise(resolve => setTimeout(resolve, 300))

    downloadProgress.value = 60
    downloadStatus.value = `正在下載 ${file.filename}...`
    await new Promise(resolve => setTimeout(resolve, 200))

    // 實際下載
    await downloadsService.downloadStaticFile(file.id, file.filename)

    // 下載完成
    downloadProgress.value = 90
    downloadStatus.value = '檔案已生成，正在啟動下載...'
    await new Promise(resolve => setTimeout(resolve, 500))

    downloadProgress.value = 100
    downloadStatus.value = '檔案已送出，請查看瀏覽器的下載紀錄'

    console.log('下載檔案成功:', file.filename)
  } catch (downloadError) {
    console.error('下載檔案失敗:', downloadError)
    downloadStatus.value = `下載 ${file.filename} 失敗，請稍後再試`
    downloadProgress.value = 0
    // 保持對話框開啟，讓用戶看到錯誤訊息
  } finally {
    downloading.value = false
    downloadingFiles.value = downloadingFiles.value.filter(id => id !== file.id)
  }
}

// 重新下載功能
const retryDownload = async () => {
  if (currentDownloadFile.value) {
    await downloadFile(currentDownloadFile.value)
  }
}

// 靜態檔案系統不支援刪除功能
// const deleteFile = async (file: DownloadFile) => { ... }

// 組件載入時初始化
onMounted(async () => {
  await loadStaticFiles()
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

/* 格式標籤樣式 */
.format-chip {
  cursor: pointer !important;
  transition: all 0.2s ease;
  border: 1px solid rgba(0, 0, 0, 0.1);
}

.format-chip:hover {
  transform: translateY(-1px);
  /* box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15) !important; */
  /* opacity: 0.9; */
}

.format-chip:active {
  transform: translateY(0);
}

.format-chip:disabled {
  cursor: not-allowed !important;
  opacity: 0.5 !important;
}

/* 下載進度對話框樣式 */
.v-dialog .v-card {
  background-color: rgba(255, 255, 255, 0.95) !important;
  backdrop-filter: blur(10px) !important;
  -webkit-backdrop-filter: blur(10px) !important;
}
</style>
