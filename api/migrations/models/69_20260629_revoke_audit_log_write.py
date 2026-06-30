from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        REVOKE UPDATE, DELETE ON security_audit_logs FROM hello_fastapi;
    """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        GRANT UPDATE, DELETE ON security_audit_logs TO hello_fastapi;
    """
