from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "irrigation_subsidies" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "facility_fee" DOUBLE PRECISION NOT NULL,
    "subsidy_reference" DOUBLE PRECISION NOT NULL,
    "working_fee" DOUBLE PRECISION NOT NULL,
    "is_active" BOOL NOT NULL DEFAULT True,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "facility_type_id" INT NOT NULL REFERENCES "facility_types" ("id") ON DELETE CASCADE,
    "irrigation_type_id" INT NOT NULL REFERENCES "irrigation_types" ("id") ON DELETE CASCADE,
    "subsidy_policy_id" INT NOT NULL REFERENCES "subsidy_policies" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "irrigation_subsidies"."facility_fee" IS '設施費用';
COMMENT ON COLUMN "irrigation_subsidies"."subsidy_reference" IS '補助參考值';
COMMENT ON COLUMN "irrigation_subsidies"."working_fee" IS '工作費';
COMMENT ON COLUMN "irrigation_subsidies"."is_active" IS '是否啟用';
COMMENT ON COLUMN "irrigation_subsidies"."created_at" IS '建立時間';
COMMENT ON COLUMN "irrigation_subsidies"."modified_at" IS '修改時間';
COMMENT ON COLUMN "irrigation_subsidies"."facility_type_id" IS '所屬設施類型';
COMMENT ON COLUMN "irrigation_subsidies"."irrigation_type_id" IS '所屬灌溉類型';
COMMENT ON COLUMN "irrigation_subsidies"."subsidy_policy_id" IS '所屬補助政策';
COMMENT ON TABLE "irrigation_subsidies" IS '灌溉補助資料表';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "irrigation_subsidies";"""
