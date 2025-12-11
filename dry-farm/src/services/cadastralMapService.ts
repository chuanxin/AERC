/**
 * 國土測繪中心地籍圖查詢服務（後端 API 版本）
 *
 * 架構說明：
 * - 前端透過後端 API (/nlsc/cadastral/*) 查詢地籍圖
 * - 後端負責調用 NLSC API 並解析 GML
 * - 前端接收 GeoJSON 格式，轉換為 OpenLayers Feature
 *
 * 優勢：
 * - 統一的 API 管理和錯誤處理
 * - 支援快取和速率限制（後端實作）
 * - 減少前端複雜度（無需處理 GML 解析）
 */

import GeoJSON from 'ol/format/GeoJSON';
import type { Feature } from 'ol';
import type { Geometry } from 'ol/geom';
import { NLSC } from './api/endpoints';
import { apiService } from './api/http';

// 地籍圖查詢參數介面
export interface CadastralQueryParams {
  countyCode: string;      // 縣市代碼 (例如: 'B' for 台中市)
  sectionCode: string;     // 地段代碼 (例如: '0532')
  landNumberMain: string;  // 地號主號 (例如: '1')
  landNumberSub: string;   // 地號副號 (例如: '0' 或空字串)
  format?: 'gml' | 'kml' | 'shp'; // 檔案格式，預設 gml
  srid?: '4326' | '3826';  // 坐標系統，預設 4326 (WGS84)
}

// 後端 API 回應介面
interface CadastralApiResponse {
  success: boolean;
  features: any[];
  message?: string;
  api_url?: string;
}

// 地籍圖查詢結果介面
export interface CadastralQueryResult {
  success: boolean;
  features: Feature<Geometry>[];
  message?: string;
  apiUrl?: string;
}

/**
 * 驗證地號格式
 */
export const validateLandNumber = (main: string, sub: string = ''): { valid: boolean; message?: string } => {
  if (!main || main.trim() === '') {
    return { valid: false, message: '請輸入地號主號' };
  }

  const mainNum = parseInt(main, 10);
  if (isNaN(mainNum) || mainNum < 0 || mainNum > 9999) {
    return { valid: false, message: '主號必須為 0-9999 的數字' };
  }

  if (sub && sub.trim() !== '') {
    const subNum = parseInt(sub, 10);
    if (isNaN(subNum) || subNum < 0 || subNum > 9999) {
      return { valid: false, message: '副號必須為 0-9999 的數字' };
    }
  }

  return { valid: true };
};

/**
 * 將 GeoJSON Features 轉換為 OpenLayers Features
 */
const convertGeoJSONToOpenLayersFeatures = (geojsonFeatures: any[]): Feature<Geometry>[] => {
  const geojsonFormat = new GeoJSON();
  const features: Feature<Geometry>[] = [];

  for (const geojsonFeature of geojsonFeatures) {
    try {
      const olFeature = geojsonFormat.readFeature(geojsonFeature, {
        dataProjection: 'EPSG:4326',      // GeoJSON 使用 WGS84
        featureProjection: 'EPSG:3857'    // OpenLayers 地圖使用 Web Mercator
      }) as Feature<Geometry>;

      // 複製屬性
      if (geojsonFeature.properties) {
        Object.keys(geojsonFeature.properties).forEach(key => {
          olFeature.set(key, geojsonFeature.properties[key]);
        });
      }

      features.push(olFeature);
    } catch (error) {
      console.error('Failed to convert GeoJSON feature:', error);
    }
  }

  return features;
};

/**
 * 查詢指定地號的地籍圖資料
 */
export const queryCadastralMap = async (
  params: CadastralQueryParams
): Promise<CadastralQueryResult> => {
  try {
    console.log('🗺️ Querying cadastral map:', params);

    const data = await apiService.post<CadastralApiResponse>(NLSC.CADASTRAL_QUERY_BY_LAND_NUMBER, {
      county_code: params.countyCode,
      section_code: params.sectionCode,
      land_number_main: params.landNumberMain,
      land_number_sub: params.landNumberSub || '0',
      format: params.format || 'gml',
      srid: params.srid || '4326'
    });

    if (!data.success) {
      return {
        success: false,
        features: [],
        message: data.message || '查詢失敗',
        apiUrl: data.api_url
      };
    }

    // 轉換為 OpenLayers Features
    const features = convertGeoJSONToOpenLayersFeatures(data.features);

    console.log(`✅ Loaded ${features.length} cadastral features`);

    return {
      success: features.length > 0,
      features,
      message: features.length === 0 ? '查無此地號的地籍資料' : undefined,
      apiUrl: data.api_url
    };

  } catch (error) {
    console.error('❌ Failed to query cadastral map:', error);
    return {
      success: false,
      features: [],
      message: error instanceof Error ? error.message : '查詢失敗',
    };
  }
};

/**
 * 使用點座標查詢地籍圖資料
 */
export const queryCadastralMapByPoint = async (
  lon: number,
  lat: number,
  srid: '4326' | '3826' = '4326',
  format: 'gml' | 'kml' | 'shp' = 'gml'
): Promise<CadastralQueryResult> => {
  try {
    console.log(`🗺️ Querying cadastral map by point: [${lon}, ${lat}]`);

    const data = await apiService.post<CadastralApiResponse>(NLSC.CADASTRAL_QUERY_BY_POINT, {
      longitude: lon,
      latitude: lat,
      srid: srid,
      format: format
    });

    if (!data.success) {
      return {
        success: false,
        features: [],
        message: data.message || '查詢失敗',
        apiUrl: data.api_url
      };
    }

    // 轉換為 OpenLayers Features
    const features = convertGeoJSONToOpenLayersFeatures(data.features);

    console.log(`✅ Loaded ${features.length} cadastral features (point query)`);

    return {
      success: features.length > 0,
      features,
      message: features.length === 0 ? '此位置查無地籍資料' : undefined,
      apiUrl: data.api_url
    };

  } catch (error) {
    console.error('❌ Failed to query cadastral map by point:', error);
    return {
      success: false,
      features: [],
      message: error instanceof Error ? error.message : '查詢失敗',
    };
  }
};
