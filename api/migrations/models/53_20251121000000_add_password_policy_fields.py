"""
新增密碼政策相關欄位

- password_changed_at: 密碼最後更改時間（用於密碼效期檢查）
- failed_login_count: 連續登入失敗次數（用於帳號鎖定機制）
- locked_until: 帳號鎖定截止時間（用於暫時鎖定帳號）
"""
from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        -- 密碼政策相關欄位
        ALTER TABLE "users" ADD "password_changed_at" TIMESTAMP;
        COMMENT ON COLUMN "users"."password_changed_at" IS '密碼最後更改時間';

        ALTER TABLE "users" ADD "failed_login_count" INT NOT NULL DEFAULT 0;
        COMMENT ON COLUMN "users"."failed_login_count" IS '連續登入失敗次數';

        ALTER TABLE "users" ADD "locked_until" TIMESTAMP;
        COMMENT ON COLUMN "users"."locked_until" IS '帳號鎖定截止時間';
    """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "users" DROP COLUMN "password_changed_at";
        ALTER TABLE "users" DROP COLUMN "failed_login_count";
        ALTER TABLE "users" DROP COLUMN "locked_until";
    """
