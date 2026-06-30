from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        REVOKE UPDATE, DELETE ON security_audit_logs FROM aerc_dryfarm_admin;
    """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        GRANT UPDATE, DELETE ON security_audit_logs TO aerc_dryfarm_admin;
    """
