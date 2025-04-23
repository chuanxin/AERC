from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "villages" ALTER COLUMN "code" TYPE VARCHAR(20) USING "code"::VARCHAR(20);
        ALTER TABLE "villages" ALTER COLUMN "name" TYPE VARCHAR(10) USING "name"::VARCHAR(10);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "villages" ALTER COLUMN "code" TYPE VARCHAR(10) USING "code"::VARCHAR(10);
        ALTER TABLE "villages" ALTER COLUMN "name" TYPE VARCHAR(20) USING "name"::VARCHAR(20);"""
