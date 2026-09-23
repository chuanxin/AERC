# 補助來源（fundingSourceId）單一資料來源
#
# 「顯示短名」是純呈現層知識，DB 沒有也不該有：offices.name 存的是全名（農業部農田
# 水利署 / 七星管理處 / 瑠公管理處），在案件列表欄位與 Excel 工作表名稱裡都太長；
# offices.short_name 存的是英文代碼（ia / iacsi / ialgo），不能給人看。因此這份對照
# 表就是它自己的 SSOT，不從 DB 派生。
#
# 但「誰是補助來源」（membership）的真相在 DB：offices.is_funding_source = true，
# 前端 step3.vue（UI 步驟 4）的下拉選單直接讀它。本檔的 key 集合是那份真相的副本，
# 會漂移——PUT /offices/{id} 可以改 is_funding_source，改完前端下拉就多一個選項、
# 使用者選得到、存得進 step4，而後端這份對照表不認得。因此有 verify_against_db()
# 在啟動時比對兩者，漂移就吼出來（見下方）。
#
# ⚠️ fundingSourceId = 0 同時是前端 step3.vue 的預設值。客戶行政作業預設即以農水署
# 預算撥款，因此 0 一律視為「農水署」而非「未選擇」，這是刻意的業務語意，不是待修正
# 的缺陷；管路補助金額明細表（routes/downloads.py）行為一致。

import logging

logger = logging.getLogger(__name__)

# 作業基金（墊付預算）：非真實 office 記錄，負整數永不與 offices.id auto-increment 衝突
FUNDING_SOURCE_ADVANCE = -1

# 農水署：對照表的 id 0，同時是前端 step3.vue 的預設值（見檔頭 ⚠️ 說明）
FUNDING_SOURCE_IA = 0

# fundingSourceId -> 顯示短名
FUNDING_SOURCE_NAMES = {
    FUNDING_SOURCE_IA: "農水署",
    16: "七星",
    17: "瑠公",
    FUNDING_SOURCE_ADVANCE: "作業基金",
}

# 對應真實 offices 記錄的 id（排除虛擬的作業基金），用於與 DB 比對
REAL_OFFICE_FUNDING_SOURCE_IDS = frozenset(FUNDING_SOURCE_NAMES) - {FUNDING_SOURCE_ADVANCE}

# 經費統計表（首頁「管理處經費統計表」）的來源子列名稱。
# 兩個具名桶直接由上方對照表派生，不另立字面值，避免與對照表漂移；
# 「其他」是統計表自己的聚合桶（七星／瑠公／案件內部來源不一致），
# 不是真實的補助來源，因此刻意不存在於 FUNDING_SOURCE_NAMES 裡。
FUNDING_SOURCE_NAME_IA = FUNDING_SOURCE_NAMES[FUNDING_SOURCE_IA]
FUNDING_SOURCE_NAME_ADVANCE = FUNDING_SOURCE_NAMES[FUNDING_SOURCE_ADVANCE]
FUNDING_SOURCE_NAME_OTHER = "其他"

# resolve_funding_source_id() 的回傳 sentinel：歷史案件內部設施橫跨多個不同來源，
# 無法判定單一來源。不是 fundingSourceId 的合法值，故用字串與 int 回傳值區分。
FUNDING_SOURCE_MIXED = "mixed"


def resolve_funding_source_id(steps4_data: dict, is_legacy: bool):
    """取得單一案件的原始 fundingSourceId 判定結果（三個消費端共用）

    ⚠️ 歷史案件不能讀案件最上層的 `steps['4'].fundingSourceId`：該欄位是歷史資料匯入
    腳本寫死的固定值 0（見 migrate_mssql_to_unified/migrate_legacy_complete.py 的
    _build_step4_data()），不反映真實來源；真實來源逐設施記錄在 facilities[] 裡，
    源自舊系統 MSSQL 的 Pay/PoolApply/EngApply.ApplyUnit 欄位。

    ⚠️ 呼叫端的 is_legacy 必須以 `grant.active_version.data_schema_version == 'legacy'`
    判斷，不可用 `grants.is_legacy` 欄位——實測全庫有 251 筆兩者不一致（其中 250 筆是
    當年度案件），用錯欄位會讓這批案件完全套用不到上述修正。

    本函式只負責取得原始值，刻意不做名稱對照、不代入預設值、不拋例外——三個消費端
    「拿到值之後怎麼辦」的容錯策略本就不同（案件列表顯示 `-`／明細表下載拋錯排除／
    經費統計表併入農水署或其他），由各呼叫端自行決定。

    Returns:
        int: 已判定出唯一的原始 fundingSourceId
        None: 無法判定（缺漏、非 int，或歷史案件無設施資料且最上層欄位也缺漏）
        FUNDING_SOURCE_MIXED: 僅歷史案件會出現，設施橫跨多個不同來源
    """
    facility_ids = _facility_funding_source_ids(steps4_data) if is_legacy else set()

    if len(facility_ids) > 1:
        return FUNDING_SOURCE_MIXED
    if facility_ids:
        return next(iter(facility_ids))

    # 新系統案件，或歷史案件的設施陣列為空／無任何有效值 → 回退讀案件最上層欄位
    case_level_id = steps4_data.get('fundingSourceId')
    if isinstance(case_level_id, int) and not isinstance(case_level_id, bool):
        return case_level_id
    return None


def _facility_funding_source_ids(steps4_data: dict) -> set:
    """取出歷史案件逐設施的有效 fundingSourceId 集合（非 int 或 bool 的值一律忽略）"""
    facilities = steps4_data.get('facilities')
    if not isinstance(facilities, list):
        return set()

    return {
        fid
        for facility in facilities
        if isinstance(facility, dict)
        for fid in (facility.get('fundingSourceId'),)
        if isinstance(fid, int) and not isinstance(fid, bool)
    }


async def verify_against_db() -> bool:
    """
    啟動時比對本檔的 id 集合與 DB offices.is_funding_source = true 的 id 集合。

    不一致不中斷啟動（補助來源顯示不到不足以讓整個 API 停擺），但必須在日誌留下
    可直接行動的訊息：明確列出是哪些 id 多了或少了，不要只說「不一致」。

    Returns:
        bool: True 表示一致
    """
    from src.database.models import Offices

    try:
        db_ids = frozenset(
            await Offices.filter(is_funding_source=True).values_list("id", flat=True)
        )
    except Exception as e:
        # 查不到就誠實說查不到，不要假裝檢查過了
        logger.error("補助來源一致性檢查無法執行（查詢 offices 失敗）: %s", e)
        return False

    if db_ids == REAL_OFFICE_FUNDING_SOURCE_IDS:
        logger.info("補助來源一致性檢查通過: %s", sorted(REAL_OFFICE_FUNDING_SOURCE_IDS))
        return True

    missing = sorted(db_ids - REAL_OFFICE_FUNDING_SOURCE_IDS)   # DB 有、對照表沒有
    extra = sorted(REAL_OFFICE_FUNDING_SOURCE_IDS - db_ids)     # 對照表有、DB 沒有
    logger.error(
        "補助來源與 DB 不一致：DB offices.is_funding_source=%s，config/funding_sources.py=%s。"
        "對照表缺少 id %s（前端下拉選得到但案件列表會顯示 '-'、管路補助金額明細表會 skip 該案件）；"
        "對照表多出 id %s（已不是補助來源但仍會被顯示）。請更新 FUNDING_SOURCE_NAMES。",
        sorted(db_ids), sorted(REAL_OFFICE_FUNDING_SOURCE_IDS), missing, extra,
    )
    return False
