<template>
  <div class="fill-height d-flex flex-column">
    <v-card class="flex-grow-1 d-flex flex-column">
      <!-- <v-card-title class="d-flex align-center pe-2">
        <v-icon icon="mdi-map-marker-path" />
        &nbsp; GIS 圖台
        <v-spacer />
        <v-btn
          density="compact"
          variant="text"
          prepend-icon="mdi-link"
          class="me-2"
          @click="copyMapLink"
        >
          複製地圖連結
        </v-btn>
        <v-btn
          icon
          variant="text"
          :title="isFluid ? '切換為固定寬度' : '切換為全寬模式'"
          @click="toggleFluid"
        >
          <v-icon>{{ isFluid ? 'mdi-arrow-collapse-horizontal' : 'mdi-arrow-expand-horizontal' }}</v-icon>
        </v-btn>
      </v-card-title> -->
      <v-divider />
      <div
        id="map"
        ref="mapContainer"
        class="map-container"
        style="min-height: 0;"
      >
        <!-- 地圖容器 -->

        <!-- 圖層管理面板 -->
        <div
          v-if="showLayersPanel"
          class="layers-panel"
          :style="{
            left: panelPosition.x + 'px',
            top: panelPosition.y + 'px'
          }"
        >
          <v-card
            class="layer-control-panel"
            :class="{ 'dragging': isDragging }"
            elevation="8"
            rounded="lg"
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
                @click="toggleLayers"
              >
                <v-icon>mdi-close</v-icon>
              </v-btn>
            </v-card-title>
            <v-divider />
            <v-card-text class="pa-0">
              <v-list density="compact">
                <div
                  v-for="(layer, index) in mapLayers"
                  :key="index"
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

                  <!-- 透明度控制滑桿 - 放在圖層名稱下方 -->
                  <div
                    v-if="layer.visible"
                    class="opacity-control-section px-3 pb-2"
                  >
                    <div class="d-flex align-center">
                      <span class="opacity-label me-2">透明度:</span>
                      <v-slider
                        v-model="layer.opacity"
                        :min="0"
                        :max="1"
                        :step="0.01"
                        thumb-label
                        density="compact"
                        hide-details
                        class="opacity-slider flex-grow-1"
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
                    v-if="index < mapLayers.length - 1"
                  />
                </div>
              </v-list>
            </v-card-text>
          </v-card>
        </div>

        <div class="map-controls">
          <v-card
            class="map-control-panel"
            elevation="3"
            rounded="lg"
          >
            <!-- 圖層按鈕 -->
            <v-row class="ma-0">
              <v-col class="pa-0 text-center">
                <v-btn
                  :title="'圖層管理'"
                  class="control-btn-vertical"
                  size="large"
                  variant="text"
                  rounded="lg"
                  @click="toggleLayers"
                >
                  <template #default>
                    <div class="d-flex flex-column align-center">
                      <v-icon size="40" class="mb-0">mdi-layers</v-icon>
                      <span class="btn-text">圖層</span>
                    </div>
                  </template>
                </v-btn>
              </v-col>
            </v-row>
            <v-divider />

            <!-- 定位按鈕 -->
            <v-row class="ma-0">
              <v-col class="pa-0 text-center">
                <v-btn
                  :title="'我的位置'"
                  class="control-btn-vertical"
                  size="large"
                  variant="text"
                  rounded="lg"
                  @click="getCurrentLocation"
                >
                  <template #default>
                    <div class="d-flex flex-column align-center">
                      <v-icon size="40" class="mb-0">mdi-crosshairs-gps</v-icon>
                      <span class="btn-text">定位</span>
                    </div>
                  </template>
                </v-btn>
              </v-col>
            </v-row>
            <v-divider />

            <!-- 展繪按鈕 -->
            <v-row class="ma-0">
              <v-col class="pa-0 text-center">
                <v-btn
                  :title="'繪圖工具'"
                  class="control-btn-vertical"
                  size="large"
                  variant="text"
                  rounded="lg"
                  :color="isDrawing ? 'primary' : ''"
                  @click="toggleDraw"
                >
                  <template #default>
                    <div class="d-flex flex-column align-center">
                      <v-icon size="40" class="mb-0">mdi-draw</v-icon>
                      <span class="btn-text">展繪</span>
                    </div>
                  </template>
                </v-btn>
              </v-col>
            </v-row>
            <v-divider />

            <!-- 量測按鈕 -->
            <v-row class="ma-0">
              <v-col class="pa-0 text-center">
                <v-btn
                  :title="'測量工具'"
                  class="control-btn-vertical"
                  size="large"
                  variant="text"
                  rounded="lg"
                  :color="isMeasuring ? 'primary' : ''"
                  @click="toggleMeasure"
                >
                  <template #default>
                    <div class="d-flex flex-column align-center">
                      <v-icon size="40" class="mb-0">mdi-ruler</v-icon>
                      <span class="btn-text">量測</span>
                    </div>
                  </template>
                </v-btn>
              </v-col>
            </v-row>
            <v-divider />

            <!-- 放大按鈕 -->
            <v-row class="ma-0">
              <v-col class="pa-0 text-center">
                <v-btn
                  :title="'放大'"
                  class="control-btn-vertical"
                  size="large"
                  variant="text"
                  rounded="lg"
                  @click="zoomIn"
                >
                  <template #default>
                    <div class="d-flex flex-column align-center">
                      <v-icon size="40" class="mb-0">mdi-plus</v-icon>
                      <span class="btn-text">放大</span>
                    </div>
                  </template>
                </v-btn>
              </v-col>
            </v-row>
            <v-divider />

            <!-- 縮小按鈕 -->
            <v-row class="ma-0">
              <v-col class="pa-0 text-center">
                <v-btn
                  :title="'縮小'"
                  class="control-btn-vertical"
                  size="large"
                  variant="text"
                  rounded="lg"
                  @click="zoomOut"
                >
                  <template #default>
                    <div class="d-flex flex-column align-center">
                      <v-icon size="40" class="mb-0">mdi-minus</v-icon>
                      <span class="btn-text">縮小</span>
                    </div>
                  </template>
                </v-btn>
              </v-col>
            </v-row>
            <v-divider />

            <!-- 首頁按鈕 -->
            <v-row class="ma-0">
              <v-col class="pa-0 text-center">
                <v-btn
                  :title="'回到原始視圖'"
                  class="control-btn-vertical"
                  size="large"
                  variant="text"
                  rounded="lg"
                  @click="resetView"
                >
                  <template #default>
                    <div class="d-flex flex-column align-center">
                      <v-icon size="40" class="mb-0">mdi-home</v-icon>
                      <span class="btn-text">重置</span>
                    </div>
                  </template>
                </v-btn>
              </v-col>
            </v-row>
          </v-card>
        </div>
      </div>
    </v-card>
    <!-- 顯示成功訊息的Snackbar -->
    <v-snackbar
      v-model="showSnackbar"
      :timeout="2000"
      color="success"
    >
      {{ snackbarMessage }}
    </v-snackbar>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, watch, onUnmounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import 'ol/ol.css';
import Map from 'ol/Map';
import View from 'ol/View';
import {defaults as defaultControls} from 'ol/control/defaults.js';
import TileLayer from 'ol/layer/Tile';
import OSM from 'ol/source/OSM';
import StadiaMaps from 'ol/source/StadiaMaps';
import TileWMS from 'ol/source/TileWMS';
import { fromLonLat, toLonLat } from 'ol/proj';
import type { LocationQueryValue } from 'vue-router';

// 定義圖層介面
interface MapLayer {
  name: string;
  visible: boolean;
  opacity: number;
  layer: any | null; // 使用 any 以避免複雜的 OpenLayers 類型問題
}

const router = useRouter();
const route = useRoute();

// 定義地圖變數，使用具體的 Map 型別
let map: Map | null = null;
const isFluid = ref(false);
const mapContainer = ref(null);
const showSnackbar = ref(false);
const snackbarMessage = ref('');
const isDrawing = ref(false);
const isMeasuring = ref(false);
const showLayersPanel = ref(false);

// 圖層面板拖拽相關
const isDragging = ref(false);
const dragOffset = ref({ x: 0, y: 0 });

// 從 localStorage 讀取保存的面板位置，如果沒有則使用默認位置
const getSavedPanelPosition = () => {
  const saved = localStorage.getItem('layersPanelPosition');
  if (saved) {
    try {
      return JSON.parse(saved);
    } catch (error) {
      console.warn('無法解析保存的面板位置:', error);
    }
  }
  // 默認位置：右上方，工具列左邊
  // 使用 rightOffset 來計算右邊距離，確保在工具列左邊
  const rightOffset = 90;  // 工具列寬度 + 間距
  const topOffset = 10;    // 頂部間距
  return {
    x: Math.max(10, (window.innerWidth || 1200) - 300 - rightOffset),
    y: topOffset
  };
};

const panelPosition = ref(getSavedPanelPosition());

// 圖層管理相關
const mapLayers = ref<MapLayer[]>([
  {
    name: '臺灣通用電子地圖',
    visible: true,
    opacity: 1,
    layer: null
  },
  {
    name: 'OpenStreetMap',
    visible: false,
    opacity: 1,
    layer: null
  },
  {
    name: 'Stamen Watercolor',
    visible: false,
    opacity: 1,
    layer: null
  },
]);

// 用於追蹤地圖是否已完全初始化
const mapInitialized = ref(false);

// 切換 fluid 狀態的方法
const toggleFluid = () => {
  isFluid.value = !isFluid.value;
  // 保存用戶偏好到 localStorage
  localStorage.setItem('preferFluid', String(isFluid.value));

  // 在布局變化後更新地圖大小
  nextTick(() => {
    setTimeout(() => {
      if (map) {
        map.updateSize();
      }
    }, 100);
  });
};

const toggleLayers = () => {
  showLayersPanel.value = !showLayersPanel.value;
};

// 圖層面板拖拽功能
const startDrag = (event: MouseEvent) => {
  isDragging.value = true;

  // 計算滑鼠相對於面板當前位置的偏移量
  dragOffset.value = {
    x: event.clientX - panelPosition.value.x,
    y: event.clientY - panelPosition.value.y
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
  panelPosition.value = {
    x: Math.max(0, Math.min(newX, maxX)),
    y: Math.max(0, Math.min(newY, maxY))
  };
};

const stopDrag = () => {
  isDragging.value = false;

  // 保存面板位置到 localStorage
  localStorage.setItem('layersPanelPosition', JSON.stringify(panelPosition.value));

  // 移除全局監聽器
  document.removeEventListener('mousemove', onDrag);
  document.removeEventListener('mouseup', stopDrag);
};

// 圖層可見性切換
const toggleLayerVisibility = (layer: MapLayer) => {
  console.log('切換圖層:', layer.name, '可見性:', layer.visible);
  if (layer.layer) {
    layer.layer.setVisible(layer.visible);
    console.log('圖層', layer.name, '已設置為:', layer.visible ? '可見' : '隱藏');
  } else {
    console.error('圖層對象不存在:', layer.name);
  }
};

// 更新圖層透明度
const updateLayerOpacity = (layer: MapLayer) => {
  if (layer.layer) {
    layer.layer.setOpacity(layer.opacity);
  }
};

// 定位功能
const getCurrentLocation = () => {
  if (!navigator.geolocation) {
    snackbarMessage.value = '您的瀏覽器不支援定位功能';
    showSnackbar.value = true;
    return;
  }

  navigator.geolocation.getCurrentPosition(
    (position) => {
      if (!map) return;

      const { longitude, latitude } = position.coords;
      const center = fromLonLat([longitude, latitude]);

      map.getView().animate({
        center: center,
        zoom: 16,
        duration: 1000
      });

      snackbarMessage.value = '已定位到您的位置';
      showSnackbar.value = true;
    },
    (error) => {
      console.error('定位失敗:', error);
      snackbarMessage.value = '定位失敗，請檢查位置權限設定';
      showSnackbar.value = true;
    },
    {
      enableHighAccuracy: true,
      timeout: 10000,
      maximumAge: 300000
    }
  );
};

// 展繪功能
const toggleDraw = () => {
  isDrawing.value = !isDrawing.value;
  if (isMeasuring.value) {
    isMeasuring.value = false;
  }

  console.log('展繪工具:', isDrawing.value ? '啟用' : '停用');
  snackbarMessage.value = isDrawing.value ? '展繪工具已啟用' : '展繪工具已停用';
  showSnackbar.value = true;

  // TODO: 實作繪圖功能
};

// 量測功能
const toggleMeasure = () => {
  isMeasuring.value = !isMeasuring.value;
  if (isDrawing.value) {
    isDrawing.value = false;
  }

  console.log('量測工具:', isMeasuring.value ? '啟用' : '停用');
  snackbarMessage.value = isMeasuring.value ? '量測工具已啟用' : '量測工具已停用';
  showSnackbar.value = true;

  // TODO: 實作測量功能
};

const zoomIn = () => {
  if (!map) return;

  const view = map.getView();
  const currentZoom = view.getZoom();
  if (currentZoom !== undefined) {
    view.animate({
      zoom: currentZoom + 1,
      duration: 250
    });
  }
};

const zoomOut = () => {
  if (!map) return;

  const view = map.getView();
  const currentZoom = view.getZoom();
  if (currentZoom !== undefined) {
    view.animate({
      zoom: currentZoom - 1,
      duration: 250
    });
  }
};

const resetView = () => {
  if (!map) return;

  map.getView().animate({
    center: fromLonLat([121.0, 23.5]), // 台灣中心點
    zoom: 7,
    duration: 500
  });
};

// 複製當前地圖連結
const copyMapLink = () => {
  if (!map) return;

  const view = map.getView();
  const center = view.getCenter();
  const zoom = view.getZoom();

  if (!center || zoom === undefined) return;

  // 將坐標從 EPSG:3857 轉換為經緯度 (EPSG:4326)
  const lonLat = toLonLat(center);

  // 構建新URL
  const url = new URL(window.location.href);
  url.searchParams.set('lon', lonLat[0].toFixed(6));
  url.searchParams.set('lat', lonLat[1].toFixed(6));
  url.searchParams.set('z', zoom.toFixed(2));

  // 複製到剪貼板
  navigator.clipboard.writeText(url.toString())
    .then(() => {
      snackbarMessage.value = '地圖連結已複製到剪貼板';
      showSnackbar.value = true;
    })
    .catch(err => {
      console.error('無法複製連結', err);
    });
};

// 監聽窗口大小變化
const handleResize = () => {
  if (map) {
    map.updateSize();
  }

  // 檢查面板位置是否需要調整（避免面板超出視窗）
  if (showLayersPanel.value) {
    const maxX = window.innerWidth - 300; // 面板寬度約300px
    const maxY = window.innerHeight - 400; // 面板高度約400px

    if (panelPosition.value.x > maxX || panelPosition.value.y > maxY) {
      panelPosition.value = {
        x: Math.max(0, Math.min(panelPosition.value.x, maxX)),
        y: Math.max(0, Math.min(panelPosition.value.y, maxY))
      };
      // 保存調整後的位置
      localStorage.setItem('layersPanelPosition', JSON.stringify(panelPosition.value));
    }
  }
};

// 監聽地圖移動事件，更新URL
const updateUrlFromMap = () => {
  if (!map || !mapInitialized.value) return;

  const view = map.getView();
  const center = view.getCenter();
  const zoom = view.getZoom();

  if (!center || zoom === undefined) return;

  // 將坐標從 EPSG:3857 轉換為經緯度 (EPSG:4326)
  const lonLat = toLonLat(center);

  // 使用 replaceState 而不是 history.pushState，以避免創建大量歷史記錄
  const query = {
    ...route.query,
    lon: lonLat[0].toFixed(6),
    lat: lonLat[1].toFixed(6),
    z: zoom.toFixed(2)
  };

  router.replace({ query });
};

// 輔助函數：安全地將 LocationQueryValue 轉換為字符串
const queryValueToString = (value: any): string | null => {
  if (typeof value === 'string') return value;
  if (Array.isArray(value) && value.length > 0) return value[0];
  return null;
};

// 從URL讀取地圖參數
const readMapParamsFromUrl = () => {
  const lonStr = queryValueToString(route.query.lon);
  const latStr = queryValueToString(route.query.lat);
  const zStr = queryValueToString(route.query.z);

  if (lonStr && latStr && zStr) {
    return {
      center: fromLonLat([parseFloat(lonStr), parseFloat(latStr)]),
      zoom: parseFloat(zStr)
    };
  }

  return {
    center: fromLonLat([121.0, 23.5]), // 台灣中心點
    zoom: 7
  };
};

onMounted(() => {
  // 從 localStorage 讀取 fluid 偏好設置
  const preferFluid = localStorage.getItem('preferFluid');
  if (preferFluid !== null) {
    isFluid.value = preferFluid === 'true';
  }

  // 確保面板位置在視窗尺寸確定後正確設置
  nextTick(() => {
    if (!localStorage.getItem('layersPanelPosition')) {
      // 如果沒有保存的位置，重新計算默認位置
      const rightOffset = 90;
      const topOffset = 10;
      panelPosition.value = {
        x: Math.max(10, window.innerWidth - 300 - rightOffset),
        y: topOffset
      };
    }
  });

  // 確保 CSS 已正確載入
  const link = document.createElement('link');
  link.rel = 'stylesheet';
  link.href = 'https://cdn.jsdelivr.net/npm/ol@v10.5.0/ol.css';
  document.head.appendChild(link);

  // 延遲一點點初始化地圖，確保 DOM 和 CSS 都準備好了
  setTimeout(() => {
    initMap();

    // 添加 resize 事件監聽器
    window.addEventListener('resize', handleResize);

    // 設置一個 MutationObserver 來監視容器大小變化
    const observer = new ResizeObserver(() => {
      if (map) {
        map.updateSize();
      }
    });

    if (mapContainer.value) {
      observer.observe(mapContainer.value);
    }
  }, 100);
});

onUnmounted(() => {
  if (map) {
    // 移除地圖移動監聽
    map.un('moveend', updateUrlFromMap);

    map.setTarget(undefined);
    map = null;
  }

  // 移除事件監聽器
  window.removeEventListener('resize', handleResize);

  // 清理拖拽事件監聽器
  document.removeEventListener('mousemove', onDrag);
  document.removeEventListener('mouseup', stopDrag);
});

function initMap() {
  try {
    // 確認元素存在
    if (!mapContainer.value) {
      console.error('找不到地圖容器元素');
      return;
    }

    // 從 URL 獲取初始地圖參數
    const mapParams = readMapParamsFromUrl();

    // 創建圖層並關聯到 mapLayers
    const nlscLayer = new TileLayer({
      source: new TileWMS({
        url: 'https://wms.nlsc.gov.tw/wms',
        params: {
          'LAYERS': 'EMAP5',
          'VERSION': '1.1.1',
          'FORMAT': 'image/png',
          'TRANSPARENT': true,
          'SRS': 'EPSG:3857'
        },
        serverType: 'geoserver',
      }),
      visible: mapLayers.value[0].visible,
      opacity: mapLayers.value[0].opacity
    });

    const osmLayer = new TileLayer({
      source: new OSM(),
      visible: mapLayers.value[1].visible
    });

    const stamenLayer = new TileLayer({
      source: new StadiaMaps({
        layer: 'stamen_watercolor',
        retina: false,
      }),
      visible: mapLayers.value[2].visible,
    });

    const layers = [nlscLayer, osmLayer, stamenLayer];

    // 關聯圖層到 mapLayers 數據結構
    mapLayers.value[0].layer = nlscLayer;
    mapLayers.value[1].layer = osmLayer;
    mapLayers.value[2].layer = stamenLayer;

    // 設置初始可見性和透明度
    mapLayers.value.forEach((layerInfo) => {
      if (layerInfo.layer) {
        layerInfo.layer.setVisible(layerInfo.visible);
        layerInfo.layer.setOpacity(layerInfo.opacity);
        console.log(`圖層 ${layerInfo.name} 初始化: 可見=${layerInfo.visible}, 透明度=${layerInfo.opacity}`);
      }
    });

    // 創建地圖
    map = new Map({
      target: mapContainer.value,
      layers: layers,
      view: new View({
        center: mapParams.center,
        zoom: mapParams.zoom,
        minZoom: 5,
        maxZoom: 19
      }),
      controls: defaultControls({
        zoom: false,
        attribution: true,
        rotate: false
      })
    });

    // 確保地圖正確渲染
    setTimeout(() => {
      if (map) {
        map.updateSize();

        // 添加地圖移動監聽，更新 URL
        map.on('moveend', updateUrlFromMap);

        // 標記地圖已初始化完成
        mapInitialized.value = true;
      }
    }, 200);

    console.log('地圖初始化成功');
  } catch (error) {
    console.error('地圖初始化失敗:', error);
  }
}

// 監視 fluid 狀態變化，以便在切換時更新地圖
watch(isFluid, () => {
  nextTick(() => {
    setTimeout(() => {
      if (map) {
        map.updateSize();
      }
    }, 100);
  });
});

// 監聽路由變化，如果URL參數變了，更新地圖
watch(() => route.query, (newQuery) => {
  if (!map || !mapInitialized.value) return;

  const lonStr = queryValueToString(newQuery.lon);
  const latStr = queryValueToString(newQuery.lat);
  const zStr = queryValueToString(newQuery.z);

  if (lonStr && latStr && zStr) {
    const view = map.getView();
    const center = fromLonLat([parseFloat(lonStr), parseFloat(latStr)]);

    view.animate({
      center: center,
      zoom: parseFloat(zStr),
      duration: 500
    });
  }
}, { deep: true });
</script>

<style>
.ol-zoom {
  display: none !important;
}

.ol-control button {
  background-color: rgba(40, 40, 40, 0.8) !important;
}

.ol-control button:hover {
  background-color: rgba(40, 40, 40, 1) !important;
}

.fill-height {
  height: 100vh;
}

#map {
  position: relative;
  overflow: hidden;
  height: 100%;
  width: 100%;
}

#map:focus {
  outline: none;
}

.container-full-height {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 151px); /* 扣除 NavBar 高度，通常是 64px */
  padding: 0 !important;
  margin: 0 !important;
  max-width: 100% !important;
  overflow: hidden;
}

.map-card {
  display: flex;
  flex-direction: column;
  flex-grow: 1;
  height: 100%;
  border-radius: 0 !important;
  overflow: hidden;
}

.map-container {
  flex-grow: 1;
  width: 100%;
  height: 0; /* 讓 flex-grow 控制高度 */
  min-height: 0; /* 移除 min-height: 100vh */
  overflow: hidden;
}

/* 針對不同螢幕尺寸調整 NavBar 高度 */
/* @media (max-width: 960px) {
  .container-full-height {
    height: calc(100vh - 103px);
  }
} */

/* 自定義地圖控制按鈕樣式 */
.map-controls {
  position: absolute;
  top: 10px;
  right: 10px;
  z-index: 1000;
}

/* 圖層管理面板樣式 */
.layers-panel {
  position: absolute;
  z-index: 1001;
  max-width: 300px;
  min-width: 250px;
  transition: none; /* 取消過渡動畫，以便拖拽更流暢 */
}

.layer-control-panel {
  background-color: rgba(255, 255, 255, 0.95) !important;
  max-height: 400px;
  overflow-y: auto;
  user-select: none; /* 防止拖拽時選中文字 */
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

.opacity-control-section {
  background-color: rgba(248, 248, 248, 0.8);
  margin: 0 8px;
  border-radius: 4px;
}

.opacity-label {
  font-size: 12px;
  color: #666;
  white-space: nowrap;
  min-width: 50px;
}

.opacity-control {
  width: 120px;
  margin-left: 12px;
}

.opacity-slider {
  margin: 0;
}

.map-control-panel {
  background-color: rgba(255, 255, 255, 0.9) !important;
  min-width: 70px; /* 增加寬度以容納文字 */
}

.control-btn-vertical {
  width: 100% !important;
  height: auto !important;
  min-height: 60px !important;
  padding: 8px 4px !important;
}

.control-btn-vertical .v-btn__content {
  flex-direction: column !important;
  height: auto !important;
}

.btn-text {
  font-size: 14px;
  color: inherit;
  line-height: 1;
  font-weight: 500;
  white-space: nowrap;
}

/* 當按鈕處於 active 狀態時，文字也會繼承顏色 */
.v-btn--active .btn-text {
  color: inherit;
}

.btn-label {
  font-size: 14px;
  color: rgba(0, 0, 0, 0.6);
  line-height: 1;
  font-weight: 500;
  margin-top: 2px;
}

.control-btn {
  width: 40px;
  height: 40px;
}
</style>
