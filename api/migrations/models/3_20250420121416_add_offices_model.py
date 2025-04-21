from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "offices" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(50) NOT NULL UNIQUE,
    "short_name" VARCHAR(10) NOT NULL UNIQUE,
    "code" VARCHAR(10) NOT NULL UNIQUE
);
COMMENT ON COLUMN "offices"."name" IS '單位名稱';
COMMENT ON COLUMN "offices"."short_name" IS '單位縮寫';
COMMENT ON COLUMN "offices"."code" IS '單位代碼';
COMMENT ON TABLE "offices" IS '單位/管理處資料表';
        ALTER TABLE "users" ADD "job_title" VARCHAR(50);
        ALTER TABLE "users" ADD "last_login" TIMESTAMPTZ;
        ALTER TABLE "users" DROP COLUMN "department";
        COMMENT ON COLUMN "users"."full_name" IS '使用者姓名';
        COMMENT ON COLUMN "users"."password" IS '密碼';
        COMMENT ON COLUMN "users"."permissions" IS '特定權限設定(JSON格式)';
        COMMENT ON COLUMN "users"."username" IS '使用者帳號';
        COMMENT ON COLUMN "users"."role" IS '角色: admin, manager, user 等';
        COMMENT ON COLUMN "users"."is_active" IS '是否啟用';
        COMMENT ON COLUMN "users"."email" IS '電子郵件';
        DROP TABLE IF EXISTS "notes";"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "users" ADD "department" VARCHAR(100);
        ALTER TABLE "users" DROP COLUMN "job_title";
        ALTER TABLE "users" DROP COLUMN "last_login";
        COMMENT ON COLUMN "users"."full_name" IS NULL;
        COMMENT ON COLUMN "users"."password" IS NULL;
        COMMENT ON COLUMN "users"."permissions" IS NULL;
        COMMENT ON COLUMN "users"."username" IS NULL;
        COMMENT ON COLUMN "users"."role" IS NULL;
        COMMENT ON COLUMN "users"."is_active" IS NULL;
        COMMENT ON COLUMN "users"."email" IS NULL;
        DROP TABLE IF EXISTS "offices";"""
