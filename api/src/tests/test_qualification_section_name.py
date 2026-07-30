"""036-qualification-section-name：地段名稱解析與資料格式錯誤判定的單元驗證。

測試粒度採直接呼叫 staticmethod：受測函數只讀取 land_section_name / updated_at /
id / meta_data 四個屬性，GrantLocations 可在無 Tortoise 初始化下於記憶體實例化，
不需資料庫、不需 mock。接線測試（_convert_to_case_item）選 new_aerc 來源搭配
include_office_boundaries=False，該路徑同樣全程不碰資料庫。

═══════════════════════════════════════════════════════════════════════════
⚠️ 讀這支測試之前必看：多數情境在現行資料下「不會發生」，這是刻意的
═══════════════════════════════════════════════════════════════════════════

以 2026-07-30 dev 全表（98,713 筆）實測，本檔案各情境的實際發生筆數：

    情境                          筆數      對應測試
    ─────────────────────────────────────────────────────────────
    單筆分組 + 有名稱             98,687    test_生產形狀_單筆分組且有名稱
    單筆分組 + 無名稱                 26    test_生產形狀_單筆分組且無名稱
    缺縣市＋鄉鎮                       1    test_既有缺縣市鄉鎮案件的訊息…
    ─────────────────────────────────────────────────────────────
    同組多筆（重複紀錄）               0    ← 9 項測試依賴此形狀
    名稱為空字串                       0    ← 1 項
    meta_data 為 NULL                  0    ← 1 項
    只缺縣市或只缺鄉鎮其一             0    ← 1 項
    三項全缺                           0    ← 1 項

也就是說 18 項測試裡有 13 項測的是目前不會發生的情境。**不要因此順手刪掉它們**，
理由分兩類：

【A 類：規格明文需求，且這裡是唯一驗證路徑——不可刪】
    「同組多筆」相關的 9 項測試守的是 FR-008／FR-009／FR-010。這三條需求的觸發
    條件之所以不可達，是因為 grant_locations 的唯一索引
    (source_system, source_id, land_section, land_number) 保證同一來源內不會重複，
    而查詢分組鍵不含 source_system——只有跨來源 source_id 碰撞才會觸發（見
    research.md 研究 2、CLAUDE.md TD-020）。
    正因為真實資料測不到，單元測試是它們僅有的驗證方式。若判定這些需求不值得
    保留，正確做法是**回頭刪掉 FR-008～010**（spec 決策 4 已評估過該替代方案），
    而不是留著需求卻拿掉驗證。

【B 類：組合完備性，無對應 FR——價值較低但成本亦低】
    meta_data 為 NULL、只缺單一欄位、三項全缺這三項。其中「只缺單一欄位」建議
    保留：county／town 是功能 035 才新增的寫入邏輯，新案件寫入時缺其一並非不可能。

═══════════════════════════════════════════════════════════════════════════
維護提醒：改動實作後請跑突變測試，別只看綠燈
═══════════════════════════════════════════════════════════════════════════

本檔案全部測試都經突變測試驗證具鑑別力（逐一破壞實作規則、確認測試抓得到）。
過程中抓出過兩個問題，都是「測試全綠但其實沒測到東西」：
  1. test_代表紀錄有名稱時取自身名稱 曾讓代表紀錄同時是排序第一名，拆掉「自身
     優先」規則後照樣通過——已改為把代表紀錄設為排序上最不利者
  2. 生產實際輸入形狀（單筆分組）原本無任何測試覆蓋，一個會讓生產 100% 案件
     失去名稱的改動完全不會被發現——已補上「生產形狀」兩項測試
"""
import asyncio
from datetime import datetime, timezone

from src.crud.qualification import QualificationCRUD
from src.database.geo_models import GrantLocations

# 擴充警告述詞前的固定訊息字面值。用途：鎖住 FR-007——既有僅缺縣市/鄉鎮的案件，
# 動態訊息產出的字串必須與此逐字相同。不得改寫此常數以遷就實作。
LEGACY_WARNING_MSG = "此案件缺少縣市／鄉鎮資料，資料格式可能有誤"

COMPLETE_META = {'county': '南投縣', 'town': '集集鎮'}

# 用獨立哨符區分「未指定 meta_data（預設給完整值）」與「明確指定 meta_data=None」，
# 不可用 None 當預設值——那樣就測不到 meta_data 為 None 這條路徑
_UNSET = object()


def _location(loc_id, section_name, updated_at=None, meta_data=_UNSET):
    """建立記憶體中的 GrantLocations（不寫入資料庫）。"""
    return GrantLocations(
        id=loc_id,
        source_system='legacy_farmdata',
        source_id=str(loc_id),
        land_section='0623',
        land_section_name=section_name,
        land_number='0878-0000',
        updated_at=updated_at or datetime(2026, 7, 1, tzinfo=timezone.utc),
        meta_data=dict(COMPLETE_META) if meta_data is _UNSET else meta_data,
    )


# === 名稱解析（FR-008、FR-009）===

def test_代表紀錄有名稱時取自身名稱():
    # 代表紀錄刻意設為排序上最不利者（id 最大且更新時間最舊）：
    # 若實作漏掉「自身優先」而直接走同組排序，會取到「其他段」。
    # 不可讓代表紀錄同時是排序第一名——那樣兩種實作都回傳同一個值，測試等於空轉。
    representative = _location(9, '福山段', updated_at=datetime(2026, 1, 1, tzinfo=timezone.utc))
    group = [representative, _location(1, '其他段', updated_at=datetime(2026, 7, 1, tzinfo=timezone.utc))]

    assert QualificationCRUD._resolve_section_name(representative, group) == '福山段'


def test_代表紀錄無名稱時從同組取得名稱且不被標記為錯誤資料():
    representative = _location(1, None)
    group = [representative, _location(2, '福山段')]

    resolved = QualificationCRUD._resolve_section_name(representative, group)

    assert resolved == '福山段'
    # 補救成功的案件不得被誤標為錯誤資料——錯誤判定必須吃「解析後」的值
    assert '地段名稱' not in QualificationCRUD._collect_missing_data_labels(representative, resolved)


def test_同組多個名稱時取更新時間較新者():
    representative = _location(1, None)
    older = _location(2, '舊名段', updated_at=datetime(2026, 1, 1, tzinfo=timezone.utc))
    newer = _location(3, '新名段', updated_at=datetime(2026, 7, 1, tzinfo=timezone.utc))

    assert QualificationCRUD._resolve_section_name(representative, [representative, older, newer]) == '新名段'


def test_更新時間相同時取識別碼較小者():
    same_time = datetime(2026, 7, 1, tzinfo=timezone.utc)
    representative = _location(1, None, updated_at=same_time)
    larger_id = _location(9, '大號段', updated_at=same_time)
    smaller_id = _location(5, '小號段', updated_at=same_time)

    assert QualificationCRUD._resolve_section_name(
        representative, [representative, larger_id, smaller_id]
    ) == '小號段'


def test_打亂輸入順序結果仍相同():
    """FR-009：解析結果必須可重現。查詢未加 ORDER BY，資料庫回傳順序不保證。"""
    same_time = datetime(2026, 7, 1, tzinfo=timezone.utc)
    representative = _location(1, None, updated_at=same_time)
    candidates = [_location(5, '小號段', updated_at=same_time),
                  _location(9, '大號段', updated_at=same_time),
                  _location(7, '中號段', updated_at=same_time)]

    results = {
        QualificationCRUD._resolve_section_name(representative, [representative] + list(order))
        for order in (candidates, candidates[::-1], [candidates[1], candidates[2], candidates[0]])
    }

    assert results == {'小號段'}


def test_同組皆無名稱時回傳None並標記為錯誤資料():
    representative = _location(1, None)
    group = [representative, _location(2, None), _location(3, '')]

    resolved = QualificationCRUD._resolve_section_name(representative, group)

    # 必須是 None 而非空字串：回傳型別需與 schema 的 Optional[str] 一致，
    # 否則 API 會回傳 "" 而非契約明訂的 null，且前端仍顯示「—」，異常不可見
    assert resolved is None
    assert '地段名稱' in QualificationCRUD._collect_missing_data_labels(representative, resolved)


def test_未提供同組紀錄時只看代表紀錄自身():
    assert QualificationCRUD._resolve_section_name(_location(1, '福山段')) == '福山段'
    assert QualificationCRUD._resolve_section_name(_location(1, None)) is None
    assert QualificationCRUD._resolve_section_name(_location(1, None), []) is None


def test_代表紀錄名稱為空字串時視同缺名稱():
    representative = _location(1, '')

    assert QualificationCRUD._resolve_section_name(representative, [representative, _location(2, '福山段')]) == '福山段'


# === 缺漏欄位判定與訊息組裝（FR-005、FR-006、FR-007）===

def test_欄位齊全時無警告():
    location = _location(1, '福山段')

    labels = QualificationCRUD._collect_missing_data_labels(location, '福山段')

    assert labels == []
    assert QualificationCRUD._build_data_format_warning(labels) is None


def test_僅缺地段名稱時訊息只指出地段名稱():
    location = _location(1, None)

    labels = QualificationCRUD._collect_missing_data_labels(location, None)

    assert labels == ['地段名稱']
    assert QualificationCRUD._build_data_format_warning(labels) == "此案件缺少地段名稱資料，資料格式可能有誤"


def test_既有缺縣市鄉鎮案件的訊息與擴充前逐字相同():
    """FR-007 迴歸鎖：擴充述詞不得改變既有案件看到的訊息。"""
    location = _location(1, '福山段', meta_data={})

    labels = QualificationCRUD._collect_missing_data_labels(location, '福山段')

    assert labels == ['縣市', '鄉鎮']
    assert QualificationCRUD._build_data_format_warning(labels) == LEGACY_WARNING_MSG


def test_meta_data為None時視同缺縣市與鄉鎮():
    """擴充前的述詞對 meta_data 為 None 亦回傳 True，判定條件必須等價（FR-007）。"""
    location = _location(1, '福山段', meta_data=None)

    assert QualificationCRUD._collect_missing_data_labels(location, '福山段') == ['縣市', '鄉鎮']


def test_僅缺單一欄位時訊息只列該欄位():
    only_town_missing = _location(1, '福山段', meta_data={'county': '南投縣'})
    only_county_missing = _location(2, '福山段', meta_data={'town': '集集鎮'})

    assert QualificationCRUD._collect_missing_data_labels(only_town_missing, '福山段') == ['鄉鎮']
    assert QualificationCRUD._collect_missing_data_labels(only_county_missing, '福山段') == ['縣市']


def test_同時缺多項時只產生一個警告並列出全部缺漏欄位():
    """FR-006：不得每個欄位各亮一個警告。"""
    location = _location(1, None, meta_data={})

    labels = QualificationCRUD._collect_missing_data_labels(location, None)
    warning = QualificationCRUD._build_data_format_warning(labels)

    assert labels == ['縣市', '鄉鎮', '地段名稱']
    assert warning == "此案件缺少縣市／鄉鎮／地段名稱資料，資料格式可能有誤"
    # 擋住「每個欄位各串一句訊息」的實作（突變測試 M12 證實此斷言有效，非空轉）
    assert warning.count('資料格式可能有誤') == 1


# === 接線驗證（_convert_to_case_item 內部的組裝順序）===

def _new_aerc_location(loc_id, section_name):
    """建立 new_aerc 來源的紀錄。

    選 new_aerc 而非 legacy_farmdata 是刻意的：legacy 分支會呼叫 _infer_legacy_case_type
    查詢 grant_versions，需要資料庫連線；new_aerc 分支只讀 meta_data，
    搭配 include_office_boundaries=False 即可全程不碰資料庫。
    """
    return GrantLocations(
        id=loc_id, source_system='new_aerc', source_id=str(loc_id),
        land_section='0300', land_section_name=section_name, land_number='0099',
        case_number='11514020120', case_status='completed', apply_year=115,
        applicant_name='測試申請人',
        updated_at=datetime(2026, 7, 1, tzinfo=timezone.utc),
        meta_data={'county': '臺中市', 'town': '東區', 'facility_area': '100'},
    )


def test_轉換時錯誤判定必須吃解析後的名稱而非代表紀錄原始名稱():
    """守住 _convert_to_case_item 內部的接線順序。

    若把 _collect_missing_data_labels 的第二個引數誤寫成 location.land_section_name
    （而非解析後的區域變數），同組補救成功的案件會被誤標為錯誤資料——不報錯、
    畫面上卻多出一個不該有的警告。此接線無法由前面直接呼叫 staticmethod 的測試涵蓋
    （突變測試 M13 證實：改壞接線時前面 14 項全數通過）。
    """
    representative = _new_aerc_location(1, None)
    group = [representative, _new_aerc_location(2, '尚武段')]

    item = asyncio.run(
        QualificationCRUD._convert_to_case_item(representative, False, group)
    )

    assert item.land_section_name == '尚武段'
    assert item.data_format_warning is None
    # 地段代碼必須原樣保留（FR-013）
    assert item.land_section == '0300'


def test_轉換時同組皆無名稱則標記錯誤且名稱為None():
    representative = _new_aerc_location(1, None)
    group = [representative, _new_aerc_location(2, None)]

    item = asyncio.run(
        QualificationCRUD._convert_to_case_item(representative, False, group)
    )

    assert item.land_section_name is None
    assert item.data_format_warning == "此案件缺少地段名稱資料，資料格式可能有誤"


# === 生產實際輸入形狀（單筆分組）===
#
# 這是 100% 的生產流量：實測全表 98,713 個分組**全部只有一筆紀錄**，因此
# _convert_to_case_item 收到的 locations_group 恆為 [representative]
# ——一個元素、且該元素就是代表紀錄本身。
#
# 上方所有測試的分組不是 0 筆（None／[]）就是 2~4 筆，沒有一個是這個形狀。
# 突變測試 M14 證實此缺口為真：插入「同組恰為一筆時直接回傳 None」會讓生產
# 環境每一筆案件都失去地段名稱，卻無任何測試失敗。以下兩項專測此形狀。

def test_生產形狀_單筆分組且有名稱():
    """對應現行資料 98,687 筆：名稱完整 → 顯示名稱、不亮警告。"""
    representative = _new_aerc_location(1, '尚武段')

    item = asyncio.run(
        QualificationCRUD._convert_to_case_item(representative, False, [representative])
    )

    assert item.land_section_name == '尚武段'
    assert item.data_format_warning is None


def test_生產形狀_單筆分組且無名稱():
    """對應現行資料 26 筆：名稱缺漏 → None + 亮「缺少地段名稱」警告。"""
    representative = _new_aerc_location(1, None)

    item = asyncio.run(
        QualificationCRUD._convert_to_case_item(representative, False, [representative])
    )

    assert item.land_section_name is None
    assert item.data_format_warning == "此案件缺少地段名稱資料，資料格式可能有誤"
