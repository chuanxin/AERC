from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "grants" DROP CONSTRAINT IF EXISTS "fk_grants_offices_211ba12b";
        ALTER TABLE "grants" ADD "_office_id" INT;
        ALTER TABLE "grants" ADD "office" VARCHAR(50) NOT NULL;
        ALTER TABLE "grants" DROP COLUMN "office_id";"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "grants" ADD "office_id" INT;
        ALTER TABLE "grants" DROP COLUMN "_office_id";
        ALTER TABLE "grants" DROP COLUMN "office";
        ALTER TABLE "grants" ADD CONSTRAINT "fk_grants_offices_211ba12b" FOREIGN KEY ("office_id") REFERENCES "offices" ("id") ON DELETE CASCADE;"""
