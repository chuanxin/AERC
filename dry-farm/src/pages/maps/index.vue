<template>
  <div class="fill-height d-flex flex-column">
    <v-card class="flex-grow-1 d-flex flex-column">
      <v-divider />
      <div
        id="map"
        ref="mapContainer"
        class="map-container"
        style="min-height: 0;"
      >
        <!-- 地圖視口組件 -->
        <MapViewport
          ref="mapViewportRef"
          :display-mode="displayMode"
          :geo-json-data="geoJsonData"
          :loading="gisLoading"
          :map-layers="mapLayers"
          :current-filter-criteria="currentFilterCriteria"
          @map-initialized="handleMapInitialized"
          @view-changed="handleViewChanged"
          @feature-clicked="handleFeatureClicked"
          @need-data-refresh="handleNeedDataRefresh"
          @layer-visibility-changed="handleLayerVisibilityChanged"
          @layer-opacity-changed="handleLayerOpacityChanged"
          @error="showError"
        />

        <!-- 引入篩選工具欄組件 -->
        <MapFilterPanel
          :loading="gisLoading"
          :year-range="yearRange"
          @quick-filter-change="handleQuickFilterChange"
          @filter-apply="handleFilterApply"
          @filter-reset="handleFilterReset"
          @update:year-range="handleYearRangeUpdate"
        />

        <!-- 引入圖層管理面板組件 -->
        <MapLayerPanel
          v-model:visible="showLayersPanel"
          :map-layers="getMapLayers"
          :selected-base-layer="getSelectedBaseLayer"
          @select-base-layer="selectBaseLayer"
          @toggle-layer-visibility="toggleLayerVisibility"
          @update-layer-opacity="updateLayerOpacity"
        />

        <!-- 引入控制按鈕面板組件 -->
        <MapToolkit
          :is-drawing="isDrawing"
          :is-measuring="isMeasuring"
          @toggle-layers="toggleLayers"
          @get-location="getCurrentLocation"
          @toggle-draw="toggleDraw"
          @toggle-measure="toggleMeasure"
          @zoom-in="zoomIn"
          @zoom-out="zoomOut"
          @reset-view="resetView"
        />

        <!-- 引入彈出信息組件 -->
        <MapPopup
          v-model:visible="showPopup"
          :type="popupType"
          :properties="popupProperties"
        />
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
import { useGisStore } from '@/stores/gis';
import { storeToRefs } from 'pinia';
import type { LocationQueryValue } from 'vue-router';
import type { GeoJsonFeatureCollection } from '@/types/gis';
import {
  applyFrontendFilters,
  getInitialOverlayLoadingParams as getInitialParams,
  type FilterCriteria
} from '@/utils/frontendFilters';
import type { GisFilters, SearchPointsParams } from '@/types/gis';

// 引入子組件
import MapViewport from './components/MapViewport.vue';
import MapLayerPanel from './components/MapLayerPanel.vue';
import MapPopup from './components/MapPopup.vue';
import MapToolkit from './components/MapToolkit.vue';
import MapFilterPanel from './components/MapFilterPanel.vue';

// 定義圖層介面
export interface MapLayer {
  name: string;
  visible: boolean;
  opacity: number;
  category: 'baselayer' | 'overlay';
  layer: any | null;
}

// 定義地圖視圖參數接口
export interface MapViewParams {
  center: [number, number];
  zoom: number;
}

const router = useRouter();
const route = useRoute();

// 使用 GIS Store
const gisStore = useGisStore();
const {
  statistics,
  loading: gisLoading,
  displayMode,
  yearRange,
  currentPointCount,
  availableSourceSystems,
} = storeToRefs(gisStore);

// 組件引用
const mapContainer = ref(null);
const mapViewportRef = ref<InstanceType<typeof MapViewport> | null>(null);

// 界面狀態
const isFluid = ref(false);
const showSnackbar = ref(false);
const snackbarMessage = ref('');
const isDrawing = ref(false);
const isMeasuring = ref(false);
const showLayersPanel = ref(false);

// 彈出信息相關
const showPopup = ref(false);
const popupType = ref<'point' | 'grid' | 'cluster'>('point');
const popupProperties = ref<Record<string, any>>({});

// 當前篩選條件
const currentFilterCriteria = ref<FilterCriteria | null>(null);

// 圖層管理狀態 - 在主組件中統一管理
const mapLayers = ref<MapLayer[]>([
  {
    name: '臺灣通用電子地圖',
    visible: true,
    opacity: 1,
    category: 'baselayer',
    layer: null
  },
  {
    name: '開放街圖 (OpenStreetMap)',
    visible: false,
    opacity: 1,
    category: 'baselayer',
    layer: null
  },
  {
    name: '水彩風格底圖',
    visible: false,
    opacity: 1,
    category: 'baselayer',
    layer: null
  },
  {
    name: '補助案件格網統計圖',
    visible: true,
    opacity: 1,
    category: 'overlay',
    layer: null
  },
  {
    name: '補助案件點位',
    visible: false,
    opacity: 1,
    category: 'overlay',
    layer: null
  }
]);

// 圖層管理方法 - 直接操作本地狀態
const getMapLayers = computed(() => {
  return mapLayers.value;
});

const getSelectedBaseLayer = computed((): string => {
  const selectedLayer = mapLayers.value.find(layer =>
    layer.category === 'baselayer' && layer.visible
  );
  return selectedLayer ? selectedLayer.name : '';
});

const selectBaseLayer = (layerName: string | null) => {
  console.log('[Index] 選擇底圖:', layerName);
  if (!layerName) return;

  // 關閉所有底圖圖層
  mapLayers.value.forEach(layer => {
    if (layer.category === 'baselayer') {
      layer.visible = false;
    }
  });

  // 啟用選中的底圖圖層
  const selectedLayer = mapLayers.value.find(layer =>
    layer.category === 'baselayer' && layer.name === layerName
  );

  if (selectedLayer) {
    selectedLayer.visible = true;
    console.log('[Index] 底圖切換成功:', selectedLayer.name);
  }

  console.log('[Index] 當前圖層狀態:', mapLayers.value.map(l => ({ name: l.name, visible: l.visible, opacity: l.opacity })));

  // 響應式更新 - 不再需要手動調用 updateLayersFromParent
  // MapViewport 的 watcher 會自動響應 mapLayers 的變化
};

const toggleLayerVisibility = (layer: MapLayer) => {
  console.log('[Index] 切換圖層可見性:', layer.name);

  // 找到對應的圖層並切換狀態
  const targetLayer = mapLayers.value.find(l => l.name === layer.name);
  if (!targetLayer) {
    console.error('[Index] 找不到目標圖層:', layer.name);
    return;
  }

  targetLayer.visible = !targetLayer.visible;
  console.log('[Index] 圖層可見性已更新:', targetLayer.name, '=', targetLayer.visible);

  // 處理疊加圖層的互斥邏輯
  if (targetLayer.category === 'overlay') {
    if (targetLayer.name === '補助案件格網統計圖' && targetLayer.visible) {
      // 切換到格網模式，關閉點位圖層
      const pointLayer = mapLayers.value.find(l => l.name === '補助案件點位');
      if (pointLayer) {
        pointLayer.visible = false;
        console.log('[Index] 關閉點位圖層，啟用格網圖層');
      }
      displayMode.value = 'grid';
    } else if (targetLayer.name === '補助案件點位' && targetLayer.visible) {
      // 切換到點位模式，關閉格網圖層
      const gridLayer = mapLayers.value.find(l => l.name === '補助案件格網統計圖');
      if (gridLayer) {
        gridLayer.visible = false;
        console.log('[Index] 關閉格網圖層，啟用點位圖層');
      }
      displayMode.value = 'points';
    }
  }

  console.log('[Index] 當前圖層狀態:', mapLayers.value.map(l => ({ name: l.name, visible: l.visible, opacity: l.opacity })));

  // 響應式更新 - MapViewport watcher 會自動處理
};

const updateLayerOpacity = (layer: MapLayer) => {
  console.log('[Index] 更新圖層透明度:', layer.name, layer.opacity);

  // 找到對應的圖層並更新透明度
  const targetLayer = mapLayers.value.find(l => l.name === layer.name);
  if (!targetLayer) {
    console.error('[Index] 找不到目標圖層:', layer.name);
    return;
  }

  targetLayer.opacity = layer.opacity;
  console.log('[Index] 圖層透明度已更新:', targetLayer.name, '=', targetLayer.opacity);

  console.log('[Index] 當前圖層狀態:', mapLayers.value.map(l => ({ name: l.name, visible: l.visible, opacity: l.opacity })));

  // 響應式更新 - MapViewport watcher 會自動處理
};

// 處理來自 MapViewport 的圖層事件
const handleLayerVisibilityChanged = (layerName: string, visible: boolean) => {
  console.log(`圖層 ${layerName} 可見性變更為: ${visible}`);

  // 根據圖層變化更新顯示模式
  if (layerName === '補助案件格網統計圖' && visible) {
    displayMode.value = 'grid';
  } else if (layerName === '補助案件點位' && visible) {
    displayMode.value = 'points';
  }
};

const handleLayerOpacityChanged = (layerName: string, opacity: number) => {
  console.log(`圖層 ${layerName} 透明度變更為: ${opacity}`);
};

// 測試函數 - 手動測試圖層控制
const testLayerControls = () => {
  console.log('=== 測試圖層控制 ===');
  console.log('當前圖層狀態:', mapLayers.value.map(l => ({ name: l.name, visible: l.visible, opacity: l.opacity })));

  // 測試底圖切換
  selectBaseLayer('開放街圖 (OpenStreetMap)');

  // 測試疊加圖層切換
  const gridLayer = mapLayers.value.find(l => l.name === '補助案件格網統計圖');
  if (gridLayer) {
    toggleLayerVisibility(gridLayer);
  }
};

// 將測試函數暴露到全域，方便在瀏覽器控制台測試
if (typeof window !== 'undefined') {
  (window as any).testLayerControls = testLayerControls;
  (window as any).mapLayers = mapLayers;
  (window as any).selectBaseLayer = selectBaseLayer;
  (window as any).toggleLayerVisibility = toggleLayerVisibility;
}

// GeoJSON 資料管理
const geoJsonData = ref<GeoJsonFeatureCollection | null>(null);

// 用於追蹤已載入的原始資料,供前端篩選使用
const allLoadedFeatures = ref<any[]>([]);
const filteredFeatures = ref<any[]>([]);

// 切換 fluid 狀態的方法
const toggleFluid = () => {
  isFluid.value = !isFluid.value;
  localStorage.setItem('preferFluid', String(isFluid.value));

  nextTick(() => {
    setTimeout(() => {
      if (mapViewportRef.value) {
        mapViewportRef.value.updateSize();
      }
    }, 100);
  });
};

// 圖層管理相關方法
const toggleLayers = () => {
  showLayersPanel.value = !showLayersPanel.value;
};

// 舊的圖層管理方法已移除，現在委派給 MapViewport

// 地圖控制方法 - 委派給 MapViewport
const getCurrentLocation = () => {
  if (mapViewportRef.value) {
    mapViewportRef.value.getCurrentLocation();
  }
};

const zoomIn = () => {
  if (mapViewportRef.value) {
    mapViewportRef.value.zoomIn();
  }
};

const zoomOut = () => {
  if (mapViewportRef.value) {
    mapViewportRef.value.zoomOut();
  }
};

const resetView = () => {
  if (mapViewportRef.value) {
    mapViewportRef.value.resetView();
  }
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

// 複製當前地圖連結
const copyMapLink = () => {
  if (mapViewportRef.value) {
    mapViewportRef.value.copyMapLink();
    snackbarMessage.value = '地圖連結已複製到剪貼板';
    showSnackbar.value = true;
  }
};

// MapViewport 事件處理方法
const handleMapInitialized = async () => {
  console.log('地圖初始化完成');

  try {
    // 初始化 GIS Store
    await gisStore.initialize();

    // 使用統一的初始載入條件設置 GIS Store
    const initialParams = getInitialParams();
    const initialYearRange: [number, number] = [initialParams.apply_year_min!, initialParams.apply_year_max!];
    yearRange.value.current = initialYearRange;
    await gisStore.updateYearRange(initialYearRange);

    console.log(`[InitMap] 使用統一初始載入條件設定年度範圍: 民國${initialParams.apply_year_min}-${initialParams.apply_year_max}年`);
  } catch (error) {
    console.error('GIS Store 初始化失敗:', error);
    showError('GIS 系統初始化失敗');
  }
};

const handleViewChanged = (params: MapViewParams) => {
  // 更新 URL
  const query = {
    ...route.query,
    lon: params.center[0].toFixed(6),
    lat: params.center[1].toFixed(6),
    z: params.zoom.toFixed(2)
  };
  router.replace({ query });
};

const handleFeatureClicked = (properties: Record<string, any>, type: 'point' | 'grid' | 'cluster') => {
  popupType.value = type;
  popupProperties.value = properties;
  showPopup.value = true;
};

const handleNeedDataRefresh = async (bbox: string, zoomLevel: number) => {
  console.log('處理資料載入請求:', { bbox, zoomLevel });

  try {
    // 檢查是否有詳細篩選條件
    const hasDetailedFilters = currentFilterCriteria.value && !!(
      currentFilterCriteria.value.applicantName ||
      currentFilterCriteria.value.landSection ||
      currentFilterCriteria.value.landNumber ||
      currentFilterCriteria.value.caseNumber ||
      currentFilterCriteria.value.sourceSystem
    );

    if (hasDetailedFilters) {
      // 有詳細篩選條件時，使用搜尋 API
      console.log('檢測到詳細篩選條件，使用搜尋 API');

      const criteria = currentFilterCriteria.value!;
      const searchParams: SearchPointsParams = {};

      // 將篩選條件轉換為搜尋參數
      if (criteria.applicantName) {
        searchParams.applicant_name = criteria.applicantName;
      }
      if (criteria.landSection) {
        searchParams.land_section = criteria.landSection;
      }
      if (criteria.caseNumber) {
        searchParams.case_number = criteria.caseNumber;
      }
      // 注意：searchGrantCases API 不支援 land_number 和 sourceSystem

      console.log('使用詳細篩選條件搜尋:', searchParams);

      // 調用搜尋 API
      await gisStore.searchCases(bbox, searchParams);
    } else {
      // 沒有詳細篩選條件時，使用一般載入 API
      console.log('使用一般載入 API');

      // 獲取統一的初始載入條件參數
      const initialParams = getInitialParams();

      // 構建查詢參數
      const queryParams: Partial<Omit<GisFilters, 'bbox'>> = {
        ...initialParams,
        apply_year_min: yearRange.value.current[0],
        apply_year_max: yearRange.value.current[1],
      };

      // 調用一般載入 API
      await gisStore.loadGrantLocations(bbox, zoomLevel, queryParams);
    }

    // 更新 geoJsonData，這會觸發 MapViewport 的 watch
    geoJsonData.value = gisStore.lastLoadedData;

    if (geoJsonData.value?.features) {
      // 保存原始資料供前端篩選使用
      allLoadedFeatures.value = [...geoJsonData.value.features];
      filteredFeatures.value = [...geoJsonData.value.features];
      console.log(`已載入 ${geoJsonData.value.features.length} 個特徵`);
    }
  } catch (error) {
    console.error('資料載入失敗:', error);
    showError('資料載入失敗');
  }
};

// 事件處理方法 - 處理快速篩選變更
const handleQuickFilterChange = (value: string) => {
  console.log('快速篩選變更:', value);
  applyFrontendFilter(value);
};

// 事件處理方法 - 處理套用篩選
const handleFilterApply = async (criteria: FilterCriteria) => {
  console.log('套用篩選條件:', criteria);

  try {
    // 保存當前篩選條件
    currentFilterCriteria.value = { ...criteria };

    const hasDetailedFilters = !!(
      criteria.applicantName ||
      criteria.landSection ||
      criteria.landNumber ||
      criteria.caseNumber ||
      criteria.sourceSystem
    );

    // 清空現有資料
    allLoadedFeatures.value = [];
    filteredFeatures.value = [];
    geoJsonData.value = null;

    console.log(hasDetailedFilters ? '檢測到詳細篩選條件,將觸發搜尋API' : '僅有年度範圍變更,將觸發一般API');

    // 強制重新載入資料 - 這會觸發 handleNeedDataRefresh 並根據 currentFilterCriteria 選擇正確的 API
    if (mapViewportRef.value) {
      mapViewportRef.value.forceDataRefresh();
    }

    snackbarMessage.value = '篩選條件已套用,重新載入資料';
    showSnackbar.value = true;
  } catch (error) {
    console.error('套用篩選失敗:', error);
    showError('套用篩選失敗');
  }
};

// 事件處理方法 - 處理重置篩選
const handleFilterReset = () => {
  console.log('重置篩選條件');

  // 清除保存的篩選條件
  currentFilterCriteria.value = null;

  allLoadedFeatures.value = [];
  filteredFeatures.value = [];
  refreshLayerData();

  const initialParams = getInitialParams();
  snackbarMessage.value = `篩選條件已重置到初始條件(民國${initialParams.apply_year_min}年)`;
  showSnackbar.value = true;
};

// 事件處理方法 - 處理年度範圍更新
const handleYearRangeUpdate = async (range: [number, number]) => {
  console.log('年度範圍更新:', range);

  try {
    yearRange.value.current = range;
    await gisStore.updateYearRange(range);
    refreshLayerData();
  } catch (error) {
    console.error('年度範圍更新失敗:', error);
    showError('年度範圍更新失敗');
  }
};

// 前端篩選處理函數
const applyFrontendFilter = (quickFilterValue: string = '') => {
  console.log('執行前端篩選, quickFilter:', quickFilterValue);
  console.log('目前已載入的特徵數量:', allLoadedFeatures.value.length);

  if (allLoadedFeatures.value.length === 0) {
    console.log('沒有已載入的資料,執行初始載入');
    refreshLayerData();
    return;
  }

  const detailedFilters: Partial<FilterCriteria> = {
    yearStart: yearRange.value.current[0],
    yearEnd: yearRange.value.current[1]
  };

  filteredFeatures.value = applyFrontendFilters(
    allLoadedFeatures.value,
    quickFilterValue,
    detailedFilters
  );

  console.log(`篩選結果: ${filteredFeatures.value.length}/${allLoadedFeatures.value.length} 個特徵`);

  // 更新 geoJsonData 以反映篩選結果
  if (geoJsonData.value) {
    geoJsonData.value = {
      ...geoJsonData.value,
      features: filteredFeatures.value,
      meta: {
        ...geoJsonData.value.meta,
        count: filteredFeatures.value.length
      }
    };
  }

  if (quickFilterValue) {
    const message = `快速篩選「${quickFilterValue}」找到 ${filteredFeatures.value.length} 筆結果`;
    snackbarMessage.value = message;
    showSnackbar.value = true;
  }
};

// 顯示錯誤訊息
const showError = (message: string) => {
  snackbarMessage.value = message;
  showSnackbar.value = true;
};

// 刷新圖層資料
const refreshLayerData = () => {
  if (mapViewportRef.value) {
    mapViewportRef.value.refreshLayers();
  }
};

// 輔助函數:安全地將 LocationQueryValue 轉換為字符串
const queryValueToString = (value: LocationQueryValue | LocationQueryValue[]): string | null => {
  if (typeof value === 'string') return value;
  if (Array.isArray(value) && value.length > 0 && typeof value[0] === 'string') return value[0];
  return null;
};

onMounted(() => {
  // 從 localStorage 讀取 fluid 偏好設置
  const preferFluid = localStorage.getItem('preferFluid');
  if (preferFluid !== null) {
    isFluid.value = preferFluid === 'true';
  }

  // 獲取統一的疊加圖層初始載入條件參數
  const initialParams = getInitialParams();

  // 同步年度範圍到 GIS Store
  const yearRangeArray: [number, number] = [initialParams.apply_year_min!, initialParams.apply_year_max!];
  yearRange.value.current = yearRangeArray;

  console.log(`[Init] 設置疊加圖層初始載入條件: 年度範圍 ${initialParams.apply_year_min}-${initialParams.apply_year_max}`);
});

// 監視 fluid 狀態變化，以便在切換時更新地圖
watch(isFluid, () => {
  nextTick(() => {
    setTimeout(() => {
      if (mapViewportRef.value) {
        mapViewportRef.value.updateSize();
      }
    }, 100);
  });
});

// 監聽路由變化，如果URL參數變了，更新地圖
watch(() => route.query, (newQuery) => {
  // 由 MapViewport 內部處理 URL 參數變化
  const lonStr = queryValueToString(newQuery.lon);
  const latStr = queryValueToString(newQuery.lat);
  const zStr = queryValueToString(newQuery.z);

  if (lonStr && latStr && zStr && mapViewportRef.value) {
    // 可以通過 props 傳遞給 MapViewport 或者讓 MapViewport 自己處理
    console.log('URL 參數變化，地圖視圖將自動更新');
  }
}, { deep: true });

// 監聽顯示模式變化
watch(displayMode, async (newMode) => {
  try {
    await gisStore.updateDisplayMode(newMode);
    if (mapViewportRef.value) {
      mapViewportRef.value.updateLayerVisibility();
      mapViewportRef.value.refreshLayers();
    }
  } catch (error) {
    console.error('顯示模式變更失敗:', error);
    showError('顯示模式變更失敗');
  }
});
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
  height: calc(100vh - 151px);
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
  height: 0;
  min-height: 0;
  overflow: hidden;
}
</style>
