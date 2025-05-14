from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "pf_diameters" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "value" DOUBLE PRECISION NOT NULL,
    "name" VARCHAR(50) NOT NULL,
    CONSTRAINT "uid_pf_diameter_name_8efada" UNIQUE ("name", "value")
);
COMMENT ON COLUMN "pf_diameters"."value" IS '管徑值';
COMMENT ON COLUMN "pf_diameters"."name" IS '管徑名稱';
COMMENT ON TABLE "pf_diameters" IS '管徑資料表';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "pf_diameters";"""
