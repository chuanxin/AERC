<template>
  <v-navigation-drawer
    :model-value="visible"
    location="end"
    width="350"
    border="0"
    @update:model-value="$emit('update:visible', $event)"
  >
    <v-toolbar
      color="primary"
      dark
      flat
    >
      <v-toolbar-title>圖層管理</v-toolbar-title>
      <v-spacer />
      <v-btn
        icon
        @click="$emit('close')"
      >
        <v-icon>mdi-close</v-icon>
      </v-btn>
    </v-toolbar>

    <v-list density="compact">
      <!-- 底圖圖層區塊 -->
      <v-list-subheader class="text-primary font-weight-bold">
        底圖圖層
      </v-list-subheader>
      <v-radio-group
        class="px-1"
        :model-value="getSelectedBaseLayer()"
        @update:model-value="selectBaseLayer"
      >
        <div
          v-for="(layer, index) in baseLayers"
          :key="`baselayer-${index}`"
        >
          <v-list-item class="px-0 py-2">
            <template #prepend>
              <v-radio
                :value="layer.name"
                color="primary"
                class="pr-5"
                density="compact"
                hide-details
              />
            </template>

            <v-list-item-title class="text-body-2 font-weight-medium">
              {{ layer.name }}
            </v-list-item-title>
          </v-list-item>

          <!-- 透明度控制滑桿 -->
          <div
            v-if="layer.visible"
            class="opacity-control-section px-0 pb-2"
          >
            <div class="d-flex align-center">
              <span class="opacity-label me-2">透明度:</span>
              <v-slider
                v-model="layer.opacity"
                class="opacity-slider flex-grow-1"
                :min="0"
                :max="1"
                :step="0.01"
                thumb-label
                density="compact"
                hide-details
                @update:model-value="updateLayerOpacity(layer)"
              >
                <template #thumb-label="{ modelValue }">
                  {{ Math.round(modelValue * 100) }}%
                </template>
              </v-slider>
            </div>
          </div>
        </div>
      </v-radio-group>

      <v-divider class="my-2" />

      <!-- 疊加圖層區塊 -->
      <v-list-subheader class="text-secondary font-weight-bold">
        疊加圖層
      </v-list-subheader>
      <div
        v-for="(layer, index) in overlayLayers"
        :key="`overlay-${index}`"
      >
        <v-list-item class="px-3 py-2">
          <template #prepend>
            <v-switch
              v-model="layer.visible"
              color="primary"
              class="pr-5"
              density="compact"
              hide-details
              @update:model-value="toggleLayerVisibility(layer)"
            />
          </template>

          <v-list-item-title class="text-body-2 font-weight-medium">
            {{ layer.name }}
          </v-list-item-title>
        </v-list-item>

        <!-- 透明度控制滑桿 -->
        <div
          v-if="layer.visible"
          class="opacity-control-section px-3 pb-2"
        >
          <div class="d-flex align-center">
            <span class="opacity-label me-2">透明度:</span>
            <v-slider
              v-model="layer.opacity"
              class="opacity-slider flex-grow-1"
              :min="0"
              :max="1"
              :step="0.01"
              thumb-label
              density="compact"
              hide-details
              @update:model-value="updateLayerOpacity(layer)"
            >
              <template #thumb-label="{ modelValue }">
                {{ Math.round(modelValue * 100) }}%
              </template>
            </v-slider>
          </div>
        </div>

        <!-- 分隔線 -->
        <v-divider
          v-if="index < overlayLayers.length - 1"
        />
      </div>
    </v-list>
  </v-navigation-drawer>
</template>

<script setup lang="ts">
import { computed } from 'vue'

// 定義 MapLayer 類型（從 index.vue 複製）
interface MapLayer {
  name: string
  visible: boolean
  opacity: number
  category: 'baselayer' | 'overlay'
  layer?: unknown // OpenLayers layer instance
}

// Props 定義
interface LayerManagementProps {
  visible: boolean
  mapLayers: MapLayer[]
  displayMode: string
}

const props = defineProps<LayerManagementProps>()

// Emits 定義
const emit = defineEmits<{
  'update:visible': [visible: boolean]
  'close': []
  'layer-visibility-changed': [layer: MapLayer]
  'layer-opacity-changed': [layer: MapLayer]
  'base-layer-selected': [layerName: string]
  'display-mode-changed': [mode: string]
}>()

// 計算屬性
const baseLayers = computed(() =>
  props.mapLayers.filter(l => l.category === 'baselayer')
)

const overlayLayers = computed(() =>
  props.mapLayers.filter(l => l.category === 'overlay')
)

// 圖層可見性切換 (僅處理疊加圖層)
const toggleLayerVisibility = (layer: MapLayer) => {
  console.log('切換疊加圖層:', layer.name, '可見性:', layer.visible)

  // 只處理疊加圖層，底圖圖層有專門的函數處理
  if (layer.category === 'overlay') {
    // 處理補助案件圖層的特殊邏輯
    if (layer.name === '補助案件格網統計圖') {
      // 切換到格網統計模式
      if (layer.visible) {
        emit('display-mode-changed', 'grid')
        // 通過 emit 通知父組件關閉點位圖層
        const pointLayer = props.mapLayers.find(l => l.name === '補助案件點位')
        if (pointLayer) {
          pointLayer.visible = false
          emit('layer-visibility-changed', pointLayer)
        }
      }
    } else if (layer.name === '補助案件點位') {
      // 切換到點位模式
      if (layer.visible) {
        emit('display-mode-changed', 'points')
        // 通過 emit 通知父組件關閉格網圖層
        const gridLayer = props.mapLayers.find(l => l.name === '補助案件格網統計圖')
        if (gridLayer) {
          gridLayer.visible = false
          emit('layer-visibility-changed', gridLayer)
        }
      }
    }

    emit('layer-visibility-changed', layer)
    console.log('疊加圖層', layer.name, '已設置為:', layer.visible ? '可見' : '隱藏')
  } else {
    console.warn('toggleLayerVisibility 僅用於疊加圖層，底圖圖層請使用 selectBaseLayer')
  }
}

// 更新圖層透明度
const updateLayerOpacity = (layer: MapLayer) => {
  emit('layer-opacity-changed', layer)
}

// 獲取當前選中的底圖圖層名稱
const getSelectedBaseLayer = (): string => {
  const selectedLayer = props.mapLayers.find(layer =>
    layer.category === 'baselayer' && layer.visible
  )
  return selectedLayer ? selectedLayer.name : ''
}

// 選擇底圖圖層 (單選模式)
const selectBaseLayer = (layerName: string | null) => {
  if (!layerName) {
    console.warn('收到空的圖層名稱')
    return
  }

  console.log('切換底圖圖層:', layerName)
  emit('base-layer-selected', layerName)
}
</script>

<style scoped>
.opacity-control-section {
  background: rgba(255, 255, 255, 0.7);
  border-radius: 8px;
  padding: 12px;
  margin: 8px 0;
}

.opacity-label {
  font-size: 0.875rem;
  color: rgba(0, 0, 0, 0.6);
  min-width: 60px;
  font-weight: 500;
}

.opacity-slider {
  margin-left: 8px;
}

.opacity-slider :deep(.v-slider-thumb__label) {
  background-color: rgba(0, 0, 0, 0.8);
  color: white;
  font-size: 0.75rem;
}
</style>