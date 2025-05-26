from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "power_equipments" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(50) NOT NULL UNIQUE,
    "code" VARCHAR(10) UNIQUE,
    "description" VARCHAR(255),
    "is_active" BOOL NOT NULL DEFAULT True
);
COMMENT ON COLUMN "power_equipments"."name" IS '動力設備名稱';
COMMENT ON COLUMN "power_equipments"."code" IS '動力設備代碼';
COMMENT ON COLUMN "power_equipments"."description" IS '動力設備描述';
COMMENT ON COLUMN "power_equipments"."is_active" IS '是否啟用';
COMMENT ON TABLE "power_equipments" IS '動力設備資料表';
        CREATE TABLE IF NOT EXISTS "regulation_equipments" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(50) NOT NULL UNIQUE,
    "code" VARCHAR(10) UNIQUE,
    "description" VARCHAR(255),
    "is_active" BOOL NOT NULL DEFAULT True
);
COMMENT ON COLUMN "regulation_equipments"."name" IS '調控設備名稱';
COMMENT ON COLUMN "regulation_equipments"."code" IS '調控設備代碼';
COMMENT ON COLUMN "regulation_equipments"."description" IS '調控設備描述';
COMMENT ON COLUMN "regulation_equipments"."is_active" IS '是否啟用';
COMMENT ON TABLE "regulation_equipments" IS '調控設備資料表';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "regulation_equipments";
        DROP TABLE IF EXISTS "power_equipments";"""
