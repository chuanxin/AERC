from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "auth_tokens" ADD "otp_verified" BOOL NOT NULL DEFAULT False;
        ALTER TABLE "auth_tokens" ADD "otp" VARCHAR(6);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "auth_tokens" DROP COLUMN "otp_verified";
        ALTER TABLE "auth_tokens" DROP COLUMN "otp";"""
