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
 * 填充圖案類型
 */
export type FillPatternType =
  | 'diagonal'        // 斜線 /
  | 'diagonal-reverse' // 反斜線 \
  | 'cross-diagonal'  // 交叉斜線 X
  | 'horizontal'      // 水平線 ≡
  | 'vertical'        // 垂直線 ‖
  | 'grid'            // 網格 #
  | 'dots'            // 點狀 ·
  | 'dots-dense'      // 密集點狀

/**
 * 圖層圖例項目
 */
export interface LayerLegendItem {
  /** 顏色（HEX 或 RGB，填充色） */
  color: string
  /** 標籤文字 */
  label: string
  /** 圖例方塊內的簡寫文字（可選） */
  text?: string
  /** 是否只顯示邊框（不填充顏色） */
  borderOnly?: boolean
  /** 邊框顏色（當 borderOnly 為 true 時使用，預設使用 color） */
  borderColor?: string
  /** 文字顏色（預設為黑色或白色，根據背景自動判斷） */
  textColor?: string
  /** 填充圖案類型 */
  pattern?: FillPatternType
  /** 圖案顏色（預設使用 borderColor 或 color） */
  patternColor?: string
  /** 圖案背景色（預設為白色或透明） */
  patternBackgroundColor?: string
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
  /** 圖層圖例資訊 */
  legend?: LayerLegendItem[]
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
    visible: false,
    opacity: 0.8,
    description: '補助案件的格網熱度統計圖',
    order: 1
  },
  {
    id: 'grant-points',
    name: '補助案件點位',
    category: 'overlay',
    group: 'historical-grants',
    visible: true,
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
    visible: true,
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
    order: 9,
    legend: [
      // 住商工行政類
      { color: 'rgb(255,255,0)', label: '住宅區', borderOnly: true, text: '住' },
      { color: 'rgb(255,0,63)', label: '商業區', borderOnly: true, text: '商' },
      { color: 'rgb(127,63,0)', label: '工業區', borderOnly: true, text: '工' },
      { color: 'rgb(0,127,255)', label: '行政區', borderOnly: true, text: '行' },
      { color: 'rgb(191,127,255)', label: '文教區', borderOnly: true, text: '文' },
      { color: 'rgb(76,38,0)', label: '倉儲區', borderOnly: true, text: '倉' },
      { color: 'rgb(127,255,0)', label: '農業區', borderOnly: true, text: '農' },
      { color: 'rgb(0,255,0)', label: '風景區', borderOnly: true, text: '風' },
      { color: 'rgb(127,255,0)', label: '保護區', borderOnly: true, text: '保', pattern: 'dots-dense', patternColor: 'rgb(127,255,0)' },
      { color: 'rgb(127,255,255)', label: '水岸發展區', borderOnly: true, text: '水', pattern: 'dots-dense', patternColor: 'rgb(127,255,255)' },
      { color: 'rgb(127,255,0)', label: '宗教專用區', borderOnly: true, text: '宗' },
      { color: 'rgb(127,255,0)', label: '保存區', borderOnly: true, text: '存' },
      { color: 'rgb(127,255,255)', label: '河川區', borderOnly: true, text: '河' },
      // 學校用地類
      { color: 'rgb(191,127,255)', label: '學校用地', text: '文' },
      { color: 'rgb(191,127,255)', label: '1.國民小學', text: '文小' },
      { color: 'rgb(191,127,255)', label: '2.國民中學', text: '文中' },
      { color: 'rgb(191,127,255)', label: '3.高級中學', text: '文高' },
      { color: 'rgb(191,127,255)', label: '4.高級職校', text: '文職' },
      { color: 'rgb(191,127,255)', label: '5.大專院校', text: '文大' },
      { color: 'rgb(191,127,255)', label: '社教用地', text: '社' },
      // 公園綠地類
      { color: 'rgb(0,255,0)', label: '公園（綠地）用地', text: '公(綠)' },
      { color: 'rgb(0,255,0)', label: '公園（兼供兒童遊樂場）用地', text: '公(兒)' },
      { color: 'rgb(0,255,0)', label: '體育場所用地', text: '體' },
      { color: 'rgb(255,0,255)', label: '廣場用地', text: '廣' },
      { color: 'rgb(0,255,0)', label: '兒童遊樂場用地', text: '兒' },
      { color: 'rgb(0,255,0)', label: '名勝古蹟紀念性（廟宇）建築用地', text: '古(廟)' },
      // 市場交通類
      { color: 'rgb(255,63,0)', label: '批發市場用地', text: '批' },
      { color: 'rgb(255,63,0)', label: '零售市場用地', text: '市' },
      { color: 'rgb(255,0,255)', label: '高速公路用地', text: '高公' },
      { color: 'rgb(0,127,255)', label: '機關用地', text: '機' },
      // 公用設施類
      { color: 'rgb(183,183,183)', label: '變電所用地', text: '變' },
      { color: 'rgb(255,63,0)', label: '停車場用地', text: '停' },
      { color: 'rgb(255,0,255)', label: '加油站用地', text: '油' },
      { color: 'rgb(183,183,183)', label: '鐵路用地', text: '鐵' },
      { color: 'rgb(127,63,0)', label: '港埠用地', text: '港' },
      { color: 'rgb(0,127,255)', label: '民用航空站用地', text: '航' },
      { color: 'rgb(183,183,183)', label: '屠宰場用地', text: '屠' },
      { color: 'rgb(183,183,183)', label: '垃圾處理廠用地', text: '垃' },
      // 特殊用地類
      { color: 'rgb(255,255,127)', label: '火葬場用地', text: '葬' },
      { color: 'rgb(255,255,127)', label: '殯儀館用地', text: '殯' },
      { color: 'rgb(0,255,0)', label: '墳墓用地', text: '墓', pattern: 'dots-dense', patternColor: 'rgb(0,255,0)' },
      { color: 'rgb(183,183,183)', label: '污水處理廠用地', text: '污' },
      { color: 'rgb(183,183,183)', label: '煤氣廠用地', text: '煤' },
      { color: 'rgb(0,255,0)', label: '園林道路用地', text: '園道' },
      { color: 'rgb(127,255,255)', label: '海濱浴場用地', text: '海浴' },
      { color: 'rgb(127,255,255)', label: '河道用地', text: '河道' }
    ]
  },
  {
    id: 'non-urban-land-use',
    name: '非都市土地使用分區圖',
    category: 'overlay',
    group: 'auxiliary',
    visible: false,
    opacity: 0.6,
    description: '非都市土地使用分區',
    order: 10,
    legend: [
      { color: '#D3D3D3', label: '住宅區；保護區；兒童遊樂場；公園；公用事業保留地；商業區；學校、文教區；機關；綠地；綠帶；行政區；道路；道路保留地' },
      { color: '#FFD700', label: '一般農業區；農業區' },
      { color: '#8B4513', label: '倉儲區；工業區' },
      { color: '#E6E6FA', label: '其他使用區；其他保留地；特定專用區' },
      { color: '#90EE90', label: '山坡地保育區' },
      { color: '#228B22', label: '森林區' },
      { color: '#00008B', label: '河川區' },
      { color: '#FFFF00', label: '特定農業區' },
      { color: '#FF0000', label: '鄉村區' },
      { color: '#FF1493', label: '風景區' },
      { color: '#800080', label: '國家公園分區圖' }
    ]
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
