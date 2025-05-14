from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "pipe_fittings" ALTER COLUMN "unit" DROP NOT NULL;
        ALTER TABLE "pipe_fittings" ALTER COLUMN "diameter3_id" DROP NOT NULL;
        ALTER TABLE "pipe_fittings" ALTER COLUMN "diameter1_id" DROP NOT NULL;
        ALTER TABLE "pipe_fittings" ALTER COLUMN "length" DROP NOT NULL;
        ALTER TABLE "pipe_fittings" ALTER COLUMN "diameter2_id" DROP NOT NULL;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "pipe_fittings" ALTER COLUMN "unit" SET NOT NULL;
        ALTER TABLE "pipe_fittings" ALTER COLUMN "diameter3_id" SET NOT NULL;
        ALTER TABLE "pipe_fittings" ALTER COLUMN "diameter1_id" SET NOT NULL;
        ALTER TABLE "pipe_fittings" ALTER COLUMN "length" SET NOT NULL;
        ALTER TABLE "pipe_fittings" ALTER COLUMN "diameter2_id" SET NOT NULL;"""
