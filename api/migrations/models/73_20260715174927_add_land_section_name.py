from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "grant_locations" ADD "land_section_name" VARCHAR(255);
COMMENT ON COLUMN "grant_locations"."land_section_name" IS '地段中文名稱';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "grant_locations" DROP COLUMN "land_section_name";"""
