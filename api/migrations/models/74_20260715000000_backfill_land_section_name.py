"""
一次性回填 grant_locations.land_section_name（地段中文名稱）

對應功能 034，針對既有紀錄依 source_system 分三個來源獨立回填：
- new_aerc：實測約 38/42 筆（直接對 grant_versions.all_steps_data 的 JSONB 陣列展開比對，
  不需要隨附資料檔；未命中的 4 筆分別是孤兒紀錄與版本資料不同步，屬已歸因的既有資料品質問題）
- legacy_farmdata：實測約 92,106/92,124 筆（讀取隨附 CSV，依 section_id 唯一鍵對照）
- ardswc_114：實測約 6,540/6,544 筆（讀取隨附 CSV，依段代碼/地號/縣市三鍵對照，
  CSV 產生階段已去重並排除無法歸因的衝突資料）

三個區塊的 UPDATE 皆含 land_section_name IS NULL 冪等防護，重複執行 aerich upgrade
不會覆蓋已回填的值，可安全重跑。

此 migration 為資料回填，無法還原（回填前的原始 NULL 狀態已不可逆推，且無法區分哪些 NULL
是本次回填遺漏、哪些是回填前就存在的既有狀態），downgrade() 為 no-op。

效能備註（2026-07-16 上線前於 UAT 驗證機發現並修正）：
legacy_farmdata 區塊的 16,391 筆 UPDATE 逐筆比對 meta_data->>'section_id'，
grant_locations 對這個 JSONB 表達式完全沒有索引，實測單筆需時約 135ms（Seq Scan
全表 ~9.8 萬列），16,391 筆合計會超過 30 分鐘。因此在 legacy_farmdata 區塊執行前，
先建立一個限定 source_system = 'legacy_farmdata' 的 partial expression index，
把這批 UPDATE 從全表掃描降為索引查找。這個索引只是為了加速這支一次性 migration，
回填完成後即可保留或捨棄（保留也無害，未來若有相同查詢型態一併受惠）。
"""
from pathlib import Path
import csv
import logging

from tortoise import BaseDBAsyncClient

logger = logging.getLogger(__name__)


async def upgrade(db: BaseDBAsyncClient) -> str:
    # 區塊一：new_aerc（直接 JOIN 現有表 + JSONB 陣列展開，不需隨附資料檔）
    new_aerc_sql = """
WITH land_elems AS (
    SELECT g.id AS grant_id,
           elem->>'landSec' AS land_sec,
           elem->>'landNumber' AS land_number,
           elem->>'landSecName' AS land_sec_name
    FROM grants g
    JOIN grant_versions gv ON gv.id = g.active_version_id
    CROSS JOIN LATERAL jsonb_array_elements(gv.all_steps_data->'steps'->'2'->'lands') AS elem
),
safe_matches AS (
    SELECT grant_id, land_sec, land_number, MIN(land_sec_name) AS land_sec_name
    FROM land_elems
    GROUP BY grant_id, land_sec, land_number
    HAVING COUNT(DISTINCT land_sec_name) = 1
)
UPDATE grant_locations gl
SET land_section_name = sm.land_sec_name
FROM safe_matches sm
WHERE gl.source_system = 'new_aerc'
  AND gl.source_id = sm.grant_id::text
  AND gl.land_section = sm.land_sec
  AND gl.land_number = sm.land_number
  AND gl.land_section_name IS NULL;
"""
    await db.execute_query(new_aerc_sql)
    _, stats = await db.execute_query(
        "SELECT COUNT(*) AS total, COUNT(land_section_name) AS filled "
        "FROM grant_locations WHERE source_system = 'new_aerc'"
    )
    total, filled = stats[0]["total"], stats[0]["filled"]
    logger.info("[034 backfill] new_aerc: total=%s filled=%s missing=%s", total, filled, total - filled)

    # 隨附資料檔目錄（與本檔案同層）
    data_dir = Path(__file__).parent / "74_20260715000000_backfill_land_section_name_data"

    # 效能優化：legacy_farmdata 的 16,391 筆 UPDATE 逐筆查 meta_data->>'section_id'，
    # 沒有這個索引會是全表 Seq Scan（實測單筆 ~135ms，合計超過 30 分鐘）。
    # IF NOT EXISTS 避免與先前手動測試建立的同名索引衝突；ANALYZE 讓 query planner
    # 立即取得新索引的統計資訊，不必等下一次 autovacuum。
    await db.execute_query(
        "CREATE INDEX IF NOT EXISTS idx_grant_locations_legacy_section_id "
        "ON grant_locations ((meta_data->>'section_id')) "
        "WHERE source_system = 'legacy_farmdata'"
    )
    await db.execute_query("ANALYZE grant_locations")

    # 區塊二：legacy_farmdata（section_id 唯一鍵比對）
    legacy_values = []
    with open(data_dir / "legacy_section_names.csv", "r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            legacy_values.append((row["land_section_name"], row["section_id"]))
    if legacy_values:
        await db.execute_many(
            "UPDATE grant_locations SET land_section_name = $1 "
            "WHERE source_system = 'legacy_farmdata' AND meta_data->>'section_id' = $2 "
            "AND land_section_name IS NULL",
            legacy_values,
        )
    _, stats = await db.execute_query(
        "SELECT COUNT(*) AS total, COUNT(land_section_name) AS filled "
        "FROM grant_locations WHERE source_system = 'legacy_farmdata'"
    )
    total, filled = stats[0]["total"], stats[0]["filled"]
    logger.info("[034 backfill] legacy_farmdata: total=%s filled=%s missing=%s", total, filled, total - filled)

    # 區塊三：ardswc_114（段代碼 + 地號 + 正規化縣市三鍵比對）
    ardswc_values = []
    with open(data_dir / "ardswc_reference.csv", "r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            ardswc_values.append(
                (row["land_section_name"], row["section_code"], row["land_number"], row["county_norm"])
            )
    if ardswc_values:
        await db.execute_many(
            "UPDATE grant_locations SET land_section_name = $1 "
            "WHERE source_system = 'ardswc_114' AND land_section = $2 "
            "AND meta_data->>'original_land_number' = $3 "
            "AND translate(meta_data->>'county','台','臺') = translate($4,'台','臺') "
            "AND land_section_name IS NULL",
            ardswc_values,
        )
    _, stats = await db.execute_query(
        "SELECT COUNT(*) AS total, COUNT(land_section_name) AS filled "
        "FROM grant_locations WHERE source_system = 'ardswc_114'"
    )
    total, filled = stats[0]["total"], stats[0]["filled"]
    logger.info("[034 backfill] ardswc_114: total=%s filled=%s missing=%s", total, filled, total - filled)

    return "SELECT 1;"


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        -- 此 migration 為資料回填，無法還原（原始 NULL 狀態已不可逆推）
        SELECT 1;
    """
