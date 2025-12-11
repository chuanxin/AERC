/**
 * 國土測繪中心地籍圖查詢服務
 * API 文件: https://api.nlsc.gov.tw/
 *
 * GML 回傳欄位說明 (實際測試結果):
 * - CITY: 縣市 (例如: 臺中市)
 * - TOWN: 鄉鎮市區 (例如: 南區)
 * - OFFICE: 地政事務所代碼 (例如: BA)
 * - SECT: 地段代碼 (例如: 0532)
 * - LANDNO: 地號8碼 (例如: 00010000)
 * - AREA: 面積(平方公尺) (例如: 1627.0)
 * - LANDUSE: 使用分區 (可能為空)
 * - LANDDETATIS: 用地編定 (可能為空)
 * - VALUESSESSED: 公告地價(元/平方公尺) (例如: 65779)
 * - VALUEANNOUNCE: 公告現值(元/平方公尺) (例如: 8197)
 */

import GML2 from 'ol/format/GML2';
import type { Feature } from 'ol';
import type { Geometry } from 'ol/geom';

// 地籍圖查詢參數介面
export interface CadastralQueryParams {
  countyCode: string;      // 縣市代碼 (例如: 'B' for 台中市)
  sectionCode: string;     // 地段代碼 (例如: '0008')
  landNumberMain: string;  // 地號主號 (例如: '1')
  landNumberSub: string;   // 地號副號 (例如: '0' 或空字串)
  format?: 'gml' | 'kml' | 'shp'; // 檔案格式，預設 gml
  srid?: '4326' | '3826';  // 坐標系統，預設 4326 (WGS84)
}

// 地籍圖查詢結果介面
export interface CadastralQueryResult {
  success: boolean;
  features: Feature<Geometry>[];
  message?: string;
  apiUrl?: string;
}

/**
 * 格式化地號為 8 碼格式
 * @param main 主號 (例如: '1', '123')
 * @param sub 副號 (例如: '0', '5', '' 或空字串)
 * @returns 8碼地號 (例如: '00010000', '01230005')
 */
export const formatLandNumber = (main: string, sub: string = ''): string => {
  // 移除前導零後重新格式化
  const mainNum = parseInt(main || '0', 10);
  const subNum = parseInt(sub || '0', 10);

  // 主號4碼 + 副號4碼
  const mainPart = mainNum.toString().padStart(4, '0');
  const subPart = subNum.toString().padStart(4, '0');

  return `${mainPart}${subPart}`;
};

/**
 * 建立 NLSC 地籍圖查詢 API URL
 * @param params 查詢參數
 * @returns API URL
 */
export const buildCadastralQueryUrl = (params: CadastralQueryParams): string => {
  const {
    countyCode,
    sectionCode,
    landNumberMain,
    landNumberSub,
    format = 'gml',
    srid = '4326'
  } = params;

  // 格式化地號為 8 碼
  const formattedLandNumber = formatLandNumber(landNumberMain, landNumberSub);

  // 建立 API URL
  const baseUrl = 'https://api.nlsc.gov.tw/dmaps/CadasMapQuery';
  return `${baseUrl}/${countyCode}/${sectionCode}/${formattedLandNumber}/${format}/${srid}`;
};

/**
 * 查詢指定地號的地籍圖資料
 * @param params 查詢參數
 * @returns 查詢結果（包含 OpenLayers Feature 物件）
 */
export const queryCadastralMap = async (
  params: CadastralQueryParams
): Promise<CadastralQueryResult> => {
  try {
    const apiUrl = buildCadastralQueryUrl(params);
    console.log('🗺️ Querying NLSC Cadastral Map API:', apiUrl);

    // 發送請求
    const response = await fetch(apiUrl);

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    // 取得 GML 文字內容
    const gmlText = await response.text();

    // 使用 OpenLayers GML2 format 解析（NLSC 使用 GML 2 格式）
    // GML2 使用 <gml:coordinates> 而不是 GML3 的 <gml:posList>
    const gmlFormat = new GML2();

    try {
      const features = gmlFormat.readFeatures(gmlText, {
        // 將資料從 EPSG:4326 (WGS84) 轉換為 EPSG:3857 (Web Mercator)
        dataProjection: `EPSG:${params.srid || '4326'}`,
        featureProjection: 'EPSG:3857'
      });

      console.log(`✅ Parsed ${features.length} features from NLSC API`);

      // 驗證每個 feature 是否有幾何資料
      features.forEach((feature, index) => {
        const geometry = feature.getGeometry();
        if (geometry) {
          console.log(`   Feature ${index + 1}: ${geometry.getType()}, extent:`, geometry.getExtent());
        } else {
          console.warn(`   Feature ${index + 1}: No geometry!`);
        }
      });

      // 檢查是否有資料
      if (features.length === 0) {
        return {
          success: false,
          features: [],
          message: '查無此地號的地籍資料',
          apiUrl
        };
      }

      return {
        success: true,
        features,
        apiUrl
      };

    } catch (parseError) {
      console.error('❌ Failed to parse GML:', parseError);
      console.log('GML content preview:', gmlText.substring(0, 500));

      return {
        success: false,
        features: [],
        message: `GML 解析失敗: ${parseError instanceof Error ? parseError.message : 'Unknown error'}`,
        apiUrl
      };
    }

  } catch (error) {
    console.error('❌ Failed to query NLSC Cadastral Map API:', error);

    return {
      success: false,
      features: [],
      message: error instanceof Error ? error.message : '查詢失敗',
    };
  }
};

/**
 * 從地段資料中提取縣市代碼
 * @param countyLandCode 縣市地政代碼 (例如: 'B')
 * @returns 縣市代碼
 */
export const extractCountyCode = (countyLandCode: string): string => {
  // 縣市地政代碼通常是單一英文字母 (A-Z)
  // 參考: https://api.nlsc.gov.tw/
  return countyLandCode.toUpperCase();
};

/**
 * 驗證地號格式
 * @param main 主號
 * @param sub 副號
 * @returns 驗證結果
 */
export const validateLandNumber = (main: string, sub: string = ''): { valid: boolean; message?: string } => {
  // 主號必填
  if (!main || main.trim() === '') {
    return { valid: false, message: '請輸入地號主號' };
  }

  // 檢查是否為數字
  const mainNum = parseInt(main, 10);
  if (isNaN(mainNum) || mainNum < 0 || mainNum > 9999) {
    return { valid: false, message: '主號必須為 0-9999 的數字' };
  }

  // 副號可選，但如果有則必須為數字
  if (sub && sub.trim() !== '') {
    const subNum = parseInt(sub, 10);
    if (isNaN(subNum) || subNum < 0 || subNum > 9999) {
      return { valid: false, message: '副號必須為 0-9999 的數字' };
    }
  }

  return { valid: true };
};

/**
 * 使用點座標查詢地籍圖資料（NLSC CadasMapPointQuery API）
 * @param lon 經度 (WGS84)
 * @param lat 緯度 (WGS84)
 * @param srid 坐標系統代碼 ('4326' 或 '3826')
 * @param format 檔案格式 ('gml', 'kml', 'shp')
 * @returns 查詢結果（包含 OpenLayers Feature 物件）
 */
export const queryCadastralMapByPoint = async (
  lon: number,
  lat: number,
  srid: '4326' | '3826' = '4326',
  format: 'gml' | 'kml' | 'shp' = 'gml'
): Promise<CadastralQueryResult> => {
  try {
    // 建立 API URL
    // API format: https://api.nlsc.gov.tw/dmaps/CadasMapPointQuery/[X坐標]/[Y坐標]/[坐標類別代碼]/[檔案格式]
    const apiUrl = `https://api.nlsc.gov.tw/dmaps/CadasMapPointQuery/${lon}/${lat}/${srid}/${format}`;
    console.log('🗺️ Querying NLSC Cadastral Map API (Point Query):', apiUrl);

    // 發送請求
    const response = await fetch(apiUrl);

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    // 取得 GML 文字內容
    const gmlText = await response.text();

    // 使用 OpenLayers GML2 format 解析（NLSC 使用 GML 2 格式）
    const gmlFormat = new GML2();

    try {
      const features = gmlFormat.readFeatures(gmlText, {
        // 將資料從 EPSG:4326 (WGS84) 轉換為 EPSG:3857 (Web Mercator)
        dataProjection: `EPSG:${srid}`,
        featureProjection: 'EPSG:3857'
      });

      console.log(`✅ Parsed ${features.length} features from NLSC Point Query API`);

      // 驗證每個 feature 是否有幾何資料
      features.forEach((feature, index) => {
        const geometry = feature.getGeometry();
        if (geometry) {
          console.log(`   Feature ${index + 1}: ${geometry.getType()}, extent:`, geometry.getExtent());
        } else {
          console.warn(`   Feature ${index + 1}: No geometry!`);
        }
      });

      // 檢查是否有資料
      if (features.length === 0) {
        return {
          success: false,
          features: [],
          message: '此位置查無地籍資料',
          apiUrl
        };
      }

      return {
        success: true,
        features,
        apiUrl
      };

    } catch (parseError) {
      console.error('❌ Failed to parse GML:', parseError);
      console.log('GML content preview:', gmlText.substring(0, 500));

      return {
        success: false,
        features: [],
        message: `GML 解析失敗: ${parseError instanceof Error ? parseError.message : 'Unknown error'}`,
        apiUrl
      };
    }

  } catch (error) {
    console.error('❌ Failed to query NLSC Cadastral Map API (Point Query):', error);

    return {
      success: false,
      features: [],
      message: error instanceof Error ? error.message : '查詢失敗',
    };
  }
};
