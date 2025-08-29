from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "grant_versions" ADD "data_schema_version" VARCHAR(6) NOT NULL DEFAULT '1.0';
        ALTER TABLE "grants" ADD "is_legacy" BOOL NOT NULL DEFAULT False;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "grants" DROP COLUMN "is_legacy";
        ALTER TABLE "grant_versions" DROP COLUMN "data_schema_version";"""
