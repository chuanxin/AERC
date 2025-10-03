/**
 * OGC Capabilities 解析工具
 * 支援 WMS、WFS、WMTS 等服務的 GetCapabilities 回應解析
 */

import WMSCapabilities from 'ol/format/WMSCapabilities'
import WMTSCapabilities from 'ol/format/WMTSCapabilities'
import type { OGCServiceType } from '@/pages/maps/config'

/**
 * 解析後的圖層資訊
 */
export interface ParsedLayerInfo {
  /** 圖層名稱 */
  name: string
  /** 圖層標題 */
  title: string
  /** 圖層摘要 */
  abstract?: string
  /** 圖層範圍 [minx, miny, maxx, maxy] */
  extent?: number[]
  /** CRS/SRS 列表 */
  crs?: string[]
  /** 其他元數據 */
  metadata?: Record<string, unknown>
}

/**
 * Capabilities 解析結果
 */
export interface CapabilitiesParseResult {
  /** 服務類型 */
  serviceType: OGCServiceType
  /** 服務版本 */
  version: string
  /** 服務標題 */
  serviceTitle?: string
  /** 服務摘要 */
  serviceAbstract?: string
  /** 可用圖層列表 */
  layers: ParsedLayerInfo[]
  /** 原始解析結果 */
  rawCapabilities?: unknown
}

/**
 * 從 URL 獲取 Capabilities XML
 */
async function fetchCapabilitiesXML(url: string): Promise<string> {
  const response = await fetch(url)
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`)
  }
  return await response.text()
}

/**
 * 解析 WMS Capabilities
 */
function parseWMSCapabilities(xmlText: string): CapabilitiesParseResult {
  const parser = new WMSCapabilities()
  const result = parser.read(xmlText) as {
    version: string
    Service?: {
      Title?: string
      Abstract?: string
    }
    Capability?: {
      Layer?: {
        Layer?: Array<{
          Name?: string
          Title?: string
          Abstract?: string
          BoundingBox?: Array<{ extent: number[]; crs: string }>
          CRS?: string[]
        }>
      }
    }
  }

  const layers: ParsedLayerInfo[] = []
  const wmsLayers = result.Capability?.Layer?.Layer || []

  for (const layer of wmsLayers) {
    if (layer.Name) {
      layers.push({
        name: layer.Name,
        title: layer.Title || layer.Name,
        abstract: layer.Abstract,
        extent: layer.BoundingBox?.[0]?.extent,
        crs: layer.CRS,
        metadata: layer
      })
    }
  }

  return {
    serviceType: 'WMS',
    version: result.version,
    serviceTitle: result.Service?.Title,
    serviceAbstract: result.Service?.Abstract,
    layers,
    rawCapabilities: result
  }
}

/**
 * 解析 WMTS Capabilities
 */
function parseWMTSCapabilities(xmlText: string): CapabilitiesParseResult {
  const parser = new WMTSCapabilities()
  const result = parser.read(xmlText) as {
    version: string
    ServiceIdentification?: {
      Title?: string
      Abstract?: string
    }
    Contents?: {
      Layer?: Array<{
        Identifier?: string
        Title?: string
        Abstract?: string
        WGS84BoundingBox?: number[]
      }>
    }
  }

  const layers: ParsedLayerInfo[] = []
  const wmtsLayers = result.Contents?.Layer || []

  for (const layer of wmtsLayers) {
    if (layer.Identifier) {
      layers.push({
        name: layer.Identifier,
        title: layer.Title || layer.Identifier,
        abstract: layer.Abstract,
        extent: layer.WGS84BoundingBox,
        metadata: layer
      })
    }
  }

  return {
    serviceType: 'WMTS',
    version: result.version,
    serviceTitle: result.ServiceIdentification?.Title,
    serviceAbstract: result.ServiceIdentification?.Abstract,
    layers,
    rawCapabilities: result
  }
}

/**
 * 解析 WFS Capabilities
 * 注意：OpenLayers 不提供 WFSCapabilities 解析器
 * WFS 服務建議直接使用 DescribeFeatureType 或 GeoJSON 輸出格式
 */
function parseWFSCapabilities(xmlText: string): CapabilitiesParseResult {
  // 簡化的 WFS Capabilities 解析（手動解析 XML）
  const parser = new DOMParser()
  const xmlDoc = parser.parseFromString(xmlText, 'text/xml')

  // 檢查解析錯誤
  const parseError = xmlDoc.querySelector('parsererror')
  if (parseError) {
    throw new Error('XML 解析錯誤')
  }

  // 提取版本
  const root = xmlDoc.documentElement
  const version = root.getAttribute('version') || '2.0.0'

  // 提取服務資訊
  const serviceIdent = xmlDoc.querySelector('ServiceIdentification, ows\\:ServiceIdentification')
  const serviceTitle = serviceIdent?.querySelector('Title, ows\\:Title')?.textContent || undefined
  const serviceAbstract = serviceIdent?.querySelector('Abstract, ows\\:Abstract')?.textContent || undefined

  // 提取圖層資訊
  const layers: ParsedLayerInfo[] = []
  const featureTypes = xmlDoc.querySelectorAll('FeatureType')

  featureTypes.forEach((ft) => {
    const name = ft.querySelector('Name')?.textContent
    const title = ft.querySelector('Title')?.textContent
    const abstract = ft.querySelector('Abstract')?.textContent

    // 提取範圍
    const bboxEl = ft.querySelector('WGS84BoundingBox, ows\\:WGS84BoundingBox')
    let extent: number[] | undefined
    if (bboxEl) {
      const lower = bboxEl.querySelector('LowerCorner, ows\\:LowerCorner')?.textContent
      const upper = bboxEl.querySelector('UpperCorner, ows\\:UpperCorner')?.textContent
      if (lower && upper) {
        const lowerCoords = lower.trim().split(/\s+/).map(Number)
        const upperCoords = upper.trim().split(/\s+/).map(Number)
        extent = [...lowerCoords, ...upperCoords]
      }
    }

    if (name) {
      layers.push({
        name,
        title: title || name,
        abstract: abstract || undefined,
        extent,
        metadata: {}
      })
    }
  })

  return {
    serviceType: 'WFS',
    version,
    serviceTitle,
    serviceAbstract,
    layers,
    rawCapabilities: xmlDoc
  }
}

/**
 * 自動偵測服務類型並解析 Capabilities
 */
function detectAndParse(xmlText: string): CapabilitiesParseResult {
  // 簡單的服務類型偵測
  const upperXml = xmlText.toUpperCase()

  if (upperXml.includes('WMS_CAPABILITIES') || upperXml.includes('<WMS_CAPABILITIES')) {
    return parseWMSCapabilities(xmlText)
  } else if (upperXml.includes('WMTS') || upperXml.includes('CAPABILITIES XMLNS="http://www.opengis.net/wmts')) {
    return parseWMTSCapabilities(xmlText)
  } else if (upperXml.includes('WFS_CAPABILITIES') || upperXml.includes('<WFS_CAPABILITIES')) {
    return parseWFSCapabilities(xmlText)
  }

  throw new Error('無法識別的 Capabilities 格式，請確認是否為 WMS、WFS 或 WMTS 服務')
}

/**
 * 主要解析函數 - 從 URL 解析
 * @param url GetCapabilities URL
 * @param serviceType 可選的服務類型，若不提供則自動偵測
 */
export async function parseCapabilitiesFromURL(
  url: string,
  serviceType?: OGCServiceType
): Promise<CapabilitiesParseResult> {
  const xmlText = await fetchCapabilitiesXML(url)
  return parseCapabilitiesFromXML(xmlText, serviceType)
}

/**
 * 主要解析函數 - 從 XML 文字解析
 * @param xmlText Capabilities XML 內容
 * @param serviceType 可選的服務類型，若不提供則自動偵測
 */
export function parseCapabilitiesFromXML(
  xmlText: string,
  serviceType?: OGCServiceType
): CapabilitiesParseResult {
  if (serviceType) {
    switch (serviceType) {
      case 'WMS':
        return parseWMSCapabilities(xmlText)
      case 'WMTS':
        return parseWMTSCapabilities(xmlText)
      case 'WFS':
        return parseWFSCapabilities(xmlText)
      default:
        throw new Error(`不支援的服務類型: ${serviceType}`)
    }
  }

  return detectAndParse(xmlText)
}

/**
 * 從檔案解析 Capabilities
 * @param file XML 檔案
 * @param serviceType 可選的服務類型
 */
export async function parseCapabilitiesFromFile(
  file: File,
  serviceType?: OGCServiceType
): Promise<CapabilitiesParseResult> {
  const xmlText = await file.text()
  return parseCapabilitiesFromXML(xmlText, serviceType)
}
