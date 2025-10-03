/**
 * Shapefile 載入工具
 * 支援前端直接讀取 .shp 檔案並轉換為 GeoJSON
 * 使用 shpjs 函式庫
 */

import shp from 'shpjs'
import type { GeoJsonFeatureCollection } from '@/types/gis'

/**
 * 載入選項
 */
interface LoadOptions {
  encoding?: string  // DBF 編碼，預設 'big5' 適用於台灣資料
}

/**
 * Shapefile 解析結果
 */
export interface ShapefileParseResult {
  layers: Array<{
    name: string
    geoJson: GeoJsonFeatureCollection
    featureCount: number
  }>
}

/**
 * 從檔案輸入載入 Shapefile
 * @param files 檔案列表（支援多選 .shp, .dbf, .prj 等）
 * @param options 載入選項
 */
export async function loadShapefileFromFiles(
  files: FileList | File[],
  options: LoadOptions = {}
): Promise<ShapefileParseResult> {
  const shapeFiles: Record<string, ArrayBuffer | string> = {}
  let baseName = '未命名圖層'

  // 解析檔案
  for (const file of Array.from(files)) {
    const extension = file.name.toLowerCase().split('.').pop()

    switch (extension) {
      case 'shp':
        shapeFiles[extension] = await file.arrayBuffer()
        baseName = file.name.replace(/\.shp$/i, '')
        break
      case 'dbf':
      case 'shx':
        shapeFiles[extension] = await file.arrayBuffer()
        break
      case 'prj':
        shapeFiles[extension] = await file.text()
        break
    }
  }

  if (!shapeFiles.shp) {
    throw new Error('未找到 .shp 檔案')
  }

  // shpjs 需要組合的 buffer 物件
  const combinedBuffer = {
    shp: shapeFiles.shp as ArrayBuffer,
    dbf: shapeFiles.dbf as ArrayBuffer | undefined,
    prj: shapeFiles.prj as string | undefined
  }

  const geoJsonData = await convertShapefileToGeoJSON(combinedBuffer, options)

  // 多檔案上傳只會有單一圖層
  return {
    layers: [{
      name: baseName,
      geoJson: geoJsonData,
      featureCount: geoJsonData.features.length
    }]
  }
}

/**
 * 從 ZIP 檔案載入 Shapefile
 * @param zipFile ZIP 檔案
 * @param options 載入選項
 */
export async function loadShapefileFromZip(
  zipFile: File,
  options: LoadOptions = {}
): Promise<ShapefileParseResult> {
  const { encoding = 'big5' } = options

  try {
    // shpjs 可以直接處理 ZIP 檔案的 ArrayBuffer
    const arrayBuffer = await zipFile.arrayBuffer()
    const parseOptions = encoding !== 'utf-8' ? { encoding } : undefined

    const geoJson = await shp(arrayBuffer, parseOptions)

    // shpjs 處理 ZIP 時可能返回：
    // 1. 單一 FeatureCollection（ZIP 包含一組 Shapefile）
    // 2. FeatureCollection 陣列（ZIP 包含多組 Shapefile）
    // 3. { [fileName]: FeatureCollection } 物件

    if (Array.isArray(geoJson)) {
      // 情況 2: 多個 FeatureCollection
      console.log(`ZIP 包含 ${geoJson.length} 個 Shapefile 圖層`)

      return {
        layers: geoJson.map((fc, index) => ({
          name: fc.fileName || `圖層 ${index + 1}`,
          geoJson: fc as GeoJsonFeatureCollection,
          featureCount: fc.features.length
        }))
      }
    } else if (typeof geoJson === 'object' && geoJson.type === 'FeatureCollection') {
      // 情況 1: 單一 FeatureCollection
      const fc = geoJson as any
      console.log(`ZIP 包含單一 Shapefile 圖層`)

      return {
        layers: [{
          name: fc.fileName || zipFile.name.replace(/\.zip$/i, ''),
          geoJson: fc as GeoJsonFeatureCollection,
          featureCount: fc.features.length
        }]
      }
    } else {
      // 情況 3: 物件形式 { fileName: FeatureCollection }
      const entries = Object.entries(geoJson)
      console.log(`ZIP 包含 ${entries.length} 個 Shapefile 圖層`)

      return {
        layers: entries.map(([fileName, fc]: [string, any]) => ({
          name: fileName.replace(/\.shp$/i, ''),
          geoJson: fc as GeoJsonFeatureCollection,
          featureCount: fc.features.length
        }))
      }
    }

  } catch (error) {
    console.error('ZIP Shapefile 載入錯誤:', error)
    throw new Error(`ZIP Shapefile 載入失敗: ${error instanceof Error ? error.message : '未知錯誤'}`)
  }
}

/**
 * 將 Shapefile 轉換為 GeoJSON
 * @param input ArrayBuffer (ZIP 或組合 buffer 物件) 或組合的 buffer 物件
 * @param options 載入選項
 */
async function convertShapefileToGeoJSON(
  input: ArrayBuffer | { shp: ArrayBuffer; dbf?: ArrayBuffer; prj?: string },
  options: LoadOptions = {}
): Promise<GeoJsonFeatureCollection> {
  const { encoding = 'big5' } = options

  try {
    // shpjs.parseShp() 可接受 ArrayBuffer (ZIP) 或 buffer 物件
    // 設定編碼選項
    const parseOptions = encoding !== 'utf-8' ? { encoding } : undefined

    const geoJson = await shp(input, parseOptions)

    // shpjs 可能返回單一 FeatureCollection 或 FeatureCollection 陣列
    const featureCollection = Array.isArray(geoJson) ? geoJson[0] : geoJson

    console.log(`成功載入 ${featureCollection.features.length} 個 features`)

    return featureCollection as GeoJsonFeatureCollection

  } catch (error) {
    console.error('Shapefile 載入錯誤:', error)
    throw new Error(`Shapefile 載入失敗: ${error instanceof Error ? error.message : '未知錯誤'}`)
  }
}

/**
 * 檢查檔案是否為 Shapefile 相關檔案
 */
export function isShapefileRelated(fileName: string): boolean {
  const extension = fileName.toLowerCase().split('.').pop()
  return ['shp', 'dbf', 'prj', 'shx', 'zip'].includes(extension || '')
}

/**
 * 檢查檔案組合是否完整
 */
export function validateShapefileSet(files: FileList | File[]): {
  isValid: boolean
  hasShp: boolean
  hasDbf: boolean
  hasPrj: boolean
  hasZip: boolean
  missingFiles: string[]
} {
  const fileNames = Array.from(files).map(f => f.name.toLowerCase())
  const extensions = fileNames.map(name => name.split('.').pop())

  const hasShp = extensions.includes('shp')
  const hasDbf = extensions.includes('dbf')
  const hasPrj = extensions.includes('prj')
  const hasZip = extensions.includes('zip')

  const missingFiles: string[] = []

  // 如果是 ZIP 檔案，就不檢查個別檔案
  if (!hasZip) {
    if (!hasShp) missingFiles.push('.shp (必需)')
    if (!hasDbf) missingFiles.push('.dbf (建議)')
    if (!hasPrj) missingFiles.push('.prj (建議)')
  }

  return {
    isValid: hasShp || hasZip,  // ZIP 或 .shp 都算有效
    hasShp,
    hasDbf,
    hasPrj,
    hasZip,
    missingFiles
  }
}
