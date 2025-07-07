<template>
  <div
    id="map-viewport"
    ref="mapContainer"
    class="map-viewport"
    style="width: 100%; height: 100%;"
  />
</template>

<script setup lang="ts">
import 'ol/ol.css';
import Map from 'ol/Map';
import View from 'ol/View';
import { defaults as defaultControls } from 'ol/control/defaults.js';
import TileLayer from 'ol/layer/Tile';
import VectorLayer from 'ol/layer/Vector';
import VectorSource from 'ol/source/Vector';
import Cluster from 'ol/source/Cluster';
import { Polygon } from 'ol/geom';
import OSM from 'ol/source/OSM';
import StadiaMaps from 'ol/source/StadiaMaps';
import WMTS from 'ol/source/WMTS';
import WMTSTileGrid from 'ol/tilegrid/WMTS';
import { get as getProjection } from 'ol/proj';
import { fromLonLat, toLonLat } from 'ol/proj';
import { Style, Fill, Stroke, Circle, Text } from 'ol/style';
import { Point } from 'ol/geom';
import { Feature } from 'ol';
import GeoJSON from 'ol/format/GeoJSON';
import type { GeoJsonFeature, GeoJsonFeatureCollection } from '@/types/gis';
import type { FilterCriteria } from '@/utils/frontendFilters';

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

// 定義組件的 Props
interface Props {
  displayMode: 'grid' | 'points';
  geoJsonData: GeoJsonFeatureCollection | null;
  loading?: boolean;
  mapLayers?: MapLayer[];  // 新增 props 接收圖層狀態
  currentFilterCriteria?: FilterCriteria | null;  // 新增篩選條件 prop
}

// 定義組件的 Emits
interface Emits {
  (e: 'map-initialized'): void;
  (e: 'view-changed', params: MapViewParams): void;
  (e: 'feature-clicked', properties: Record<string, any>, type: 'point' | 'grid' | 'cluster'): void;
  (e: 'need-data-refresh', bbox: string, zoomLevel: number): void;
  (e: 'layer-visibility-changed', layerName: string, visible: boolean): void;
  (e: 'layer-opacity-changed', layerName: string, opacity: number): void;
  (e: 'error', message: string): void;
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  geoJsonData: null,
  currentFilterCriteria: null
});

const emit = defineEmits<Emits>();

// 組件內部狀態
const mapContainer = ref<HTMLElement | null>(null);
let map: Map | null = null;
const mapInitialized = ref(false);
const isProgrammaticZoom = ref(false);

// 圖層引用 - 僅儲存 OpenLayers 實例引用
const grantPointsLayer = ref<VectorLayer | null>(null);
const grantGridLayer = ref<VectorLayer | null>(null);

// 使用父組件傳入的圖層狀態，不再自主管理
const mapLayers = computed(() => props.mapLayers || []);

// 追蹤已載入的原始資料，供前端篩選使用
const allLoadedFeatures = ref<GeoJsonFeature[]>([]);
const filteredFeatures = ref<GeoJsonFeature[]>([]);

// 圖層管理方法 - 改為純粹的父組件通知模式
const getSelectedBaseLayer = (): string => {
  const selectedLayer = mapLayers.value.find(layer =>
    layer.category === 'baselayer' && layer.visible
  );
  return selectedLayer ? selectedLayer.name : '';
};

const selectBaseLayer = (layerName: string) => {
  console.log('[MapViewport] 通知父組件選擇底圖:', layerName);
  emit('layer-visibility-changed', layerName, true);
};

const toggleLayerVisibility = (layerName: string) => {
  console.log('[MapViewport] 通知父組件切換圖層可見性:', layerName);
  const layer = mapLayers.value.find(l => l.name === layerName);
  if (layer) {
    emit('layer-visibility-changed', layerName, !layer.visible);
  }
};

const updateLayerOpacity = (layerName: string, opacity: number) => {
  console.log('[MapViewport] 通知父組件更新圖層透明度:', layerName, opacity);
  emit('layer-opacity-changed', layerName, opacity);
};

// 從父組件同步圖層狀態到 OpenLayers 實例
const updateLayersFromParent = (newLayers: MapLayer[]) => {
  console.log('[MapViewport] 同步父組件圖層狀態到 OpenLayers:', newLayers);

  if (!map) {
    console.warn('[MapViewport] 地圖實例未初始化，無法同步圖層狀態');
    return;
  }

  // 直接更新 OpenLayers 圖層實例，不修改 computed mapLayers
  newLayers.forEach((layerState) => {
    // 在當前的 mapLayers 中找到對應的圖層實例
    const localLayer = mapLayers.value.find(layer => layer.name === layerState.name);

    if (localLayer?.layer) {
      console.log(`[MapViewport] 更新 OpenLayers 圖層: ${layerState.name}, visible=${layerState.visible}, opacity=${layerState.opacity}`);
      localLayer.layer.setVisible(layerState.visible);
      localLayer.layer.setOpacity(layerState.opacity);
    } else {
      console.warn(`[MapViewport] 找不到 OpenLayers 圖層實例: ${layerState.name}`);
    }
  });

  // 觸發地圖重新渲染
  map.render();
  console.log('[MapViewport] 地圖已重新渲染');
};

// 暴露給父組件的方法
const mapControls = {
  zoomIn,
  zoomOut,
  resetView,
  getCurrentLocation,
  copyMapLink,
  updateSize: () => map?.updateSize(),
  getMapInstance: () => map,
  getMapLayers: () => mapLayers.value,
  getSelectedBaseLayer,
  selectBaseLayer,
  toggleLayerVisibility,
  updateLayerOpacity,
  updateLayersFromParent  // 新增方法
};

// 地圖控制方法
function zoomIn() {
  if (!map) return;

  const view = map.getView();
  const currentZoom = view.getZoom();
  if (currentZoom !== undefined) {
    console.log('手動放大,從 zoom:', currentZoom, '到', currentZoom + 1);

    isProgrammaticZoom.value = true;
    view.animate({
      zoom: currentZoom + 1,
      duration: 250
    });

    setTimeout(() => {
      isProgrammaticZoom.value = false;
    }, 300);
  }
}

function zoomOut() {
  if (!map) return;

  const view = map.getView();
  const currentZoom = view.getZoom();
  if (currentZoom !== undefined) {
    console.log('手動縮小,從 zoom:', currentZoom, '到', currentZoom - 1);

    isProgrammaticZoom.value = true;
    view.animate({
      zoom: currentZoom - 1,
      duration: 250
    });

    setTimeout(() => {
      isProgrammaticZoom.value = false;
    }, 300);
  }
}

function resetView() {
  if (!map) return;

  console.log('重置視圖到台灣中心點');

  isProgrammaticZoom.value = true;
  map.getView().animate({
    center: fromLonLat([121.0, 23.5]),
    zoom: 7,
    duration: 500
  });

  setTimeout(() => {
    isProgrammaticZoom.value = false;
  }, 600);
}

function getCurrentLocation() {
  if (!navigator.geolocation) {
    emit('error', '您的瀏覽器不支援定位功能');
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

      emit('view-changed', {
        center: [longitude, latitude],
        zoom: 16
      });
    },
    (error) => {
      console.error('定位失敗:', error);
      emit('error', '定位失敗,請檢查位置權限設定');
    },
    {
      enableHighAccuracy: true,
      timeout: 10000,
      maximumAge: 300000
    }
  );
}

function copyMapLink() {
  if (!map) return;

  const view = map.getView();
  const center = view.getCenter();
  const zoom = view.getZoom();

  if (!center || zoom === undefined) return;

  const lonLat = toLonLat(center);
  const url = new URL(window.location.href);
  url.searchParams.set('lon', lonLat[0].toFixed(6));
  url.searchParams.set('lat', lonLat[1].toFixed(6));
  url.searchParams.set('z', zoom.toFixed(2));

  navigator.clipboard.writeText(url.toString())
    .then(() => {
      // 成功複製，可以通過事件通知父組件
    })
    .catch(err => {
      console.error('無法複製連結', err);
      emit('error', '無法複製地圖連結');
    });
}

// 視圖變化處理
const handleViewChange = () => {
  if (!mapInitialized.value || isProgrammaticZoom.value) {
    return;
  }

  if (!map) return;

  const view = map.getView();
  const center = view.getCenter();
  const zoom = view.getZoom();

  if (!center || zoom === undefined) return;

  const lonLat = toLonLat(center);
  emit('view-changed', {
    center: lonLat,
    zoom: zoom
  });
};

// 顯示特徵彈出視窗
const showFeaturePopup = (feature: Feature) => {
  const properties = feature.getProperties();

  let popupType: 'point' | 'grid' | 'cluster' = 'point';

  if (properties.cluster) {
    popupType = 'cluster';
  } else if (properties.gridKey) {
    popupType = 'grid';
  }

  emit('feature-clicked', properties, popupType);
};

// 將 OpenLayers extent 轉換為 bbox 字符串
const extentToBbox = (extent: number[]) => {
  const bottomLeft = toLonLat([extent[0], extent[1]]);
  const topRight = toLonLat([extent[2], extent[3]]);
  return `${bottomLeft[0]},${bottomLeft[1]},${topRight[0]},${topRight[1]}`;
};

// 從 resolution 計算縮放等級
const resolutionToZoomLevel = (resolution: number) => {
  return Math.round(Math.log2(156543.03392804097 / resolution));
};

// OpenLayers 圖層資料載入器 - 修改為請求父組件載入資料
const requestDataForLayer = (
  layerType: 'grid' | 'points',
  extent: number[],
  resolution: number,
  projection: import('ol/proj/Projection').default
) => {
  if (props.loading) {
    console.log(`[${layerType}Layer] 正在載入中,跳過此次請求`);
    return;
  }

  const bbox = extentToBbox(extent);
  const zoomLevel = resolutionToZoomLevel(resolution);

  console.log(`[${layerType}Layer] 請求父組件載入資料:`, {
    bbox,
    zoomLevel,
    resolution,
    projection: projection.getCode()
  });

  if (layerType === 'grid' && props.displayMode !== 'grid') {
    console.log('[GridLayer] 當前非格網統計模式,跳過請求');
    return;
  }

  if (layerType === 'points' && props.displayMode !== 'points') {
    console.log('[PointsLayer] 當前非點位模式,跳過請求');
    return;
  }

  // 向父組件發送資料載入請求
  const forceHighZoom = Math.max(zoomLevel, 15);
  emit('need-data-refresh', bbox, forceHighZoom);
};

// 處理接收到的 GeoJSON 資料
const processGeoJsonData = (vectorSource: VectorSource, layerType: 'grid' | 'points') => {
  if (!props.geoJsonData || !props.geoJsonData.features) {
    console.log(`[${layerType}Layer] 無資料可處理`);
    vectorSource.clear();
    return;
  }

  const features = props.geoJsonData.features;
  console.log(`[${layerType}Layer] 處理 ${features.length} 個特徵`);

  vectorSource.clear();

  if (layerType === 'grid') {
    updateGridLayer(features);
    console.log(`[GridLayer] 處理了 ${features.length} 個點位進行格網統計`);
  } else {
    try {
      const geoJSONFormat = new GeoJSON();
      const olFeatures = geoJSONFormat.readFeatures(props.geoJsonData, {
        featureProjection: 'EPSG:3857'
      });

      vectorSource.addFeatures(olFeatures);
      console.log(`[PointsLayer] 載入了 ${olFeatures.length} 個點位`);
    } catch (error) {
      console.error(`[PointsLayer] GeoJSON 解析失敗:`, error);
      // 降級處理
      const olFeatures = features.map((featureData: GeoJsonFeature) => {
        if (featureData.geometry?.type === 'Point') {
          const coords = featureData.geometry.coordinates as [number, number];
          const point = new Point(fromLonLat(coords));
          return new Feature({
            geometry: point,
            ...featureData.properties
          });
        }
        return null;
      }).filter((f): f is Feature<Point> => f !== null);

      vectorSource.addFeatures(olFeatures);
      console.log(`[PointsLayer] 手動載入了 ${olFeatures.length} 個點位`);
    }
  }
};

// 更新格網統計圖層
const updateGridLayer = (features: GeoJsonFeature[]) => {
  console.log(`[updateGridLayer] 開始處理 ${features.length} 個特徵`);

  if (!grantGridLayer.value || !map) {
    console.log('[updateGridLayer] 缺少格網圖層或地圖實例');
    return;
  }

  const gridSource = grantGridLayer.value.getSource();
  if (!gridSource) {
    console.log('[updateGridLayer] 格網圖層沒有資料源');
    return;
  }

  gridSource.clear();

  if (features.length === 0) {
    console.log('[updateGridLayer] 沒有資料,清空格網');
    return;
  }

  const extent = map.getView().calculateExtent(map.getSize());
  const zoom = map.getView().getZoom() || 7;

  let gridSize: number;
  if (zoom < 8) {
    gridSize = 20000;
  } else if (zoom < 12) {
    gridSize = 10000;
  } else if (zoom < 16) {
    gridSize = 5000;
  } else {
    gridSize = 1000;
  }

  console.log(`[updateGridLayer] 使用格網大小: ${gridSize}, 縮放等級: ${zoom}`);

  const gridStats: Record<string, { count: number; bounds: number[] }> = {};

  let validPointCount = 0;
  const rawFeatures = toRaw(features);
  for (let i = 0; i < rawFeatures.length; i++) {
    const feature = rawFeatures[i];
    if (feature.geometry?.type === 'Point') {
      validPointCount++;
      const coords = feature.geometry.coordinates as [number, number];
      const projectedCoords = fromLonLat(coords);

      const gridX = Math.floor(projectedCoords[0] / gridSize) * gridSize;
      const gridY = Math.floor(projectedCoords[1] / gridSize) * gridSize;
      const gridKey = `${gridX},${gridY}`;

      if (!gridStats[gridKey]) {
        gridStats[gridKey] = {
          count: 0,
          bounds: [gridX, gridY, gridX + gridSize, gridY + gridSize]
        };
      }

      gridStats[gridKey].count++;
    }
  }

  console.log(`[updateGridLayer] 處理了 ${validPointCount} 個有效點位,建立了 ${Object.keys(gridStats).length} 個格網`);

  const gridFeatures: Feature[] = [];
  const allCounts = Object.values(gridStats).map(s => s.count);
  const maxCount = Math.max(...allCounts);
  console.log(`[updateGridLayer] 格網最大案件數: ${maxCount}`);

  Object.entries(gridStats).forEach(([gridKey, stat]) => {
    if (stat.count > 0) {
      const [minX, minY, maxX, maxY] = stat.bounds;
      const polygon = new Polygon([[
        [minX, minY],
        [maxX, minY],
        [maxX, maxY],
        [minX, maxY],
        [minX, minY]
      ]]);

      const intensity = stat.count / maxCount;
      const opacity = Math.max(0.2, intensity * 0.8);

      let fillColor: string;
      if (stat.count >= maxCount * 0.8) {
        fillColor = `rgba(255, 0, 0, ${opacity})`;
      } else if (stat.count >= maxCount * 0.6) {
        fillColor = `rgba(255, 165, 0, ${opacity})`;
      } else if (stat.count >= maxCount * 0.4) {
        fillColor = `rgba(255, 255, 0, ${opacity})`;
      } else if (stat.count >= maxCount * 0.2) {
        fillColor = `rgba(173, 255, 47, ${opacity})`;
      } else {
        fillColor = `rgba(0, 255, 0, ${opacity})`;
      }

      const gridFeature = new Feature({
        geometry: polygon,
        count: stat.count,
        gridKey: gridKey,
        maxCount: maxCount
      });

      gridFeature.setStyle(new Style({
        fill: new Fill({
          color: fillColor
        }),
        stroke: new Stroke({
          color: 'rgba(255, 255, 255, 0.8)',
          width: 1
        }),
        text: new Text({
          text: stat.count.toString(),
          fill: new Fill({
            color: '#000000'
          }),
          stroke: new Stroke({
            color: '#ffffff',
            width: 2
          }),
          font: 'bold 14px Arial',
          textAlign: 'center',
          textBaseline: 'middle'
        })
      }));

      gridFeatures.push(gridFeature);
    }
  });

  gridSource.addFeatures(gridFeatures);
  console.log(`[updateGridLayer] 建立了 ${gridFeatures.length} 個格網,總計 ${features.length} 個點位`);

  if (map) {
    map.render();
  }
};

// 建立聚合點位樣式
const createClusterStyle = (feature: Feature | import('ol/render/Feature').default) => {
  const features = feature.get('features') as Feature[];
  const size = features ? features.length : 1;

  if (size === 1) {
    const singleFeature = features[0];
    const sourceSystem = singleFeature.get('source_system');

    const isNewSystem = sourceSystem === 'new_aerc';
    const fillColor = isNewSystem ? '#3498db' : '#e74c3c';
    const strokeColor = isNewSystem ? '#2980b9' : '#c0392b';

    return new Style({
      image: new Circle({
        radius: 8,
        fill: new Fill({
          color: fillColor
        }),
        stroke: new Stroke({
          color: strokeColor,
          width: 2
        })
      })
    });
  } else {
    let radius = 15;
    let fillColor = '#ff9500';
    let strokeColor = '#e67e00';

    if (size >= 100) {
      radius = 25;
      fillColor = '#e74c3c';
      strokeColor = '#c0392b';
    } else if (size >= 50) {
      radius = 22;
      fillColor = '#f39c12';
      strokeColor = '#d68910';
    } else if (size >= 20) {
      radius = 19;
      fillColor = '#ff9500';
      strokeColor = '#e67e00';
    } else if (size >= 10) {
      radius = 17;
      fillColor = '#ffb74d';
      strokeColor = '#ff9800';
    }

    return new Style({
      image: new Circle({
        radius: radius,
        fill: new Fill({
          color: fillColor
        }),
        stroke: new Stroke({
          color: strokeColor,
          width: 3
        })
      }),
      text: new Text({
        text: size.toString(),
        fill: new Fill({
          color: '#ffffff'
        }),
        stroke: new Stroke({
          color: strokeColor,
          width: 2
        }),
        font: 'bold 14px Arial',
        textAlign: 'center',
        textBaseline: 'middle'
      })
    });
  }
};

// 從URL讀取地圖參數
const readMapParamsFromUrl = (): MapViewParams => {
  const urlParams = new URLSearchParams(window.location.search);
  const lonStr = urlParams.get('lon');
  const latStr = urlParams.get('lat');
  const zStr = urlParams.get('z');

  if (lonStr && latStr && zStr) {
    return {
      center: [parseFloat(lonStr), parseFloat(latStr)],
      zoom: parseFloat(zStr)
    };
  }

  return {
    center: [121.0, 23.5], // 台灣中心點
    zoom: 7
  };
};

// 地圖初始化
async function initMap() {
  try {
    if (!mapContainer.value) {
      console.error('找不到地圖容器元素');
      return;
    }

    const mapParams = readMapParamsFromUrl();

    // 建立 WMTS 瓦片網格配置
    const projection = getProjection('EPSG:3857');
    if (!projection) {
      throw new Error('無法取得 EPSG:3857 投影');
    }

    const resolutions = [
      156543.03392804097, 78271.51696402048, 39135.75848201024, 19567.87924100512,
      9783.93962050256, 4891.96981025128, 2445.98490512564, 1222.99245256282,
      611.49622628141, 305.748113140705, 152.8740565703525, 76.43702828517625,
      38.21851414258813, 19.109257071294063, 9.554628535647032, 4.777314267823516,
      2.388657133911758, 1.194328566955879, 0.5971642834779395, 0.29858214173896974
    ];
    const matrixIds = [];
    for (let z = 0; z < 20; z++) {
      matrixIds.push(z.toString());
    }

    // 建立圖層
    const nlscLayer = new TileLayer({
      source: new WMTS({
        url: 'https://wmts.nlsc.gov.tw/wmts?',
        layer: 'EMAP5',
        matrixSet: 'GoogleMapsCompatible',
        format: 'image/jpeg',
        projection: projection,
        tileGrid: new WMTSTileGrid({
          origin: [-20037508.34278925, 20037508.34278925],
          resolutions: resolutions,
          matrixIds: matrixIds,
        }),
        style: 'default',
        wrapX: true,
        requestEncoding: 'KVP' as const,
      }),
      visible: mapLayers.value.find(l => l.name === '臺灣通用電子地圖')?.visible || false,
      opacity: mapLayers.value.find(l => l.name === '臺灣通用電子地圖')?.opacity || 1
    });

    const osmLayer = new TileLayer({
      source: new OSM(),
      visible: mapLayers.value.find(l => l.name === '開放街圖 (OpenStreetMap)')?.visible || false,
      opacity: mapLayers.value.find(l => l.name === '開放街圖 (OpenStreetMap)')?.opacity || 1
    });

    const stamenLayer = new TileLayer({
      source: new StadiaMaps({
        layer: 'stamen_watercolor',
        retina: false,
        apiKey: 'fb83ebeb-aba3-4c37-ba97-3107a384e553',
      }),
      visible: mapLayers.value.find(l => l.name === '水彩風格底圖')?.visible || false,
      opacity: mapLayers.value.find(l => l.name === '水彩風格底圖')?.opacity || 1
    });

    // 建立補助案件格網統計圖層
    const gridVectorSource = new VectorSource({
      loader: (extent, resolution, projection) => {
        try {
          console.log('[GridLayer] OpenLayers 觸發資料請求');
          requestDataForLayer('grid', extent, resolution, projection);
        } catch (error) {
          console.error('[GridLayer] 請求失敗:', error);
          emit('error', '格網圖層載入失敗');
        }
      },
      strategy: (extent) => {
        const buffer = 0.1;
        const width = extent[2] - extent[0];
        const height = extent[3] - extent[1];
        return [[
          extent[0] - width * buffer,
          extent[1] - height * buffer,
          extent[2] + width * buffer,
          extent[3] + height * buffer
        ]];
      }
    });

    const gridLayer = new VectorLayer({
      source: gridVectorSource,
      visible: mapLayers.value.find(l => l.name === '補助案件格網統計圖')?.visible || false,
      opacity: mapLayers.value.find(l => l.name === '補助案件格網統計圖')?.opacity || 0.8
    });

    // 建立補助案件點位圖層
    const baseVectorSource = new VectorSource({
      format: new GeoJSON(),
      loader: (extent, resolution, projection) => {
        try {
          console.log('[GrantLayer] OpenLayers 觸發資料請求');
          requestDataForLayer('points', extent, resolution, projection);
        } catch (error) {
          console.error('[GrantLayer] 請求失敗:', error);
          emit('error', '點位圖層載入失敗');
        }
      },
      strategy: (extent) => {
        const buffer = 0.1;
        const width = extent[2] - extent[0];
        const height = extent[3] - extent[1];
        return [[
          extent[0] - width * buffer,
          extent[1] - height * buffer,
          extent[2] + width * buffer,
          extent[3] + height * buffer
        ]];
      }
    });

    const clusterSource = new Cluster({
      source: baseVectorSource,
      distance: 50,
      minDistance: 20,
    });

    const grantLayer = new VectorLayer({
      source: clusterSource,
      style: (feature) => {
        return createClusterStyle(feature);
      },
      visible: mapLayers.value.find(l => l.name === '補助案件點位')?.visible || false,
      opacity: mapLayers.value.find(l => l.name === '補助案件點位')?.opacity || 1
    });

    // 儲存圖層引用
    grantGridLayer.value = gridLayer;
    grantPointsLayer.value = grantLayer;

    // 建立圖層實例映射表，用於後續圖層狀態同步
    const layerInstanceMap = new Map();
    layerInstanceMap.set('臺灣通用電子地圖', nlscLayer);
    layerInstanceMap.set('開放街圖 (OpenStreetMap)', osmLayer);
    layerInstanceMap.set('水彩風格底圖', stamenLayer);
    layerInstanceMap.set('補助案件格網統計圖', gridLayer);
    layerInstanceMap.set('補助案件點位', grantLayer);

    // 如果父組件有傳入 mapLayers，則將圖層實例加入其中
    if (props.mapLayers) {
      props.mapLayers.forEach(layerState => {
        const instance = layerInstanceMap.get(layerState.name);
        if (instance && layerState.layer === null) {
          layerState.layer = instance;
        }
      });
    }

    const layers = [nlscLayer, osmLayer, stamenLayer, gridLayer, grantLayer];

    // 創建地圖
    map = new Map({
      target: mapContainer.value,
      layers: layers,
      view: new View({
        center: fromLonLat(mapParams.center),
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

    // 添加點擊事件處理
    map.on('singleclick', (event) => {
      const features = map!.getFeaturesAtPixel(event.pixel);
      if (features.length > 0) {
        const feature = features[0];
        if (feature) {
          showFeaturePopup(feature);
        }
      }
    });

    // 確保地圖正確渲染
    setTimeout(async () => {
      if (map) {
        map.updateSize();

        // 添加地圖移動和縮放事件監聽
        map.on('moveend', handleViewChange);

        let zoomTimeout: ReturnType<typeof setTimeout>;
        map.getView().on('change:resolution', () => {
          clearTimeout(zoomTimeout);
          zoomTimeout = setTimeout(() => {
            handleViewChange();
          }, 500);
        });

        mapInitialized.value = true;

        const initialZoom = map?.getView().getZoom();
        console.log('地圖初始化完成，初始縮放等級:', initialZoom);

        emit('map-initialized');

        // 確保初始化後觸發圖層資料載入
        setTimeout(() => {
          if (props.displayMode === 'grid' && grantGridLayer.value) {
            const gridSource = grantGridLayer.value.getSource();
            if (gridSource) {
              console.log('[InitMap] 初始化完成，觸發格網圖層資料載入');
              gridSource.refresh();
            }
          } else if (props.displayMode === 'points' && grantPointsLayer.value) {
            const clusterSource = grantPointsLayer.value.getSource() as Cluster;
            const baseSource = clusterSource?.getSource();
            if (baseSource) {
              console.log('[InitMap] 初始化完成，觸發點位圖層資料載入');
              baseSource.refresh();
            }
          }
        }, 100);

        console.log('地圖初始化完成，OpenLayers 將使用初始篩選條件載入圖層資料');
      }
    }, 200);

    console.log('地圖初始化成功');
  } catch (error) {
    console.error('地圖初始化失敗:', error);
    emit('error', '地圖初始化失敗');
  }
}

// 更新圖層可見性
const updateLayerVisibility = () => {
  if (grantPointsLayer.value && grantGridLayer.value) {
    if (props.displayMode === 'grid') {
      grantGridLayer.value.setVisible(
        mapLayers.value.find(l => l.name === '補助案件格網統計圖')?.visible || false
      );
      grantPointsLayer.value.setVisible(false);
    } else {
      grantGridLayer.value.setVisible(false);
      grantPointsLayer.value.setVisible(
        mapLayers.value.find(l => l.name === '補助案件點位')?.visible || false
      );
    }
  }
};

// 刷新圖層資料
const refreshLayers = () => {
  if (grantGridLayer.value && props.displayMode === 'grid') {
    console.log('[RefreshLayers] 刷新格網統計圖層');
    const gridSource = grantGridLayer.value.getSource();
    if (gridSource) {
      gridSource.refresh();
    }
  }

  if (grantPointsLayer.value && props.displayMode === 'points') {
    console.log('[RefreshLayers] 刷新點位圖層');
    const clusterSource = grantPointsLayer.value.getSource() as Cluster;
    clusterSource?.getSource()?.refresh();
  }
};

// 強制重新載入資料
const forceDataRefresh = () => {
  if (!map) {
    console.log('[ForceDataRefresh] 地圖尚未初始化');
    return;
  }

  const view = map.getView();
  const extent = view.calculateExtent(map.getSize());
  const resolution = view.getResolution();

  if (resolution) {
    const bbox = extentToBbox(extent);
    const zoomLevel = resolutionToZoomLevel(resolution);

    console.log('[ForceDataRefresh] 強制重新載入資料:', { bbox, zoomLevel });
    emit('need-data-refresh', bbox, zoomLevel);
  }
};

// 監聽窗口大小變化
const handleResize = () => {
  if (map) {
    map.updateSize();
  }
};

// 暴露方法給父組件
defineExpose({
  ...mapControls,
  refreshLayers,
  updateLayerVisibility,
  forceDataRefresh
});

// 生命週期
onMounted(() => {
  // 延遲初始化以確保 DOM 準備就緒
  setTimeout(async () => {
    await initMap();
    window.addEventListener('resize', handleResize);

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
    map.un('moveend', handleViewChange);
    map.setTarget(undefined);
    map = null;
  }
  window.removeEventListener('resize', handleResize);
});

// 監聽 props 變化
watch(() => props.displayMode, () => {
  updateLayerVisibility();
  refreshLayers();
});

watch(() => props.mapLayers, (newLayers) => {
  // 更新圖層可見性和透明度
  console.log('[MapViewport] Watcher triggered for props.mapLayers:', newLayers);
  if (newLayers && newLayers.length > 0 && map) {
    updateLayersFromParent(newLayers);
  }
}, { deep: true, immediate: true });

watch(() => props.geoJsonData, (newData) => {
  // 當接收到新的 GeoJSON 資料時，更新對應的圖層
  if (grantGridLayer.value && props.displayMode === 'grid') {
    const gridSource = grantGridLayer.value.getSource();
    if (gridSource) {
      processGeoJsonData(gridSource, 'grid');
    }
  }

  if (grantPointsLayer.value && props.displayMode === 'points') {
    const clusterSource = grantPointsLayer.value.getSource() as Cluster;
    const baseSource = clusterSource?.getSource();
    if (baseSource) {
      processGeoJsonData(baseSource, 'points');
    }
  }
}, { deep: true });
</script>

<style scoped>
.map-viewport {
  position: relative;
  overflow: hidden;
}

.map-viewport:focus {
  outline: none;
}
</style>
