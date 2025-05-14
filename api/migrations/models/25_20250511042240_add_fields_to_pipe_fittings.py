from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "pipe_fittings" ADD "is_terminal" BOOL NOT NULL DEFAULT False;
        ALTER TABLE "pipe_fittings" ADD "year" INT;
        ALTER TABLE "pipe_fittings" ADD "is_active" BOOL NOT NULL DEFAULT True;
        ALTER TABLE "pipe_fittings" ADD "modified_by_id" INT;
        ALTER TABLE "pipe_fittings" ADD "modified_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP;
        ALTER TABLE "pipe_fittings" ADD "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP;
        ALTER TABLE "pipe_fittings" ADD "created_by_id" INT;
        ALTER TABLE "pipe_fittings" ADD "compatibility_group" JSONB;
        ALTER TABLE "pipe_fittings" ADD "typical_location" VARCHAR(255);
        ALTER TABLE "pipe_fittings" ADD CONSTRAINT "fk_pipe_fit_users_e2d51da7" FOREIGN KEY ("modified_by_id") REFERENCES "users" ("id") ON DELETE SET NULL;
        ALTER TABLE "pipe_fittings" ADD CONSTRAINT "fk_pipe_fit_users_842e4d14" FOREIGN KEY ("created_by_id") REFERENCES "users" ("id") ON DELETE CASCADE;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "pipe_fittings" DROP CONSTRAINT IF EXISTS "fk_pipe_fit_users_842e4d14";
        ALTER TABLE "pipe_fittings" DROP CONSTRAINT IF EXISTS "fk_pipe_fit_users_e2d51da7";
        ALTER TABLE "pipe_fittings" DROP COLUMN "is_terminal";
        ALTER TABLE "pipe_fittings" DROP COLUMN "year";
        ALTER TABLE "pipe_fittings" DROP COLUMN "is_active";
        ALTER TABLE "pipe_fittings" DROP COLUMN "modified_by_id";
        ALTER TABLE "pipe_fittings" DROP COLUMN "modified_at";
        ALTER TABLE "pipe_fittings" DROP COLUMN "created_at";
        ALTER TABLE "pipe_fittings" DROP COLUMN "created_by_id";
        ALTER TABLE "pipe_fittings" DROP COLUMN "compatibility_group";
        ALTER TABLE "pipe_fittings" DROP COLUMN "typical_location";"""
