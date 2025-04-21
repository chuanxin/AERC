from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "sections" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(50) NOT NULL,
    "code" VARCHAR(10) NOT NULL,
    "town_id" INT NOT NULL REFERENCES "towns" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_sections_town_id_d90c34" UNIQUE ("town_id", "name"),
    CONSTRAINT "uid_sections_town_id_1bf360" UNIQUE ("town_id", "code")
);
COMMENT ON COLUMN "sections"."name" IS '地段名稱';
COMMENT ON COLUMN "sections"."code" IS '地段代碼';
COMMENT ON COLUMN "sections"."town_id" IS '所屬鄉鎮市區';
COMMENT ON TABLE "sections" IS '地段資料表';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "sections";"""
