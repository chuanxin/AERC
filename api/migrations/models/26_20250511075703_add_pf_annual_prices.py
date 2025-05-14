from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "pf_annual_prices" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "is_active" BOOL NOT NULL DEFAULT True,
    "year" INT NOT NULL,
    "price" DOUBLE PRECISION NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "created_by_id" INT REFERENCES "users" ("id") ON DELETE CASCADE,
    "modified_by_id" INT REFERENCES "users" ("id") ON DELETE SET NULL,
    "office_id" INT REFERENCES "offices" ("id") ON DELETE CASCADE,
    "pipe_fitting_id" INT NOT NULL REFERENCES "pipe_fittings" ("pomno") ON DELETE CASCADE,
    CONSTRAINT "uid_pf_annual_p_pipe_fi_1abacf" UNIQUE ("pipe_fitting_id", "year", "office_id")
);
CREATE INDEX IF NOT EXISTS "idx_pf_annual_p_pipe_fi_1abacf" ON "pf_annual_prices" ("pipe_fitting_id", "year", "office_id");
COMMENT ON COLUMN "pf_annual_prices"."is_active" IS '是否啟用';
COMMENT ON COLUMN "pf_annual_prices"."year" IS '年度';
COMMENT ON COLUMN "pf_annual_prices"."price" IS '價格';
COMMENT ON COLUMN "pf_annual_prices"."created_at" IS '建立時間';
COMMENT ON COLUMN "pf_annual_prices"."modified_at" IS '修改時間';
COMMENT ON COLUMN "pf_annual_prices"."created_by_id" IS '建立人帳號';
COMMENT ON COLUMN "pf_annual_prices"."modified_by_id" IS '修改人帳號';
COMMENT ON COLUMN "pf_annual_prices"."office_id" IS '所屬單位/管理處';
COMMENT ON COLUMN "pf_annual_prices"."pipe_fitting_id" IS '所屬管件';
COMMENT ON TABLE "pf_annual_prices" IS '管件年度價格資料表';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "pf_annual_prices";"""
