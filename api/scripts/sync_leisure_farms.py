#!/usr/bin/env python3
r"""
休閒農場資料同步腳本
從農業部開放資料 API 同步休閒農場資料到本地資料庫

資料來源：農業部開放資料平台
API URL: https://data.moa.gov.tw/Service/OpenData/ODwsv/ODwsvQualityFarm.aspx?&UnitId=376

用法:
    # 開發環境
    cd /Users/cxin/dev/AERC
    python api/scripts/sync_leisure_farms.py [--dry-run] [--verbose]

    # 生產環境
    cd C:\AERC\AERC-Deploy
    runtime\.venv\Scripts\python.exe app\api\scripts\sync_leisure_farms.py [--dry-run]

    # Docker 環境
    docker exec -it aerc-api python scripts/sync_leisure_farms.py

參數:
    --dry-run: 測試模式，僅顯示要同步的資料，不實際寫入資料庫
    --verbose: 顯示詳細的處理過程
    --env-file PATH: 指定 .env 文件路徑（可選，預設自動偵測）

環境變數:
    DATABASE_URL: PostgreSQL 連線字串
"""

import asyncio
import argparse
import httpx
import logging
from datetime import datetime, date
from decimal import Decimal
from typing import List, Optional, Dict, Tuple
import sys
import os
from pathlib import Path

# 設定 Python 路徑以便 import 專案模組
script_dir = Path(__file__).resolve().parent
api_dir = script_dir.parent
sys.path.insert(0, str(api_dir))

# NOTE: 不要在這裡 import 需要環境變數的模組
# Tortoise 需要在載入 .env 後才能 import

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# MOA API URL
MOA_API_URL = "https://data.moa.gov.tw/Service/OpenData/ODwsv/ODwsvQualityFarm.aspx"
MOA_UNIT_ID = "376"


def load_env_file(env_path: Path = None) -> bool:
    """
    載入 .env 文件中的環境變數

    Args:
        env_path: .env 文件路徑，若未指定則自動搜尋

    Note:
        在 Docker 環境中，環境變數已透過 docker-compose.yml 載入，
        此函數會偵測並跳過載入。
    """
    # 檢查是否已有必要的環境變數（Docker 環境）
    required_vars = ["DATABASE_URL"]

    existing_vars = [var for var in required_vars if os.environ.get(var)]
    if len(existing_vars) == len(required_vars):
        print("[INFO] 環境變數已存在（Docker 環境），跳過載入 .env")
        return True

    if env_path is None:
        # 自動偵測 .env 位置
        # 1. 檢查 api 目錄的父目錄（開發環境: AERC/.env）
        dev_env = api_dir.parent / ".env"
        # 2. 檢查生產環境路徑（C:\AERC\AERC-Deploy\.env）
        if "AERC-Deploy" in str(api_dir):
            # 生產環境: app/api -> AERC-Deploy
            prod_env = api_dir.parent.parent / ".env"
        else:
            prod_env = None

        # 優先使用生產環境
        if prod_env and prod_env.exists():
            env_path = prod_env
        elif dev_env.exists():
            env_path = dev_env
        else:
            print(f"[WARN] 找不到 .env 文件")
            print(f"  嘗試的路徑:")
            print(f"    - {dev_env}")
            if prod_env:
                print(f"    - {prod_env}")
            print(f"  請確保環境變數已設定或使用 --env-file 參數指定路徑")
            return False

    if not env_path.exists():
        print(f"[ERROR] .env 文件不存在: {env_path}")
        return False

    print(f"[INFO] 載入環境變數: {env_path}")

    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                # 跳過空行和註解
                if not line or line.startswith('#'):
                    continue

                # 解析 KEY=VALUE
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()

                    # 移除引號
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]

                    # 只設定尚未存在的環境變數（不覆蓋已設定的）
                    if key not in os.environ:
                        os.environ[key] = value

        print(f"[OK] 環境變數載入成功")

        # 驗證必要的環境變數
        missing_vars = [var for var in required_vars if not os.environ.get(var)]
        if missing_vars:
            print(f"[WARN] 缺少以下環境變數: {', '.join(missing_vars)}")
            return False

        return True

    except Exception as e:
        print(f"[ERROR] 載入 .env 文件失敗: {e}")
        return False


async def fetch_moa_data() -> List[dict]:
    """從 MOA API 取得休閒農場資料"""
    try:
        # 注意：MOA 政府網站可能有 SSL 憑證問題，暫時跳過驗證
        async with httpx.AsyncClient(timeout=60.0, verify=False) as client:
            response = await client.get(
                MOA_API_URL,
                params={"UnitId": MOA_UNIT_ID}
            )
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Fetched {len(data)} records from MOA API")
            return data
            
    except httpx.HTTPError as e:
        logger.error(f"HTTP error fetching MOA data: {e}")
        raise
    except Exception as e:
        logger.error(f"Error fetching MOA data: {e}")
        raise


def parse_date(date_str: Optional[str]) -> Optional[date]:
    """
    解析日期字串，回傳 date 物件或 None

    支援格式:
    - 民國年: 104/7/24 -> 2015-07-24
    - 西元年: 2015/07/24, 2015-07-24, 2015.07.24
    """
    if not date_str or date_str.strip() == "":
        return None

    try:
        date_str = date_str.strip()

        # 先嘗試解析民國年格式 (如 "104/7/24" 或 "109/7/23")
        if '/' in date_str:
            parts = date_str.split('/')
            if len(parts) == 3:
                year = int(parts[0])
                # 如果年份小於 1900，假設是民國年
                if year < 1900:
                    year = year + 1911
                month = int(parts[1])
                day = int(parts[2])
                return datetime(year, month, day).date()

        # 嘗試標準日期格式
        for fmt in ["%Y/%m/%d", "%Y-%m-%d", "%Y.%m.%d"]:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.date()
            except ValueError:
                continue

        logger.warning(f"Unable to parse date: {date_str}")
        return None

    except Exception as e:
        logger.warning(f"Error parsing date '{date_str}': {e}")
        return None


def clean_string(value: Optional[str]) -> Optional[str]:
    """清理字串，移除多餘空白"""
    if value is None:
        return None
    value = str(value).strip()
    return value if value else None


async def sync_leisure_farms(data: List[dict], dry_run: bool = False, verbose: bool = False) -> Tuple[dict, List[Dict]]:
    """
    同步休閒農場資料到資料庫
    使用 UPSERT 邏輯：根據農場名稱+縣市+鄉鎮進行比對

    Args:
        data: MOA API 回傳的休閒農場資料
        dry_run: 測試模式，不實際寫入資料庫
        verbose: 顯示詳細的處理過程

    Returns:
        (stats, failed_records): 統計資訊和失敗記錄列表
    """
    from tortoise import connections

    conn = connections.get("default")

    stats = {
        "total_fetched": len(data),
        "inserted": 0,
        "updated": 0,
        "errors": 0,
        "skipped": 0
    }

    failed_records: List[Dict] = []

    for idx, record in enumerate(data, 1):
        try:
            # 解析必要欄位
            farm_name = clean_string(record.get("FarmNm_CH"))
            county = clean_string(record.get("County"))
            township = clean_string(record.get("Township"))
            longitude_str = clean_string(record.get("Longitude"))
            latitude_str = clean_string(record.get("Latitude"))

            if verbose:
                logger.info(f"[{idx}/{len(data)}] Processing: {farm_name} ({county} {township})")

            # 檢查必要欄位
            missing_fields = []
            if not farm_name:
                missing_fields.append("FarmNm_CH")
            if not county:
                missing_fields.append("County")
            if not township:
                missing_fields.append("Township")
            if not longitude_str:
                missing_fields.append("Longitude")
            if not latitude_str:
                missing_fields.append("Latitude")

            if missing_fields:
                reason = f"缺少必要欄位: {', '.join(missing_fields)}"
                logger.warning(f"[{idx}] SKIPPED - {farm_name or '未知'}: {reason}")
                failed_records.append({
                    "index": idx,
                    "farm_name": farm_name or "未知",
                    "county": county,
                    "township": township,
                    "reason": reason,
                    "type": "missing_fields",
                    "raw_data": record
                })
                stats["skipped"] += 1
                continue

            # 解析座標
            try:
                longitude = Decimal(longitude_str)
                latitude = Decimal(latitude_str)

                # 驗證座標範圍（台灣座標大約在 119-122 經度，21-26 緯度）
                if not (119 <= longitude <= 122):
                    raise ValueError(f"經度超出台灣範圍: {longitude}")
                if not (21 <= latitude <= 26):
                    raise ValueError(f"緯度超出台灣範圍: {latitude}")

            except Exception as e:
                reason = f"座標格式錯誤: {e}"
                logger.warning(f"[{idx}] SKIPPED - {farm_name}: {reason}")
                failed_records.append({
                    "index": idx,
                    "farm_name": farm_name,
                    "county": county,
                    "township": township,
                    "reason": reason,
                    "type": "invalid_coordinates",
                    "longitude": longitude_str,
                    "latitude": latitude_str
                })
                stats["skipped"] += 1
                continue

            # 解析其他欄位
            address = clean_string(record.get("Address_CH"))
            phone = clean_string(record.get("TEL"))
            web_url = clean_string(record.get("WebURL"))
            certify_start = parse_date(record.get("CertifySDate"))
            certify_end = parse_date(record.get("CertifyEDate"))
            identify_item = clean_string(record.get("IdentifyItem"))
            photo_url = clean_string(record.get("Photo"))

            # 驗證欄位長度（避免資料庫截斷錯誤）
            if farm_name and len(farm_name) > 255:
                reason = f"農場名稱過長 ({len(farm_name)} 字元)"
                logger.warning(f"[{idx}] SKIPPED - {farm_name[:50]}...: {reason}")
                failed_records.append({
                    "index": idx,
                    "farm_name": farm_name,
                    "county": county,
                    "township": township,
                    "reason": reason,
                    "type": "field_too_long"
                })
                stats["skipped"] += 1
                continue

            if dry_run:
                if verbose:
                    logger.info(f"[DRY-RUN] Would upsert: {farm_name} ({county} {township})")
                stats["inserted"] += 1  # 假設會插入（實際需要查詢才知道）
                continue

            # 使用 UPSERT：根據 farm_name + county + township 唯一識別
            # 注意：使用 ::numeric 明確轉換類型以避免 PostgreSQL 類型推斷問題
            upsert_query = """
                INSERT INTO leisure_farms (
                    farm_name, county, township, address, phone, web_url,
                    certify_start_date, certify_end_date, identify_item, photo_url,
                    longitude, latitude, geom, last_synced, created_at
                ) VALUES (
                    $1, $2, $3, $4, $5, $6, $7, $8, $9, $10,
                    $11::numeric, $12::numeric,
                    ST_SetSRID(ST_MakePoint($11::numeric, $12::numeric), 4326),
                    NOW(), NOW()
                )
                ON CONFLICT (farm_name, county, township)
                DO UPDATE SET
                    address = EXCLUDED.address,
                    phone = EXCLUDED.phone,
                    web_url = EXCLUDED.web_url,
                    certify_start_date = EXCLUDED.certify_start_date,
                    certify_end_date = EXCLUDED.certify_end_date,
                    identify_item = EXCLUDED.identify_item,
                    photo_url = EXCLUDED.photo_url,
                    longitude = EXCLUDED.longitude,
                    latitude = EXCLUDED.latitude,
                    geom = EXCLUDED.geom,
                    last_synced = NOW()
                RETURNING (xmax = 0) AS inserted
            """

            result = await conn.execute_query_dict(
                upsert_query,
                [
                    farm_name, county, township, address, phone, web_url,
                    certify_start, certify_end, identify_item, photo_url,
                    str(longitude), str(latitude)
                ]
            )

            if result and result[0].get("inserted"):
                stats["inserted"] += 1
                if verbose:
                    logger.info(f"[{idx}] INSERTED: {farm_name}")
            else:
                stats["updated"] += 1
                if verbose:
                    logger.info(f"[{idx}] UPDATED: {farm_name}")

        except Exception as e:
            reason = f"資料庫錯誤: {str(e)}"
            logger.error(f"[{idx}] ERROR - {record.get('FarmNm_CH', 'unknown')}: {reason}")
            failed_records.append({
                "index": idx,
                "farm_name": record.get('FarmNm_CH', '未知'),
                "county": record.get('County'),
                "township": record.get('Township'),
                "reason": reason,
                "type": "database_error",
                "error": str(e)
            })
            stats["errors"] += 1

    return stats, failed_records


async def ensure_unique_constraint():
    """確保資料庫有必要的唯一約束"""
    from tortoise import connections
    
    conn = connections.get("default")
    
    # 檢查並建立唯一約束
    check_query = """
        SELECT COUNT(*) as cnt FROM pg_constraint 
        WHERE conname = 'leisure_farms_farm_name_county_township_key'
    """
    
    result = await conn.execute_query_dict(check_query)
    
    if result[0]["cnt"] == 0:
        logger.info("Creating unique constraint on leisure_farms...")
        
        create_constraint = """
            ALTER TABLE leisure_farms 
            ADD CONSTRAINT leisure_farms_farm_name_county_township_key 
            UNIQUE (farm_name, county, township)
        """
        
        try:
            await conn.execute_query(create_constraint)
            logger.info("Unique constraint created successfully")
        except Exception as e:
            logger.warning(f"Could not create unique constraint (may already exist): {e}")


async def main(dry_run: bool = False, verbose: bool = False):
    """
    主程式：同步休閒農場資料

    Args:
        dry_run: 測試模式，不實際寫入資料庫
        verbose: 顯示詳細的處理過程
    """
    # 在函數內部 import（確保環境變數已載入）
    from tortoise import Tortoise
    from src.database.config import TORTOISE_ORM

    logger.info("=" * 80)
    logger.info("休閒農場資料同步腳本")
    if dry_run:
        logger.info("[DRY-RUN 模式] 不會實際寫入資料庫")
    logger.info("=" * 80)

    start_time = datetime.now()

    try:
        # 初始化資料庫
        logger.info("正在連接資料庫...")
        await Tortoise.init(config=TORTOISE_ORM)
        logger.info("資料庫連接成功\n")

        # 確保有唯一約束
        if not dry_run:
            await ensure_unique_constraint()

        # 從 MOA API 取得資料
        logger.info("正在從農業部 API 取得資料...")
        moa_data = await fetch_moa_data()

        if not moa_data:
            logger.warning("未從 API 取得任何資料")
            return

        logger.info(f"成功取得 {len(moa_data)} 筆資料\n")

        # 同步到資料庫
        logger.info("開始同步資料...")
        stats, failed_records = await sync_leisure_farms(moa_data, dry_run, verbose)

        # 輸出統計
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        logger.info("\n" + "=" * 80)
        logger.info("同步完成！")
        logger.info("=" * 80)
        logger.info(f"執行時間: {duration:.2f} 秒")
        logger.info(f"總計取得: {stats['total_fetched']} 筆")
        logger.info(f"新增: {stats['inserted']} 筆")
        logger.info(f"更新: {stats['updated']} 筆")
        logger.info(f"略過: {stats['skipped']} 筆")
        logger.info(f"錯誤: {stats['errors']} 筆")
        logger.info("=" * 80)

        # 顯示失敗記錄
        if failed_records:
            logger.info("\n" + "=" * 80)
            logger.info(f"失敗記錄明細 ({len(failed_records)} 筆)")
            logger.info("=" * 80)

            # 按類型分組
            by_type = {}
            for record in failed_records:
                record_type = record.get("type", "unknown")
                if record_type not in by_type:
                    by_type[record_type] = []
                by_type[record_type].append(record)

            for record_type, records in by_type.items():
                logger.info(f"\n[{record_type.upper()}] {len(records)} 筆:")
                for rec in records:
                    logger.info(f"  [{rec['index']}] {rec['farm_name']} ({rec.get('county', '')}{rec.get('township', '')})")
                    logger.info(f"      原因: {rec['reason']}")
                    if verbose and 'raw_data' in rec:
                        logger.info(f"      原始資料: {rec['raw_data']}")

            logger.info("=" * 80)

    except Exception as e:
        logger.error(f"\n同步失敗: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise

    finally:
        await Tortoise.close_connections()
        logger.info("\n資料庫連接已關閉")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="休閒農場資料同步腳本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例:
  開發環境:
    # 測試模式（不實際寫入）
    python api/scripts/sync_leisure_farms.py --dry-run

    # 測試模式 + 顯示詳細過程
    python api/scripts/sync_leisure_farms.py --dry-run --verbose

    # 實際同步
    python api/scripts/sync_leisure_farms.py

  生產環境:
    # 測試模式
    cd C:\\AERC\\AERC-Deploy
    runtime\\.venv\\Scripts\\python.exe app\\api\\scripts\\sync_leisure_farms.py --dry-run

    # 實際同步
    runtime\\.venv\\Scripts\\python.exe app\\api\\scripts\\sync_leisure_farms.py

    # 指定 .env 路徑
    runtime\\.venv\\Scripts\\python.exe app\\api\\scripts\\sync_leisure_farms.py --env-file C:\\AERC\\AERC-Deploy\\.env

  Docker 環境:
    docker exec -it aerc-api python scripts/sync_leisure_farms.py
        """
    )
    parser.add_argument("--dry-run", action="store_true", help="測試模式，不實際寫入資料庫")
    parser.add_argument("--verbose", action="store_true", help="顯示詳細的處理過程")
    parser.add_argument("--env-file", type=str, help="指定 .env 文件路徑（可選）")
    args = parser.parse_args()

    # 設定日誌級別
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # 載入環境變數
    env_file_path = Path(args.env_file) if args.env_file else None
    if not load_env_file(env_file_path):
        print("\n[ERROR] 環境變數載入失敗，無法繼續執行")
        print("[TIP] 請確認 .env 文件存在，或使用 --env-file 參數指定路徑")
        sys.exit(1)

    print()  # 空行分隔
    asyncio.run(main(dry_run=args.dry_run, verbose=args.verbose))
