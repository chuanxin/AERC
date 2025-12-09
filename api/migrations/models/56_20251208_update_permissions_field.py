"""
Migration 56: 更新使用者權限欄位定義

變更說明：
- 更新 permissions 欄位註解（定義完整結構）
- 新增 GIN 索引加速 JSONB 查詢

權限結構：
{
  "mode": "default" | "scoped" | "custom",
  "scope": {
    "office_ids": [11, 12],
    "own_only": false,
    "department_filter": {...}
  },
  "custom": {
    "modules": {
      "grants": ["view", "create", ...],
      "users": [...],
      ...
    }
  }
}

Created: 2025-12-08
"""

from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        -- 更新權限欄位註解（重新定義用途）
        COMMENT ON COLUMN "users"."permissions" IS
        '使用者權限設定（JSONB）：完整結構包含 mode（權限模式）、scope（權限範圍）、custom（自訂權限矩陣）';

        -- 建立 GIN 索引加速 JSONB 查詢（如果不存在）
        CREATE INDEX IF NOT EXISTS "idx_users_permissions"
        ON "users" USING GIN ("permissions");
    """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        -- 移除索引
        DROP INDEX IF EXISTS "idx_users_permissions";

        -- 恢復原始註解
        COMMENT ON COLUMN "users"."permissions" IS '特定權限設定(JSON格式)';
    """
