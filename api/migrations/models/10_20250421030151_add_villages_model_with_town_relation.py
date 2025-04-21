from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "villages" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(20) NOT NULL,
    "code" VARCHAR(10) NOT NULL,
    "town_id" INT NOT NULL REFERENCES "towns" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_villages_town_id_c7808d" UNIQUE ("town_id", "name"),
    CONSTRAINT "uid_villages_town_id_f213ea" UNIQUE ("town_id", "code")
);
COMMENT ON COLUMN "villages"."name" IS '村里名稱';
COMMENT ON COLUMN "villages"."code" IS '村里代碼';
COMMENT ON COLUMN "villages"."town_id" IS '所屬鄉鎮市區';
COMMENT ON TABLE "villages" IS '村里資料表';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "villages";"""
