from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "password_history" (
            "id" SERIAL NOT NULL PRIMARY KEY,
            "password_hash" VARCHAR(128) NOT NULL,
            "changed_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
            "changed_by_ip" VARCHAR(45),
            "user_agent" VARCHAR(255),
            "change_method" VARCHAR(50),
            "user_id" INT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE
        );
        CREATE INDEX IF NOT EXISTS "idx_password_history_user_changed"
            ON "password_history" ("user_id", "changed_at" DESC);
        COMMENT ON TABLE "password_history" IS '密碼歷史記錄表';
        COMMENT ON COLUMN "password_history"."password_hash" IS '歷史密碼 hash';
        COMMENT ON COLUMN "password_history"."changed_at" IS '密碼變更時間';
        COMMENT ON COLUMN "password_history"."changed_by_ip" IS '變更來源 IP';
        COMMENT ON COLUMN "password_history"."user_agent" IS 'User Agent';
        COMMENT ON COLUMN "password_history"."change_method" IS '變更方式: password_reset, user_change, admin_reset';
        COMMENT ON COLUMN "password_history"."user_id" IS '使用者';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "password_history";"""
