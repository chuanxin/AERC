import httpClient from './api/http';
import { SPATIAL } from './api/endpoints';

export interface OfficeBoundaryResult {
  gid: number;
  ia_code: string;
  ia_name: string;
  mng_code: string;
  mng_name: string;
  stn_code: string;
  stn_name: string;
  grp_code: string;
  grp_name: string;
  area: number;
  record_date: string | null;
  sg: string;
  stngrp: string;
  part: string;
}

export interface CountyBoundaryResult {
  gid: number;
  countyid: string;
  countycode: string;
  countyname: string;
  countyeng: string;
}

export interface SpatialQueryResponse<T> {
  office_boundaries?: T[];
  county_boundaries?: T[];
  count: number;
  query_geometry: any;
}

/**
 * Query office boundaries spatial intersection
 */
export const queryOfficeBoundaries = async (geometryData: any): Promise<SpatialQueryResponse<OfficeBoundaryResult>> => {
  try {
    const response = await httpClient.post(SPATIAL.OFFICE, geometryData);
    return response.data;
  } catch (error) {
    console.error('Error querying office boundaries:', error);
    throw error;
  }
};

/**
 * Query county boundaries spatial intersection
 */
export const queryCountyBoundaries = async (geometryData: any): Promise<SpatialQueryResponse<CountyBoundaryResult>> => {
  try {
    const response = await httpClient.post(SPATIAL.COUNTY, geometryData);
    return response.data;
  } catch (error) {
    console.error('Error querying county boundaries:', error);
    throw error;
  }
};