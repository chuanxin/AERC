<template>
  <v-card class="shapefile-uploader">
    <v-card-title class="d-flex align-center">
      <v-icon class="me-2">
        mdi-file-upload
      </v-icon>
      Shapefile 圖層載入
    </v-card-title>

    <v-card-text>
      <!-- 檔案上傳區域 -->
      <div class="upload-area">
        <v-file-input
          v-model="selectedFiles"
          label="選擇 Shapefile 檔案"
          multiple
          accept=".shp,.dbf,.prj,.shx,.zip"
          prepend-icon="mdi-file-multiple"
          variant="outlined"
          :loading="uploading"
          @update:model-value="onFilesSelected"
        />

        <!-- 檔案驗證狀態 -->
        <div
          v-if="validation"
          class="mt-2"
        >
          <v-alert
            v-if="!validation.isValid"
            type="warning"
            variant="tonal"
            density="compact"
          >
            <div class="text-body-2">
              <div>缺少必要檔案：</div>
              <ul class="ml-4">
                <li
                  v-for="missing in validation.missingFiles"
                  :key="missing"
                >
                  {{ missing }}
                </li>
              </ul>
            </div>
          </v-alert>

          <v-alert
            v-else
            type="success"
            variant="tonal"
            density="compact"
          >
            檔案組合完整，可以載入
          </v-alert>
        </div>

        <!-- 載入選項 -->
        <v-expansion-panels
          v-if="selectedFiles.length > 0"
          variant="accordion"
          class="mt-3"
        >
          <v-expansion-panel title="載入選項">
            <v-expansion-panel-text>
              <v-select
                v-model="loadOptions.encoding"
                label="文字編碼"
                :items="encodingOptions"
                variant="outlined"
                density="compact"
              />

              <v-text-field
                v-model="layerName"
                label="圖層名稱"
                variant="outlined"
                density="compact"
                placeholder="輸入自訂圖層名稱"
              />

              <v-color-picker
                v-model="layerColor"
                mode="hex"
                hide-inputs
                show-swatches
                swatches-max-height="100"
              />
            </v-expansion-panel-text>
          </v-expansion-panel>
        </v-expansion-panels>
      </div>
    </v-card-text>

    <v-card-actions>
      <v-spacer />
      <v-btn
        variant="text"
        @click="clearFiles"
      >
        清除
      </v-btn>
      <v-btn
        color="primary"
        variant="flat"
        :disabled="!canLoad"
        :loading="uploading"
        @click="loadShapefile"
      >
        載入圖層
      </v-btn>
    </v-card-actions>

    <!-- 載入進度 -->
    <v-progress-linear
      v-if="uploading"
      indeterminate
      color="primary"
    />
  </v-card>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
// import { loadShapefileFromFiles, loadShapefileFromZip, validateShapefileSet, isShapefileRelated } from '@/utils/shapefileLoader'
import type { GeoJsonFeatureCollection } from '@/types/gis'

// Props 定義
interface ShapefileUploaderProps {
  maxFileSize?: number // MB
}

const props = withDefaults(defineProps<ShapefileUploaderProps>(), {
  maxFileSize: 50
})

// Emits 定義
const emit = defineEmits<{
  'layer-loaded': [data: {
    name: string
    geoJson: GeoJsonFeatureCollection
    style: {
      color: string
      opacity: number
    }
  }]
  'error': [message: string]
}>()

// 響應式狀態
const selectedFiles = ref<File[]>([])
const uploading = ref(false)
const layerName = ref('')
const layerColor = ref('#2196F3')

// 載入選項
const loadOptions = ref({
  encoding: 'big5' // 台灣資料通常使用 Big5
})

// 編碼選項
const encodingOptions = [
  { title: 'Big5 (繁體中文)', value: 'big5' },
  { title: 'UTF-8', value: 'utf-8' },
  { title: 'GBK (簡體中文)', value: 'gbk' },
  { title: 'ASCII', value: 'ascii' }
]

// 檔案驗證結果
const validation = ref<ReturnType<typeof validateShapefileSet> | null>(null)

// 計算屬性
const canLoad = computed(() => {
  return selectedFiles.value.length > 0 &&
         validation.value?.isValid &&
         !uploading.value
})

// 監聽檔案選擇
watch(selectedFiles, (newFiles) => {
  if (newFiles.length > 0) {
    // 驗證檔案組合
    // validation.value = validateShapefileSet(newFiles)

    // 自動生成圖層名稱
    if (!layerName.value) {
      const shpFile = newFiles.find(f => f.name.toLowerCase().endsWith('.shp'))
      if (shpFile) {
        layerName.value = shpFile.name.replace(/\.shp$/i, '')
      }
    }
  } else {
    validation.value = null
    layerName.value = ''
  }
})

// 檔案選擇處理
const onFilesSelected = (files: File[]) => {
  // 檢查檔案大小
  const oversizedFiles = files.filter(f => f.size > props.maxFileSize * 1024 * 1024)
  if (oversizedFiles.length > 0) {
    emit('error', `檔案過大：${oversizedFiles.map(f => f.name).join(', ')} (限制: ${props.maxFileSize}MB)`)
    return
  }

  // 篩選 Shapefile 相關檔案
  // const validFiles = files.filter(f => isShapefileRelated(f.name))
  // selectedFiles.value = validFiles
}

// 載入 Shapefile
const loadShapefile = async () => {
  if (!canLoad.value) return

  uploading.value = true

  try {
    let geoJsonData: GeoJsonFeatureCollection

    // 檢查是否為 ZIP 檔案
    const zipFile = selectedFiles.value.find(f => f.name.toLowerCase().endsWith('.zip'))

    if (zipFile) {
      // 從 ZIP 載入
      // geoJsonData = await loadShapefileFromZip(zipFile, loadOptions.value)
      throw new Error('ZIP 載入功能需要安裝 shapefile 和 jszip 套件')
    } else {
      // 從檔案列表載入
      // geoJsonData = await loadShapefileFromFiles(selectedFiles.value, loadOptions.value)
      throw new Error('檔案載入功能需要安裝 shapefile 和 jszip 套件')
    }

    // 發送載入完成事件
    emit('layer-loaded', {
      name: layerName.value || '未命名圖層',
      geoJson: geoJsonData,
      style: {
        color: layerColor.value,
        opacity: 0.7
      }
    })

    // 清除檔案
    clearFiles()

  } catch (error) {
    console.error('Shapefile 載入錯誤:', error)
    emit('error', error instanceof Error ? error.message : '載入失敗')
  } finally {
    uploading.value = false
  }
}

// 清除檔案
const clearFiles = () => {
  selectedFiles.value = []
  layerName.value = ''
  validation.value = null
}

// 模擬驗證函數（實際需要導入真實的函數）
const validateShapefileSet = (files: File[]) => {
  const fileNames = files.map(f => f.name.toLowerCase())
  const hasShp = fileNames.some(name => name.endsWith('.shp'))
  const hasDbf = fileNames.some(name => name.endsWith('.dbf'))
  const hasPrj = fileNames.some(name => name.endsWith('.prj'))

  const missingFiles: string[] = []
  if (!hasShp) missingFiles.push('.shp (必需)')
  if (!hasDbf) missingFiles.push('.dbf (建議)')
  if (!hasPrj) missingFiles.push('.prj (建議)')

  return {
    isValid: hasShp,
    hasShp,
    hasDbf,
    hasPrj,
    missingFiles
  }
}
</script>

<style scoped>
.shapefile-uploader {
  max-width: 500px;
}

.upload-area {
  min-height: 200px;
}

.v-file-input :deep(.v-field__input) {
  min-height: 60px;
}

/* 拖放區域樣式 */
.upload-area:hover .v-file-input {
  border-color: rgb(var(--v-theme-primary));
}
</style>
