from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "grant_attachments" ADD "category" VARCHAR(20) NOT NULL;
        ALTER TABLE "grant_attachments" ADD "uploaded_by_id" INT NOT NULL;
        ALTER TABLE "grant_attachments" ADD "version_id" INT;
        ALTER TABLE "grant_attachments" ADD "filesize" BIGINT NOT NULL;
        ALTER TABLE "grant_attachments" ADD "filepath" VARCHAR(500) NOT NULL;
        ALTER TABLE "grant_attachments" RENAME COLUMN "upload_time" TO "uploaded_at";
        ALTER TABLE "grant_attachments" ADD "original_filename" VARCHAR(255) NOT NULL;
        ALTER TABLE "grant_attachments" ADD "step" INT NOT NULL;
        ALTER TABLE "grant_attachments" ADD "mime_type" VARCHAR(100) NOT NULL;
        ALTER TABLE "grant_attachments" ADD "internal_filename" VARCHAR(255) NOT NULL;
        ALTER TABLE "grant_attachments" ADD "status" VARCHAR(20) NOT NULL DEFAULT 'active';
        ALTER TABLE "grant_attachments" ADD "related_attachment_id" INT;
        ALTER TABLE "grant_attachments" ADD "checksum" VARCHAR(64) NOT NULL;
        ALTER TABLE "grant_attachments" DROP COLUMN "file_type";
        ALTER TABLE "grant_attachments" DROP COLUMN "file_path";
        ALTER TABLE "grant_attachments" DROP COLUMN "file_size";
        ALTER TABLE "grant_attachments" DROP COLUMN "file_name";
        COMMENT ON COLUMN "grant_attachments"."grant_id" IS '所屬補助申請案件';
        ALTER TABLE "grant_attachments" ALTER COLUMN "description" TYPE TEXT USING "description"::TEXT;
        COMMENT ON COLUMN "grant_attachments"."description" IS '附件說明或備註';
        COMMENT ON COLUMN "grants"."received_time" IS '建檔時間';
        COMMENT ON COLUMN "grants"."received_date" IS '建檔日期';
        ALTER TABLE "grant_attachments" ADD CONSTRAINT "fk_grant_at_grant_ve_c5d622d6" FOREIGN KEY ("version_id") REFERENCES "grant_versions" ("id") ON DELETE CASCADE;
        ALTER TABLE "grant_attachments" ADD CONSTRAINT "fk_grant_at_grant_at_9a3e1e2d" FOREIGN KEY ("related_attachment_id") REFERENCES "grant_attachments" ("id") ON DELETE CASCADE;
        ALTER TABLE "grant_attachments" ADD CONSTRAINT "fk_grant_at_users_e553c1be" FOREIGN KEY ("uploaded_by_id") REFERENCES "users" ("id") ON DELETE CASCADE;
        CREATE INDEX IF NOT EXISTS "idx_grant_attac_interna_b76bd3" ON "grant_attachments" ("internal_filename");
        CREATE INDEX IF NOT EXISTS "idx_grant_attac_status_4e6a4e" ON "grant_attachments" ("status");
        CREATE INDEX IF NOT EXISTS "idx_grant_attac_grant_i_e27364" ON "grant_attachments" ("grant_id", "step", "category");
        CREATE INDEX IF NOT EXISTS "idx_grant_attac_uploade_5920a0" ON "grant_attachments" ("uploaded_at");"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP INDEX IF EXISTS "idx_grant_attac_uploade_5920a0";
        DROP INDEX IF EXISTS "idx_grant_attac_grant_i_e27364";
        DROP INDEX IF EXISTS "idx_grant_attac_status_4e6a4e";
        DROP INDEX IF EXISTS "idx_grant_attac_interna_b76bd3";
        ALTER TABLE "grant_attachments" DROP CONSTRAINT IF EXISTS "fk_grant_at_users_e553c1be";
        ALTER TABLE "grant_attachments" DROP CONSTRAINT IF EXISTS "fk_grant_at_grant_at_9a3e1e2d";
        ALTER TABLE "grant_attachments" DROP CONSTRAINT IF EXISTS "fk_grant_at_grant_ve_c5d622d6";
        COMMENT ON COLUMN "grants"."received_time" IS '收件時間';
        COMMENT ON COLUMN "grants"."received_date" IS '收件日期';
        ALTER TABLE "grant_attachments" ADD "file_type" VARCHAR(50) NOT NULL;
        ALTER TABLE "grant_attachments" ADD "file_path" VARCHAR(255) NOT NULL;
        ALTER TABLE "grant_attachments" RENAME COLUMN "uploaded_at" TO "upload_time";
        ALTER TABLE "grant_attachments" ADD "file_size" INT NOT NULL;
        ALTER TABLE "grant_attachments" ADD "file_name" VARCHAR(255) NOT NULL;
        ALTER TABLE "grant_attachments" DROP COLUMN "category";
        ALTER TABLE "grant_attachments" DROP COLUMN "uploaded_by_id";
        ALTER TABLE "grant_attachments" DROP COLUMN "version_id";
        ALTER TABLE "grant_attachments" DROP COLUMN "filesize";
        ALTER TABLE "grant_attachments" DROP COLUMN "filepath";
        ALTER TABLE "grant_attachments" DROP COLUMN "original_filename";
        ALTER TABLE "grant_attachments" DROP COLUMN "step";
        ALTER TABLE "grant_attachments" DROP COLUMN "mime_type";
        ALTER TABLE "grant_attachments" DROP COLUMN "internal_filename";
        ALTER TABLE "grant_attachments" DROP COLUMN "status";
        ALTER TABLE "grant_attachments" DROP COLUMN "related_attachment_id";
        ALTER TABLE "grant_attachments" DROP COLUMN "checksum";
        COMMENT ON COLUMN "grant_attachments"."grant_id" IS '所屬案件';
        ALTER TABLE "grant_attachments" ALTER COLUMN "description" TYPE VARCHAR(255) USING "description"::VARCHAR(255);
        COMMENT ON COLUMN "grant_attachments"."description" IS '檔案描述';"""
