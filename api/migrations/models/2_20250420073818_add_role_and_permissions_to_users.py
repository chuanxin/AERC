from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "users" ADD "role" VARCHAR(50)NOT NULL DEFAULT 'user';
        ALTER TABLE "users" ADD "permissions" JSONB;
        ALTER TABLE "users" ADD "is_active" BOOL NOT NULL DEFAULT True;
        ALTER TABLE "users" ADD "department" VARCHAR(100);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "users" DROP COLUMN "role";
        ALTER TABLE "users" DROP COLUMN "permissions";
        ALTER TABLE "users" DROP COLUMN "is_active";
        ALTER TABLE "users" DROP COLUMN "department";"""
