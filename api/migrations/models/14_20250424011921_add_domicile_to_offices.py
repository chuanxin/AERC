from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "grants" ADD "county" VARCHAR(30) NOT NULL;
        ALTER TABLE "grants" ADD "town" VARCHAR(30) NOT NULL;
        ALTER TABLE "grants" ADD "village" VARCHAR(30);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "grants" DROP COLUMN "county";
        ALTER TABLE "grants" DROP COLUMN "town";
        ALTER TABLE "grants" DROP COLUMN "village";"""
