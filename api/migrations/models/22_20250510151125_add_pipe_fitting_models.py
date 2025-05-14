from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "pipe_fittings" (
    "pomno" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(50) NOT NULL,
    "unit" VARCHAR(10) NOT NULL,
    "description" VARCHAR(255),
    "length" DOUBLE PRECISION NOT NULL,
    "diameter1_id" INT NOT NULL REFERENCES "pf_diameters" ("id") ON DELETE CASCADE,
    "diameter2_id" INT NOT NULL REFERENCES "pf_diameters" ("id") ON DELETE CASCADE,
    "diameter3_id" INT NOT NULL REFERENCES "pf_diameters" ("id") ON DELETE CASCADE,
    "material_id" INT NOT NULL REFERENCES "pf_materials" ("id") ON DELETE CASCADE,
    "module_id" INT NOT NULL REFERENCES "pf_modules" ("id") ON DELETE CASCADE,
    "office_id" INT REFERENCES "offices" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_pipe_fittin_name_139cf7" UNIQUE ("name", "material_id", "module_id", "diameter1_id", "diameter2_id", "diameter3_id", "office_id")
);
CREATE INDEX IF NOT EXISTS "idx_pipe_fittin_name_139cf7" ON "pipe_fittings" ("name", "material_id", "module_id", "diameter1_id", "diameter2_id", "diameter3_id", "office_id");
COMMENT ON COLUMN "pipe_fittings"."pomno" IS '管件代碼';
COMMENT ON COLUMN "pipe_fittings"."name" IS '管件名稱或料號';
COMMENT ON COLUMN "pipe_fittings"."unit" IS '管件計量單位';
COMMENT ON COLUMN "pipe_fittings"."description" IS '管件描述';
COMMENT ON COLUMN "pipe_fittings"."length" IS '管件長度';
COMMENT ON COLUMN "pipe_fittings"."diameter1_id" IS '所屬管徑1';
COMMENT ON COLUMN "pipe_fittings"."diameter2_id" IS '所屬管徑2';
COMMENT ON COLUMN "pipe_fittings"."diameter3_id" IS '所屬管徑3';
COMMENT ON COLUMN "pipe_fittings"."material_id" IS '所屬管件材質';
COMMENT ON COLUMN "pipe_fittings"."module_id" IS '所屬管件功能類型';
COMMENT ON COLUMN "pipe_fittings"."office_id" IS '所屬單位/管理處';
COMMENT ON TABLE "pipe_fittings" IS '管件資料表';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "pipe_fittings";"""
