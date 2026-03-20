"""
一次性同步 grant_locations 的 case_status、apply_year、case_number

問題：
- grant_locations.case_status / apply_year / case_number 為 grants 的去正規化副本
- 歷史上只有儲存 Step 2 時才觸發同步，grants.status 變更後未同步
- 導致 GIS 地圖顯示的案件狀態與年度可能為過時值

修正：
- new_aerc：grant_locations.source_id = grants.id::text
- legacy_farmdata：grant_locations.source_id → grant_versions.version → grants.id

後續：
- grants.status 異動時已由 crud/grants.py update_grant_status 呼叫
  sync_single_grant_metadata 進行增量同步，不再需要批次修復
"""
from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        -- 同步 new_aerc 案件
        UPDATE grant_locations
        SET case_status = g.status,
            apply_year  = g.year,
            case_number = g.case_number,
            updated_at  = NOW()
        FROM grants g
        WHERE grant_locations.source_system = 'new_aerc'
          AND grant_locations.source_id = g.id::text
          AND (grant_locations.case_status IS DISTINCT FROM g.status
               OR grant_locations.apply_year  IS DISTINCT FROM g.year
               OR grant_locations.case_number IS DISTINCT FROM g.case_number);

        -- 同步 legacy_farmdata 案件
        -- join 路徑：grant_locations.source_id → grant_versions.version → grants.id
        UPDATE grant_locations
        SET case_status = g.status,
            apply_year  = g.year,
            case_number = g.case_number,
            updated_at  = NOW()
        FROM grants g
        JOIN grant_versions gv ON gv.grant_id = g.id
        WHERE grant_locations.source_system = 'legacy_farmdata'
          AND grant_locations.source_id = gv.version::text
          AND (grant_locations.case_status IS DISTINCT FROM g.status
               OR grant_locations.apply_year  IS DISTINCT FROM g.year
               OR grant_locations.case_number IS DISTINCT FROM g.case_number);
    """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        -- 此 migration 為資料同步，無法還原（原始值已不存在）
        SELECT 1;
    """
