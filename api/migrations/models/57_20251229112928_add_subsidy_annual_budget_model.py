from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "subsidy_annual_budgets" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "year" INT NOT NULL,
    "approved_budget" DECIMAL(15,2) NOT NULL DEFAULT 0,
    "approved_area" DECIMAL(10,4) NOT NULL DEFAULT 0,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "created_by_id" INT REFERENCES "users" ("id") ON DELETE SET NULL,
    "modified_by_id" INT REFERENCES "users" ("id") ON DELETE SET NULL,
    "office_id" INT NOT NULL REFERENCES "offices" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_subsidy_ann_year_b14ae3" UNIQUE ("year", "office_id")
);
CREATE INDEX IF NOT EXISTS "idx_subsidy_ann_year_b14ae3" ON "subsidy_annual_budgets" ("year", "office_id");
COMMENT ON COLUMN "subsidy_annual_budgets"."year" IS '年度（民國年）';
COMMENT ON COLUMN "subsidy_annual_budgets"."approved_budget" IS '核定執行預算金額';
COMMENT ON COLUMN "subsidy_annual_budgets"."approved_area" IS '核定執行面積（公頃）';
COMMENT ON COLUMN "subsidy_annual_budgets"."created_at" IS '建立時間';
COMMENT ON COLUMN "subsidy_annual_budgets"."modified_at" IS '修改時間';
COMMENT ON COLUMN "subsidy_annual_budgets"."created_by_id" IS '建立人帳號';
COMMENT ON COLUMN "subsidy_annual_budgets"."modified_by_id" IS '修改人帳號';
COMMENT ON COLUMN "subsidy_annual_budgets"."office_id" IS '所屬管理處';
COMMENT ON TABLE "subsidy_annual_budgets" IS '補助年度預算計畫表';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "subsidy_annual_budgets";"""
