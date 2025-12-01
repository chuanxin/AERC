"""
修正密碼政策欄位的時區類型

問題：Migration 53 使用了 TIMESTAMP (timezone-naive)
修正：改為 TIMESTAMPTZ (timezone-aware)，與系統其他 datetime 欄位一致

影響欄位：
- users.password_changed_at: TIMESTAMP → TIMESTAMPTZ
- users.locked_until: TIMESTAMP → TIMESTAMPTZ

相關 Issue：
- Windows 部署環境中 asyncpg 拋出 "can't subtract offset-naive and offset-aware datetimes"
- 程式碼使用 datetime.now(timezone.utc) 但資料庫欄位是 TIMESTAMP
"""
from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        -- 修正 password_changed_at 欄位類型
        ALTER TABLE "users"
        ALTER COLUMN "password_changed_at" TYPE TIMESTAMPTZ
        USING "password_changed_at" AT TIME ZONE 'UTC';

        -- 修正 locked_until 欄位類型
        ALTER TABLE "users"
        ALTER COLUMN "locked_until" TYPE TIMESTAMPTZ
        USING "locked_until" AT TIME ZONE 'UTC';
    """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        -- 還原為 TIMESTAMP (不建議)
        ALTER TABLE "users"
        ALTER COLUMN "password_changed_at" TYPE TIMESTAMP
        USING "password_changed_at" AT TIME ZONE 'UTC';

        ALTER TABLE "users"
        ALTER COLUMN "locked_until" TYPE TIMESTAMP
        USING "locked_until" AT TIME ZONE 'UTC';
    """
