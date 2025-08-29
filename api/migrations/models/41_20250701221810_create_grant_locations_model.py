from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "grant_locations" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "source_system" VARCHAR(20) NOT NULL,
    "source_id" VARCHAR(255) NOT NULL,
    "apply_year" INT,
    "applicant_name" VARCHAR(255),
    "land_section" VARCHAR(255),
    "land_number" VARCHAR(255),
    "land_type" VARCHAR(50),
    "case_status" VARCHAR(50),
    "comment" TEXT,
    "meta_data" JSONB,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON COLUMN "grant_locations"."source_system" IS '資料來源 (''new_aerc'' or ''legacy_farmdata'')';
COMMENT ON COLUMN "grant_locations"."source_id" IS '在資料來原系統中的唯一id (grant.id or MapNo)';
COMMENT ON COLUMN "grant_locations"."apply_year" IS '申請年度 (民國年)';
COMMENT ON COLUMN "grant_locations"."applicant_name" IS '申請人姓名';
COMMENT ON COLUMN "grant_locations"."land_section" IS '地段';
COMMENT ON COLUMN "grant_locations"."land_number" IS '地號';
COMMENT ON COLUMN "grant_locations"."land_type" IS '地目代碼: 1:田, 2:旱, 3:林, 4:原, 5:雜, 6:其他, 7:未登記, 8:空白';
COMMENT ON COLUMN "grant_locations"."case_status" IS '案件狀態';
COMMENT ON COLUMN "grant_locations"."comment" IS '土地資料備註';
COMMENT ON COLUMN "grant_locations"."meta_data" IS '即時顯示的彈出資訊';

-- Manually add the PostGIS geometry column and create indexes
SELECT AddGeometryColumn('public', 'grant_locations', 'geom', 4326, 'POINT', 2);
CREATE INDEX "idx_grant_locations_geom" ON "grant_locations" USING GIST ("geom");
ALTER TABLE "grant_locations" ADD CONSTRAINT "unique_location_identifier" UNIQUE ("source_system", "source_id", "land_section", "land_number");

-- Manually add comments for clarity
COMMENT ON COLUMN grant_locations.geom IS 'PostGIS 的點位幾何欄位 (使用 WGS84 座標系統)';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "grant_locations";"""
