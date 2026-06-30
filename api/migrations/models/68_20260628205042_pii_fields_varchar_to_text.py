from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "grants" ALTER COLUMN "applicant_id" TYPE TEXT USING "applicant_id"::TEXT;
        ALTER TABLE "grants" ALTER COLUMN "applicant_phone2" TYPE TEXT USING "applicant_phone2"::TEXT;
        ALTER TABLE "grants" ALTER COLUMN "address" TYPE TEXT USING "address"::TEXT;
        ALTER TABLE "grants" ALTER COLUMN "applicant_name" TYPE TEXT USING "applicant_name"::TEXT;
        ALTER TABLE "grants" ALTER COLUMN "applicant_phone" TYPE TEXT USING "applicant_phone"::TEXT;
        ALTER TABLE "users" ALTER COLUMN "full_name" TYPE TEXT USING "full_name"::TEXT;
        ALTER TABLE "users" ALTER COLUMN "mobile" TYPE TEXT USING "mobile"::TEXT;
        ALTER TABLE "users" ALTER COLUMN "phone_ext" TYPE TEXT USING "phone_ext"::TEXT;
        ALTER TABLE "users" ALTER COLUMN "phone" TYPE TEXT USING "phone"::TEXT;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "users" ALTER COLUMN "full_name" TYPE VARCHAR(50) USING "full_name"::VARCHAR(50);
        ALTER TABLE "users" ALTER COLUMN "mobile" TYPE VARCHAR(20) USING "mobile"::VARCHAR(20);
        ALTER TABLE "users" ALTER COLUMN "phone_ext" TYPE VARCHAR(10) USING "phone_ext"::VARCHAR(10);
        ALTER TABLE "users" ALTER COLUMN "phone" TYPE VARCHAR(20) USING "phone"::VARCHAR(20);
        ALTER TABLE "grants" ALTER COLUMN "applicant_id" TYPE VARCHAR(10) USING "applicant_id"::VARCHAR(10);
        ALTER TABLE "grants" ALTER COLUMN "applicant_phone2" TYPE VARCHAR(20) USING "applicant_phone2"::VARCHAR(20);
        ALTER TABLE "grants" ALTER COLUMN "address" TYPE VARCHAR(255) USING "address"::VARCHAR(255);
        ALTER TABLE "grants" ALTER COLUMN "applicant_name" TYPE VARCHAR(50) USING "applicant_name"::VARCHAR(50);
        ALTER TABLE "grants" ALTER COLUMN "applicant_phone" TYPE VARCHAR(20) USING "applicant_phone"::VARCHAR(20);"""
