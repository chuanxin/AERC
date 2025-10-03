/**
 * shpjs 類型聲明
 * https://github.com/calvinmetcalf/shapefile-js
 */

declare module 'shpjs' {
  /**
   * GeoJSON FeatureCollection
   */
  interface FeatureCollection {
    type: 'FeatureCollection'
    features: Feature[]
    fileName?: string
  }

  /**
   * GeoJSON Feature
   */
  interface Feature {
    type: 'Feature'
    geometry: Geometry
    properties: Record<string, any>
  }

  /**
   * GeoJSON Geometry
   */
  interface Geometry {
    type: 'Point' | 'LineString' | 'Polygon' | 'MultiPoint' | 'MultiLineString' | 'MultiPolygon'
    coordinates: any
  }

  /**
   * Shapefile buffer 組合
   */
  interface ShapefileBuffers {
    shp: ArrayBuffer
    dbf?: ArrayBuffer
    prj?: string
  }

  /**
   * 解析選項
   */
  interface ParseOptions {
    encoding?: string
  }

  /**
   * 主函數：解析 Shapefile
   * @param input ZIP ArrayBuffer 或 Shapefile buffer 組合
   * @param options 解析選項
   * @returns FeatureCollection 或 FeatureCollection 陣列
   */
  function shp(
    input: ArrayBuffer | ShapefileBuffers,
    options?: ParseOptions
  ): Promise<FeatureCollection | FeatureCollection[]>

  export default shp
}
