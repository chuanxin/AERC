from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "subsidy_settings" DROP CONSTRAINT IF EXISTS "fk_subsidy__facility_1766400c";
        ALTER TABLE "subsidy_settings" RENAME COLUMN "ficility_type_id" TO "facility_type_id";
        ALTER TABLE "subsidy_settings" ADD CONSTRAINT "fk_subsidy__facility_c0bcd3e0" FOREIGN KEY ("facility_type_id") REFERENCES "facility_types" ("id") ON DELETE CASCADE;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "subsidy_settings" DROP CONSTRAINT IF EXISTS "fk_subsidy__facility_c0bcd3e0";
        ALTER TABLE "subsidy_settings" RENAME COLUMN "facility_type_id" TO "ficility_type_id";
        ALTER TABLE "subsidy_settings" ADD CONSTRAINT "fk_subsidy__facility_1766400c" FOREIGN KEY ("ficility_type_id") REFERENCES "facility_types" ("id") ON DELETE CASCADE;"""
