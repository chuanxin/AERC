/**
 * 地圖圖層配置管理（簡化版）
 * 統一的圖層配置來源，集中管理所有圖層和分組
 */

/**
 * OGC 服務類型
 */
export type OGCServiceType = 'WMS' | 'WFS' | 'WMTS'

/**
 * OGC 服務配置
 */
export interface OGCServiceConfig {
  /** 服務類型 */
  type: OGCServiceType
  /** 服務 URL */
  url: string
  /** 圖層名稱 */
  layerName: string
  /** 服務版本 */
  version?: string
  /** 圖層標題（從 Capabilities 解析） */
  title?: string
  /** 圖層摘要（從 Capabilities 解析） */
  abstract?: string
  /** 圖層範圍 */
  extent?: number[]
  /** 其他服務參數 */
  params?: Record<string, any>
  /** 原始 Capabilities 物件（WMTS 必需） */
  rawCapabilities?: any
}

/**
 * 圖層類型定義
 */
export interface MapLayer {
  /** 圖層唯一識別碼 */
  id: string
  /** 圖層顯示名稱 */
  name: string
  /** 圖層類別 */
  category: 'baselayer' | 'overlay'
  /** 套疊圖層分組（僅 overlay 使用） */
  group?: string
  /** 當前可見性 */
  visible: boolean
  /** 當前透明度 (0-1) */
  opacity: number
  /** 圖層描述（可選） */
  description?: string
  /** 排序順序 */
  order: number
  /** OpenLayers 圖層實例 */
  layer?: any
  /** 是否為使用者自訂圖層 */
  isCustom?: boolean
  /** OGC 服務配置（僅自訂圖層使用） */
  ogcConfig?: OGCServiceConfig
}

/**
 * 圖層分組資訊
 */
export interface LayerGroupInfo {
  id: string
  title: string
  icon?: string
  order: number
}

/**
 * 套疊圖層分組定義
 * 集中管理所有分組 - 新增分組只需在此添加
 * 注意：order 值決定分組在 OpenLayers 中的 zIndex 基礎層級
 *      order 值越小，分組在地圖上顯示越靠上層
 */
export const LAYER_GROUPS: Record<string, { title: string; icon?: string; order: number }> = {
  'historical-grants': {
    title: '歷史補助案件',
    icon: 'mdi-history',
    order: 2
  },
  'auxiliary': {
    title: '輔助圖層',
    icon: 'mdi-layers-triple',
    order: 3
  },
  'custom': {
    title: '自訂圖層',
    icon: 'mdi-water',
    order: 1
  }
}

/**
 * 圖層配置 - 單一真實來源
 * 所有圖層在此集中定義和管理
 */
export const MAP_LAYERS: MapLayer[] = [
  // ===== 底圖圖層 =====
  {
    id: 'nlsc-map',
    name: '臺灣通用電子地圖',
    category: 'baselayer',
    visible: true,
    opacity: 1,
    description: '國土測繪中心提供的臺灣通用電子地圖',
    order: 1
  },
  {
    id: 'osm-map',
    name: '開放街圖 (OpenStreetMap)',
    category: 'baselayer',
    visible: false,
    opacity: 1,
    description: '開源社群維護的全球地圖',
    order: 2
  },
  {
    id: 'stamen-watercolor',
    name: '水彩風格底圖',
    category: 'baselayer',
    visible: false,
    opacity: 1,
    description: 'Stamen 水彩風格地圖',
    order: 3
  },

  // ===== 套疊圖層 - 歷史補助案件 =====
  {
    id: 'grant-grid',
    name: '補助案件格網統計圖',
    category: 'overlay',
    group: 'historical-grants',
    visible: true,
    opacity: 0.8,
    description: '補助案件的格網熱度統計圖',
    order: 1
  },
  {
    id: 'grant-points',
    name: '補助案件點位',
    category: 'overlay',
    group: 'historical-grants',
    visible: false,
    opacity: 1,
    description: '補助案件的點位分佈圖',
    order: 2
  },

  // ===== 套疊圖層 - 輔助圖層 =====
  {
    id: 'land-section',
    name: '地段外圍圖(段籍圖)',
    category: 'overlay',
    group: 'auxiliary',
    visible: false,
    opacity: 0.6,
    description: '地籍圖地段外圍線',
    order: 3
  },
  {
    id: 'village-boundary',
    name: '村里界',
    category: 'overlay',
    group: 'auxiliary',
    visible: false,
    opacity: 0.6,
    description: '行政區村里界線',
    order: 4
  },
  {
    id: 'township-boundary',
    name: '鄉鎮市區界',
    category: 'overlay',
    group: 'auxiliary',
    visible: false,
    opacity: 0.6,
    description: '行政區鄉鎮市區界線',
    order: 5
  },
  {
    id: 'public-land',
    name: '公有土地地籍圖',
    category: 'overlay',
    group: 'auxiliary',
    visible: false,
    opacity: 0.6,
    description: '公有土地地籍範圍',
    order: 6
  },
  {
    id: 'orthophoto-general',
    name: '正射影像圖（通用）',
    category: 'overlay',
    group: 'auxiliary',
    visible: false,
    opacity: 0.6,
    description: '正射影像圖通用版本',
    order: 7
  },
  {
    id: 'orthophoto-hybrid',
    name: '正射影像(混合)',
    category: 'overlay',
    group: 'auxiliary',
    visible: false,
    opacity: 0.6,
    description: '正射影像混合版本',
    order: 8
  },
  {
    id: 'urban-land-use',
    name: '都市計畫土地使用分區圖',
    category: 'overlay',
    group: 'auxiliary',
    visible: false,
    opacity: 0.6,
    description: '都市計畫土地使用分區',
    order: 9
  },
  {
    id: 'non-urban-land-use',
    name: '非都市土地使用分區圖',
    category: 'overlay',
    group: 'auxiliary',
    visible: false,
    opacity: 0.6,
    description: '非都市土地使用分區',
    order: 10
  },
  {
    id: 'functional-zone-land-designated-use',
    name: '國土功能分區圖',
    category: 'overlay',
    group: 'auxiliary',
    visible: false,
    opacity: 0.6,
    description: '國土功能分區',
    order: 11
  },
  {
    id: 'indigenous-reserve',
    name: '原住民保留地範圍圖',
    category: 'overlay',
    group: 'auxiliary',
    visible: false,
    opacity: 0.6,
    description: '原住民保留地範圍',
    order: 12
  }
]

/**
 * 根據圖層 ID 查找圖層
 */
export const getLayerById = (id: string): MapLayer | undefined => {
  return MAP_LAYERS.find(layer => layer.id === id)
}

/**
 * 獲取所有分組資訊（按順序排列）
 * order 值越小，在視覺上顯示越靠上方
 */
export const getLayerGroups = (): LayerGroupInfo[] => {
  return Object.entries(LAYER_GROUPS)
    .map(([id, info]) => ({ id, ...info }))
    .sort((a, b) => a.order - b.order)
}

/**
 * 更新分組的順序值
 */
export const updateGroupOrder = (groupId: string, newOrder: number): void => {
  if (LAYER_GROUPS[groupId]) {
    LAYER_GROUPS[groupId].order = newOrder
  }
}

/**
 * 新增自訂圖層到 MAP_LAYERS（執行時期動態新增，不持久化）
 * @param layer 圖層配置
 */
export const addCustomLayer = (layer: MapLayer): void => {
  // 確保圖層標記為自訂且屬於 custom 分組
  layer.isCustom = true
  layer.group = 'custom'
  layer.category = 'overlay'

  // 計算新圖層的 order（custom 分組中最大 order + 1）
  const customLayers = MAP_LAYERS.filter(l => l.group === 'custom')
  const maxOrder = customLayers.length > 0
    ? Math.max(...customLayers.map(l => l.order))
    : 0
  layer.order = maxOrder + 1

  MAP_LAYERS.push(layer)
}

/**
 * 移除自訂圖層
 * @param layerId 圖層 ID
 */
export const removeCustomLayer = (layerId: string): void => {
  const index = MAP_LAYERS.findIndex(l => l.id === layerId && l.isCustom)
  if (index !== -1) {
    MAP_LAYERS.splice(index, 1)
  }
}

/**
 * 取得所有自訂圖層
 */
export const getCustomLayers = (): MapLayer[] => {
  return MAP_LAYERS.filter(l => l.isCustom && l.group === 'custom')
}
