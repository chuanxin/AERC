/**
 * Proj4 Configuration Module
 *
 * This module registers custom projection definitions for use with OpenLayers.
 * Currently supports TWD97 (Taiwan Datum 1997) coordinate system.
 *
 * @module proj4Config
 */

import proj4 from 'proj4';
import { register } from 'ol/proj/proj4';
import { get as getProjection } from 'ol/proj';

/**
 * TWD97 (Taiwan Datum 1997) - EPSG:3826
 *
 * Official projection for Taiwan land surveying and mapping.
 * Transverse Mercator projection with GRS80 ellipsoid.
 *
 * Projection parameters:
 * - Central meridian: 121°E
 * - False easting: 250,000 m
 * - False northing: 0 m
 * - Scale factor: 0.9999
 *
 * Valid coordinate ranges:
 * - X (Easting): ~140,000 to ~360,000 meters
 * - Y (Northing): ~2,400,000 to ~2,800,000 meters
 */
const TWD97_EPSG_3826 = '+proj=tmerc +lat_0=0 +lon_0=121 +k=0.9999 +x_0=250000 +y_0=0 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs +type=crs';

/**
 * Initialize proj4 with custom projection definitions
 *
 * This function must be called before using any custom projections in OpenLayers.
 * Typically called during application initialization.
 *
 * @example
 * ```typescript
 * // In main.ts or app initialization
 * import { initProj4 } from '@/utils/proj4Config';
 * initProj4();
 * ```
 */
export function initProj4(): void {
  // Register TWD97 projection definition
  proj4.defs('EPSG:3826', TWD97_EPSG_3826);

  // Register all proj4 definitions with OpenLayers
  register(proj4);

  // Verify projection is available
  const twd97Projection = getProjection('EPSG:3826');
  if (!twd97Projection) {
    console.error('Failed to register EPSG:3826 (TWD97) projection');
  } else {
    console.log('✓ EPSG:3826 (TWD97) projection registered successfully');
  }
}

/**
 * Validate TWD97 coordinates
 *
 * Checks if the provided coordinates are within reasonable bounds for Taiwan.
 *
 * @param x - Easting coordinate (meters)
 * @param y - Northing coordinate (meters)
 * @returns True if coordinates are valid, false otherwise
 *
 * @example
 * ```typescript
 * if (validateTWD97Coordinates(250000, 2750000)) {
 *   // Coordinates are valid
 * }
 * ```
 */
export function validateTWD97Coordinates(x: number, y: number): boolean {
  // Valid ranges for Taiwan
  const MIN_X = 140000;
  const MAX_X = 360000;
  const MIN_Y = 2400000;
  const MAX_Y = 2800000;

  return x >= MIN_X && x <= MAX_X && y >= MIN_Y && y <= MAX_Y;
}

/**
 * Get projection definition for a given EPSG code
 *
 * @param epsgCode - EPSG code (e.g., 'EPSG:3826')
 * @returns Proj4 definition string or undefined if not found
 */
export function getProjectionDef(epsgCode: string): proj4.ProjectionDefinition | undefined {
  return proj4.defs(epsgCode);
}
