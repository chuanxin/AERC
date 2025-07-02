from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        -- Add case_number column to grant_locations table
        ALTER TABLE "grant_locations" ADD COLUMN "case_number" VARCHAR(100);
        
        -- Add comment for the new column
        COMMENT ON COLUMN "grant_locations"."case_number" IS '案件編號';
    """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        -- Remove case_number column from grant_locations table
        ALTER TABLE "grant_locations" DROP COLUMN IF EXISTS "case_number";
    """
