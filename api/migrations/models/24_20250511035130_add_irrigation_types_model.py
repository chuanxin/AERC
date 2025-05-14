from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "irrigation_types" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(50) NOT NULL UNIQUE,
    "code" VARCHAR(10) NOT NULL UNIQUE,
    "description" VARCHAR(255),
    "is_active" BOOL NOT NULL DEFAULT True,
    "parent_id" INT REFERENCES "irrigation_types" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "irrigation_types"."name" IS '灌溉類型名稱';
COMMENT ON COLUMN "irrigation_types"."code" IS '灌溉類型代碼';
COMMENT ON COLUMN "irrigation_types"."description" IS '灌溉類型描述';
COMMENT ON COLUMN "irrigation_types"."is_active" IS '是否啟用';
COMMENT ON COLUMN "irrigation_types"."parent_id" IS '父類型';
COMMENT ON TABLE "irrigation_types" IS '灌溉類型資料表';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "irrigation_types";"""
