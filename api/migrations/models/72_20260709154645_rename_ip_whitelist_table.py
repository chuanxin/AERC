from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "ip_whitelist_entries" RENAME TO "security_ip_whitelist";"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "security_ip_whitelist" RENAME TO "ip_whitelist_entries";"""
