from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "towns" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(20) NOT NULL,
    "code" VARCHAR(10) NOT NULL,
    "is_indigenous" BOOL NOT NULL DEFAULT False,
    "indigenous_type" VARCHAR(10),
    "county_id" INT NOT NULL REFERENCES "counties" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_towns_county__51dcc2" UNIQUE ("county_id", "name"),
    CONSTRAINT "uid_towns_county__3be4be" UNIQUE ("county_id", "code")
);
COMMENT ON COLUMN "towns"."name" IS '鄉鎮市區名稱';
COMMENT ON COLUMN "towns"."code" IS '鄉鎮市區代碼';
COMMENT ON COLUMN "towns"."is_indigenous" IS '是否為原民區域';
COMMENT ON COLUMN "towns"."indigenous_type" IS '原民區域類型(1:山地鄉 2:平地鄉)';
COMMENT ON COLUMN "towns"."county_id" IS '所屬縣市';
COMMENT ON TABLE "towns" IS '鄉鎮市區資料表';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "towns";"""
