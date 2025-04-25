from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "grants" RENAME COLUMN "_office_id" TO "office_id";"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "grants" RENAME COLUMN "office_id" TO "_office_id";"""
