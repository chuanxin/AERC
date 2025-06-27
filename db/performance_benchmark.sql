-- PostgreSQL + PostGIS 效能基準測試
-- 使用方法：docker-compose exec db psql -U hello_fastapi -d hello_fastapi_dev -f /performance_benchmark.sql

\echo '=== PostgreSQL + PostGIS 效能基準測試 ==='
\echo ''

-- 啟用計時
\timing on

\echo '1. 基本資料庫操作測試 (10,000 筆記錄)'
DROP TABLE IF EXISTS basic_perf_test;
CREATE TABLE basic_perf_test (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    value NUMERIC,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 插入測試
INSERT INTO basic_perf_test (name, value, description)
SELECT 
    'test_item_' || generate_series,
    random() * 1000,
    'Description for item ' || generate_series
FROM generate_series(1, 10000);

\echo '2. 基本查詢效能測試'
SELECT COUNT(*) as total_records FROM basic_perf_test;
SELECT COUNT(*) as high_value_records FROM basic_perf_test WHERE value > 500;
SELECT AVG(value) as average_value FROM basic_perf_test;

\echo '3. 索引效能測試'
CREATE INDEX idx_basic_perf_value ON basic_perf_test(value);
CREATE INDEX idx_basic_perf_name ON basic_perf_test(name);

-- 測試索引查詢
SELECT * FROM basic_perf_test WHERE value BETWEEN 400 AND 600 LIMIT 10;

\echo '4. 空間資料測試 (1,000 個地理點)'
DROP TABLE IF EXISTS spatial_perf_test;
CREATE TABLE spatial_perf_test (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    location GEOMETRY(POINT, 4326),
    area GEOMETRY(POLYGON, 4326),
    created_at TIMESTAMP DEFAULT NOW()
);

-- 插入台灣範圍內的隨機點
INSERT INTO spatial_perf_test (name, location)
SELECT 
    'sensor_' || generate_series,
    ST_Point(
        120 + random() * 2,  -- 經度 120-122
        24 + random() * 2    -- 緯度 24-26
    )
FROM generate_series(1, 1000);

\echo '5. 空間索引建立'
CREATE INDEX idx_spatial_location ON spatial_perf_test USING GIST (location);

\echo '6. 空間查詢效能測試'
-- 查找台北市附近的點 (25km 範圍內)
SELECT COUNT(*) as points_near_taipei
FROM spatial_perf_test 
WHERE ST_DWithin(
    location, 
    ST_Point(121.5654, 25.0378), -- 台北市政府座標
    0.25  -- 約 25km (度數)
);

-- 查找特定區域內的點
SELECT COUNT(*) as points_in_region
FROM spatial_perf_test 
WHERE ST_Within(
    location,
    ST_MakeEnvelope(121.0, 24.5, 122.0, 25.5, 4326) -- 台北地區範圍
);

\echo '7. 複雜空間運算測試'
-- 計算所有點到台北101的距離
SELECT 
    name,
    ST_Distance(
        ST_Transform(location, 3826),  -- 轉換為台灣座標系統 (TWD97)
        ST_Transform(ST_Point(121.5654, 25.0340), 3826)  -- 台北101
    ) / 1000 as distance_km
FROM spatial_perf_test 
ORDER BY distance_km 
LIMIT 5;

\echo '8. 資料庫大小統計'
SELECT 
    pg_size_pretty(pg_database_size(current_database())) as database_size,
    pg_size_pretty(pg_total_relation_size('basic_perf_test')) as basic_table_size,
    pg_size_pretty(pg_total_relation_size('spatial_perf_test')) as spatial_table_size;

\echo '9. 索引使用統計'
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan as times_used,
    pg_size_pretty(pg_relation_size(indexname::regclass)) as index_size
FROM pg_stat_user_indexes 
WHERE tablename IN ('basic_perf_test', 'spatial_perf_test')
ORDER BY tablename, indexname;

\echo '10. PostGIS 函數效能測試'
SELECT 
    'PostGIS Version' as test_type,
    PostGIS_version() as result
UNION ALL
SELECT 
    'Geometry Types Count',
    COUNT(*)::text
FROM spatial_perf_test 
WHERE GeometryType(location) = 'POINT';

-- 清理測試資料
\echo ''
\echo '清理測試資料...'
DROP TABLE IF EXISTS basic_perf_test;
DROP TABLE IF EXISTS spatial_perf_test;

\echo ''
\echo '=== 效能測試完成 ==='
\echo '注意事項：'
\echo '1. 首次執行可能較慢（冷啟動效應）'
\echo '2. 生產環境的效能會因硬體和資料量而異'
\echo '3. 建議在不同負載下多次測試'
\timing off