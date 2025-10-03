<template>
  <v-dialog
    v-model="dialogVisible"
    width="400"
    height="600"
    persistent
  >
    <v-card height="600" rounded="lg">
      <!-- Toolbar with Extension -->
      <v-toolbar
        color="primary"
        dark
      >
        <v-toolbar-title>新增自訂圖層</v-toolbar-title>
        <v-spacer />
        <v-btn
          icon
          @click="closeDialog"
        >
          <v-icon>mdi-close</v-icon>
        </v-btn>

        <template #extension>
          <v-tabs
            v-model="inputMode"
            color="white"
            grow
          >
            <v-tab value="url">
              OGC 服務
            </v-tab>
            <v-tab value="shapefile">
              Shapefile
            </v-tab>
          </v-tabs>
        </template>
      </v-toolbar>

      <v-card-text class="pt-4 dialog-content">

        <!-- URL 模式 -->
        <div v-if="inputMode === 'url'">
          <v-select
            v-model="selectedServiceType"
            :items="serviceTypes"
            label="服務類型"
            hint="留空則自動偵測"
            persistent-hint
            clearable
            density="comfortable"
            class="mb-4"
          />

          <v-text-field
            v-model="capabilitiesUrl"
            label="GetCapabilities URL"
            placeholder="https://example.com/geoserver/wms?service=WMS&request=GetCapabilities"
            :error-messages="urlError"
            :loading="parsing"
            density="comfortable"
            @input="urlError = ''"
          >
            <template #append>
              <v-btn
                color="primary"
                :disabled="!capabilitiesUrl || parsing"
                :loading="parsing"
                size="small"
                @click="parseFromURL"
              >
                解析
              </v-btn>
            </template>
          </v-text-field>

          <!-- 解析錯誤提示 -->
          <v-alert
            v-if="parseError"
            type="error"
            variant="tonal"
            density="compact"
            class="mt-3"
            closable
            @click:close="parseError = ''"
          >
            {{ parseError }}
          </v-alert>

          <!-- OGC 服務資訊 -->
          <div
            v-if="parsedResult"
            class="mt-4"
          >
            <v-chip
              color="primary"
              size="small"
              class="mb-2"
            >
              {{ parsedResult.serviceType }} {{ parsedResult.version }}
            </v-chip>
            <div class="text-subtitle-2">
              {{ parsedResult.serviceTitle }}
            </div>
            <div
              v-if="parsedResult.serviceAbstract"
              class="text-caption text-medium-emphasis"
            >
              {{ parsedResult.serviceAbstract }}
            </div>
          </div>
        </div>

        <!-- Shapefile 模式 -->
        <div v-else-if="inputMode === 'shapefile'">
          <v-file-input
            v-model="shapefileFiles"
            label="上傳 Shapefile 檔案"
            multiple
            accept=".shp,.dbf,.prj,.shx,.zip"
            prepend-icon="mdi-file-upload"
            hint="方式 1：選擇多個檔案（.shp + .prj）｜方式 2：上傳單一 ZIP 檔案"
            persistent-hint
            :error-messages="shapefileError"
            :loading="parsing"
            density="comfortable"
            @update:model-value="onShapefileSelected"
          >
            <template #append>
              <v-btn
                color="primary"
                :disabled="!shapefileValidation?.isValid || !shapefileFiles.length || parsing"
                :loading="parsing"
                size="small"
                @click="loadShapefile"
              >
                解析
              </v-btn>
            </template>
          </v-file-input>

          <!-- Shapefile 驗證狀態 -->
          <v-alert
            v-if="shapefileValidation && !shapefileValidation.isValid"
            type="warning"
            variant="tonal"
            density="compact"
            class="mt-3"
          >
            <div class="text-body-2">
              缺少必要檔案：{{ shapefileValidation.missingFiles.join(', ') }}
            </div>
          </v-alert>

          <!-- 解析錯誤提示 -->
          <v-alert
            v-if="parseError"
            type="error"
            variant="tonal"
            density="compact"
            class="mt-3"
            closable
            @click:close="parseError = ''"
          >
            {{ parseError }}
          </v-alert>

          <!-- Shapefile 資訊 -->
          <div
            v-if="shapefileParseResult"
            class="mt-4"
          >
            <v-chip
              color="success"
              size="small"
              class="mb-2"
            >
              Shapefile
            </v-chip>
            <div class="text-subtitle-2">
              已解析 {{ shapefileParseResult.layers.length }} 個圖層
            </div>
          </div>
        </div>

        <!-- 圖層選擇區域 -->
        <div class="mt-4">
          <v-divider class="mb-4" />

          <div class="d-flex align-center justify-space-between mb-3">
            <span class="text-subtitle-1">
              選擇圖層
            </span>
            <v-chip
              v-if="showLayerSelection"
              size="small"
              color="primary"
              variant="tonal"
            >
              {{ selectedCount }} / {{ totalLayersCount }}
            </v-chip>
          </div>

          <v-text-field
            v-if="showLayerSelection"
            v-model="layerSearch"
            prepend-inner-icon="mdi-magnify"
            label="搜尋圖層"
            clearable
            hide-details
            density="compact"
            class="mb-3"
          />

          <!-- 圖層列表容器 -->
          <div class="layer-selection-container">
            <!-- 已解析：顯示圖層列表 -->
            <v-list
              v-if="showLayerSelection && filteredLayers.length > 0"
              density="compact"
            >
              <v-list-item
                v-for="layer in filteredLayers"
                :key="layer.name"
                @click="toggleLayerSelection(layer.name)"
              >
                <template #prepend>
                  <v-checkbox-btn
                    :model-value="isLayerSelected(layer.name)"
                  />
                </template>
                <v-list-item-title>{{ layer.title }}</v-list-item-title>
                <v-list-item-subtitle v-if="layer.abstract">
                  {{ layer.abstract }}
                </v-list-item-subtitle>
              </v-list-item>
            </v-list>

            <!-- 已解析但搜尋無結果 -->
            <v-alert
              v-else-if="showLayerSelection && filteredLayers.length === 0"
              type="info"
              variant="tonal"
              density="compact"
            >
              沒有找到符合的圖層
            </v-alert>

            <!-- 未解析：顯示空狀態 -->
            <v-empty-state
              v-else
              icon="mdi-layers-outline"
              title="尚未載入圖層"
              :text="inputMode === 'url' ? '請輸入 OGC 服務 URL 並點擊「解析」' : '請選擇 Shapefile 檔案並點擊「解析」'"
            />
          </div>
        </div>
      </v-card-text>

      <!-- 底部按鈕 -->
      <v-card-actions
        v-if="showLayerSelection"
        class="px-6 pb-4"
      >
        <v-spacer />
        <v-btn
          variant="text"
          @click="closeDialog"
        >
          取消
        </v-btn>
        <v-btn
          color="primary"
          :disabled="selectedCount === 0"
          @click="confirmSelection"
        >
          加入圖層
          <span v-if="selectedCount > 0"> ({{ selectedCount }})</span>
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import {
  parseCapabilitiesFromURL,
  type CapabilitiesParseResult
} from '@/utils/ogcCapabilitiesParser'
import {
  loadShapefileFromFiles,
  loadShapefileFromZip,
  validateShapefileSet,
  type ShapefileParseResult
} from '@/utils/shapefileLoader'
import type { OGCServiceType, OGCServiceConfig } from './config'
import type { GeoJsonFeatureCollection } from '@/types/gis'

// Props & Emits
const props = defineProps<{
  visible: boolean
  serviceUrl?: string
}>()

const emit = defineEmits<{
  'update:visible': [value: boolean]
  'layers-added': [configs: OGCServiceConfig[]]
  'shapefile-loaded': [
    data: Array<{ name: string; geoJson: GeoJsonFeatureCollection }>,
    callback: (success: boolean, error?: string) => void
  ]
}>()

// Dialog 狀態
const dialogVisible = computed({
  get: () => props.visible,
  set: (value) => emit('update:visible', value)
})

// 輸入模式
const inputMode = ref<'url' | 'shapefile'>('url')

// 服務類型選項
const serviceTypes = [
  { title: 'WMS', value: 'WMS' },
  { title: 'WFS', value: 'WFS' },
  { title: 'WMTS', value: 'WMTS' }
]
const selectedServiceType = ref<OGCServiceType | null>(null)

// URL 輸入
const capabilitiesUrl = ref(props.serviceUrl || '')
const urlError = ref('')

// 解析狀態
const parsing = ref(false)
const parseError = ref('')
const parsedResult = ref<CapabilitiesParseResult | null>(null)

// 圖層選擇
const selectedLayers = ref<string[]>([])
const layerSearch = ref('')

// Shapefile 相關狀態
const shapefileFiles = ref<File[]>([])
const shapefileError = ref('')
const shapefileValidation = ref<ReturnType<typeof validateShapefileSet> | null>(null)
const shapefileParseResult = ref<ShapefileParseResult | null>(null)
const selectedShapefileLayers = ref<string[]>([])
const shapefileLoadedCount = ref(0)

// 狀態驅動的計算屬性
const showLayerSelection = computed(() => {
  return (parsedResult.value !== null || shapefileParseResult.value !== null)
})

const selectedCount = computed(() => {
  return inputMode.value === 'shapefile'
    ? selectedShapefileLayers.value.length
    : selectedLayers.value.length
})

const totalLayersCount = computed(() => {
  return inputMode.value === 'shapefile'
    ? (shapefileParseResult.value?.layers.length || 0)
    : (parsedResult.value?.layers.length || 0)
})

// 過濾後的圖層列表（統一處理 OGC 和 Shapefile）
const filteredLayers = computed(() => {
  // Shapefile 模式
  if (inputMode.value === 'shapefile' && shapefileParseResult.value) {
    const layers = shapefileParseResult.value.layers.map(layer => ({
      name: layer.name,
      title: layer.name,
      abstract: `包含 ${layer.featureCount} 個特徵`
    }))

    if (!layerSearch.value) return layers

    const search = layerSearch.value.toLowerCase()
    return layers.filter(layer =>
      layer.title.toLowerCase().includes(search) ||
      layer.name.toLowerCase().includes(search)
    )
  }

  // OGC 服務模式
  if (!parsedResult.value) return []
  const layers = parsedResult.value.layers
  if (!layerSearch.value) return layers

  const search = layerSearch.value.toLowerCase()
  return layers.filter(
    (layer) =>
      layer.title.toLowerCase().includes(search) ||
      layer.name.toLowerCase().includes(search) ||
      layer.abstract?.toLowerCase().includes(search)
  )
})

// 從 URL 解析
const parseFromURL = async () => {
  if (!capabilitiesUrl.value) {
    urlError.value = '請輸入 GetCapabilities URL'
    return
  }

  parsing.value = true
  parseError.value = ''

  try {
    parsedResult.value = await parseCapabilitiesFromURL(
      capabilitiesUrl.value,
      selectedServiceType.value || undefined
    )
    // 成功解析後自動顯示圖層選擇區域（透過 showLayerSelection computed）
  } catch (error) {
    parseError.value = `解析失敗: ${(error as Error).message}`
  } finally {
    parsing.value = false
  }
}

// 切換圖層選擇（統一處理 OGC 和 Shapefile）
const toggleLayerSelection = (layerName: string) => {
  if (inputMode.value === 'shapefile') {
    const index = selectedShapefileLayers.value.indexOf(layerName)
    if (index > -1) {
      selectedShapefileLayers.value.splice(index, 1)
    } else {
      selectedShapefileLayers.value.push(layerName)
    }
  } else {
    const index = selectedLayers.value.indexOf(layerName)
    if (index > -1) {
      selectedLayers.value.splice(index, 1)
    } else {
      selectedLayers.value.push(layerName)
    }
  }
}

// 檢查圖層是否被選中（統一處理）
const isLayerSelected = (layerName: string): boolean => {
  if (inputMode.value === 'shapefile') {
    return selectedShapefileLayers.value.includes(layerName)
  } else {
    return selectedLayers.value.includes(layerName)
  }
}

// Shapefile 檔案選擇處理
const onShapefileSelected = (files: File[]) => {
  shapefileError.value = ''

  if (files.length === 0) {
    shapefileValidation.value = null
    return
  }

  // 驗證檔案組合
  shapefileValidation.value = validateShapefileSet(files)
}

// 載入 Shapefile（解析並進入 Step 2 選擇圖層）
const loadShapefile = async () => {
  if (!shapefileValidation.value?.isValid || shapefileFiles.value.length === 0) {
    return
  }

  parsing.value = true
  parseError.value = ''

  try {
    let parseResult: ShapefileParseResult

    // 檢查是否為 ZIP 檔案
    const zipFile = shapefileFiles.value.find(f => f.name.toLowerCase().endsWith('.zip'))

    if (zipFile) {
      // 從 ZIP 載入
      parseResult = await loadShapefileFromZip(zipFile, { encoding: 'big5' })
    } else {
      // 從檔案列表載入
      parseResult = await loadShapefileFromFiles(shapefileFiles.value, { encoding: 'big5' })
    }

    // 驗證解析結果
    if (!parseResult.layers || parseResult.layers.length === 0) {
      throw new Error('Shapefile 中沒有有效的圖層')
    }

    console.log(`[Dialog] Shapefile 解析成功: ${parseResult.layers.length} 個圖層`)

    shapefileParseResult.value = parseResult
    // 成功解析後自動顯示圖層選擇區域（透過 showLayerSelection computed）

  } catch (error) {
    const errorMsg = (error as Error).message
    parseError.value = `Shapefile 載入失敗: ${errorMsg}`
    console.error('[Dialog] Shapefile 載入失敗:', error)
  } finally {
    parsing.value = false
  }
}

// 確認選擇並載入圖層
const confirmSelection = () => {
  // Shapefile 模式
  if (inputMode.value === 'shapefile') {
    if (!shapefileParseResult.value || selectedShapefileLayers.value.length === 0) {
      return
    }

    // 取得選中的圖層資料
    const selectedLayersData = selectedShapefileLayers.value
      .map(layerName =>
        shapefileParseResult.value!.layers.find(l => l.name === layerName)
      )
      .filter(layer => layer !== undefined)
      .map(layer => ({
        name: layer!.name,
        geoJson: layer!.geoJson
      }))

    console.log(`[Dialog] 確認載入 ${selectedLayersData.length} 個 Shapefile 圖層`)

    // 發送 shapefile 載入事件，等待回調確認實際結果
    emit('shapefile-loaded',
      selectedLayersData,
      (success: boolean, error?: string) => {
        if (success) {
          // 成功後直接關閉對話框（snackbar 由 index.vue 處理）
          closeDialog()
        } else {
          parseError.value = error || 'Shapefile 圖層建立失敗'
        }
      }
    )

    return
  }

  // OGC 服務模式
  if (!parsedResult.value) return

  const configs: OGCServiceConfig[] = selectedLayers.value.map((layerName) => {
    const layerInfo = parsedResult.value!.layers.find((l) => l.name === layerName)!

    return {
      type: parsedResult.value!.serviceType,
      url: capabilitiesUrl.value,
      layerName,
      version: parsedResult.value!.version,
      title: layerInfo.title,
      abstract: layerInfo.abstract,
      extent: layerInfo.extent,
      params: {}
    }
  })

  emit('layers-added', configs)
  // 成功後直接關閉對話框
  closeDialog()
}

// 關閉對話框並重置狀態
const closeDialog = () => {
  // 重置 OGC 狀態
  inputMode.value = 'url'
  selectedServiceType.value = null
  capabilitiesUrl.value = props.serviceUrl || ''
  urlError.value = ''
  parseError.value = ''
  parsedResult.value = null
  selectedLayers.value = []
  layerSearch.value = ''

  // 重置 Shapefile 狀態
  shapefileFiles.value = []
  shapefileError.value = ''
  shapefileValidation.value = null
  shapefileParseResult.value = null
  selectedShapefileLayers.value = []
  shapefileLoadedCount.value = 0

  dialogVisible.value = false
}
</script>

<style scoped>
.dialog-content {
  height: calc(600px - 128px); /* 600px card height - toolbar height (64px + 48px extension) */
  overflow-y: auto;
}

.layer-selection-container {
  max-height: 280px;
  overflow-y: auto;
  border: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
  border-radius: 4px;
}
</style>
