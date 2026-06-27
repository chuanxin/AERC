from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE "security_audit_logs" (
            "id" BIGSERIAL NOT NULL PRIMARY KEY,
            "occurred_at" TIMESTAMPTZ NOT NULL DEFAULT now(),
            "actor_id" INTEGER,
            "actor_username" VARCHAR(20),
            "actor_role" VARCHAR(50),
            "event_type" VARCHAR(20) NOT NULL,
            "action" VARCHAR(30) NOT NULL,
            "resource_type" VARCHAR(50),
            "resource_id" VARCHAR(100),
            "ip_address" VARCHAR(45),
            "user_agent" VARCHAR(500),
            "endpoint" VARCHAR(200),
            "changed_fields" JSONB,
            "result" VARCHAR(10) NOT NULL,
            "failure_reason" VARCHAR(500)
        );
        CREATE INDEX "idx_audit_occurred_at" ON "security_audit_logs" ("occurred_at" DESC);
        CREATE INDEX "idx_audit_actor_id" ON "security_audit_logs" ("actor_id");
        CREATE INDEX "idx_audit_event_type" ON "security_audit_logs" ("event_type");
        CREATE OR REPLACE FUNCTION prevent_audit_log_modification()
        RETURNS TRIGGER AS $$
        BEGIN
          RAISE EXCEPTION '稽核記錄不可修改或刪除';
        END;
        $$ LANGUAGE plpgsql;
        CREATE TRIGGER no_update_audit_logs
          BEFORE UPDATE ON "security_audit_logs"
          FOR EACH ROW EXECUTE FUNCTION prevent_audit_log_modification();
        CREATE TRIGGER no_delete_audit_logs
          BEFORE DELETE ON "security_audit_logs"
          FOR EACH ROW EXECUTE FUNCTION prevent_audit_log_modification();"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TRIGGER IF EXISTS no_delete_audit_logs ON "security_audit_logs";
        DROP TRIGGER IF EXISTS no_update_audit_logs ON "security_audit_logs";
        DROP FUNCTION IF EXISTS prevent_audit_log_modification();
        DROP TABLE IF EXISTS "security_audit_logs";"""
