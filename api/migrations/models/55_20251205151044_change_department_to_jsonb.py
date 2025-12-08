from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        -- 將 department 從 VARCHAR 改為 JSONB
        ALTER TABLE "users" ALTER COLUMN "department" TYPE JSONB USING
            CASE
                WHEN "department" IS NULL THEN NULL
                WHEN "department" = '' THEN NULL
                -- 如果已經是有效的 JSON，直接轉換
                WHEN "department"::text ~ '^\\s*[\\{\\[]' THEN "department"::JSONB
                -- 否則包裝為 legacy_text 格式
                ELSE jsonb_build_object('legacy_text', "department")
            END;

        -- 加入 GIN 索引提升查詢效能
        CREATE INDEX IF NOT EXISTS idx_users_department ON "users" USING GIN ("department");

        -- 更新註解
        COMMENT ON COLUMN "users"."department" IS '部門詳細資訊 JSON: {''branch'': {''code'': ''1'', ''name'': ''北港分處''}, ''station'': {''code'': ''01'', ''name'': ''鹿寮站''}} 或 {''legacy_text'': ''自由輸入文字''}';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        -- 降級時將 JSONB 轉回 VARCHAR
        DROP INDEX IF EXISTS idx_users_department;

        ALTER TABLE "users" ALTER COLUMN "department" TYPE VARCHAR(100) USING
            CASE
                WHEN "department" IS NULL THEN NULL
                WHEN "department" ? 'legacy_text' THEN "department"->>'legacy_text'
                WHEN "department" ? 'branch' AND "department" ? 'station' THEN
                    ("department"->'branch'->>'name' || ' ' || "department"->'station'->>'name')
                WHEN "department" ? 'branch' THEN "department"->'branch'->>'name'
                ELSE "department"::text
            END;

        COMMENT ON COLUMN "users"."department" IS '所屬部門/工作站';"""
