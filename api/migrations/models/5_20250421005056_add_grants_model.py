from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "grants" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "sn" INT NOT NULL,
    "case_number" VARCHAR(20) NOT NULL,
    "year" INT NOT NULL,
    "applicant_name" VARCHAR(50) NOT NULL,
    "applicant_id" VARCHAR(10) NOT NULL,
    "applicant_phone" VARCHAR(20) NOT NULL,
    "address" VARCHAR(255) NOT NULL,
    "manager" VARCHAR(50) NOT NULL,
    "received_date" DATE NOT NULL,
    "received_time" TIMETZ NOT NULL,
    "status" VARCHAR(20) NOT NULL DEFAULT 'draft',
    "status_detail" VARCHAR(50),
    "current_step" INT NOT NULL DEFAULT 1,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "created_by_id" INT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE,
    "modified_by_id" INT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE,
    "office_id" INT REFERENCES "offices" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "grants"."sn" IS '流水號，每年每管理處內唯一';
COMMENT ON COLUMN "grants"."case_number" IS '案件編號';
COMMENT ON COLUMN "grants"."year" IS '申請年度';
COMMENT ON COLUMN "grants"."applicant_name" IS '申請人姓名';
COMMENT ON COLUMN "grants"."applicant_id" IS '申請人身分證字號';
COMMENT ON COLUMN "grants"."applicant_phone" IS '申請人電話';
COMMENT ON COLUMN "grants"."address" IS '詳細地址';
COMMENT ON COLUMN "grants"."manager" IS '承辦人姓名';
COMMENT ON COLUMN "grants"."received_date" IS '收件日期';
COMMENT ON COLUMN "grants"."received_time" IS '收件時間';
COMMENT ON COLUMN "grants"."status" IS '案件狀態: draft, submitted, reviewing, approved, rejected, completed';
COMMENT ON COLUMN "grants"."status_detail" IS '狀態詳情';
COMMENT ON COLUMN "grants"."current_step" IS '目前步驟';
COMMENT ON COLUMN "grants"."created_at" IS '建立時間';
COMMENT ON COLUMN "grants"."modified_at" IS '修改時間';
COMMENT ON COLUMN "grants"."created_by_id" IS '建立者';
COMMENT ON COLUMN "grants"."modified_by_id" IS '修改者';
COMMENT ON COLUMN "grants"."office_id" IS '管理處';
COMMENT ON TABLE "grants" IS '補助申請案件資料表';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "grants";"""
