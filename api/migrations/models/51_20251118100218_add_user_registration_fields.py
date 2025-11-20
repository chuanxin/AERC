from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "user_registrations" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "application_reason" TEXT NOT NULL,
    "status" VARCHAR(8) NOT NULL DEFAULT 'pending',
    "reviewed_at" TIMESTAMPTZ,
    "review_comment" TEXT,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "reviewed_by_id" INT REFERENCES "users" ("id") ON DELETE CASCADE,
    "user_id" INT NOT NULL UNIQUE REFERENCES "users" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_user_regist_status_ac3686" ON "user_registrations" ("status");
CREATE INDEX IF NOT EXISTS "idx_user_regist_created_c5b61d" ON "user_registrations" ("created_at");
COMMENT ON COLUMN "user_registrations"."application_reason" IS '申請原因說明';
COMMENT ON COLUMN "user_registrations"."status" IS '申請狀態';
COMMENT ON COLUMN "user_registrations"."reviewed_at" IS '審核時間';
COMMENT ON COLUMN "user_registrations"."review_comment" IS '審核意見';
COMMENT ON COLUMN "user_registrations"."created_at" IS '申請時間';
COMMENT ON COLUMN "user_registrations"."modified_at" IS '修改時間';
COMMENT ON COLUMN "user_registrations"."reviewed_by_id" IS '審核人員';
COMMENT ON COLUMN "user_registrations"."user_id" IS '申請的使用者帳號';
COMMENT ON TABLE "user_registrations" IS '帳號申請記錄表';
        ALTER TABLE "users" ADD "phone_ext" VARCHAR(10);
        ALTER TABLE "users" ADD "phone" VARCHAR(20);
        ALTER TABLE "users" ADD "mobile" VARCHAR(20);
        ALTER TABLE "users" ADD "department" VARCHAR(100);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "users" DROP COLUMN "phone_ext";
        ALTER TABLE "users" DROP COLUMN "phone";
        ALTER TABLE "users" DROP COLUMN "mobile";
        ALTER TABLE "users" DROP COLUMN "department";
        DROP TABLE IF EXISTS "user_registrations";"""
