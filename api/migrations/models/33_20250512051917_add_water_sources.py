from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "water_sources" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(50) NOT NULL UNIQUE,
    "code" VARCHAR(10) UNIQUE,
    "description" VARCHAR(255),
    "is_active" BOOL NOT NULL DEFAULT True
);
COMMENT ON COLUMN "water_sources"."name" IS '水源名稱';
COMMENT ON COLUMN "water_sources"."code" IS '水源代碼';
COMMENT ON COLUMN "water_sources"."description" IS '水源描述';
COMMENT ON COLUMN "water_sources"."is_active" IS '是否啟用';
COMMENT ON TABLE "water_sources" IS '水源資料表';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "water_sources";"""
