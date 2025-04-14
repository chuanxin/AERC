<template>
  <v-container :fluid="isFluid" class="pt-0 container-full-height">
    <v-card class="pa-0 mb-6 map-card">
      <v-card-title class="d-flex align-center pe-2">
        <v-icon icon="mdi-map-marker-path" />
        &nbsp; GIS 圖台
        <v-spacer></v-spacer>
        <v-btn
          density="compact"
          variant="text"
          prepend-icon="mdi-link"
          @click="copyMapLink"
          class="me-2"
        >
          複製地圖連結
        </v-btn>
        <v-btn
          icon
          variant="text"
          @click="toggleFluid"
          :title="isFluid ? '切換為固定寬度' : '切換為全寬模式'"
        >
          <v-icon>{{ isFluid ? 'mdi-arrow-collapse-horizontal' : 'mdi-arrow-expand-horizontal' }}</v-icon>
        </v-btn>
      </v-card-title>
      <v-divider />
      <div id="map" ref="mapContainer" class="map-container">
        <!-- 地圖容器 -->
        <div class="map-controls">
          <v-card class="map-control-panel" elevation="3" rounded="xs">
            <!-- 放大按鈕 -->
            <v-row class="ma-0">
              <v-col class="pa-0">
                <v-btn icon variant="text" @click="zoomIn" density="comfortable">
                  <v-icon>mdi-plus</v-icon>
                </v-btn>
              </v-col>
            </v-row>
            <v-divider />
            <!-- 縮小按鈕 -->
            <v-row class="ma-0">
              <v-col class="pa-0">
                <v-btn icon variant="text" @click="zoomOut" density="comfortable">
                  <v-icon>mdi-minus</v-icon>
                </v-btn>
              </v-col>
            </v-row>
            <!-- 首頁按鈕 -->
            <v-divider />
            <v-row class="ma-0">
              <v-col class="pa-0">
                <v-btn icon variant="text" @click="resetView" density="comfortable">
                  <v-icon>mdi-home</v-icon>
                </v-btn>
              </v-col>
            </v-row>
          </v-card>
        </div>
      </div>
    </v-card>
    <!-- 顯示成功訊息的Snackbar -->
    <v-snackbar v-model="showSnackbar" :timeout="2000" color="success">
      {{ snackbarMessage }}
    </v-snackbar>
  </v-container>
</template>

<script setup>
import { useRouter, useRoute } from 'vue-router';
import 'ol/ol.css';
import Map from 'ol/Map';
import View from 'ol/View';
import {defaults as defaultControls} from 'ol/control/defaults.js';
import TileLayer from 'ol/layer/Tile';
import OSM from 'ol/source/OSM';
import { fromLonLat, toLonLat } from 'ol/proj';

const router = useRouter();
const route = useRoute();

let map = null;
const isFluid = ref(false);
const mapContainer = ref(null);
const showSnackbar = ref(false);
const snackbarMessage = ref('');

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

    // 創建基本的 OSM 圖層
    const osmLayer = new TileLayer({
      source: new OSM(),
      visible: true
    });

    // 創建地圖
    map = new Map({
      target: mapContainer.value,
      layers: [osmLayer],
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

#map {
  position: relative;
  overflow: hidden;
  height: 100%;
}

#map:focus {
  outline: none;
}

.container-full-height {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 150px);
}

.map-card {
  display: flex;
  flex-direction: column;
  flex-grow: 1;
}

.map-container {
  min-height: 500px;
  flex-grow: 1;
  width: 100%;
}

@media (min-height: 700px) {
  .map-container {
    height: 60vh;
  }
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
}

.control-btn {
  width: 40px;
  height: 40px;
}
</style>
