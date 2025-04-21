from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "crop_categories" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(50) NOT NULL UNIQUE
);
COMMENT ON COLUMN "crop_categories"."name" IS '作物類別名稱';
COMMENT ON TABLE "crop_categories" IS '作物類別資料表';
        CREATE TABLE IF NOT EXISTS "crop_names" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(50) NOT NULL,
    "category_id" INT NOT NULL REFERENCES "crop_categories" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_crop_names_categor_3cce6d" UNIQUE ("category_id", "name")
);
COMMENT ON COLUMN "crop_names"."name" IS '作物名稱';
COMMENT ON COLUMN "crop_names"."category_id" IS '所屬作物類別';
COMMENT ON TABLE "crop_names" IS '作物名稱資料表';
        CREATE TABLE IF NOT EXISTS "funding_sources" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(50) NOT NULL UNIQUE,
    "code" VARCHAR(10) NOT NULL UNIQUE
);
COMMENT ON COLUMN "funding_sources"."name" IS '補助來源名稱';
COMMENT ON COLUMN "funding_sources"."code" IS '補助來源代碼';
COMMENT ON TABLE "funding_sources" IS '補助來源資料表';
        ALTER TABLE "grants" ADD "bulletin_sys" VARCHAR(20);
        ALTER TABLE "grants" ADD "bulletin" VARCHAR(20);
        COMMENT ON COLUMN "grants"."status" IS '案件狀態: 0:完成申請人資料, 1:完成土地資料, 2:完成灌溉調控設施, 3:完成田間管路, 4:完成現場勘查, 5:完成補助申請資料, 6:完成結案申報, 7:完成測試合格的時間, 8:完成撥款作業, 9:完成撥款, 99:駁回申請';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "grants" DROP COLUMN "bulletin_sys";
        ALTER TABLE "grants" DROP COLUMN "bulletin";
        COMMENT ON COLUMN "grants"."status" IS '案件狀態: draft, submitted, reviewing, approved, rejected, completed';
        DROP TABLE IF EXISTS "crop_names";
        DROP TABLE IF EXISTS "crop_categories";
        DROP TABLE IF EXISTS "funding_sources";"""
