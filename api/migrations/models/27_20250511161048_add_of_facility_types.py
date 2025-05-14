from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "facility_types" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(50) NOT NULL UNIQUE,
    "code" VARCHAR(10) NOT NULL UNIQUE,
    "description" VARCHAR(255),
    "is_active" BOOL NOT NULL DEFAULT True,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON COLUMN "facility_types"."name" IS '設施類型名稱';
COMMENT ON COLUMN "facility_types"."code" IS '設施類型代碼';
COMMENT ON COLUMN "facility_types"."description" IS '設施類型描述';
COMMENT ON COLUMN "facility_types"."is_active" IS '是否啟用';
COMMENT ON COLUMN "facility_types"."created_at" IS '建立時間';
COMMENT ON COLUMN "facility_types"."modified_at" IS '修改時間';
COMMENT ON TABLE "facility_types" IS '設施類型資料表';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "facility_types";"""
