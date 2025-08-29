from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "grant_versions" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" INT NOT NULL,
    "all_steps_data" JSONB NOT NULL,
    "all_steps_data_hash" VARCHAR(64),
    "comment" VARCHAR(255),
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "created_by_id" INT REFERENCES "users" ("id") ON DELETE CASCADE,
    "grant_id" INT NOT NULL REFERENCES "grants" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_grant_versi_grant_i_9b9285" UNIQUE ("grant_id", "version")
);
COMMENT ON COLUMN "grant_versions"."version" IS '版本資訊';
COMMENT ON COLUMN "grant_versions"."all_steps_data" IS '所有步驟的資料(JSON格式)';
COMMENT ON COLUMN "grant_versions"."all_steps_data_hash" IS '所有步驟資料的Hash值，用於檢查版本變更';
COMMENT ON COLUMN "grant_versions"."comment" IS '版本說明';
COMMENT ON COLUMN "grant_versions"."created_at" IS '建立時間';
COMMENT ON COLUMN "grant_versions"."modified_at" IS '修改時間';
COMMENT ON COLUMN "grant_versions"."created_by_id" IS '建立人帳號';
COMMENT ON COLUMN "grant_versions"."grant_id" IS '所屬補助申請';
COMMENT ON TABLE "grant_versions" IS '補助申請單版本資料表';
        ALTER TABLE "grants" ADD "active_version_id_id" INT;
        ALTER TABLE "grants" ADD CONSTRAINT "fk_grants_grant_ve_359378ba" FOREIGN KEY ("active_version_id_id") REFERENCES "grant_versions" ("id") ON DELETE CASCADE;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "grants" DROP CONSTRAINT IF EXISTS "fk_grants_grant_ve_359378ba";
        ALTER TABLE "grants" DROP COLUMN "active_version_id_id";
        DROP TABLE IF EXISTS "grant_versions";"""
