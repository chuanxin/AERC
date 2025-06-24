from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "grants" DROP CONSTRAINT IF EXISTS "fk_grants_grant_ve_359378ba";
        ALTER TABLE "grants" RENAME COLUMN "active_version_id_id" TO "active_version_id";
        ALTER TABLE "grants" ADD CONSTRAINT "fk_grants_grant_ve_c6ec1b4d" FOREIGN KEY ("active_version_id") REFERENCES "grant_versions" ("id") ON DELETE CASCADE;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "grants" DROP CONSTRAINT IF EXISTS "fk_grants_grant_ve_c6ec1b4d";
        ALTER TABLE "grants" RENAME COLUMN "active_version_id" TO "active_version_id_id";
        ALTER TABLE "grants" ADD CONSTRAINT "fk_grants_grant_ve_359378ba" FOREIGN KEY ("active_version_id_id") REFERENCES "grant_versions" ("id") ON DELETE CASCADE;"""
