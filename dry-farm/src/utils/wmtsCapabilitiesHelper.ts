/**
 * WMTS Capabilities 增強解析工具
 * 處理 TileMatrixSet、ResourceURL 等 WMTS 特有的複雜配置
 */

import WMTSCapabilities from 'ol/format/WMTSCapabilities'
import { optionsFromCapabilities } from 'ol/source/WMTS'
import type { Options as WMTSOptions } from 'ol/source/WMTS'

/**
 * WMTS 圖層完整資訊（包含 TileMatrixSet 等）
 */
export interface WMTSLayerInfo {
  /** 圖層識別符 */
  identifier: string
  /** 圖層標題 */
  title: string
  /** 圖層摘要 */
  abstract?: string
  /** 支援的格式 */
  formats: string[]
  /** 支援的 TileMatrixSet */
  tileMatrixSets: string[]
  /** 範圍 */
  extent?: number[]
  /** 維度資訊 */
  dimensions?: Array<{
    identifier: string
    default: string
    values: string[]
  }>
  /** ResourceURL（RESTful 模式） */
  resourceUrls?: Array<{
    format: string
    template: string
    resourceType: string
  }>
}

/**
 * TileMatrixSet 資訊
 */
export interface TileMatrixSetInfo {
  /** 識別符 */
  identifier: string
  /** 支援的 CRS */
  supportedCRS: string
  /** 瓦片矩陣列表 */
  tileMatrices: Array<{
    identifier: string
    scaleDenominator: number
    topLeftCorner: number[]
    tileWidth: number
    tileHeight: number
    matrixWidth: number
    matrixHeight: number
  }>
}

/**
 * WMTS 服務完整資訊
 */
export interface WMTSServiceInfo {
  /** 服務版本 */
  version: string
  /** 服務標題 */
  title?: string
  /** 服務摘要 */
  abstract?: string
  /** 圖層列表 */
  layers: WMTSLayerInfo[]
  /** TileMatrixSet 列表 */
  tileMatrixSets: TileMatrixSetInfo[]
  /** 原始 Capabilities 物件 */
  rawCapabilities: any
}

/**
 * 從 Capabilities XML 解析完整的 WMTS 服務資訊
 */
export function parseWMTSServiceInfo(xmlText: string): WMTSServiceInfo {
  const parser = new WMTSCapabilities()
  const capabilities = parser.read(xmlText)

  // 提取服務基本資訊
  const version = capabilities.version || '1.0.0'
  const title = capabilities.ServiceIdentification?.Title
  const abstract = capabilities.ServiceIdentification?.Abstract

  // 提取圖層資訊
  const layers: WMTSLayerInfo[] = []
  const rawLayers = capabilities.Contents?.Layer || []

  for (const layer of rawLayers) {
    const layerInfo: WMTSLayerInfo = {
      identifier: layer.Identifier || '',
      title: layer.Title || layer.Identifier || '',
      abstract: layer.Abstract,
      formats: layer.Format || [],
      tileMatrixSets: (layer.TileMatrixSetLink || []).map((link: any) => link.TileMatrixSet),
      extent: layer.WGS84BoundingBox,
      resourceUrls: layer.ResourceURL?.map((ru: any) => ({
        format: ru.format,
        template: ru.template,
        resourceType: ru.resourceType
      }))
    }

    // 提取維度資訊
    if (layer.Dimension && Array.isArray(layer.Dimension)) {
      layerInfo.dimensions = layer.Dimension.map((dim: any) => ({
        identifier: dim.Identifier,
        default: dim.Default,
        values: dim.Value || []
      }))
    }

    layers.push(layerInfo)
  }

  // 提取 TileMatrixSet 資訊
  const tileMatrixSets: TileMatrixSetInfo[] = []
  const rawTMS = capabilities.Contents?.TileMatrixSet || []

  for (const tms of rawTMS) {
    const tmsInfo: TileMatrixSetInfo = {
      identifier: tms.Identifier || '',
      supportedCRS: tms.SupportedCRS || '',
      tileMatrices: (tms.TileMatrix || []).map((tm: any) => ({
        identifier: tm.Identifier,
        scaleDenominator: tm.ScaleDenominator,
        topLeftCorner: tm.TopLeftCorner,
        tileWidth: tm.TileWidth,
        tileHeight: tm.TileHeight,
        matrixWidth: tm.MatrixWidth,
        matrixHeight: tm.MatrixHeight
      }))
    }
    tileMatrixSets.push(tmsInfo)
  }

  return {
    version,
    title,
    abstract,
    layers,
    tileMatrixSets,
    rawCapabilities: capabilities
  }
}

/**
 * 檢查圖層是否與當前地圖投影相容
 * @param layerInfo 圖層資訊
 * @param tileMatrixSets 所有 TileMatrixSet
 * @param mapProjection 地圖投影（如 'EPSG:3857'）
 * @returns 相容的 TileMatrixSet 識別符，若不相容則返回 null
 */
export function findCompatibleTileMatrixSet(
  layerInfo: WMTSLayerInfo,
  tileMatrixSets: TileMatrixSetInfo[],
  mapProjection: string
): string | null {
  // 優先尋找完全匹配的投影
  for (const tmsId of layerInfo.tileMatrixSets) {
    const tms = tileMatrixSets.find(t => t.identifier === tmsId)
    if (tms && tms.supportedCRS.includes(mapProjection)) {
      return tmsId
    }
  }

  // 如果沒有完全匹配，尋找相容的（如 urn:ogc:def:crs:EPSG::3857 vs EPSG:3857）
  const projectionCode = mapProjection.split(':').pop() || ''
  for (const tmsId of layerInfo.tileMatrixSets) {
    const tms = tileMatrixSets.find(t => t.identifier === tmsId)
    if (tms && tms.supportedCRS.includes(projectionCode)) {
      return tmsId
    }
  }

  return null
}

/**
 * 選擇最佳的圖片格式
 * @param formats 支援的格式列表
 * @returns 最佳格式
 */
export function selectBestFormat(formats: string[]): string {
  // 優先順序：PNG（透明）> WebP > JPEG
  if (formats.includes('image/png')) return 'image/png'
  if (formats.includes('image/webp')) return 'image/webp'
  if (formats.includes('image/jpeg')) return 'image/jpeg'
  if (formats.includes('image/jpg')) return 'image/jpg'

  // 回退到第一個可用格式
  return formats[0] || 'image/png'
}

/**
 * 使用 OpenLayers 內建方法生成 WMTS Source 配置
 * @param capabilities 原始 Capabilities 物件
 * @param layerIdentifier 圖層識別符
 * @returns WMTS Source 配置選項，若失敗則返回 null
 */
export function generateWMTSOptions(
  capabilities: any,
  layerIdentifier: string
): WMTSOptions | null {
  try {
    // 使用 OpenLayers 提供的 optionsFromCapabilities 函數
    // 這會自動處理 TileMatrixSet、TileGrid 等複雜配置
    const options = optionsFromCapabilities(capabilities, {
      layer: layerIdentifier
    })

    if (!options) {
      console.warn(`無法為圖層 ${layerIdentifier} 生成 WMTS 配置`)
      return null
    }

    return options
  } catch (error) {
    console.error('生成 WMTS 配置時發生錯誤:', error)
    return null
  }
}

/**
 * 檢查 WMTS 服務是否可用
 * @param serviceUrl 服務 URL
 * @returns 是否可用
 */
export async function checkWMTSServiceAvailability(serviceUrl: string): Promise<boolean> {
  try {
    const response = await fetch(serviceUrl, {
      method: 'HEAD',
      mode: 'cors'
    })
    return response.ok
  } catch (error) {
    console.error('WMTS 服務檢查失敗:', error)
    return false
  }
}

/**
 * 驗證圖層配置是否完整
 * @param layerInfo 圖層資訊
 * @returns 驗證結果
 */
export function validateWMTSLayerConfig(layerInfo: WMTSLayerInfo): {
  isValid: boolean
  errors: string[]
} {
  const errors: string[] = []

  if (!layerInfo.identifier) {
    errors.push('缺少圖層識別符')
  }

  if (!layerInfo.tileMatrixSets || layerInfo.tileMatrixSets.length === 0) {
    errors.push('圖層未指定任何 TileMatrixSet')
  }

  if (!layerInfo.formats || layerInfo.formats.length === 0) {
    errors.push('圖層未指定任何格式')
  }

  return {
    isValid: errors.length === 0,
    errors
  }
}
