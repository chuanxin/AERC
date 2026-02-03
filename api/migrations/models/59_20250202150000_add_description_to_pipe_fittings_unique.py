"""
Migration: 將 description 加入 pipe_fittings 唯一約束
Date: 2025-02-02

變更內容：
1. 處理重複記錄（規格相同 + description 都是 NULL）的資料
2. 將 description 欄位改為 NOT NULL + 預設空字串
3. 更新唯一約束，加入 description 欄位
"""

from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        -- ============================================================
        -- STEP 1: 為重複記錄自動生成 description
        -- 邏輯：每組重複中，pomno 最小的設為空字串，其餘依序編號 #1, #2...
        -- ============================================================

        WITH ranked AS (
            SELECT
                pomno,
                ROW_NUMBER() OVER (
                    PARTITION BY name, material_id, module_id,
                                 COALESCE(diameter1_id, -1),
                                 COALESCE(diameter2_id, -1),
                                 COALESCE(diameter3_id, -1),
                                 office_id
                    ORDER BY pomno
                ) as rn,
                COUNT(*) OVER (
                    PARTITION BY name, material_id, module_id,
                                 COALESCE(diameter1_id, -1),
                                 COALESCE(diameter2_id, -1),
                                 COALESCE(diameter3_id, -1),
                                 office_id
                ) as group_count
            FROM pipe_fittings
            WHERE description IS NULL
        )
        UPDATE pipe_fittings pf
        SET description = CASE
            WHEN r.rn = 1 THEN ''
            ELSE '#' || (r.rn - 1)::text
        END
        FROM ranked r
        WHERE pf.pomno = r.pomno
          AND r.group_count > 1;

        -- ============================================================
        -- STEP 2: 將剩餘的 NULL 改為空字串
        -- ============================================================

        UPDATE pipe_fittings
        SET description = ''
        WHERE description IS NULL;

        -- ============================================================
        -- STEP 3: 修改欄位為 NOT NULL + 預設值
        -- ============================================================

        ALTER TABLE pipe_fittings
        ALTER COLUMN description SET DEFAULT '';

        ALTER TABLE pipe_fittings
        ALTER COLUMN description SET NOT NULL;

        -- ============================================================
        -- STEP 4: 更新唯一約束（加入 description）
        -- ============================================================

        ALTER TABLE pipe_fittings
        DROP CONSTRAINT IF EXISTS uid_pipe_fittin_name_139cf7;

        ALTER TABLE pipe_fittings
        ADD CONSTRAINT uid_pipe_fittin_name_desc_unique
        UNIQUE (name, material_id, module_id, diameter1_id, diameter2_id, diameter3_id, office_id, description);

        -- ============================================================
        -- STEP 5: 更新索引（加入 description）
        -- ============================================================

        DROP INDEX IF EXISTS idx_pipe_fittin_name_139cf7;

        CREATE INDEX idx_pipe_fittin_name_desc
        ON pipe_fittings (name, material_id, module_id, diameter1_id, diameter2_id, diameter3_id, office_id, description);
    """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        -- 還原索引
        DROP INDEX IF EXISTS idx_pipe_fittin_name_desc;

        CREATE INDEX idx_pipe_fittin_name_139cf7
        ON pipe_fittings (name, material_id, module_id, diameter1_id, diameter2_id, diameter3_id, office_id);

        -- 還原唯一約束
        ALTER TABLE pipe_fittings
        DROP CONSTRAINT IF EXISTS uid_pipe_fittin_name_desc_unique;

        ALTER TABLE pipe_fittings
        ADD CONSTRAINT uid_pipe_fittin_name_139cf7
        UNIQUE (name, material_id, module_id, diameter1_id, diameter2_id, diameter3_id, office_id);

        -- 還原欄位為 nullable
        ALTER TABLE pipe_fittings
        ALTER COLUMN description DROP NOT NULL;

        ALTER TABLE pipe_fittings
        ALTER COLUMN description DROP DEFAULT;

        -- 注意：自動生成的 description 值（#1, #2...）不會自動還原
    """
