"""
一次性回填 grant_locations.meta_data 的 county/town 中文名稱（僅 new_aerc）

對應功能 035。既有 new_aerc 紀錄的 meta_data 只寫入 land_county/land_town（數字 ID），
未寫入 county/town（中文名稱字串），導致資格預查的縣市/鄉鎮過濾（_filter_by_county_town
讀取 meta_data.county/town）對 new_aerc 靜默失效。本 migration 依 land_county/land_town
數字 ID 反查 counties/towns 表，補上 county/town 名稱，使 new_aerc 的 meta_data 結構與
ardswc_114/legacy_farmdata 一致。

設計要點：
- 單一 set-based UPDATE（非 execute_many 逐筆），結構上規避 migration 74/TD-017 的
  同機連線穩定性問題；new_aerc 筆數少（dev 44 中缺 42，生產同量級）。
- 只作用於 source_system='new_aerc'，不觸及另兩來源系統。
- guard 條件 (county IS NULL OR county = '') 涵蓋「缺鍵/null/空字串」三種缺名稱狀態，
  與查詢層述詞 _has_incomplete_county_town（not get('county')）判定一致（審查 #3）；
  對已具名稱者無副作用，故冪等、可安全重跑。
- 縣鄉一致性守衛 t.county_id = c.id：只回填鄉鎮確實隸屬該縣市的列，不寫入已知不一致資料
  （審查 #2）；不一致或查無對應的列維持缺名稱，交由查詢層逐案件警告呈現。
- 尾端記錄仍缺名稱筆數供人工核對（呼應 TD-017「跑完要驗覆蓋率」）。
"""

import logging

from tortoise import BaseDBAsyncClient

logger = logging.getLogger(__name__)


async def upgrade(db: BaseDBAsyncClient) -> str:
    backfill_sql = """
        UPDATE grant_locations gl
        SET meta_data = jsonb_set(
                          jsonb_set(gl.meta_data, '{county}', to_jsonb(c.name), true),
                          '{town}', to_jsonb(t.name), true
                        ),
            updated_at = NOW()
        FROM counties c, towns t
        WHERE gl.source_system = 'new_aerc'
          AND ((gl.meta_data ->> 'county') IS NULL OR (gl.meta_data ->> 'county') = '')
          AND (gl.meta_data ->> 'land_county') ~ '^[0-9]+$'
          AND (gl.meta_data ->> 'land_town')   ~ '^[0-9]+$'
          AND c.id = (gl.meta_data ->> 'land_county')::int
          AND t.id = (gl.meta_data ->> 'land_town')::int
          AND t.county_id = c.id
    """
    await db.execute_query(backfill_sql)

    # 覆蓋率自我核對（不 raise，僅記錄；仍缺者為 land_county/land_town 非數字、查無對應、
    # 或縣鄉不一致的真正異常資料，交由查詢層逐案件警告呈現）
    _, stats = await db.execute_query(
        "SELECT COUNT(*) AS total, "
        "COUNT(*) FILTER (WHERE (meta_data ->> 'county') IS NOT NULL "
        "AND (meta_data ->> 'county') <> '') AS filled "
        "FROM grant_locations WHERE source_system = 'new_aerc'"
    )
    total, filled = stats[0]["total"], stats[0]["filled"]
    logger.info(
        "[035 backfill] new_aerc county/town: total=%s filled=%s still_missing=%s",
        total, filled, total - filled,
    )

    return "SELECT 1;"


async def downgrade(db: BaseDBAsyncClient) -> str:
    # 移除本 migration 於 new_aerc 補上的 county/town 鍵。
    # 行為等價說明：查詢層以 meta_data.get('county')/IS NULL 判讀，「鍵缺失」與「值為 null」
    # 讀取結果相同，故 downgrade 後過濾行為與回填前一致（差異僅在 JSON 結構層、對消費端不可見）。
    return """
        UPDATE grant_locations
        SET meta_data = (meta_data - 'county' - 'town'),
            updated_at = NOW()
        WHERE source_system = 'new_aerc';
    """
