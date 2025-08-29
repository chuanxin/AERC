from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "grants" ADD "is_disaster_case" BOOL NOT NULL DEFAULT False;
        ALTER TABLE "grants" ADD "disaster_case_description" TEXT;
    """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "grants" DROP COLUMN "is_disaster_case";
        ALTER TABLE "grants" DROP COLUMN "disaster_case_description";
    """
