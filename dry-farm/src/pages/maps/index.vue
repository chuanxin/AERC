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
import { useRouter, useRoute } from 'vue-router';
import 'ol/ol.css';
import Map from 'ol/Map';
import View from 'ol/View';
import {defaults as defaultControls} from 'ol/control/defaults.js';
import TileLayer from 'ol/layer/Tile';
import OSM from 'ol/source/OSM';
import StadiaMaps from 'ol/source/StadiaMaps';
import TileWMS from 'ol/source/TileWMS';  // 添加 WMS 導入
import { fromLonLat, toLonLat } from 'ol/proj';

const router = useRouter();
const route = useRoute();

let map = null;
const isFluid = ref(false);
const mapContainer = ref(null);
const showSnackbar = ref(false);
const snackbarMessage = ref('');
const isDrawing = ref(false);
const isMeasuring = ref(false);
const showLayersPanel = ref(false);

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
  console.log('圖層管理');
  // TODO: 實作圖層管理面板
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
  view.animate({
    zoom: currentZoom + 1,
    duration: 250
  });
};

const zoomOut = () => {
  if (!map) return;

  const view = map.getView();
  const currentZoom = view.getZoom();
  view.animate({
    zoom: currentZoom - 1,
    duration: 250
  });
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

  if (!center) return;

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
};

// 監聽地圖移動事件，更新URL
const updateUrlFromMap = () => {
  if (!map || !mapInitialized.value) return;

  const view = map.getView();
  const center = view.getCenter();
  const zoom = view.getZoom();

  if (!center) return;

  // 將坐標從 EPSG:3857 轉換為經緯度 (EPSG:4326)
  const lonLat = toLonLat(center);

  // 使用 replaceState 而不是 history.pushState，以避免創建大量歷史記錄
  const query = {
    ...route.query,
    lon: lonLat[0].toFixed(6),
    lat: lonLat[1].toFixed(6),
    z: zoom.toFixed(2)
  };

  router.replace({ query }, { replace: true });
};

// 從URL讀取地圖參數
const readMapParamsFromUrl = () => {
  const { lon, lat, z } = route.query;

  if (lon && lat && z) {
    return {
      center: fromLonLat([parseFloat(lon), parseFloat(lat)]),
      zoom: parseFloat(z)
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

    const layers = [
      new TileLayer({
        source: new OSM(),
        visible: false
      }),
      new TileLayer({
        source: new StadiaMaps({
          // layer: 'stamen_terrain',
          // layer: 'stamen_toner',
          layer: 'stamen_watercolor',
          retina: false,
        }),
        visible: false,
      }),
      // 臺灣通用電子地圖透明 WMS 圖層
      new TileLayer({
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
        visible: true,
        opacity: 0.8  // 設定透明度
      })
    ];

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

  const { lon, lat, z } = newQuery;

  if (lon && lat && z) {
    const view = map.getView();
    const center = fromLonLat([parseFloat(lon), parseFloat(lat)]);

    view.animate({
      center: center,
      zoom: parseFloat(z),
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
  } */
}

/* 自定義地圖控制按鈕樣式 */
.map-controls {
  position: absolute;
  top: 10px;
  right: 10px;
  z-index: 1000;
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
