from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "counties" ADD "land_code" VARCHAR(10);
        ALTER TABLE "towns" ADD "land_code" VARCHAR(10);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "towns" DROP COLUMN "land_code";
        ALTER TABLE "counties" DROP COLUMN "land_code";"""
