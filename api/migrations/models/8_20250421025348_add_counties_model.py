from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "counties" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(10) NOT NULL UNIQUE,
    "code" VARCHAR(10) NOT NULL UNIQUE
);
COMMENT ON COLUMN "counties"."name" IS '縣市名稱';
COMMENT ON COLUMN "counties"."code" IS '縣市代碼';
COMMENT ON TABLE "counties" IS '縣市資料表';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "counties";"""
