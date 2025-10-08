<template>
  <v-navigation-drawer
    :model-value="visible"
    :disable-resize-watcher="true"
    location="end"
    width="300"
    border="0"
    @update:model-value="$emit('update:visible', $event)"
  >
    <v-toolbar
      border
      color="white"
      density="compact"
    >
      <v-toolbar-title>圖層管理</v-toolbar-title>
      <v-spacer />
      <v-btn
        icon
        density="compact"
        color="success"
        :ripple="false"
        @click="$emit('add-custom-layer')"
      >
        <v-icon>mdi-plus</v-icon>
      </v-btn>
      <v-btn
        icon
        density="compact"
        :ripple="false"
        rounded="xl"
        @click="$emit('close')"
      >
        <v-icon>mdi-close</v-icon>
      </v-btn>
    </v-toolbar>

    <v-list
      density="compact"
      class="pt-0"
    >
      <!-- 套疊圖層 TreeView（扁平化顯示各分組） -->
      <v-treeview
        :key="`overlay-tree-${groupOrderVersion}`"
        v-model:opened="overlayOpenedItems"
        :items="overlayTreeItems"
        density="compact"
        item-value="id"
        item-title="title"
        :selected="[]"
        hide-actions
        separate-roots
        indent-lines
        open-on-click
        fluid
        @update:selected="() => {}"
      >
        <!-- prepend 圖標：僅為 category 顯示 -->
        <template #prepend="{ item, isOpen }">
          <v-icon
            v-if="item.type === 'category'"
            :icon="isOpen ? 'mdi-folder-open' : 'mdi-folder'"
          />
        </template>

        <!-- 自定義標題 -->
        <template #title="{ item }">
          <div v-if="item.type === 'category'" class="category-header">
            <span class="font-weight-bold text-primary">
              {{ item.title }}
            </span>
            <!-- 分組順序調整按鈕 -->
            <div class="d-flex group-order-buttons ml-2">
              <v-btn
                icon
                size="x-small"
                variant="text"
                :disabled="!canMoveGroupUp(item.id)"
                @click.stop="moveGroupUp(item.id)"
              >
                <v-icon size="small">mdi-arrow-up</v-icon>
              </v-btn>
              <v-btn
                icon
                size="x-small"
                variant="text"
                :disabled="!canMoveGroupDown(item.id)"
                @click.stop="moveGroupDown(item.id)"
              >
                <v-icon size="small">mdi-arrow-down</v-icon>
              </v-btn>
            </div>
          </div>
          <!-- 套疊圖層項目的完整內容 -->
          <div v-else-if="item.type === 'overlay' && item.layer" class="overlay-item-container">
            <!-- 圖層名稱行 -->
            <div class="d-flex align-center justify-space-between">
              <div class="d-flex align-center flex-grow-1">
                <v-switch
                  v-model="item.layer.visible"
                  max-width="30"
                  class="ml-2"
                  color="primary"
                  density="compact"
                  hide-details
                  flat
                  @update:model-value="toggleLayerVisibility(item.layer)"
                />
                <span class="text-body-2 font-weight-medium ml-2">
                  {{ item.title }}
                </span>
              </div>
            </div>

            <!-- 透明度控制滑桿和順序調整按鈕（僅在圖層可見時顯示） -->
            <div
              v-if="item.layer.visible"
              class="overlay-opacity-section"
            >
              <div class="d-flex align-center">
                <!-- <span class="opacity-label-compact me-0">透明度</span> -->
                <div class="text-caption">透明度</div>

                <v-slider
                  v-model="item.layer.opacity"
                  class="opacity-slider-compact flex-grow-1"
                  density="compact"
                  :min="0"
                  :max="1"
                  :step="0.1"
                  thumb-label
                  hide-details
                  track-color="green"
                  @update:model-value="updateLayerOpacity(item.layer)"
                >
                  <template #thumb-label="{ modelValue }">
                    {{ Math.round((1 - modelValue) * 100) }}%
                  </template>
                </v-slider>

                <!-- 順序調整按鈕（與透明度滑桿同列） -->
                <div class="d-flex layer-order-buttons ml-2">
                  <v-btn
                    icon
                    size="x-small"
                    variant="text"
                    :disabled="!canMoveUp(item.layer)"
                    @click.stop="moveLayerUp(item.layer)"
                  >
                    <v-icon size="small">mdi-arrow-up</v-icon>
                  </v-btn>
                  <v-btn
                    icon
                    size="x-small"
                    variant="text"
                    :disabled="!canMoveDown(item.layer)"
                    @click.stop="moveLayerDown(item.layer)"
                  >
                    <v-icon size="small">mdi-arrow-down</v-icon>
                  </v-btn>
                </div>
              </div>
            </div>
          </div>
        </template>
      </v-treeview>

      <v-divider class="ma-0 pa-0" />

      <!-- 底圖圖層 TreeView -->
      <v-treeview
        v-model:opened="baselayerOpenedItems"
        :items="baselayerTreeItems"
        density="compact"
        item-value="id"
        item-title="title"
        :selected="[]"
        hide-actions
        indent-lines
        open-on-click
        fluid
        @update:selected="() => {}"
      >
        <!-- prepend 圖標：僅為 category 顯示 -->
        <template #prepend="{ item, isOpen }">
          <v-icon v-if="item.type === 'category'" :icon="isOpen ? 'mdi-folder-open' : 'mdi-folder'"></v-icon>
        </template>

        <!-- 自定義根節點標題 -->
        <template #title="{ item }">
          <div v-if="item.type === 'category'" class="category-header">
            <span class="font-weight-bold text-primary">
              {{ item.title }}
            </span>
          </div>
          <!-- 底圖圖層項目的完整內容 -->
          <div v-else-if="item.type === 'baselayer' && item.layer" class="baselayer-item-container">
            <!-- 圖層名稱行 -->
            <v-radio
              :value="item.layer.name"
              :label="item.title"
              :model-value="getSelectedBaseLayer()"
              color="primary"
              density="compact"
              class="baselayer-radio"
              hide-details
              @click="selectBaseLayer(item.layer.name)"
            />

            <!-- 透明度控制滑桿（緊湊顯示在下方） -->
            <div
              v-if="item.layer.visible"
              class="baselayer-opacity-section"
            >
              <div class="d-flex align-center">
                <!-- <span class="opacity-label-compact me-0">透明度</span> -->
                <div class="text-caption">透明度</div>

                <v-slider
                  v-model="item.layer.opacity"
                  class="opacity-slider-compact flex-grow-1"
                  density="compact"
                  :min="0"
                  :max="1"
                  :step="0.1"
                  thumb-label
                  hide-details
                  track-color="green"
                  @update:model-value="updateLayerOpacity(item.layer)"
                >
                  <template #thumb-label="{ modelValue }">
                    {{ Math.round((1 - modelValue) * 100) }}%
                  </template>
                </v-slider>
              </div>
            </div>
          </div>
        </template>
      </v-treeview>
    </v-list>
  </v-navigation-drawer>
</template>

<script setup lang="ts">
import { computed, ref, nextTick } from 'vue'
import { getLayerGroups } from './config'
import type { MapLayer } from './config'

// TreeView 項目類型定義
interface TreeItem {
  id: string
  title: string
  type: 'category' | 'overlay' | 'baselayer'
  layer?: MapLayer
  children?: TreeItem[]
}

// Props 定義
interface LayerManagementProps {
  visible: boolean
  mapLayers: MapLayer[]
  displayMode: string
}

const props = defineProps<LayerManagementProps>()

// TreeView 展開狀態管理
const overlayOpenedItems = ref<string[]>(['historical-grants', 'auxiliary'])
const baselayerOpenedItems = ref<string[]>(['baselayer'])

// 暴露給父組件的方法：展開自訂圖層分組
const expandCustomGroup = () => {
  if (!overlayOpenedItems.value.includes('custom')) {
    overlayOpenedItems.value.push('custom')
  }
}

// 使用 defineExpose 暴露方法
defineExpose({
  expandCustomGroup
})

// 用於觸發 overlayTreeItems 重新計算的響應式變量
const groupOrderVersion = ref(0)

// Emits 定義
const emit = defineEmits<{
  'update:visible': [visible: boolean]
  'close': []
  'layer-visibility-changed': [layer: MapLayer]
  'layer-opacity-changed': [layer: MapLayer]
  'base-layer-selected': [layerName: string]
  'display-mode-changed': [mode: string]
  'layer-order-changed': [layerId: string, direction: 'up' | 'down']
  'group-order-changed': [groupId: string, direction: 'up' | 'down']
  'add-custom-layer': []
}>()

// 計算屬性
const baseLayers = computed(() =>
  props.mapLayers.filter(l => l.category === 'baselayer')
)

const overlayLayers = computed(() =>
  props.mapLayers.filter(l => l.category === 'overlay')
)

// 套疊圖層 TreeView 數據結構（扁平化顯示，直接顯示分組）
const overlayTreeItems = computed((): TreeItem[] => {
  // 引入 groupOrderVersion 以追蹤分組順序變更
  groupOrderVersion.value // eslint-disable-line @typescript-eslint/no-unused-expressions

  // 獲取所有分組配置
  const groups = getLayerGroups()

  // 直接返回分組，不再包裹在「套疊圖層」下
  return groups.map(groupInfo => {
    // 根據 group 篩選圖層並按 order 排序（降序，order 越大越在上層）
    const layersInGroup = overlayLayers.value
      .filter(layer => layer.group === groupInfo.id)
      .sort((a, b) => b.order - a.order) // 降序：order 大的在前（顯示在上方）

    return {
      id: groupInfo.id,
      title: groupInfo.title,
      type: 'category' as const,
      children: layersInGroup.map((layer) => ({
        id: layer.id, // 使用圖層的唯一 ID 而不是 index
        title: layer.name,
        type: 'overlay' as const,
        layer
      }))
    }
  }).filter(category => category.children.length > 0) // 只保留有圖層的分類
})

// 底圖圖層 TreeView 數據結構（扁平化顯示）
const baselayerTreeItems = computed((): TreeItem[] => [
  {
    id: 'baselayer',
    title: '底圖',
    type: 'category',
    children: baseLayers.value.map((layer, index) => ({
      id: `baselayer-${index}`,
      title: layer.name,
      type: 'baselayer' as const,
      layer
    }))
  }
])

// 圖層可見性切換 (僅處理疊加圖層)
const toggleLayerVisibility = (layer: MapLayer) => {
  console.log('切換疊加圖層:', layer.name, '可見性:', layer.visible)

  // 只處理疊加圖層，底圖圖層有專門的函數處理
  if (layer.category === 'overlay') {
    // 處理補助案件圖層的特殊邏輯（使用 ID 而非名稱）
    if (layer.id === 'grant-grid') {
      // 切換到格網統計模式
      if (layer.visible) {
        emit('display-mode-changed', 'grid')
        // 通過 emit 通知父組件關閉點位圖層
        const pointLayer = props.mapLayers.find(l => l.id === 'grant-points')
        if (pointLayer) {
          pointLayer.visible = false
          emit('layer-visibility-changed', pointLayer)
        }
      }
    } else if (layer.id === 'grant-points') {
      // 切換到點位模式
      if (layer.visible) {
        emit('display-mode-changed', 'points')
        // 通過 emit 通知父組件關閉格網圖層
        const gridLayer = props.mapLayers.find(l => l.id === 'grant-grid')
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
  // 限制最低透明度為 0.1，避免圖層完全不可見
  if (layer.opacity < 0.1) {
    layer.opacity = 0.1
  }
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

// 圖層順序調整
const moveLayerUp = (layer: MapLayer) => {
  emit('layer-order-changed', layer.id, 'up')
}

const moveLayerDown = (layer: MapLayer) => {
  emit('layer-order-changed', layer.id, 'down')
}

// 判斷是否可以上移（order 不是分組內最大值）
const canMoveUp = (layer: MapLayer): boolean => {
  const layersInGroup = overlayLayers.value.filter(l => l.group === layer.group)
  if (layersInGroup.length <= 1) return false
  const maxOrder = Math.max(...layersInGroup.map(l => l.order))
  return layer.order < maxOrder
}

// 判斷是否可以下移（order 不是分組內最小值）
const canMoveDown = (layer: MapLayer): boolean => {
  const layersInGroup = overlayLayers.value.filter(l => l.group === layer.group)
  if (layersInGroup.length <= 1) return false
  const minOrder = Math.min(...layersInGroup.map(l => l.order))
  return layer.order > minOrder
}

// ===== 分組順序調整相關函數 =====

// 獲取實際渲染的分組（有圖層的分組）
const getVisibleGroups = () => {
  const allGroups = getLayerGroups()
  return allGroups.filter(group => {
    const hasLayers = overlayLayers.value.some(layer => layer.group === group.id)
    return hasLayers
  })
}

// 判斷分組是否可以上移（order 不是可見分組中的最小值）
const canMoveGroupUp = (groupId: string): boolean => {
  const visibleGroups = getVisibleGroups()
  if (visibleGroups.length <= 1) return false
  const currentGroup = visibleGroups.find(g => g.id === groupId)
  if (!currentGroup) return false
  const minOrder = Math.min(...visibleGroups.map(g => g.order))
  return currentGroup.order > minOrder
}

// 判斷分組是否可以下移（order 不是可見分組中的最大值）
const canMoveGroupDown = (groupId: string): boolean => {
  const visibleGroups = getVisibleGroups()
  if (visibleGroups.length <= 1) return false
  const currentGroup = visibleGroups.find(g => g.id === groupId)
  if (!currentGroup) return false
  const maxOrder = Math.max(...visibleGroups.map(g => g.order))
  return currentGroup.order < maxOrder
}

// 分組上移
const moveGroupUp = (groupId: string) => {
  emit('group-order-changed', groupId, 'up')
  // 使用 nextTick 延遲觸發重新計算，避免 Vuetify TreeView ID 衝突
  nextTick(() => {
    groupOrderVersion.value++
  })
}

// 分組下移
const moveGroupDown = (groupId: string) => {
  emit('group-order-changed', groupId, 'down')
  // 使用 nextTick 延遲觸發重新計算，避免 Vuetify TreeView ID 衝突
  nextTick(() => {
    groupOrderVersion.value++
  })
}
</script>

<style scoped>
/* 固定 toolbar 在頂部 */
:deep(.v-navigation-drawer__content) {
  display: flex;
  flex-direction: column;
  height: 100%;
}

:deep(.v-toolbar) {
  position: sticky;
  top: 0;
  z-index: 2;
  flex-shrink: 0;
}

:deep(.v-list) {
  flex: 1;
  overflow-y: auto;
}

/* TreeView 分類標題樣式 */
.category-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

/* 分組順序調整按鈕 */
.group-order-buttons {
  gap: 2px;
  opacity: 0.5;
  transition: opacity 0.2s;
}

.category-header:hover .group-order-buttons {
  opacity: 1;
}

.group-order-buttons .v-btn {
  min-width: 24px;
  height: 24px;
}

/* 圖層項目樣式 */
.layer-item {
  font-weight: 500;
}

/* 圖層順序調整按鈕 */
.layer-order-buttons {
  gap: 2px;
  opacity: 0.7;
  transition: opacity 0.2s;
}

.overlay-item-container:hover .layer-order-buttons {
  opacity: 1;
}

.layer-order-buttons .v-btn {
  min-width: 24px;
  height: 24px;
}

/* 套疊圖層透明度區域 - 與文字對齊 */
.overlay-opacity-section {
  margin-top: 0px;
  margin-right: 0px;
  margin-left: 5px;
}

:deep(.baselayer-radio .v-label) {
  font-size: 0.875rem;
  font-weight: 500;
}

/* 底圖圖層透明度區域 - 與文字對齊 */
.baselayer-opacity-section {
  margin-top: 0px;
  margin-right: 30px;
  margin-left: 5px;
}

.opacity-slider-compact :deep(.v-slider-thumb__label) {
  background-color: rgba(0, 0, 0, 0.8);
  color: white !important;
  font-size: 0.7rem;
}
</style>
