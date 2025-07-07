<template>
  <!-- 圖層管理面板 -->
  <div
    v-if="visible"
    class="layers-panel"
    :style="{
      left: position.x + 'px',
      top: position.y + 'px',
      maxWidth: layerPanelMaxWidth
    }"
  >
    <v-card
      class="layer-control-panel"
      :class="{ 'dragging': isDragging }"
      elevation="8"
      rounded="lg"
      :max-height="layerPanelMaxHeight"
      :min-height="layerPanelMinHeight"
      height="auto"
    >
      <v-card-title
        class="d-flex align-center justify-space-between pa-0 draggable-header"
        @mousedown="startDrag"
      >
        <div class="d-flex align-center">
          <v-icon
            size="small"
            class="me-2 drag-handle"
          >
            mdi-drag
          </v-icon>
          <span class="text-h6">圖層管理</span>
        </div>
        <v-btn
          icon
          variant="text"
          size="small"
          @click="handleClose"
        >
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-card-title>
      <v-divider />
      <v-card-text
        class="pa-0"
        :style="{ maxHeight: layerPanelContentMaxHeight, overflowY: 'auto' }"
      >
        <v-list
          density="compact"
          :max-height="layerPanelContentMaxHeight"
          style="overflow-y: auto;"
        >
          <!-- 底圖圖層區塊 -->
          <v-list-subheader class="text-primary font-weight-bold">
            底圖圖層
          </v-list-subheader>
          <v-radio-group
            class="px-1"
            :model-value="selectedBaseLayer"
            @update:model-value="handleSelectBaseLayer"
          >
            <div
              v-for="(layer, index) in mapLayers.filter(l => l.category === 'baselayer')"
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

              <!-- 透明度控制滑桿 - 放在圖層名稱下方 -->
              <div
                v-if="layer.visible"
                class="opacity-control-section px-0 pb-2"
              >
                <div class="d-flex align-center">
                  <span class="opacity-label me-2">透明度:</span>
                  <v-slider
                    :model-value="layer.opacity"
                    class="opacity-slider flex-grow-1"
                    :min="0"
                    :max="1"
                    :step="0.01"
                    thumb-label
                    density="compact"
                    hide-details
                    @update:model-value="(value) => handleUpdateLayerOpacity(layer, value)"
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
            v-for="(layer, index) in mapLayers.filter(l => l.category === 'overlay')"
            :key="`overlay-${index}`"
          >
            <v-list-item class="px-3 py-2">
              <template #prepend>
                <v-switch
                  :model-value="layer.visible"
                  color="primary"
                  class="pr-5"
                  density="compact"
                  hide-details
                  @update:model-value="(value) => handleToggleLayerVisibility(layer, value)"
                />
              </template>

              <v-list-item-title class="text-body-2 font-weight-medium">
                {{ layer.name }}
              </v-list-item-title>
            </v-list-item>

            <!-- 透明度控制滑桿 - 放在圖層名稱下方 -->
            <div
              v-if="layer.visible"
              class="opacity-control-section px-0 pb-2"
            >
              <div class="d-flex align-center">
                <span class="opacity-label me-2">透明度:</span>
                <v-slider
                  :model-value="layer.opacity"
                  class="opacity-slider flex-grow-1"
                  :min="0"
                  :max="1"
                  :step="0.01"
                  thumb-label
                  density="compact"
                  hide-details
                  @update:model-value="(value) => handleUpdateLayerOpacity(layer, value)"
                >
                  <template #thumb-label="{ modelValue }">
                    {{ Math.round(modelValue * 100) }}%
                  </template>
                </v-slider>
              </div>
            </div>

            <!-- 分隔線 -->
            <v-divider
              v-if="index < mapLayers.filter(l => l.category === 'overlay').length - 1"
            />
          </div>
        </v-list>
      </v-card-text>
    </v-card>
  </div>
</template>

<script setup lang="ts">
// 定義MapLayer介面
export interface MapLayer {
  name: string;
  visible: boolean;
  opacity: number;
  category: 'baselayer' | 'overlay';
  layer: any | null; // OpenLayers layer
}

// 組件props
const props = defineProps<{
  visible: boolean;
  mapLayers: MapLayer[];
  selectedBaseLayer: string;
}>();

// 組件事件
const emit = defineEmits<{
  'update:visible': [value: boolean];
  'update:mapLayers': [layers: MapLayer[]];
  'select-base-layer': [layerName: string];
  'toggle-layer-visibility': [layer: MapLayer];
  'update-layer-opacity': [layer: MapLayer];
}>();

// 面板位置狀態
const position = ref({ x: 10, y: 10 });

// 面板拖拽相關
const isDragging = ref(false);
const dragOffset = ref({ x: 0, y: 0 });

// 面板高度控制 - 使用 computed 屬性實現響應式
const layerPanelMaxHeight = computed(() => {
  if (typeof window === 'undefined') return '400px';

  const viewportHeight = window.innerHeight;
  const safeMargin = 120;
  const maxHeight = Math.min(viewportHeight - safeMargin, 600);

  return `${maxHeight}px`;
});

const layerPanelMinHeight = computed(() => {
  if (typeof window === 'undefined') return '200px';

  const viewportHeight = window.innerHeight;

  // 根據視窗高度調整最小高度
  if (viewportHeight < 600) {
    return '150px';
  } else if (viewportHeight < 800) {
    return '200px';
  } else {
    return '250px';
  }
});

// 圖層面板內容區域最大高度
const layerPanelContentMaxHeight = computed(() => {
  if (typeof window === 'undefined') return '300px';

  const viewportHeight = window.innerHeight;
  const safeMargin = 180; // 包含標題欄和按鈕的高度
  const maxHeight = Math.min(viewportHeight - safeMargin, 500);

  return `${maxHeight}px`;
});

// 圖層面板最大寬度
const layerPanelMaxWidth = computed(() => {
  if (typeof window === 'undefined') return '350px';

  const viewportWidth = window.innerWidth;

  // 根據視窗寬度調整面板寬度
  if (viewportWidth < 768) {
    return `${Math.min(viewportWidth - 40, 300)}px`;
  } else if (viewportWidth < 1024) {
    return '320px';
  } else {
    return '350px';
  }
});

// 圖層面板拖拽功能
const startDrag = (event: MouseEvent) => {
  isDragging.value = true;

  // 計算滑鼠相對於面板當前位置的偏移量
  dragOffset.value = {
    x: event.clientX - position.value.x,
    y: event.clientY - position.value.y
  };

  // 添加全局監聽器
  document.addEventListener('mousemove', onDrag);
  document.addEventListener('mouseup', stopDrag);

  // 防止文字選擇
  event.preventDefault();
};

const onDrag = (event: MouseEvent) => {
  if (!isDragging.value) return;

  // 計算新位置
  const newX = event.clientX - dragOffset.value.x;
  const newY = event.clientY - dragOffset.value.y;

  // 獲取視窗邊界
  const maxX = window.innerWidth - 300; // 面板寬度約300px
  const maxY = window.innerHeight - 400; // 面板高度約400px

  // 限制在視窗範圍內
  position.value = {
    x: Math.max(0, Math.min(newX, maxX)),
    y: Math.max(0, Math.min(newY, maxY))
  };
};

const stopDrag = () => {
  isDragging.value = false;

  // 移除全局監聽器
  document.removeEventListener('mousemove', onDrag);
  document.removeEventListener('mouseup', stopDrag);
};

// 選擇底圖圖層
const handleSelectBaseLayer = (layerName: string | null) => {
  if (layerName) {
    emit('select-base-layer', layerName);
  }
};

// 圖層可見性切換
const handleToggleLayerVisibility = (layer: MapLayer, value: boolean | null) => {
  if (value !== null) {
    console.log('[MapLayerPanel] 切換圖層可見性:', layer.name, 'to', value);
    emit('toggle-layer-visibility', layer);
  }
};

// 更新圖層透明度
const handleUpdateLayerOpacity = (layer: MapLayer, newOpacity: number | null) => {
  if (newOpacity !== null) {
    const updatedLayer = { ...layer, opacity: newOpacity };
    console.log('[MapLayerPanel] 更新圖層透明度:', layer.name, newOpacity);
    emit('update-layer-opacity', updatedLayer);
  }
};

// 關閉面板
const handleClose = () => {
  emit('update:visible', false);
};

// 初始化
// 從 localStorage 讀取保存的面板位置，如果沒有則使用默認位置
const getSavedPanelPosition = () => {
  // 默認位置：右上方，工具列左邊
  // 使用 rightOffset 來計算右邊距離，確保在工具列左邊
  const rightOffset = 90;  // 工具列寬度 + 間距
  const topOffset = 10;    // 頂部間距
  return {
    x: Math.max(10, (window.innerWidth || 1200) - 300 - rightOffset),
    y: topOffset
  };
};

// 初始化面板位置
position.value = getSavedPanelPosition();

// 監聽窗口大小變化，調整面板位置
window.addEventListener('resize', () => {
  // 檢查面板位置是否需要調整（避免面板超出視窗）
  if (props.visible) {
    const maxX = window.innerWidth - 300; // 面板寬度約300px
    const maxY = window.innerHeight - 400; // 面板高度約400px

    if (position.value.x > maxX || position.value.y > maxY) {
      position.value = {
        x: Math.max(0, Math.min(position.value.x, maxX)),
        y: Math.max(0, Math.min(position.value.y, maxY))
      };
    }
  }
});

// 組件卸載時清理事件監聽器
onUnmounted(() => {
  document.removeEventListener('mousemove', onDrag);
  document.removeEventListener('mouseup', stopDrag);
  window.removeEventListener('resize', handleResize);
});

// 監聽窗口大小變化
const handleResize = () => {
  // 檢查面板位置是否需要調整（避免面板超出視窗）
  if (props.visible) {
    const maxX = window.innerWidth - 300; // 面板寬度約300px
    const maxY = window.innerHeight - 400; // 面板高度約400px

    if (position.value.x > maxX || position.value.y > maxY) {
      position.value = {
        x: Math.max(0, Math.min(position.value.x, maxX)),
        y: Math.max(0, Math.min(position.value.y, maxY))
      };
    }
  }
};
</script>

<style scoped>
/* 圖層管理面板樣式 */
.layers-panel {
  position: absolute;
  z-index: 1001;
  max-width: 350px; /* 稍微增加最大寬度 */
  min-width: 250px;
  width: auto; /* 讓寬度根據內容調整 */
  transition: none; /* 取消過渡動畫，以便拖拽更流暢 */
}

.layer-control-panel {
  background-color: rgba(255, 255, 255, 0.95) !important;
  max-height: calc(100vh - 120px); /* 使用視窗高度減去安全邊距 */
  min-height: 200px; /* 設定最小高度 */
  height: auto; /* 自動調整高度 */
  overflow-y: auto;
  user-select: none; /* 防止拖拽時選中文字 */
  width: auto; /* 讓寬度根據內容調整 */
  display: flex;
  flex-direction: column;
}

.layer-control-panel .v-card-text {
  flex: 1;
  overflow-y: auto;
  max-height: none;
}

.layer-control-panel .v-list {
  padding: 0;
}

.layer-control-panel .v-list-subheader {
  background-color: rgba(248, 248, 248, 0.9);
  padding: 12px 16px;
  margin: 0;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  font-weight: 600;
  letter-spacing: 0.5px;
}

.layer-control-panel .v-list-item {
  min-height: 48px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  transition: background-color 0.2s ease;
}

.layer-control-panel .v-list-item:hover {
  background-color: rgba(0, 0, 0, 0.02);
}

.layer-control-panel .v-list-item:last-child {
  border-bottom: none;
}

.draggable-header {
  cursor: move;
  user-select: none;
}

.draggable-header:hover {
  background-color: rgba(0, 0, 0, 0.05);
}

.layer-control-panel.dragging {
  opacity: 0.8;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3) !important;
  cursor: move;
}

.drag-handle {
  opacity: 0.6;
  color: #666;
}

/* 透明度控制區域優化 */
.opacity-control-section {
  background-color: rgba(248, 248, 248, 0.8);
  margin: 0 8px;
  border-radius: 4px;
  padding: 8px 12px;
  transition: background-color 0.2s ease;
}

.opacity-control-section:hover {
  background-color: rgba(240, 240, 240, 0.9);
}

/* 自定義滾動條樣式 */
.layer-control-panel::-webkit-scrollbar {
  width: 6px;
}

.layer-control-panel::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.1);
  border-radius: 3px;
}

.layer-control-panel::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.3);
  border-radius: 3px;
}

.layer-control-panel::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 0, 0, 0.5);
}
</style>
