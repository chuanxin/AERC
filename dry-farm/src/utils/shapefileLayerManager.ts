/**
 * OpenLayers Shapefile 圖層管理工具
 * 用於在地圖中動態載入和管理 Shapefile 圖層
 */

import VectorLayer from 'ol/layer/Vector'
import VectorSource from 'ol/source/Vector'
import GeoJSON from 'ol/format/GeoJSON'
import { Style, Fill, Stroke, Circle } from 'ol/style'
import type { Map as OLMap } from 'ol'
import type { GeoJsonFeatureCollection } from '@/types/gis'

/**
 * Shapefile 圖層配置
 */
export interface ShapefileLayerConfig {
  name: string
  geoJson: GeoJsonFeatureCollection
  style?: {
    fillColor?: string
    strokeColor?: string
    strokeWidth?: number
    opacity?: number
    pointRadius?: number
  }
  visible?: boolean
  zIndex?: number
}

/**
 * Shapefile 圖層管理器
 */
export class ShapefileLayerManager {
  private map: OLMap
  private layers: Map<string, VectorLayer> = new Map()

  constructor(map: OLMap) {
    this.map = map
  }

  /**
   * 添加 Shapefile 圖層到地圖
   */
  addShapefileLayer(config: ShapefileLayerConfig): VectorLayer {
    // 檢查圖層是否已存在
    if (this.layers.has(config.name)) {
      console.warn(`圖層 "${config.name}" 已存在，將被覆蓋`)
      this.removeLayer(config.name)
    }

    // 創建向量資料源
    const vectorSource = new VectorSource({
      features: new GeoJSON().readFeatures(config.geoJson, {
        featureProjection: 'EPSG:3857', // Web Mercator
        dataProjection: 'EPSG:4326'     // WGS84
      })
    })

    // 創建樣式
    const style = this.createLayerStyle(config.style || {})

    // 創建向量圖層
    const vectorLayer = new VectorLayer({
      source: vectorSource,
      style: style,
      visible: config.visible !== false,
      zIndex: config.zIndex || 100
    })

    // 設置圖層屬性
    vectorLayer.set('name', config.name)
    vectorLayer.set('type', 'shapefile')

    // 添加到地圖和管理器
    this.map.addLayer(vectorLayer)
    this.layers.set(config.name, vectorLayer)

    console.log(`Shapefile 圖層 "${config.name}" 已載入，包含 ${vectorSource.getFeatures().length} 個要素`)

    return vectorLayer
  }

  /**
   * 移除圖層
   */
  removeLayer(name: string): boolean {
    const layer = this.layers.get(name)
    if (layer) {
      this.map.removeLayer(layer)
      this.layers.delete(name)
      console.log(`圖層 "${name}" 已移除`)
      return true
    }
    return false
  }

  /**
   * 取得圖層
   */
  getLayer(name: string): VectorLayer | undefined {
    return this.layers.get(name)
  }

  /**
   * 取得所有 Shapefile 圖層
   */
  getAllLayers(): { name: string; layer: VectorLayer }[] {
    return Array.from(this.layers.entries()).map(([name, layer]) => ({
      name,
      layer
    }))
  }

  /**
   * 設置圖層可見性
   */
  setLayerVisible(name: string, visible: boolean): boolean {
    const layer = this.layers.get(name)
    if (layer) {
      layer.setVisible(visible)
      return true
    }
    return false
  }

  /**
   * 設置圖層透明度
   */
  setLayerOpacity(name: string, opacity: number): boolean {
    const layer = this.layers.get(name)
    if (layer) {
      layer.setOpacity(Math.max(0, Math.min(1, opacity)))
      return true
    }
    return false
  }

  /**
   * 縮放到圖層範圍
   */
  zoomToLayer(name: string, options?: { padding?: number; maxZoom?: number }): boolean {
    const layer = this.layers.get(name)
    if (layer) {
      const source = layer.getSource()
      if (source) {
        const extent = source.getExtent()
        this.map.getView().fit(extent, {
          padding: options?.padding ? [options.padding, options.padding, options.padding, options.padding] : [50, 50, 50, 50],
          maxZoom: options?.maxZoom || 18
        })
        return true
      }
    }
    return false
  }

  /**
   * 清除所有 Shapefile 圖層
   */
  clearAllLayers(): void {
    for (const [name] of this.layers) {
      this.removeLayer(name)
    }
  }

  /**
   * 創建圖層樣式
   */
  private createLayerStyle(styleConfig: NonNullable<ShapefileLayerConfig['style']>) {
    const {
      fillColor = '#2196F3',
      strokeColor = '#1976D2',
      strokeWidth = 2,
      opacity = 0.7,
      pointRadius = 6
    } = styleConfig

    return new Style({
      fill: new Fill({
        color: this.hexToRgba(fillColor, opacity)
      }),
      stroke: new Stroke({
        color: strokeColor,
        width: strokeWidth
      }),
      image: new Circle({
        radius: pointRadius,
        fill: new Fill({
          color: this.hexToRgba(fillColor, opacity)
        }),
        stroke: new Stroke({
          color: strokeColor,
          width: strokeWidth
        })
      })
    })
  }

  /**
   * 將 HEX 顏色轉換為 RGBA
   */
  private hexToRgba(hex: string, alpha: number): string {
    const r = parseInt(hex.slice(1, 3), 16)
    const g = parseInt(hex.slice(3, 5), 16)
    const b = parseInt(hex.slice(5, 7), 16)
    return `rgba(${r}, ${g}, ${b}, ${alpha})`
  }
}

/**
 * 預設樣式配置
 */
export const defaultShapefileStyles = {
  polygon: {
    fillColor: '#2196F3',
    strokeColor: '#1976D2',
    strokeWidth: 2,
    opacity: 0.5
  },
  line: {
    strokeColor: '#FF9800',
    strokeWidth: 3,
    opacity: 0.8
  },
  point: {
    fillColor: '#4CAF50',
    strokeColor: '#388E3C',
    strokeWidth: 2,
    opacity: 0.8,
    pointRadius: 8
  }
}

/**
 * 偵測幾何類型並回傳對應的預設樣式
 */
export function getDefaultStyleByGeometry(geoJson: GeoJsonFeatureCollection) {
  if (!geoJson.features.length) return defaultShapefileStyles.polygon

  const firstFeature = geoJson.features[0]
  const geometryType = firstFeature.geometry?.type

  switch (geometryType) {
    case 'Point':
    case 'MultiPoint':
      return defaultShapefileStyles.point
    case 'LineString':
    case 'MultiLineString':
      return defaultShapefileStyles.line
    case 'Polygon':
    case 'MultiPolygon':
    default:
      return defaultShapefileStyles.polygon
  }
}
