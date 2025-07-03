// GIS 相關的 TypeScript 類型定義

export interface GeoJsonGeometry {
  type: 'Point' | 'LineString' | 'Polygon' | 'MultiPoint' | 'MultiLineString' | 'MultiPolygon';
  coordinates: number[] | number[][] | number[][][];
}

// 個別點位屬性
export interface GrantLocationProperties {
  cluster: false; // 標記為非聚合點位
  id: number;
  source_system: 'new_aerc' | 'legacy_farmdata';
  source_id: string;
  applicant_name: string;
  land_section: string;
  land_number: string;
  apply_year: number;
  case_status: string;
  land_type: string;
  meta_data?: Record<string, any>;
}

// 聚合點位屬性
export interface ClusterProperties {
  cluster: true; // 標記為聚合點位
  point_count: number;
  source_system: 'new_aerc' | 'legacy_farmdata';
  cluster_ids: number[];
  cluster_source_ids: string[];
  cluster_applicants: string[];
  year_range: string;
  land_sections: string[];
  zoom_level: number;
  grid_size: number;
}

// 聯合類型
export type FeatureProperties = GrantLocationProperties | ClusterProperties;

export interface GeoJsonFeature {
  type: 'Feature';
  geometry: GeoJsonGeometry;
  properties: FeatureProperties;
}

// 聚合相關的 meta 資訊
export interface ClusteringMeta {
  enabled: boolean;
  zoom_level?: number;
  grid_size?: number;
  strategy: 'grid_snap' | 'individual_points';
}

export interface PerformanceMeta {
  limit_applied: number;
  optimization: 'clustering' | 'limit_only';
}

export interface GeoJsonFeatureCollection {
  type: 'FeatureCollection';
  features: GeoJsonFeature[];
  meta: {
    count: number;
    bbox?: string;
    clustering: ClusteringMeta;
    filters: GisFilters;
    performance: PerformanceMeta;
  };
}

export interface GisFilters {
  bbox?: string;
  source_system?: 'new_aerc' | 'legacy_farmdata';
  apply_year_min?: number;
  apply_year_max?: number;
  applicant_name?: string;
  land_section?: string;
  case_number?: string;
  limit?: number;
  no_clustering?: boolean;
}

export interface GisStatistics {
  source_system: string;
  total_points: number;
  earliest_year: number;
  latest_year: number;
  bbox_polygon?: string;
}

export interface GisStatsResponse {
  statistics: GisStatistics[];
  total_points: number;
}

export interface GisSearchResult {
  id: number;
  source_system: string;
  source_id: string;
  applicant_name: string;
  land_section: string;
  land_number: string;
  apply_year: number;
  case_status: string;
  longitude: number;
  latitude: number;
  geometry: string; // GeoJSON string
}

export interface GisSearchResponse {
  results: GisSearchResult[];
  count: number;
  search_criteria: {
    applicant_name?: string;
    land_section?: string;
    case_number?: string;
  };
}

// 年度範圍類型
export interface YearRange {
  min: number;
  max: number;
  current: [number, number];
}

// 顯示模式類型
export type DisplayMode = 'points' | 'heatmap';

// GIS Store 狀態接口
export interface GisState {
  // 資料
  currentFeatures: GeoJsonFeature[];
  statistics: GisStatsResponse | null;

  // UI 狀態
  loading: boolean;
  error: string | null;
  displayMode: DisplayMode;

  // 篩選條件
  filters: GisFilters;
  yearRange: YearRange;

  // 地圖狀態
  currentBounds: string | null;
  selectedFeature: GeoJsonFeature | null;
}

// API 請求參數類型（等同於 GisFilters）
export type GetPointsParams = GisFilters;

export interface SearchPointsParams {
  applicant_name?: string;
  land_section?: string;
  case_number?: string;
  limit?: number;
}
