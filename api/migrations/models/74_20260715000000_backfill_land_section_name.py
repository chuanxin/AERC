"""
一次性回填 grant_locations.land_section_name（地段中文名稱）

對應功能 034，針對既有紀錄依 source_system 分三個來源獨立回填：
- new_aerc：實測約 38/42 筆（直接對 grant_versions.all_steps_data 的 JSONB 陣列展開比對，
  不需要隨附資料檔；未命中的 4 筆分別是孤兒紀錄與版本資料不同步，屬已歸因的既有資料品質問題）
- legacy_farmdata：實測約 92,106/92,124 筆（讀取隨附 CSV，依 section_id 唯一鍵對照）
- ardswc_114：實測約 6,540/6,544 筆（讀取隨附 CSV，依段代碼/地號/縣市/鄉鎮四鍵對照，
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

覆蓋率自我修復（2026-07-17 UAT 演練發現並修正）：UAT 驗證時因第一次執行耗時過久被手動
中斷、加入索引優化後重跑，事後覆蓋率檢查發現 legacy_farmdata 有 102 筆仍是 NULL，其中
84 筆的比對鍵在隨附資料檔中其實有對應資料——推測與第一次中斷殘留的暫態影響有關，但無法
在事後完整鑑識證實根因。為了讓正式環境即使遇到任何未預見的類似暫態問題，也能在單次
aerich upgrade 執行內收斂到完整覆蓋率、不需要人工介入或後續補丁 migration，legacy_farmdata
與 ardswc_114 兩個 execute_many 區塊之後都加了一段「查詢仍為 NULL 但比對鍵有對應資料的
紀錄，針對這些再補一次」的自我修復重試。正常情況下這個檢查應回傳空集合，幾乎零成本；
只有在異常情況下才會補救對應的少量紀錄，不會重跑全部筆數。

ardswc_114 比對鍵加入鄉鎮（2026-07-17 修正）：原本段代碼/地號/縣市三鍵比對存在結構性風險——
段代碼（NLSC sectcode）只保證同一鄉鎮內唯一，不保證同縣市跨鄉鎮也唯一，理論上可能發生同縣市
不同鄉鎮剛好段代碼與地號都相同、比對到錯誤資料的情況（與資格預查 _filter_by_county_town 已知
會重現的跨鄉鎮誤帶案件是同一種根因）。已用 dev 環境 temp_rwb_grants 實測驗證目前資料無此情況
（三鍵與四鍵比對覆蓋率同為 6,540/6,544），改為四鍵純粹是為資料量更大的正式環境預先補上結構性
防護，不影響既有結果；ardswc_reference.csv 已同步改為五欄（新增 town）。

地號雙引號雜訊清理（2026-07-17 補充修正）：UAT 同步水保署資料後實測發現，dev 環境
temp_rwb_grants 有 1 筆（段代碼0244/地號0037-0282/南投縣/國姓鄉）地號欄位帶著開頭
多餘的雙引號字元（很可能是 temp_rwb_grants 當初匯入時的殘留瑕疵），這個瑕疵同時存在於
dev 自己的 grant_locations 與 CSV 產生結果，兩邊剛好都髒，dev 環境測試時「意外」比對
成功；但 UAT 的 grant_locations 這筆是乾淨值，導致 CSV 的髒值配不上乾淨值而漏配。
比照現有「台/臺」正規化的做法，在比對時（不是只清理 CSV 內容本身）用
trim(both '"' from meta_data->>'original_land_number') 兩側都容忍這種雜訊，
不論目標環境的資料是否帶有這個瑕疵都能正確比對，已用 dev 資料重跑驗證覆蓋率不變
（6,540/6,544，且原本因此瑕疵漏比對的那 1 筆這次正確填入）。
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
    # 2026-07-17 改寫：原本用 execute_many() 逐筆送出 16,391 次個別網路往返，UAT 上實測
    # 會觸發 ConnectionResetError（WinError 10054）——已用最小可重現案例證實是這台環境
    # 對「大量連續網路往返」的連線穩定性問題，跟 SQL 邏輯、索引、資料量都無關。改用
    # PostgreSQL 的 unnest() 陣列展開語法，把整批資料包成陣列參數一次性送出，將 16,391
    # 次往返降為 1 次，從根本上規避這個問題（而不是仰賴操作者臨場判斷要不要中斷改手動
    # 執行）。已用 dev 資料驗證覆蓋率與原本逐筆版本完全一致。
    legacy_names: list[str] = []
    legacy_section_ids: list[str] = []
    with open(data_dir / "legacy_section_names.csv", "r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            legacy_names.append(row["land_section_name"])
            legacy_section_ids.append(row["section_id"])
    if legacy_names:
        await db.execute_query(
            "UPDATE grant_locations gl SET land_section_name = v.name "
            "FROM (SELECT unnest($1::text[]) AS name, unnest($2::text[]) AS section_id) v "
            "WHERE gl.source_system = 'legacy_farmdata' "
            "AND gl.meta_data->>'section_id' = v.section_id "
            "AND gl.land_section_name IS NULL",
            [legacy_names, legacy_section_ids],
        )

    # 覆蓋率自我修復：正常情況下應回傳空集合，只有異常情況才會補救到對應筆數
    # （改寫為單一往返後，先前 execute_many 逐筆執行才會出現的暫態遺漏問題理論上不會
    # 再重現，但保留這道防線作為防禦性測底，成本極低）
    _, legacy_still_null = await db.execute_query(
        "SELECT DISTINCT meta_data->>'section_id' AS section_id FROM grant_locations "
        "WHERE source_system = 'legacy_farmdata' AND land_section_name IS NULL "
        "AND meta_data->>'section_id' IS NOT NULL"
    )
    legacy_still_null_ids = {row["section_id"] for row in legacy_still_null}
    if legacy_still_null_ids:
        retry_pairs = [
            (name, sid) for name, sid in zip(legacy_names, legacy_section_ids)
            if sid in legacy_still_null_ids
        ]
        if retry_pairs:
            logger.warning(
                "[034 backfill] legacy_farmdata: 偵測到 %s 個 section_id 於首輪執行後仍為 NULL，執行補救重試",
                len(retry_pairs),
            )
            retry_names, retry_section_ids = zip(*retry_pairs)
            await db.execute_query(
                "UPDATE grant_locations gl SET land_section_name = v.name "
                "FROM (SELECT unnest($1::text[]) AS name, unnest($2::text[]) AS section_id) v "
                "WHERE gl.source_system = 'legacy_farmdata' "
                "AND gl.meta_data->>'section_id' = v.section_id "
                "AND gl.land_section_name IS NULL",
                [list(retry_names), list(retry_section_ids)],
            )

    _, stats = await db.execute_query(
        "SELECT COUNT(*) AS total, COUNT(land_section_name) AS filled "
        "FROM grant_locations WHERE source_system = 'legacy_farmdata'"
    )
    total, filled = stats[0]["total"], stats[0]["filled"]
    logger.info("[034 backfill] legacy_farmdata: total=%s filled=%s missing=%s", total, filled, total - filled)

    # 區塊三：ardswc_114（段代碼 + 地號 + 正規化縣市 + 鄉鎮四鍵比對）
    # 鄉鎮納入比對鍵的理由：段代碼（NLSC sectcode）只保證同一鄉鎮內唯一，不保證同縣市跨鄉鎮
    # 也唯一，三鍵比對存在理論上的跨鄉鎮撞鍵風險（與資格預查 _filter_by_county_town 那個已知
    # bug 同一種根因）。已用 dev 資料實測驗證：加入鄉鎮後覆蓋率與三鍵版本完全一致（6,540/6,544
    # 不變），純粹是為資料量更大的正式環境加一層結構性防護，不影響既有結果。
    # 2026-07-17 改寫：同 legacy_farmdata，原本 execute_many 逐筆送出 ~6,540 次往返改為
    # unnest() 陣列展開，一次性送出五欄陣列參數，降為 1 次網路往返。
    ardswc_names: list[str] = []
    ardswc_section_codes: list[str] = []
    ardswc_land_numbers: list[str] = []
    ardswc_county_norms: list[str] = []
    ardswc_towns: list[str] = []
    with open(data_dir / "ardswc_reference.csv", "r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            ardswc_names.append(row["land_section_name"])
            ardswc_section_codes.append(row["section_code"])
            ardswc_land_numbers.append(row["land_number"])
            ardswc_county_norms.append(row["county_norm"])
            ardswc_towns.append(row["town"])
    if ardswc_names:
        await db.execute_query(
            "UPDATE grant_locations gl SET land_section_name = v.name "
            "FROM (SELECT unnest($1::text[]) AS name, unnest($2::text[]) AS section_code, "
            "unnest($3::text[]) AS land_number, unnest($4::text[]) AS county_norm, "
            "unnest($5::text[]) AS town) v "
            "WHERE gl.source_system = 'ardswc_114' "
            "AND gl.land_section = v.section_code "
            "AND trim(both '\"' from gl.meta_data->>'original_land_number') = v.land_number "
            "AND translate(gl.meta_data->>'county','台','臺') = v.county_norm "
            "AND gl.meta_data->>'town' = v.town "
            "AND gl.land_section_name IS NULL",
            [ardswc_names, ardswc_section_codes, ardswc_land_numbers, ardswc_county_norms, ardswc_towns],
        )

    # 覆蓋率自我修復：比對鍵是四欄組合（段代碼、地號、正規化縣市、鄉鎮），邏輯同 legacy_farmdata
    _, ardswc_still_null = await db.execute_query(
        "SELECT DISTINCT land_section, trim(both '\"' from meta_data->>'original_land_number') AS land_number, "
        "translate(meta_data->>'county', '台', '臺') AS county_norm, meta_data->>'town' AS town "
        "FROM grant_locations WHERE source_system = 'ardswc_114' AND land_section_name IS NULL "
        "AND land_section IS NOT NULL AND meta_data->>'original_land_number' IS NOT NULL "
        "AND meta_data->>'town' IS NOT NULL"
    )
    ardswc_still_null_keys = {
        (row["land_section"], row["land_number"], row["county_norm"], row["town"]) for row in ardswc_still_null
    }
    if ardswc_still_null_keys:
        retry_rows = [
            row for row in zip(ardswc_names, ardswc_section_codes, ardswc_land_numbers,
                                ardswc_county_norms, ardswc_towns)
            if (row[1], row[2], row[3], row[4]) in ardswc_still_null_keys
        ]
        if retry_rows:
            logger.warning(
                "[034 backfill] ardswc_114: 偵測到 %s 個比對鍵於首輪執行後仍為 NULL，執行補救重試",
                len(retry_rows),
            )
            r_names, r_codes, r_numbers, r_counties, r_towns = zip(*retry_rows)
            await db.execute_query(
                "UPDATE grant_locations gl SET land_section_name = v.name "
                "FROM (SELECT unnest($1::text[]) AS name, unnest($2::text[]) AS section_code, "
                "unnest($3::text[]) AS land_number, unnest($4::text[]) AS county_norm, "
                "unnest($5::text[]) AS town) v "
                "WHERE gl.source_system = 'ardswc_114' "
                "AND gl.land_section = v.section_code "
                "AND trim(both '\"' from gl.meta_data->>'original_land_number') = v.land_number "
                "AND translate(gl.meta_data->>'county','台','臺') = v.county_norm "
                "AND gl.meta_data->>'town' = v.town "
                "AND gl.land_section_name IS NULL",
                [list(r_names), list(r_codes), list(r_numbers), list(r_counties), list(r_towns)],
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
