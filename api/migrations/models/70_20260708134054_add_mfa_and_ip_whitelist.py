from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "auth_tokens" ADD "otp_attempt_count" INT NOT NULL DEFAULT 0;
        ALTER TABLE "auth_tokens" ADD "otp_sent_at" TIMESTAMPTZ;
        CREATE TABLE IF NOT EXISTS "ip_whitelist_entries" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "cidr" VARCHAR(50) NOT NULL,
    "name" VARCHAR(100) NOT NULL,
    "is_active" BOOL NOT NULL DEFAULT True,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "created_by_id" INT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_ip_whitelis_is_acti_ff2914" ON "ip_whitelist_entries" ("is_active");
COMMENT ON COLUMN "auth_tokens"."otp_attempt_count" IS '累計 OTP 核對失敗次數（MFA_VERIFICATION 用，達 5 次即撤銷）';
COMMENT ON COLUMN "auth_tokens"."otp_sent_at" IS '最近一次發送 OTP 的時間（MFA_VERIFICATION 60 秒冷卻基準）';
COMMENT ON COLUMN "ip_whitelist_entries"."cidr" IS 'IPv4 CIDR 網段，如 192.168.1.0/24';
COMMENT ON COLUMN "ip_whitelist_entries"."name" IS '說明名稱';
COMMENT ON COLUMN "ip_whitelist_entries"."is_active" IS '是否啟用（停用不刪除）';
COMMENT ON COLUMN "ip_whitelist_entries"."created_at" IS '建立時間';
COMMENT ON COLUMN "ip_whitelist_entries"."created_by_id" IS '建立者';
COMMENT ON TABLE "ip_whitelist_entries" IS 'IP 白名單網段資料表';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "auth_tokens" DROP COLUMN "otp_attempt_count";
        ALTER TABLE "auth_tokens" DROP COLUMN "otp_sent_at";
        DROP TABLE IF EXISTS "ip_whitelist_entries";"""
