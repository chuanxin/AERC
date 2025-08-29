-- 檢查並顯示當前狀態
DO $$
BEGIN
    RAISE NOTICE 'Starting PostGIS setup for database: %', current_database();
END
$$;

-- 啟用 PostGIS 核心擴展
CREATE EXTENSION IF NOT EXISTS postgis;

-- 嘗試安裝其他有用的擴展
DO $$
BEGIN
    -- PostGIS Topology
    BEGIN
        CREATE EXTENSION IF NOT EXISTS postgis_topology;
        RAISE NOTICE 'PostGIS Topology extension enabled successfully';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE 'PostGIS Topology extension not available: %', SQLERRM;
    END;
    
    -- FuzzyStrMatch（用於地理編碼）
    BEGIN
        CREATE EXTENSION IF NOT EXISTS fuzzystrmatch;
        RAISE NOTICE 'FuzzyStrMatch extension enabled successfully';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE 'FuzzyStrMatch extension not available: %', SQLERRM;
    END;
    
    -- PostGIS Tiger Geocoder（美國地址編碼，可選）
    BEGIN
        CREATE EXTENSION IF NOT EXISTS postgis_tiger_geocoder;
        RAISE NOTICE 'PostGIS Tiger Geocoder extension enabled successfully';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE 'PostGIS Tiger Geocoder extension not available: %', SQLERRM;
    END;
END
$$;

-- 授予適當權限
GRANT USAGE ON SCHEMA public TO PUBLIC;
GRANT CREATE ON SCHEMA public TO PUBLIC;

-- 顯示安裝結果
DO $$
DECLARE
    postgis_ver text;
    geos_ver text;
    proj_ver text;
BEGIN
    -- 獲取版本信息
    SELECT PostGIS_version() INTO postgis_ver;
    SELECT GEOS_version() INTO geos_ver;
    SELECT PROJ_version() INTO proj_ver;
    
    RAISE NOTICE '=== PostGIS Setup Complete ===';
    RAISE NOTICE 'PostGIS version: %', postgis_ver;
    RAISE NOTICE 'GEOS version: %', geos_ver;
    RAISE NOTICE 'PROJ version: %', proj_ver;
    RAISE NOTICE '================================';
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Could not retrieve version information: %', SQLERRM;
END
$$;

-- 創建一個簡單的測試表來驗證功能
CREATE TABLE IF NOT EXISTS postgis_test (
    id SERIAL PRIMARY KEY,
    name TEXT,
    location GEOMETRY(POINT, 4326),
    created_at TIMESTAMP DEFAULT NOW()
);

-- 插入一個測試點（台北市政府座標）
INSERT INTO postgis_test (name, location) 
VALUES ('台北市政府', ST_SetSRID(ST_Point(121.5654, 25.0378), 4326))
ON CONFLICT DO NOTHING;

-- 創建空間索引
CREATE INDEX IF NOT EXISTS idx_postgis_test_location 
ON postgis_test USING GIST (location);

DO $$
BEGIN
    RAISE NOTICE 'PostGIS test table created and sample data inserted';
    RAISE NOTICE 'You can test with: SELECT name, ST_AsText(location) FROM postgis_test;';
END
$$;