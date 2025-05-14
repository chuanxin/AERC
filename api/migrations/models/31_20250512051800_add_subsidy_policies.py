from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "subsidy_policies" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "year" INT NOT NULL,
    "general_subsidy_ratio" DOUBLE PRECISION NOT NULL,
    "gold_corridor_ratio" DOUBLE PRECISION NOT NULL,
    "indigenous_increase_ratio" DOUBLE PRECISION NOT NULL,
    "total_cap" DOUBLE PRECISION NOT NULL,
    "person_cap" DOUBLE PRECISION NOT NULL,
    "engine_cap" DOUBLE PRECISION NOT NULL,
    "control_device_min_area" DOUBLE PRECISION NOT NULL,
    "control_device_cap" DOUBLE PRECISION NOT NULL,
    "storage_cap" DOUBLE PRECISION NOT NULL,
    "storage_min_area" DOUBLE PRECISION NOT NULL,
    "reapplication_ratio" DOUBLE PRECISION NOT NULL,
    "design_fee_ratio" DOUBLE PRECISION NOT NULL,
    "is_active" BOOL NOT NULL DEFAULT True,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "created_by_id" INT REFERENCES "users" ("id") ON DELETE CASCADE,
    "funding_source_id" INT NOT NULL REFERENCES "funding_sources" ("id") ON DELETE CASCADE,
    "modified_by_id" INT REFERENCES "users" ("id") ON DELETE SET NULL
);
COMMENT ON COLUMN "subsidy_policies"."year" IS '年度';
COMMENT ON COLUMN "subsidy_policies"."general_subsidy_ratio" IS '一般補助比例(%)';
COMMENT ON COLUMN "subsidy_policies"."gold_corridor_ratio" IS '金色走廊補助比例(%)';
COMMENT ON COLUMN "subsidy_policies"."indigenous_increase_ratio" IS '原民區域增額補助比例(%)';
COMMENT ON COLUMN "subsidy_policies"."total_cap" IS '補助上限';
COMMENT ON COLUMN "subsidy_policies"."person_cap" IS '每人補助上限';
COMMENT ON COLUMN "subsidy_policies"."engine_cap" IS '每台引擎補助上限';
COMMENT ON COLUMN "subsidy_policies"."control_device_min_area" IS '控制裝置最小面積(公頃)';
COMMENT ON COLUMN "subsidy_policies"."control_device_cap" IS '控制裝置補助上限';
COMMENT ON COLUMN "subsidy_policies"."storage_cap" IS '儲水設備補助上限';
COMMENT ON COLUMN "subsidy_policies"."storage_min_area" IS '儲水設備最小面積(公頃)';
COMMENT ON COLUMN "subsidy_policies"."reapplication_ratio" IS '再申請比例(%)';
COMMENT ON COLUMN "subsidy_policies"."design_fee_ratio" IS '設計費比例(%)';
COMMENT ON COLUMN "subsidy_policies"."is_active" IS '是否啟用';
COMMENT ON COLUMN "subsidy_policies"."created_at" IS '建立時間';
COMMENT ON COLUMN "subsidy_policies"."modified_at" IS '修改時間';
COMMENT ON COLUMN "subsidy_policies"."created_by_id" IS '建立人帳號';
COMMENT ON COLUMN "subsidy_policies"."funding_source_id" IS '所屬補助來源';
COMMENT ON COLUMN "subsidy_policies"."modified_by_id" IS '修改人帳號';
COMMENT ON TABLE "subsidy_policies" IS '補助政策資料表';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "subsidy_policies";"""
