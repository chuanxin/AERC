from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        -- 新增 grants.tag 欄位（案件自定義標籤，自由文字，最多 50 字元）
        ALTER TABLE "grants"
            ADD COLUMN "tag" VARCHAR(50) NULL;

        -- 建立索引以支援標籤篩選查詢效能
        CREATE INDEX IF NOT EXISTS "grants_tag_idx" ON "grants" ("tag");
    """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP INDEX IF EXISTS "grants_tag_idx";
        ALTER TABLE "grants" DROP COLUMN IF EXISTS "tag";
    """
