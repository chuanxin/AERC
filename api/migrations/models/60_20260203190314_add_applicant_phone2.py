from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP INDEX IF EXISTS "idx_pipe_fittin_name_750ed8";
        ALTER TABLE "grants" ADD "applicant_phone2" VARCHAR(20);
        CREATE INDEX IF NOT EXISTS "idx_pipe_fittin_name_139cf7" ON "pipe_fittings" ("name", "material_id", "module_id", "diameter1_id", "diameter2_id", "diameter3_id", "office_id");"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP INDEX IF EXISTS "idx_pipe_fittin_name_139cf7";
        ALTER TABLE "grants" DROP COLUMN "applicant_phone2";
        CREATE INDEX IF NOT EXISTS "idx_pipe_fittin_name_750ed8" ON "pipe_fittings" ("name", "material_id", "module_id", "diameter1_id", "diameter2_id", "diameter3_id", "office_id", "description");"""
