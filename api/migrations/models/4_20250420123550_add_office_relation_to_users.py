from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "users" ADD "office_id" INT;
        COMMENT ON COLUMN "users"."modified_at" IS '修改時間';
        COMMENT ON COLUMN "users"."created_at" IS '建立時間';
        ALTER TABLE "users" ADD CONSTRAINT "fk_users_offices_82a747d8" FOREIGN KEY ("office_id") REFERENCES "offices" ("id") ON DELETE CASCADE;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "users" DROP CONSTRAINT IF EXISTS "fk_users_offices_82a747d8";
        ALTER TABLE "users" DROP COLUMN "office_id";
        COMMENT ON COLUMN "users"."modified_at" IS NULL;
        COMMENT ON COLUMN "users"."created_at" IS NULL;"""
