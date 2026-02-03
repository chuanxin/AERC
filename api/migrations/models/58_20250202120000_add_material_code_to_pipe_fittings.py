"""
Migration 58: Add item_sn column to pipe_fittings table

這個遷移新增 item_sn 欄位來解決 pomno 同時兼任技術ID與業務料號的問題。
- pomno 保持為技術主鍵（不改變現有API/前端）
- item_sn 作為業務料號/品號（新材料必填，既有材料為NULL）
"""

from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE pipe_fittings 
        ADD COLUMN item_sn VARCHAR(50) NULL;
        
        COMMENT ON COLUMN pipe_fittings.item_sn IS '業務料號/品號（與pomno分離）';
        
        CREATE INDEX idx_pipe_fittings_item_sn ON pipe_fittings(item_sn) 
        WHERE item_sn IS NOT NULL;
    """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP INDEX IF EXISTS idx_pipe_fittings_item_sn;
        ALTER TABLE pipe_fittings DROP COLUMN IF EXISTS item_sn;
    """
