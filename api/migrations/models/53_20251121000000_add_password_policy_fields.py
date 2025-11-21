from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "users" ADD "password_changed_at" TIMESTAMP;
        ALTER TABLE "users" ADD "failed_login_count" INT NOT NULL DEFAULT 0;
        ALTER TABLE "users" ADD "locked_until" TIMESTAMP;
    """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "users" DROP COLUMN "password_changed_at";
        ALTER TABLE "users" DROP COLUMN "failed_login_count";
        ALTER TABLE "users" DROP COLUMN "locked_until";
    """
