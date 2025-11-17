from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "auth_tokens" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "token_type" VARCHAR(18) NOT NULL,
    "token" VARCHAR(128) NOT NULL UNIQUE,
    "status" VARCHAR(7) NOT NULL DEFAULT 'pending',
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "expires_at" TIMESTAMPTZ NOT NULL,
    "used_at" TIMESTAMPTZ,
    "ip_address" VARCHAR(45),
    "user_agent" VARCHAR(255),
    "user_id" INT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_auth_tokens_token_30e699" ON "auth_tokens" ("token");
CREATE INDEX IF NOT EXISTS "idx_auth_tokens_user_id_ef3929" ON "auth_tokens" ("user_id", "token_type", "status");
CREATE INDEX IF NOT EXISTS "idx_auth_tokens_expires_00120e" ON "auth_tokens" ("expires_at");
COMMENT ON COLUMN "auth_tokens"."token_type" IS 'Token 類型';
COMMENT ON COLUMN "auth_tokens"."token" IS 'Token 值（UUID）';
COMMENT ON COLUMN "auth_tokens"."status" IS 'Token 狀態';
COMMENT ON COLUMN "auth_tokens"."created_at" IS '建立時間';
COMMENT ON COLUMN "auth_tokens"."expires_at" IS '過期時間';
COMMENT ON COLUMN "auth_tokens"."used_at" IS '使用時間';
COMMENT ON COLUMN "auth_tokens"."ip_address" IS '請求 IP 地址';
COMMENT ON COLUMN "auth_tokens"."user_agent" IS '請求 User-Agent';
COMMENT ON COLUMN "auth_tokens"."user_id" IS '所屬用戶';
COMMENT ON TABLE "auth_tokens" IS '認證 Token 資料表';
        ALTER TABLE "users" ADD "email_verified" BOOL NOT NULL DEFAULT False;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "users" DROP COLUMN "email_verified";
        DROP TABLE IF EXISTS "auth_tokens";"""
