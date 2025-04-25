from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "grants" DROP CONSTRAINT IF EXISTS "fk_grants_users_0e06f3c8";
        CREATE TABLE IF NOT EXISTS "grant_attachments" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "file_name" VARCHAR(255) NOT NULL,
    "file_path" VARCHAR(255) NOT NULL,
    "file_type" VARCHAR(50) NOT NULL,
    "file_size" INT NOT NULL,
    "upload_time" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "description" VARCHAR(255),
    "grant_id" INT NOT NULL REFERENCES "grants" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "grant_attachments"."file_name" IS '檔案名稱';
COMMENT ON COLUMN "grant_attachments"."file_path" IS '檔案路徑';
COMMENT ON COLUMN "grant_attachments"."file_type" IS '檔案類型';
COMMENT ON COLUMN "grant_attachments"."file_size" IS '檔案大小(bytes)';
COMMENT ON COLUMN "grant_attachments"."upload_time" IS '上傳時間';
COMMENT ON COLUMN "grant_attachments"."description" IS '檔案描述';
COMMENT ON COLUMN "grant_attachments"."grant_id" IS '所屬案件';
COMMENT ON TABLE "grant_attachments" IS '補助案件附件資料表';
        CREATE TABLE IF NOT EXISTS "grant_comments" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "comment" TEXT NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "grant_id" INT NOT NULL REFERENCES "grants" ("id") ON DELETE CASCADE,
    "user_id" INT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "grant_comments"."comment" IS '評論內容';
COMMENT ON COLUMN "grant_comments"."created_at" IS '建立時間';
COMMENT ON COLUMN "grant_comments"."grant_id" IS '所屬案件';
COMMENT ON COLUMN "grant_comments"."user_id" IS '評論者';
COMMENT ON TABLE "grant_comments" IS '補助案件評論資料表';
        CREATE TABLE IF NOT EXISTS "grant_history" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "status" VARCHAR(12) NOT NULL,
    "changed_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "notes" TEXT,
    "changed_by_id" INT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE,
    "grant_id" INT NOT NULL REFERENCES "grants" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "grant_history"."status" IS '案件狀態';
COMMENT ON COLUMN "grant_history"."changed_at" IS '修改時間';
COMMENT ON COLUMN "grant_history"."notes" IS '備註';
COMMENT ON COLUMN "grant_history"."changed_by_id" IS '修改人員';
COMMENT ON COLUMN "grant_history"."grant_id" IS '所屬案件';
COMMENT ON TABLE "grant_history" IS '補助案件歷史紀錄資料表';
        ALTER TABLE "grants" RENAME COLUMN "manager" TO "undertracker";
        ALTER TABLE "grants" DROP COLUMN "modified_by_id";
        COMMENT ON COLUMN "grants"."created_by_id" IS '建立人帳號';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "grants" RENAME COLUMN "undertracker" TO "manager";
        ALTER TABLE "grants" ADD "modified_by_id" INT NOT NULL;
        COMMENT ON COLUMN "grants"."created_by_id" IS '建立者';
        DROP TABLE IF EXISTS "grant_history";
        DROP TABLE IF EXISTS "grant_comments";
        DROP TABLE IF EXISTS "grant_attachments";
        ALTER TABLE "grants" ADD CONSTRAINT "fk_grants_users_0e06f3c8" FOREIGN KEY ("modified_by_id") REFERENCES "users" ("id") ON DELETE CASCADE;"""
