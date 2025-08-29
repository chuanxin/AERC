from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "grant_papers" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "document_type" VARCHAR(50) NOT NULL,
    "document_data" JSONB NOT NULL,
    "data_hash" VARCHAR(64),
    "generated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "is_valid" BOOL NOT NULL DEFAULT True,
    "created_by_id" INT REFERENCES "users" ("id") ON DELETE CASCADE,
    "version_id" INT NOT NULL REFERENCES "grant_versions" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_grant_paper_version_5eb41f" UNIQUE ("version_id", "document_type")
);
CREATE INDEX IF NOT EXISTS "idx_grant_paper_version_5eb41f" ON "grant_papers" ("version_id", "document_type");
COMMENT ON COLUMN "grant_papers"."document_type" IS '文件類型';
COMMENT ON COLUMN "grant_papers"."document_data" IS '文件內容';
COMMENT ON COLUMN "grant_papers"."data_hash" IS '文件內容的Hash值，用於檢查變更';
COMMENT ON COLUMN "grant_papers"."generated_at" IS '建立時間';
COMMENT ON COLUMN "grant_papers"."is_valid" IS '文件是否有效';
COMMENT ON COLUMN "grant_papers"."created_by_id" IS '建立人帳號';
COMMENT ON COLUMN "grant_papers"."version_id" IS '所屬補助申請版本';
COMMENT ON TABLE "grant_papers" IS '補助申請文件表';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "grant_papers";"""
