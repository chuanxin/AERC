from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "auth_nonces" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "nonce" VARCHAR(128) NOT NULL UNIQUE,
    "expires_at" TIMESTAMPTZ NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS "idx_auth_nonces_nonce_0287ea" ON "auth_nonces" ("nonce");
CREATE INDEX IF NOT EXISTS "idx_auth_nonces_expires_f15277" ON "auth_nonces" ("expires_at");
COMMENT ON TABLE "auth_nonces" IS '防重放攻擊 nonce 儲存表';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "auth_nonces";"""
