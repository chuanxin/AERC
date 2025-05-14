from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "subsidy_settings" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "year" INT NOT NULL,
    "working_fee_cap" DOUBLE PRECISION NOT NULL,
    "design_fee_ratio" DOUBLE PRECISION NOT NULL,
    "subsidy_ratio" DOUBLE PRECISION NOT NULL,
    "subsidy_cap" DOUBLE PRECISION NOT NULL,
    "is_active" BOOL NOT NULL DEFAULT True,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "created_by_id" INT REFERENCES "users" ("id") ON DELETE CASCADE,
    "ficility_type_id" INT NOT NULL REFERENCES "facility_types" ("id") ON DELETE CASCADE,
    "founding_source_id" INT NOT NULL REFERENCES "funding_sources" ("id") ON DELETE CASCADE,
    "irrigation_type_id" INT NOT NULL REFERENCES "irrigation_types" ("id") ON DELETE CASCADE,
    "modified_by_id" INT REFERENCES "users" ("id") ON DELETE SET NULL
);
COMMENT ON COLUMN "subsidy_settings"."year" IS '年度';
COMMENT ON COLUMN "subsidy_settings"."working_fee_cap" IS '工作費上限(元/公頃)';
COMMENT ON COLUMN "subsidy_settings"."design_fee_ratio" IS '規劃設計費比例(%)';
COMMENT ON COLUMN "subsidy_settings"."subsidy_ratio" IS '補助比例(%)';
COMMENT ON COLUMN "subsidy_settings"."subsidy_cap" IS '補助上限(元/公頃)';
COMMENT ON COLUMN "subsidy_settings"."is_active" IS '是否啟用';
COMMENT ON COLUMN "subsidy_settings"."created_at" IS '建立時間';
COMMENT ON COLUMN "subsidy_settings"."modified_at" IS '修改時間';
COMMENT ON COLUMN "subsidy_settings"."created_by_id" IS '建立人帳號';
COMMENT ON COLUMN "subsidy_settings"."ficility_type_id" IS '所屬設施類型';
COMMENT ON COLUMN "subsidy_settings"."founding_source_id" IS '所屬補助來源';
COMMENT ON COLUMN "subsidy_settings"."irrigation_type_id" IS '所屬灌溉類型';
COMMENT ON COLUMN "subsidy_settings"."modified_by_id" IS '修改人帳號';
COMMENT ON TABLE "subsidy_settings" IS '補助設定資料表';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "subsidy_settings";"""
