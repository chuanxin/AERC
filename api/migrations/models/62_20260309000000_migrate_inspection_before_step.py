from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        UPDATE grant_attachments
        SET step = 3
        WHERE step = 5
          AND category = 'inspection_before'
          AND status = 'active';
    """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        UPDATE grant_attachments
        SET step = 5
        WHERE step = 3
          AND category = 'inspection_before'
          AND status = 'active';
    """
