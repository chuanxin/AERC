from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "qualification_queries" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "query_type" VARCHAR(10) NOT NULL,
    "location_data" JSONB NOT NULL,
    "query_options" JSONB,
    "search_results" JSONB,
    "area_statistics" JSONB,
    "result_count" INT NOT NULL DEFAULT 0,
    "query_hash" VARCHAR(64),
    "response_time_ms" INT,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON COLUMN "qualification_queries"."query_type" IS '查詢類型';
COMMENT ON COLUMN "qualification_queries"."location_data" IS '地區查詢參數: {county, town, section?, landNumber?}';
COMMENT ON COLUMN "qualification_queries"."query_options" IS '查詢選項: {years, includeStatistics}';
COMMENT ON COLUMN "qualification_queries"."search_results" IS '查詢結果快取';
COMMENT ON COLUMN "qualification_queries"."area_statistics" IS '面積統計結果快取';
COMMENT ON COLUMN "qualification_queries"."result_count" IS '查詢結果數量';
COMMENT ON COLUMN "qualification_queries"."query_hash" IS '查詢參數雜湊值(用於快取)';
COMMENT ON COLUMN "qualification_queries"."response_time_ms" IS '查詢響應時間(毫秒)';
COMMENT ON COLUMN "qualification_queries"."created_at" IS '查詢時間';
COMMENT ON COLUMN "qualification_queries"."updated_at" IS '更新時間';
COMMENT ON TABLE "qualification_queries" IS '重複案件查詢記錄表';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "qualification_queries";"""
