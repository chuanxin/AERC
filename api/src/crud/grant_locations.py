import logging
import json
from typing import List, Dict, Any
from tortoise import connections

from src.database.models import Grants
from src.database.geo_models import GrantLocations

logger = logging.getLogger(__name__)

async def sync_grant_locations(grant_id: int, step2_data: Dict[str, Any]):
    """
    同步補助案件的土地位置資料到 grant_locations 表
    這個函數執行 'upsert' 操作並清理舊資料
    
    Args:
        grant_id: 補助案件ID
        step2_data: Step2的土地資料，期待包含 'lands' 陣列
    """
    logger.info(f"🔍 [DEBUG] sync_grant_locations收到: grant_id={grant_id}")
    logger.info(f"🔍 [DEBUG] step2_data內容: {json.dumps(step2_data, ensure_ascii=False, indent=2)}")
    
    # 提取土地資料陣列
    land_parcels = step2_data.get('lands', [])
    logger.info(f"🔍 [DEBUG] 解析出的land_parcels: {land_parcels}")

    if not isinstance(land_parcels, list):
        logger.warning(f"Step 2 data for grant {grant_id} does not contain a valid list of lands.")
        return

    if not land_parcels:
        logger.info(f"No land parcels to sync for grant {grant_id}")
        return

    current_location_keys = set()

    # 取得案件資訊（在迴圈外取得，避免重複查詢）
    grant = await Grants.get(id=grant_id)
    applicant_name = grant.applicant_name
    apply_year = grant.year
    case_status = grant.status
    case_number = grant.case_number

    # 🔧 修復：使用正確的 Tortoise 連接方式（僅用於 PostGIS upsert）
    conn = connections.get("default")

    try:
        for parcel in land_parcels:
            try:
                # 🔧 修復：使用正確的欄位名稱 (camelCase -> snake_case 轉換)
                land_section = parcel.get('landSec')          # 前端: landSec
                land_number = parcel.get('landNumber')        # 前端: landNumber
                longitude = parcel.get('longitude')           # 前端: longitude (根層級)
                latitude = parcel.get('latitude')             # 前端: latitude (根層級)
                # address_data = parcel.get('facilityAddress', {})

                # 🔧 修復：詳細的欄位驗證和錯誤訊息
                missing_fields = []
                if not land_section:
                    missing_fields.append('landSec')
                if not land_number:
                    missing_fields.append('landNumber')
                if not longitude:
                    missing_fields.append('longitude')
                if not latitude:
                    missing_fields.append('latitude')
                
                if missing_fields:
                    logger.warning(f"Skipping parcel due to missing fields: {missing_fields}. Parcel data: {parcel}")
                    continue

                # 建立唯一識別key
                location_key = f"{grant_id}_{land_section}_{land_number}"
                current_location_keys.add(location_key)

                # 🔧 修復：準備地理資料 - 確保座標格式正確
                try:
                    lng_float = float(longitude)
                    lat_float = float(latitude)
                    geom_wkt = f"POINT({lng_float} {lat_float})"
                except (ValueError, TypeError) as e:
                    logger.error(f"Invalid coordinates for grant {grant_id}: lng={longitude}, lat={latitude}, error={e}")
                    continue
                
                # 🔧 修復：建立更詳細的註釋
                county_name = parcel.get('landCounty', '')
                town_name = parcel.get('landTown', '')
                comment = f"Land: County-{county_name}, Town-{town_name}, Number-{land_number}"
                # comment = f"Facility Address: {address_data.get('county', '')} {address_data.get('town', '')} {address_data.get('address', '')}"

                
                # 🔧 修復：完整的元資料
                meta_data = {
                    "land_area": parcel.get('landArea'),
                    "land_area_ha": parcel.get('landAreaHa'), 
                    "facility_area": parcel.get('facilityArea'),
                    "facility_area_ha": parcel.get('facilityAreaHa'),
                    "crops": parcel.get('crops', []),
                    "land_county": parcel.get('landCounty'),
                    "land_town": parcel.get('landTown'),
                    "is_aboriginal_area": parcel.get('isAboriginalArea', False),
                    "is_irrigation_area": parcel.get('isIrrigationArea', False),
                    "is_reapplied": parcel.get('isReapplied', False)
                }

                # 🔧 修復：使用正確的 Tortoise ORM 查詢方式
                upsert_sql = """
                INSERT INTO grant_locations (
                    source_system, source_id, land_section, land_number, geom, 
                    applicant_name, apply_year, case_status, comment, meta_data, 
                    created_at, updated_at, case_number
                )
                VALUES ($1, $2, $3, $4, ST_GeomFromText($5, 4326), $6, $7, $8, $9, $10, NOW(), NOW(), $11)
                ON CONFLICT (source_system, source_id, land_section, land_number) DO UPDATE SET
                    geom = EXCLUDED.geom,
                    applicant_name = EXCLUDED.applicant_name,
                    apply_year = EXCLUDED.apply_year,
                    case_status = EXCLUDED.case_status,
                    comment = EXCLUDED.comment,
                    meta_data = EXCLUDED.meta_data,
                    updated_at = NOW()
                """
                
                # 🔧 修復：正確的參數傳遞方式
                params = [
                    'new_aerc',           # $1: source_system
                    str(grant_id),        # $2: source_id  
                    str(land_section),    # $3: land_section
                    str(land_number),     # $4: land_number
                    geom_wkt,             # $5: geom (WKT format)
                    applicant_name,       # $6: applicant_name
                    apply_year,           # $7: apply_year
                    case_status,          # $8: case_status
                    comment,              # $9: comment
                    json.dumps(meta_data, ensure_ascii=False),  # $10: meta_data (JSON)
                    case_number           #11: case_number
                ]
                
                # 🔧 修復：使用正確的 execute_query_dict 方法
                await conn.execute_query_dict(upsert_sql, params)
                
                logger.info(f"✅ Synced location for grant {grant_id}, land {land_section}-{land_number} at ({lng_float}, {lat_float})")

            except Exception as e:
                logger.error(f"❌ Error processing parcel for grant {grant_id}: {parcel}. Error: {e}")
                # 繼續處理下一筆，不要讓單筆錯誤影響整體同步

        # 清理不再存在的土地資料 (Pruning)
        if current_location_keys:
            existing_results = await GrantLocations.filter(
                source_system='new_aerc',
                source_id=str(grant_id)
            ).values('id', 'land_section', 'land_number')

            locations_to_delete = [
                loc['id']
                for loc in existing_results
                if f"{grant_id}_{loc['land_section']}_{loc['land_number']}" not in current_location_keys
            ]

            if locations_to_delete:
                await GrantLocations.filter(id__in=locations_to_delete).delete()
                logger.info(f"🗑️ Pruned {len(locations_to_delete)} old locations for grant {grant_id}")

        logger.info(f"🎯 Synchronization complete for grant {grant_id}. Processed {len(current_location_keys)} locations.")

    except Exception as e:
        logger.error(f"❌ Fatal error during sync_grant_locations for grant {grant_id}: {e}")
        raise  # 重新拋出錯誤，讓上層處理


async def sync_single_grant_metadata(grant_id: int, status: str, year: int) -> None:
    """
    當 grants.status 異動時，同步對應的 grant_locations 欄位。
    僅更新 source_system = 'new_aerc' 的資料列。
    使用 ORM filter().update() 以確保在 in_transaction() 內使用正確的 transaction connection。
    """
    await GrantLocations.filter(
        source_system='new_aerc',
        source_id=str(grant_id)
    ).update(
        case_status=status,
        apply_year=year,
    )
    logger.info(f"✅ sync_single_grant_metadata: grant_id={grant_id}, status={status}, year={year}")


