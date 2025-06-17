from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        -- 先新增允許 NULL 的欄位
        ALTER TABLE "grant_history" ADD "session_id" VARCHAR(100);
        ALTER TABLE "grant_history" ADD "grant_status" VARCHAR(12);
        ALTER TABLE "grant_history" ADD "action_type" VARCHAR(19);
        ALTER TABLE "grant_history" ADD "old_value" JSONB;
        ALTER TABLE "grant_history" ADD "step_number" INT;
        ALTER TABLE "grant_history" ADD "ip_address" VARCHAR(45);
        ALTER TABLE "grant_history" ADD "new_value" JSONB;
        ALTER TABLE "grant_history" ADD "changed_fields" JSONB;

        -- 為現有資料設定預設值，將舊的 status 欄位資料遷移到新欄位
        UPDATE "grant_history" SET 
            "action_type" = 'status_change',
            "grant_status" = "status"
        WHERE "action_type" IS NULL;
        
        -- 現在可以安全地設定 NOT NULL 約束
        ALTER TABLE "grant_history" ALTER COLUMN "action_type" SET NOT NULL;
        
        -- 最後刪除舊的 status 欄位
        ALTER TABLE "grant_history" DROP COLUMN "status";

        COMMENT ON COLUMN "grants"."active_version_id_id" IS '目前現行的版本ID';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        COMMENT ON COLUMN "grants"."active_version_id_id" IS '目前活躍的版本ID';

         -- 恢復舊的 status 欄位
        ALTER TABLE "grant_history" ADD "status" VARCHAR(12);
        
        -- 將 grant_status 的資料遷移回 status 欄位
        UPDATE "grant_history" SET "status" = "grant_status" WHERE "grant_status" IS NOT NULL;
        
        -- 設定 status 為 NOT NULL（如果有需要的話，先設定預設值）
        UPDATE "grant_history" SET "status" = 'draft' WHERE "status" IS NULL;
        ALTER TABLE "grant_history" ALTER COLUMN "status" SET NOT NULL;
        
        -- 刪除新增的欄位
        ALTER TABLE "grant_history" DROP COLUMN "session_id";
        ALTER TABLE "grant_history" DROP COLUMN "grant_status";
        ALTER TABLE "grant_history" DROP COLUMN "action_type";
        ALTER TABLE "grant_history" DROP COLUMN "old_value";
        ALTER TABLE "grant_history" DROP COLUMN "step_number";
        ALTER TABLE "grant_history" DROP COLUMN "ip_address";
        ALTER TABLE "grant_history" DROP COLUMN "new_value";
        ALTER TABLE "grant_history" DROP COLUMN "changed_fields";"""
