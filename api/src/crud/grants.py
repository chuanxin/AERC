from typing import List, Optional, Dict, Any, Union
from datetime import datetime, date

from fastapi import HTTPException
from tortoise.exceptions import DoesNotExist, IntegrityError
from src.exceptions import AppError
from tortoise.transactions import in_transaction
from tortoise.expressions import Q

from src.database.models import (Offices, Counties, Towns, Villages, Grants, GrantHistory, GrantStatus, GrantActionType, GrantVersions, GrantPapers)
from src.config.field_mappings import FieldMappingConfig, validate_step_fields
from src.schemas.users import UserOutSchema
from src.services.data_encryption import data_encryption_service, GRANT_PII_FIELDS
from src.schemas.grants import (
    GrantInSchema, GrantUpdateSchema, GrantStepSchema, 
    GrantSearchSchema, GrantLandInSchema, GrantCreateRequestSchema, GrantCreateResponseSchema
)
from src.crud.grant_versions import calculate_data_hash
from src.schemas.token import Status

from datetime import datetime, date

import json
import logging
import pytz

TAIWAN_TZ = pytz.timezone('Asia/Taipei')

def get_taiwan_now():
    """獲取本地時區的當前時間"""
    return datetime.now(TAIWAN_TZ)

def get_taiwan_time_naive():
    """獲取本地時區的當前時間（無時區資訊，適用於 TimeField）"""
    # 先獲取本地時間，然後完全移除任何時區資訊
    taiwan_datetime = datetime.now(TAIWAN_TZ)
    # 創建一個全新的 time 對象，確保沒有任何時區資訊
    return taiwan_datetime.replace(tzinfo=None).time()

def get_taiwan_date():
    """獲取本地時區的當前日期"""
    return datetime.now(TAIWAN_TZ).date()

def get_taiwan_datetime():
    """獲取本地時區的當前日期時間（用於 DatetimeField）"""
    return datetime.now(TAIWAN_TZ)


logger = logging.getLogger(__name__)


async def generate_land_locations(lands: List[Dict[str, Any]]) -> str:
    """生成土地位置摘要（不包含面積資訊，按縣市鄉鎮聚合顯示）

    從 step2 的 lands 陣列中提取縣市、鄉鎮、地段資訊，
    轉換代碼為文字並按縣市鄉鎮分組聚合，相同縣市鄉鎮的段名會聚合顯示。

    Args:
        lands: step2 的 lands 陣列，包含 landCounty, landTown, landSecName 等欄位

    Returns:
        土地位置字串（聚合顯示），例如：
        - 單一縣市鄉鎮："宜蘭縣宜蘭市-○○、△△、□□段"
        - 多個縣市鄉鎮："宜蘭縣宜蘭市-○○、△△段；花蓮縣花蓮市-□□、◇◇段"
        - 無土地資料："無土地資料"
    """
    if not lands:
        return "無土地資料"

    # 建立縣市代碼到名稱的快取映射
    county_cache = {}
    town_cache = {}

    # 收集所有唯一的縣市和鄉鎮代碼
    county_codes = set()
    town_keys = set()  # (county_code, town_code)

    for land in lands:
        county_code = str(land.get("landCounty", ""))
        town_code = str(land.get("landTown", ""))

        if county_code:
            county_codes.add(county_code)
            if town_code:
                town_keys.add((county_code, town_code))

    # 批次查詢縣市名稱（使用 id 而不是 code）
    if county_codes:
        county_ids = [int(code) for code in county_codes if code.isdigit()]
        counties = await Counties.filter(id__in=county_ids).all()
        for county in counties:
            county_cache[str(county.id)] = county.name

    # 批次查詢鄉鎮名稱（使用 id 而不是 code）
    for county_code, town_code in town_keys:
        if county_code.isdigit() and town_code.isdigit():
            county = await Counties.filter(id=int(county_code)).first()
            if county:
                town = await Towns.filter(county=county, id=int(town_code)).first()
                if town:
                    town_cache[(county_code, town_code)] = town.name

    # 按縣市鄉鎮分組聚合（與歷史案件相同邏輯）
    location_groups = {}  # {county_town: [section_names]}

    for land in lands:
        county_code = str(land.get("landCounty", ""))
        town_code = str(land.get("landTown", ""))
        sec_name = land.get("landSecName", "")

        county_name = county_cache.get(county_code, "")
        town_name = town_cache.get((county_code, town_code), "")

        # 修正：允許只有縣市+地段的土地資料（鄉鎮可選）
        if county_name and sec_name:
            # 提取段名（去除"段"字，如果存在）
            section_name = sec_name.replace("段", "").strip()

            # 以縣市鄉鎮為 key 分組（如果沒有鄉鎮，只用縣市）
            location_key = f"{county_name}{town_name}" if town_name else county_name
            if location_key not in location_groups:
                location_groups[location_key] = set()
            location_groups[location_key].add(section_name)

    # 組合顯示：縣市鄉鎮-段名1、段名2...段
    if location_groups:
        formatted_locations = []
        for location, section_names in sorted(location_groups.items()):
            sorted_sections = sorted(section_names)
            sections_str = "、".join(sorted_sections)
            formatted_locations.append(f"{location}-{sections_str}段")

        return "；".join(formatted_locations)
    else:
        return "無土地資料"


async def get_grants(
    year: Optional[int] = None,
    office_id: Optional[int] = None,
    search: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: Optional[int] = None,
    current_user = None,  # 添加使用者權限控制
    tag: Optional[str] = None,  # 標籤完全比對篩選
) -> List[Dict[str, Any]]:
    """取得補助申請案件列表，可依條件過濾

    Args:
        year: 申請年度過濾
        office_id: 管理處過濾
        search: 搜尋關鍵字（案件編號、申請人姓名、身分證字號）
        status: 案件狀態過濾（例如：'completed'）
        skip: 分頁跳過筆數
        limit: 分頁每頁筆數
        current_user: 當前使用者（用於權限控制）

    Returns:
        案件列表
    """
    try:
        from src.database.models import GrantStatus
        
        # 建立基本查詢：過濾掉已刪除的案件
        query = Grants.all().filter(status__not=GrantStatus.SOFT_DELETE)

        # 角色範圍過濾：依角色決定可見範圍，消除原有的多層 hasattr/condition 巢狀
        role = getattr(current_user, 'role', None) if current_user else None
        if role == 'admin':
            pass  # 無範圍限制，可見全部
        elif role in ('manager', 'staff'):
            user_office = getattr(current_user, 'office', None)
            if not user_office:
                from src.exceptions import AppError
                raise AppError(403, "帳號尚未指派管理處，請聯繫系統管理員完成設定")
            query = query.filter(office_id=user_office.id)
        elif role == 'user':
            user_office = getattr(current_user, 'office', None)
            if not user_office:
                from src.exceptions import AppError
                raise AppError(403, "帳號尚未指派管理處，請聯繫系統管理員完成設定")
            query = query.filter(office_id=user_office.id)
        else:
            return []  # 未知角色，拒絕存取
        
        # 應用過濾條件
        if year:
            query = query.filter(year=year)
        if office_id:
            query = query.filter(office_id=office_id)
        # status 過濾只針對歷史案件（is_legacy=true），新系統案件不受限制
        if status:
            # 歷史案件必須符合 status，新系統案件不受限制
            logger.info(f"應用 status 過濾: {status}，邏輯：(is_legacy=True & status={status}) | (is_legacy=False)")
            query = query.filter(
                (Q(is_legacy=True) & Q(status=status)) | Q(is_legacy=False)
            )
        if search:
            # applicant_name/applicant_id 已加密，不能用 DB __icontains，只對 case_number 做 DB 篩選
            # Python 層補充 applicant_name/applicant_id 的解密篩選（見下方）
            query = query.filter(Q(case_number__icontains=search))
        if tag:
            query = query.filter(tag__icontains=tag)
        
        # 執行查詢並預載入相關資料
        query = query.prefetch_related(
            'created_by',  # 建立者資訊
            'active_version'  # 啟用版本資訊
        ).offset(skip)

        # 只在 limit 有值時才應用限制（None = 查詢全部）
        if limit is not None:
            query = query.limit(limit)

        grants = await query.order_by('-created_at')

        # Python 層補充 applicant_name/applicant_id 解密後的 search 篩選
        if search:
            search_lower = search.lower()
            grants = [
                g for g in grants
                if search_lower in (g.case_number or "").lower()
                or search_lower in (data_encryption_service.decrypt(g.applicant_name) or "").lower()
                or search_lower in (data_encryption_service.decrypt(g.applicant_id) or "").lower()
            ]

        # 統計查詢結果
        legacy_count = sum(1 for g in grants if g.is_legacy)
        non_legacy_count = len(grants) - legacy_count
        logger.info(f"查詢結果：總共 {len(grants)} 筆案件（歷史: {legacy_count}, 新系統: {non_legacy_count}）")

        # 格式化結果
        results = []
        for grant in grants:
            # 基本案件資訊（PII 欄位解密後回傳）
            grant_data = {
                "id": grant.id,
                "case_number": grant.case_number,
                "year": grant.year,
                "applicant_name": data_encryption_service.decrypt(grant.applicant_name),
                "applicant_id": data_encryption_service.decrypt(grant.applicant_id),
                "county": grant.county,
                "town": grant.town,
                "village": grant.village,
                "office": grant.office,
                "office_id": grant.office_id,
                "undertracker": grant.undertracker,
                "status": grant.status,
                "current_step": grant.current_step,
                "is_disaster_case": grant.is_disaster_case,
                "created_at": grant.created_at,
                "modified_at": grant.modified_at,
                "is_legacy": grant.is_legacy,
                "tag": grant.tag,
            }
            
            # 添加建立者資訊（legacy 資料因 schema 不相容，不提供建立者資訊）
            if not grant.is_legacy and hasattr(grant, 'created_by') and grant.created_by:
                grant_data["created_by"] = {
                    "id": grant.created_by.id,
                    "username": grant.created_by.username,
                    "full_name": data_encryption_service.decrypt(grant.created_by.full_name)
                }
            
            # 從 active_version 取得額外資訊
            # 統一從 all_steps_data 提取，歷史案件和新案件使用相同邏輯
            facility_area = None
            facility_area_m2 = None
            facility_type = None
            land_locations = None

            if hasattr(grant, 'active_version') and grant.active_version:
                try:
                    version_data = grant.active_version.all_steps_data
                    if version_data and isinstance(version_data, dict):
                        steps = version_data.get("steps", {})

                        # 從 step 2 取得土地/設施面積
                        step2_data = steps.get("2", {}) or steps.get(2, {})
                        if step2_data:
                            facility_area = step2_data.get("totalFacilityAreaHa")
                            facility_area_m2 = step2_data.get("totalFacilityArea")

                            # 生成土地位置摘要
                            lands = step2_data.get("lands", [])
                            if lands and isinstance(lands, list):
                                land_locations = await generate_land_locations(lands)

                        # 從 step 5 取得設施類型/灌溉類型
                        # 歷史案件：優先從 legacy_data 獲取，因為沒有 step5
                        if grant.is_legacy:
                            legacy_data = version_data.get("legacy_data", {})
                            facility_type = legacy_data.get("irrigation_type") or legacy_data.get("facility_type")
                        else:
                            step5_data = steps.get("5", {}) or steps.get(5, {})
                            if step5_data:
                                facility_type = step5_data.get("irrigationType")

                except Exception as e:
                    logger.warning(f"解析版本資料失敗，案件: {grant.case_number}, 錯誤: {str(e)}")

            # 將計算出的資料添加到結果
            grant_data.update({
                "facility_area": facility_area,
                "facility_type": facility_type,
                # 關注點分離：返回未格式化的數字，讓前端處理格式化和搜尋
                "facility_area_m2": int(float(facility_area_m2)) if facility_area_m2 else None,
                # 土地位置摘要（僅包含縣市鄉鎮地段，不含面積）
                "land_locations": land_locations
            })
            
            results.append(grant_data)
        
        logger.info(f"成功取得 {len(results)} 筆案件資料")
        return results
        
    except Exception as e:
        logger.error(f"取得案件列表失敗: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"取得案件列表失敗: {str(e)}"
        )


# async def get_grants_by_status(
#     status: str,
#     year: Optional[int] = None,
#     office_id: Optional[int] = None,
#     search: Optional[str] = None,
#     skip: int = 0,
#     limit: int = 100
# ) -> List[Dict[str, Any]]:
#     """依狀態取得補助申請案件列表，可依條件過濾"""
#     # 建立基本查詢
#     query = Grant.filter(status=status)
    
#     # 應用過濾條件
#     if year:
#         query = query.filter(year=year)
#     if office_id:
#         query = query.filter(office_id=office_id)
#     if search:
#         query = query.filter(
#             Q(case_number__contains=search) | 
#             Q(applicant_name__contains=search) |
#             Q(applicant_id__contains=search)
#         )
    
#     # 設定關聯欄位預載入
#     query = query.select_related('county', 'town', 'office')
    
#     # 執行查詢
#     grants = await query.offset(skip).limit(limit).order_by('-created_at')
    
#     # 格式化結果
#     results = []
#     for grant in grants:
#         # 嘗試獲取土地資訊
#         land = await Land.filter(grant_id=grant.id).first()
#         facility_area = None
#         facility_type = None
        
#         if land:
#             facility_area = land.facility_area
        
#         # 嘗試獲取最終設施類型
#         pipes = await Pipe.filter(grant_id=grant.

# async def get_grant(grant_id: int) -> Dict[str, Any]:
#     """依ID取得單一補助申請案件詳細資料"""
#     try:
#         grant = await Grant.get(id=grant_id).prefetch_related(
#             'county', 'town', 'village', 'office'
#         )
#     except DoesNotExist:
#         raise HTTPException(status_code=404, detail=f"補助案件ID {grant_id} 不存在")
    
#     # 準備基本資料
#     result = {
#         "id": grant.id,
#         "case_number": grant.case_number,
#         "year": grant.year,
#         "applicant_name": grant.applicant_name,
#         "applicant_id": grant.applicant_id,
#         "applicant_phone": grant.applicant_phone,
#         "county": {
#             "id": grant.county.id,
#             "name": grant.county.name,
#             "code": grant.county.code
#         },
#         "town": {
#             "id": grant.town.id,
#             "name": grant.town.name,
#             "code": grant.town.code,
#             "is_indigenous": grant.town.is_indigenous,
#             "indigenous_type": grant.town.indigenous_type
#         },
#         "village": None,
#         "address": grant.address,
#         "office": {
#             "id": grant.office.id,
#             "name": grant.office.name,
#             "short_name": grant.office.short_name,
#             "code": grant.office.code
#         },
#         "manager": grant.manager,
#         "received_date": grant.received_date,
#         "received_time": grant.received_time.strftime("%H:%M") if isinstance(grant.received_time, time) else grant.received_time,
#         "status": grant.status,
#         "status_detail": grant.status_detail,
#         "current_step": grant.current_step,
#         "created_at": grant.created_at,
#         "modified_at": grant.modified_at
#     }
    
#     # 加入村里資訊（如果有）
#     if grant.village:
#         result["village"] = {
#             "id": grant.village.id,
#             "name": grant.village.name,
#             "code": grant.village.code
#         }
    
#     # 獲取土地資訊
#     land = await Land.filter(grant_id=grant.id).first()
#     if land:
#         result.update({
#             "land_number": land.land_number,
#             "land_area": float(land.land_area),
#             "land_area_ha": float(land.land_area_ha),
#             "facility_area": float(land.facility_area),
#             "facility_area_ha": float(land.facility_area_ha)
#         })
    
#     # 獲取設施類型
#     pipe = await Pipe.filter(grant_id=grant.id, type="end").first()
#     if pipe:
#         result["facility_type"] = pipe.installation_type
    
#     # 獲取補助金額資訊
#     subsidy = await Subsidy.filter(grant_id=grant.id).first()
#     if subsidy:
#         result.update({
#             "pipe_line_subsidy": float(subsidy.pipe_line_subsidy),
#             "facility_subsidy": float(subsidy.facility_subsidy),
#             "design_fee": float(subsidy.design_fee),
#             "total_budget": float(subsidy.total_budget)
#         })
    
#     return result


# async def get_grant_by_case_number(case_number: str) -> Dict[str, Any]:
#     """依案件編號取得單一補助申請案件詳細資料"""
#     try:
#         grant = await Grant.get(case_number=case_number).prefetch_related(
#             'county', 'town', 'village', 'office'
#         )
#         return await get_grant(grant.id)
#     except DoesNotExist:
#         raise HTTPException(status_code=404, detail=f"補助案件編號 {case_number} 不存在")
def format_tw_date(date_obj):
    """將日期對象轉換為民國年格式 (民國YYY/MM/DD)"""
    if not date_obj:
        return None
    tw_year = date_obj.year - 1911
    return f"{tw_year:03d}/{date_obj.month:02d}/{date_obj.day:02d}"

def parse_tw_date(date_str: str) -> Optional[date]:
    """將民國年格式 (YYY/MM/DD) 轉換為西元日期對象"""
    if not date_str or '/' not in date_str:
        return None
    
    try:
        parts = date_str.split('/')
        if len(parts) != 3:
            return None
        
        tw_year, month, day = parts
        gregorian_year = int(tw_year) + 1911
        
        return date(year=gregorian_year, month=int(month), day=int(day))
    except (ValueError, TypeError):
        return None
    

def map_frontend_to_backend(frontend_data: Union[Dict[str, Any], GrantCreateRequestSchema]) -> Dict[str, Any]:
    """
    Map frontend GrantCreateRequest data to backend grant creation format.
    
    Frontend (GrantCreateRequest) -> Backend (Grants model) field mapping:
    - name -> applicant_name
    - id -> applicant_id  
    - phone -> applicant_phone
    - county -> county
    - countyId -> (not used directly, county name used instead)
    - town -> town
    - townId -> (not used directly, town name used instead)
    - village -> village
    - villageId -> (not used directly, village name used instead)
    - address -> address
    - undertracker -> undertracker
    - office -> office
    - officeId -> office_id
    - valid -> (frontend validation flag, not stored in backend)
    
    Args:
        frontend_data: Dict or GrantCreateRequestSchema containing frontend fields
        
    Returns:
        Dict with backend-compatible field names and values
        
    Raises:
        ValueError: If required fields are missing or invalid
    """
    # Convert schema object to dict if needed
    if isinstance(frontend_data, GrantCreateRequestSchema):
        data_dict = frontend_data.model_dump()
    else:
        # Validate using schema if it's a raw dict
        validated_data = GrantCreateRequestSchema(**frontend_data)
        data_dict = validated_data.model_dump()
    
    # Map frontend fields to backend fields
    backend_data = {
        'applicant_name': data_dict['name'],
        'applicant_id': data_dict['id'],
        'applicant_phone': data_dict['phone'],
        'county': data_dict['county'],
        'town': data_dict['town'],
        'village': data_dict.get('village'),  # Optional field
        'address': data_dict['address'],
        'undertracker': data_dict['undertracker'],
        'office': data_dict['office'],
        'office_id': data_dict.get('officeId'),  # May be None if not provided
        'is_disaster_case': data_dict.get('isDisasterCase', False),  # Disaster case flag
        'disaster_case_description': data_dict.get('disasterCaseDescription', ''),  # Disaster case description
    }
    
    # Clean up None/empty values for optional fields
    if not backend_data['village']:
        backend_data['village'] = None
    
    # Validate office_id is provided when office is specified
    if backend_data['office'] and not backend_data['office_id']:
        logger.warning(f"Office '{backend_data['office']}' provided without office_id")
    
    logger.info(f"Mapped frontend data to backend format for applicant: {backend_data['applicant_name']}")
    return backend_data


async def create_grant(data, current_user):
    """建立新的補助申請案件"""
    async with in_transaction():
        try:
            # If data is a GrantCreateRequestSchema or dictionary (from frontend), map it to backend format
            if isinstance(data, (dict, GrantCreateRequestSchema)):
                mapped_data = map_frontend_to_backend(data)
                # Create a simple object with the mapped data for backward compatibility
                class MappedData:
                    def __init__(self, **kwargs):
                        for key, value in kwargs.items():
                            setattr(self, key, value)
                
                data = MappedData(**mapped_data)
            
            # 準備目前年度(民國年)
            current_year = datetime.now().year - 1911
            
            # 建立 Grant 物件但不儲存，讓我們可以生成 case_number
            grant = Grants(
                year=current_year,
                applicant_name=data_encryption_service.encrypt(data.applicant_name),
                applicant_id=data_encryption_service.encrypt(data.applicant_id),
                applicant_phone=data_encryption_service.encrypt(data.applicant_phone if hasattr(data, 'applicant_phone') else ''),
                county=data.county,
                town=data.town,
                village=data.village if hasattr(data, 'village') and data.village else None,
                address=data_encryption_service.encrypt(data.address),
                office=data.office,
                office_id=data.office_id if hasattr(data, 'office_id') else None,
                undertracker=data.undertracker,
                is_disaster_case=data.is_disaster_case if hasattr(data, 'is_disaster_case') else False,
                disaster_case_description=data.disaster_case_description if hasattr(data, 'disaster_case_description') else '',
                created_by_id=current_user.id,
                received_date=get_taiwan_date(),
                received_time=get_taiwan_time_naive(),
                status=GrantStatus.DRAFT,
                current_step=1
            )

            # 從當前使用者的 department 提取工作站代碼
            station_code = None
            if hasattr(current_user, 'department') and current_user.department:
                dept = current_user.department
                if isinstance(dept, dict) and 'station' in dept:
                    station = dept['station']
                    if isinstance(station, dict) and 'code' in station:
                        station_code = station['code']

            # 儲存 Grant (save 方法會自動處理 sn 和 case_number)
            await grant.save(station_code=station_code)

            # 建立歷史紀錄
            await GrantHistory.create(
                grant=grant,
                grant_status=GrantStatus.DRAFT,
                action_type=GrantActionType.CASE_CREATE,
                changed_by_id=current_user.id,
                notes="案件初次建立"
            )

            # 準備初始版本資料 - step0的資料 + 其他步驟空值
            initial_version_data = {
                "steps": {
                    "2": {},
                    "3": {},
                    "4": {},
                    "5": {},
                    "6": {},
                    "7": {},
                    "8": {}
                }
            }
            
            # 計算初始版本的雜湊值
            data_hash = calculate_data_hash(initial_version_data)
            
            # 建立第一個版本記錄
            initial_version = await GrantVersions.create(
                grant_id=grant.id,
                version=1,
                all_steps_data=initial_version_data,
                all_steps_data_hash=data_hash,
                comment="初始版本 - 案件建立",
                created_by_id=current_user.id
            )
            
            # 🆕 設定案件的 active_version 為剛創建的初始版本
            await Grants.filter(id=grant.id).update(active_version_id=initial_version.id)
            
            logger.info(f"成功建立案件 {grant.case_number} 和初始版本 (Version ID: {initial_version.id})，已設定為啟用版本")

            # 返回案件資訊 GrantCreateResponseSchema
            response_data = {
                "id": grant.id,
                "case_number": grant.case_number,
                "year": grant.year,
                "applicant_name": data.applicant_name,  # 使用原始明文，不需從 grant 物件解密
                "status": grant.status,
                "received_date": grant.received_date,
                "received_time": grant.received_time.strftime("%H:%M"),
                "initial_version_id": initial_version.id,
                "initial_version": 1,
                "is_disaster_case": grant.is_disaster_case,
                "disaster_case_description": grant.disaster_case_description,
                "office_id": grant.office_id,
                "undertracker": grant.undertracker,
            }

            validated_response = GrantCreateResponseSchema(**response_data)
            logger.info(f"[create_grant] 驗證後的回應: {validated_response.model_dump()}")
        
            return validated_response.model_dump()
        
        except ValueError as e:
            logger.error(f"資料映射錯誤: {str(e)}")
            raise HTTPException(status_code=400, detail="資料格式錯誤")
        except IntegrityError as e:
            logger.error(f"建立補助申請案件失敗（唯一約束衝突）: {str(e)}")
            raise HTTPException(status_code=409, detail="建立補助申請案件失敗")
        except Exception as e:
            raise AppError(500, "建立補助申請案件失敗，請稍後再試", diagnostic=str(e))


async def get_grant_by_case_number(case_number: str, grants_id: Optional[int] = None) -> Dict[str, Any]:
    """依案件編號取得單一補助申請案件詳細資料

    Args:
        case_number: 案件編號
        grants_id: 案件ID（可選，用於區分重複的 case_number）

    修正：優先使用 grants_id 查詢，避免歷史案件轉新系統時 case_number 重複的問題
    """
    try:
        # 優先使用 grants_id（精確匹配）
        if grants_id:
            grant = await Grants.get(id=grants_id).prefetch_related(
                'created_by', 'attachments', 'comments__user', 'history__changed_by', 'active_version'
            )
            # 驗證 case_number 是否匹配（防止 ID 與 case_number 不一致）
            if grant.case_number != case_number:
                raise HTTPException(
                    status_code=400,
                    detail=f"案件ID {grants_id} 與案號 {case_number} 不匹配"
                )
        else:
            # 回退到 case_number 查詢（可能有重複問題）
            grant = await Grants.get(case_number=case_number).prefetch_related(
                'created_by', 'attachments', 'comments__user', 'history__changed_by', 'active_version'
            )
        
        # Format the grant data（PII 欄位解密後回傳）
        result = {
            "id": grant.id,
            "case_number": grant.case_number,
            "year": grant.year,
            "applicant_name": data_encryption_service.decrypt(grant.applicant_name),
            "applicant_id": data_encryption_service.decrypt(grant.applicant_id),
            "applicant_phone": data_encryption_service.decrypt(grant.applicant_phone),
            "county": grant.county,
            "town": grant.town,
            "village": grant.village,
            "address": data_encryption_service.decrypt(grant.address),
            "office": grant.office,
            "office_id": grant.office_id,
            "undertracker": grant.undertracker,
            "tag": grant.tag,
            "received_date": format_tw_date(grant.received_date) if grant.received_date else None,
            "received_time": grant.received_time.strftime("%H:%M") if grant.received_time else None,
            "status": grant.status,
            "current_step": grant.current_step,
            "created_at": grant.created_at,
            "modified_at": grant.modified_at,
            "is_legacy": grant.is_legacy,
            "created_by": {
                "id": grant.created_by.id,
                "username": grant.created_by.username,
                "full_name": data_encryption_service.decrypt(grant.created_by.full_name)
            } if not grant.is_legacy and hasattr(grant, "created_by") and grant.created_by else None,
            
            # Add active version information
            "active_version": {
                "id": grant.active_version.id,
                "version": grant.active_version.version,
                "comment": grant.active_version.comment,
                "created_at": grant.active_version.created_at,
                "data_schema_version": grant.active_version.data_schema_version,
                "all_steps_data": grant.active_version.all_steps_data  # 添加完整步驟資料用於版本繼承
            } if hasattr(grant, "active_version") and grant.active_version else None,
            
            "comments": [
                {
                    "id": comment.id,
                    "text": comment.text,
                    "created_at": comment.created_at,
                    "user": {
                        "id": comment.user.id,
                        "username": comment.user.username,
                        "full_name": data_encryption_service.decrypt(comment.user.full_name)
                    } if comment.user else None
                }
                for comment in grant.comments
            ] if hasattr(grant, "comments") else [],
            
            "history": [
                {
                    "id": history.id,
                    "status": history.grant_status,
                    "notes": history.notes,
                    # "created_at": history.created_at,
                    "changed_by": {
                        "id": history.changed_by.id,
                        "username": history.changed_by.username,
                        "full_name": data_encryption_service.decrypt(history.changed_by.full_name)
                    } if history.changed_by else None
                }
                for history in grant.history
            ] if hasattr(grant, "history") else []
        }

        # Add attachments if available
        if hasattr(grant, "attachments"):
            result["attachments"] = [
                {
                    "id": attachment.id,
                    "file_name": attachment.original_filename,  # 使用正確的欄位名稱
                    "file_path": attachment.filepath,  # 使用正確的欄位名稱
                    "file_type": attachment.mime_type,  # 使用正確的欄位名稱
                    "file_size": attachment.filesize,  # 使用正確的欄位名稱
                    "upload_time": attachment.uploaded_at.isoformat() if hasattr(attachment, "uploaded_at") else None,  # 使用正確的欄位名稱
                    "description": attachment.description
                }
                for attachment in grant.attachments
            ]
        else:
            result["attachments"] = []
        
        return result
    except DoesNotExist:
        raise HTTPException(status_code=404, detail=f"補助案件編號 {case_number} 不存在")
    except Exception as e:
        raise AppError(500, "取得案件資料失敗", diagnostic=str(e))


@validate_step_fields(step=1)
async def get_grant_step_data(case_number: str, step: int) -> Dict[str, Any]:
    """取得補助申請案件特定步驟資料"""
    try:
        # Get the grant by case number
        grant = await Grants.get(case_number=case_number)
        
        # Basic data returned for all steps
        result = {
            "id": grant.id,
            "case_number": grant.case_number,
            "current_step": grant.current_step,
            "status": grant.status
        }
        
        # Add step-specific data using field mapping configuration
        if step == 1:  # Basic applicant information step - 從 grants 表讀取
            # 使用配置映射自動生成響應字段
            step_data = build_step_response_data(grant, step)
            result.update(step_data)
            
        elif step >= 2 and step <= 8:  # Steps 2-8 - 從 grant_versions.all_steps_data.steps[step] 讀取
            try:
                # 從 grant_versions 表讀取步驟資料 - 優先使用 active_version
                logger.info(f"開始讀取 step {step} 資料，案件: {case_number}, grant.active_version_id: {grant.active_version_id}")
                
                current_version = None
                if grant.active_version_id:
                    current_version = await GrantVersions.get(id=grant.active_version_id)
                    logger.info(f"使用案件指定的啟用版本 {current_version.version} 讀取 step {step} 資料，案件: {case_number}")
                else:
                    # 如果沒有設定 active_version，則查找最新版本
                    current_version = await GrantVersions.filter(
                        grant_id=grant.id
                    ).order_by('-version').first()
                    
                    if current_version:
                        logger.info(f"使用最新版本 {current_version.version} 讀取 step {step} 資料，案件: {case_number}")
                    else:
                        logger.warning(f"未找到任何版本記錄，案件: {case_number}")
                
                if current_version and current_version.all_steps_data:
                    logger.info(f"版本 {current_version.version} 的 all_steps_data 結構: {current_version.all_steps_data}")
                    steps_data = current_version.all_steps_data.get("steps", {})
                    logger.info(f"steps_data 包含的步驟: {list(steps_data.keys())}")
                    step_data = steps_data.get(str(step), {})
                    logger.info(f"Step {step} 的原始資料: {step_data}")
                    
                    if step_data:
                        result.update(step_data)
                        logger.info(f"成功從版本 {current_version.version} 讀取 step {step} 資料，案件: {case_number}")
                    else:
                        logger.info(f"Step {step} 資料為空，案件: {case_number}")
                else:
                    logger.warning(f"未找到版本資料或版本資料為空，案件: {case_number}, current_version: {current_version}")
                    if current_version:
                        logger.warning(f"版本 {current_version.version} 的 all_steps_data: {current_version.all_steps_data}")
                    
            except Exception as version_error:
                logger.error(f"從版本讀取 step {step} 資料失敗，案件: {case_number}, 錯誤: {str(version_error)}")
                # 如果版本讀取失敗，返回空資料但不報錯
                pass
            
        return result
    except DoesNotExist:
        raise HTTPException(status_code=404, detail=f"補助案件編號 {case_number} 不存在")


def build_step_response_data(grant: Grants, step: int) -> Dict[str, Any]:
    """根據字段映射配置構建步驟響應數據；PII 欄位解密後回傳。"""
    db_to_api_mapping = FieldMappingConfig.get_db_to_api_mapping(step)
    step_data = {}

    for db_field, api_field in db_to_api_mapping.items():
        try:
            db_value = getattr(grant, db_field, None)
            if db_field in GRANT_PII_FIELDS:
                db_value = data_encryption_service.decrypt(db_value)
            if api_field == "receivedDate" and db_value:
                step_data[api_field] = format_tw_date(db_value)
            elif api_field == "receivedTime" and db_value:
                step_data[api_field] = db_value.strftime("%H:%M") if hasattr(db_value, 'strftime') else str(db_value)
            else:
                step_data[api_field] = db_value

        except AttributeError:
            logger.warning(f"字段 {db_field} 在 Grant 模型中不存在")
            step_data[api_field] = None
    
    return step_data


async def update_grant_step_data(case_number: str, step: int, data, current_user):
    """更新補助申請案件特定步驟資料"""
    async with in_transaction():
        try:
            # Get the grant by case number
            grant = await Grants.get(case_number=case_number)
            
            # 提取追蹤資訊（如果有的話）
            tracking_info = {}
            actual_data = data
            
            # 檢查是否包含追蹤資訊
            if isinstance(data, dict) and 'data' in data:
                actual_data = data.get('data', {})
                tracking_info = {
                    'action_type': data.get('action_type', GrantActionType.STEP_DATA_UPDATE.value),
                    'changed_fields': data.get('changed_fields', []),
                    'old_value': data.get('old_value', {}),
                    'session_id': data.get('session_id'),
                    'notes': data.get('notes', f"更新步驟 {step} 資料")
                }
            else:
                tracking_info = {
                    'action_type': GrantActionType.STEP_DATA_UPDATE.value,
                    'changed_fields': [],
                    'old_value': {},
                    'session_id': None,
                    'notes': f"更新步驟 {step} 資料"
                }
            
            # Update step-specific data
            if step == 1:  # Basic applicant information step
                update_data = {}

                if "name" in actual_data:
                    update_data["applicant_name"] = data_encryption_service.encrypt(actual_data["name"])
                if "applicant_name" in actual_data:
                    update_data.setdefault("applicant_name", data_encryption_service.encrypt(actual_data["applicant_name"]))
                if "id" in actual_data:
                    update_data["applicant_id"] = data_encryption_service.encrypt(actual_data["id"])
                if "applicant_id" in actual_data:
                    update_data.setdefault("applicant_id", data_encryption_service.encrypt(actual_data["applicant_id"]))
                if "phone" in actual_data:
                    update_data["applicant_phone"] = data_encryption_service.encrypt(actual_data["phone"])
                if "applicant_phone" in actual_data:
                    update_data.setdefault("applicant_phone", data_encryption_service.encrypt(actual_data["applicant_phone"]))
                if "phone2" in actual_data:
                    update_data["applicant_phone2"] = data_encryption_service.encrypt(actual_data["phone2"])
                if "applicant_phone2" in actual_data:
                    update_data.setdefault("applicant_phone2", data_encryption_service.encrypt(actual_data["applicant_phone2"]))
                if "county" in actual_data:
                    update_data["county"] = actual_data["county"]
                if "town" in actual_data:
                    update_data["town"] = actual_data["town"]
                if "village" in actual_data:
                    update_data["village"] = actual_data["village"]
                if "address" in actual_data:
                    update_data["address"] = data_encryption_service.encrypt(actual_data["address"])
                if "undertracker" in actual_data:
                    update_data["undertracker"] = actual_data["undertracker"]
                if "isDisasterCase" in actual_data:
                    update_data["is_disaster_case"] = actual_data["isDisasterCase"]
                if "disasterCaseDescription" in actual_data:
                    update_data["disaster_case_description"] = actual_data["disasterCaseDescription"]

                await Grants.filter(id=grant.id).update(**update_data)

                if grant.current_step < step:
                    await Grants.filter(id=grant.id).update(current_step=step)

                if update_data or tracking_info.get('changed_fields'):
                    _PII_KEYS = {"name", "applicant_name", "id", "applicant_id",
                                 "phone", "applicant_phone", "phone2", "applicant_phone2", "address"}
                    history_new_value = {
                        k: ("***" if k in _PII_KEYS else v)
                        for k, v in actual_data.items()
                    }
                    await GrantHistory.create(
                        grant=grant,
                        action_type=tracking_info.get('action_type', GrantActionType.DATA_UPDATE.value),
                        grant_status=grant.status,
                        step_number=step,
                        changed_fields=tracking_info.get('changed_fields'),
                        old_value=tracking_info.get('old_value'),
                        new_value=history_new_value,
                        session_id=tracking_info.get('session_id'),
                        changed_by_id=current_user.id,
                        notes=tracking_info.get('notes')
                    )
                
            elif step == 2:  # Land information step - 儲存到 grant_versions.all_steps_data.steps["2"]
                try:
                    # 🆕 Step 2 資料儲存到案件的 active_version 指向的版本
                    logger.info(f"開始處理 step 2 資料更新，案件: {case_number}")
                    
                    # 優先使用案件的 active_version，如果沒有則使用最新版本
                    current_version = None
                    if grant.active_version_id:
                        current_version = await GrantVersions.get(id=grant.active_version_id)
                        logger.info(f"使用案件指定的啟用版本 {current_version.version}，案件: {case_number}")
                    else:
                        # 如果沒有設定 active_version，則查找最新版本
                        current_version = await GrantVersions.filter(
                            grant_id=grant.id
                        ).order_by('-version').first()
                        
                        if current_version:
                            # 設定為 active_version
                            await Grants.filter(id=grant.id).update(active_version_id=current_version.id)
                            logger.info(f"自動設定最新版本 {current_version.version} 為啟用版本，案件: {case_number}")
                    
                    if not current_version:
                        # 如果沒有任何版本，創建初始版本
                        initial_version_data = {
                            "steps": {
                                "2": {},
                                "3": {},
                                "4": {},
                                "5": {},
                                "6": {},
                                "7": {},
                                "8": {}
                            }
                        }
                        
                        data_hash = calculate_data_hash(initial_version_data)
                        
                        current_version = await GrantVersions.create(
                            grant_id=grant.id,
                            version=1,
                            all_steps_data=initial_version_data,
                            all_steps_data_hash=data_hash,
                            comment="系統自動建立初始版本",
                            created_by_id=current_user.id
                        )
                        
                        # 設定為 active_version
                        await Grants.filter(id=grant.id).update(active_version_id=current_version.id)
                        logger.info(f"為案件 {case_number} 創建並設定初始版本 1 為啟用版本")
                    
                    # 取得目前的 all_steps_data
                    current_all_steps_data = current_version.all_steps_data or {"steps": {}}
                    if "steps" not in current_all_steps_data:
                        current_all_steps_data["steps"] = {}

                    # Phase 1: 檢查是否為清除操作（只有元資料欄位）
                    metadata_fields = {'_caseNumber', 'valid', 'case_number', 'id', 'current_step', 'status'}
                    actual_data_keys = set(actual_data.keys()) if isinstance(actual_data, dict) else set()
                    business_data_keys = actual_data_keys - metadata_fields

                    if len(business_data_keys) == 0:
                        # 只有元資料 → 這是清除操作 → 刪除整個 step key
                        if "2" in current_all_steps_data["steps"]:
                            del current_all_steps_data["steps"]["2"]
                            logger.info(f"🗑️ Step 2 清除完成（刪除 key），案件: {case_number}")
                        else:
                            logger.info(f"🗑️ Step 2 本來就是空的，無需清除，案件: {case_number}")
                    else:
                        # 有業務資料 → 正常更新
                        current_all_steps_data["steps"]["2"] = actual_data
                        logger.info(f"Step 2 更新完成（{len(business_data_keys)} 個業務欄位），案件: {case_number}")
                    
                    # 計算新的雜湊值
                    new_data_hash = calculate_data_hash(current_all_steps_data)
                    
                    # 更新版本資料
                    await GrantVersions.filter(id=current_version.id).update(
                        all_steps_data=current_all_steps_data,
                        all_steps_data_hash=new_data_hash,
                        modified_at=get_taiwan_datetime()
                    )
                    
                    logger.info(f"成功更新 step 2 資料到版本 {current_version.version}，案件: {case_number}")
                    
                    # 更新案件的當前步驟（如果需要）
                    if grant.current_step < step:
                        await Grants.filter(id=grant.id).update(current_step=step)
                    
                    # 建立歷史紀錄
                    await GrantHistory.create(
                        grant=grant,
                        action_type=tracking_info.get('action_type', GrantActionType.VERSION_UPDATE.value),
                        grant_status=grant.status,
                        step_number=step,
                        changed_fields=tracking_info.get('changed_fields', []),
                        old_value=tracking_info.get('old_value', {}),
                        new_value=actual_data,
                        session_id=tracking_info.get('session_id'),
                        changed_by_id=current_user.id,
                        notes=f"Step 2 資料更新到版本 {current_version.version} - {tracking_info.get('notes', '')}"
                    )
                    
                    # Import and call the synchronization function
                    from src.crud.grant_locations import sync_grant_locations
                    
                    # /debug
                    logger.info(f"🔍 [DEBUG] Step2資料內容: {json.dumps(actual_data, ensure_ascii=False, indent=2)}")
                    # debug/
                    
                    await sync_grant_locations(grant.id, actual_data)

                    logger.info(f"Step 2 資料處理完成，案件: {case_number}, 版本: {current_version.version}")
                    
                except Exception as step2_error:
                    logger.error(f"Step 2 資料更新失敗，案件: {case_number}, 錯誤: {str(step2_error)}")
                    raise AppError(500, "Step 2 資料更新失敗", diagnostic=str(step2_error))
                    
            elif step >= 3 and step <= 8:  # Steps 3-8 也儲存到 grant_versions
                try:
                    # 🆕 Steps 3-8 也儲存到案件的 active_version 指向的版本
                    logger.info(f"開始處理 step {step} 資料更新，案件: {case_number}")
                    
                    # 優先使用案件的 active_version，如果沒有則使用最新版本
                    current_version = None
                    if grant.active_version_id:
                        current_version = await GrantVersions.get(id=grant.active_version_id)
                        logger.info(f"使用案件指定的啟用版本 {current_version.version}，案件: {case_number}")
                    else:
                        # 如果沒有設定 active_version，則查找最新版本
                        current_version = await GrantVersions.filter(
                            grant_id=grant.id
                        ).order_by('-version').first()
                        
                        if current_version:
                            # 設定為 active_version
                            await Grants.filter(id=grant.id).update(active_version_id=current_version.id)
                            logger.info(f"自動設定最新版本 {current_version.version} 為啟用版本，案件: {case_number}")
                    
                    if not current_version:
                        # 如果沒有任何版本，創建初始版本
                        initial_version_data = {
                            "steps": {str(i): {} for i in range(2, 9)}
                        }
                        
                        data_hash = calculate_data_hash(initial_version_data)
                        
                        current_version = await GrantVersions.create(
                            grant_id=grant.id,
                            version=1,
                            all_steps_data=initial_version_data,
                            all_steps_data_hash=data_hash,
                            comment="系統自動建立初始版本",
                            created_by_id=current_user.id
                        )
                        
                        # 設定為 active_version
                        await Grants.filter(id=grant.id).update(active_version_id=current_version.id)
                        logger.info(f"為案件 {case_number} 創建並設定初始版本 1 為啟用版本")
                    
                    # 取得目前的 all_steps_data
                    current_all_steps_data = current_version.all_steps_data or {"steps": {}}
                    if "steps" not in current_all_steps_data:
                        current_all_steps_data["steps"] = {}

                    # Phase 1: 檢查是否為清除操作（只有元資料欄位）
                    # 元資料欄位不算真正的業務資料
                    metadata_fields = {'_caseNumber', 'valid', 'case_number', 'id', 'current_step', 'status'}
                    actual_data_keys = set(actual_data.keys()) if isinstance(actual_data, dict) else set()
                    business_data_keys = actual_data_keys - metadata_fields

                    if len(business_data_keys) == 0:
                        # 只有元資料 → 這是清除操作 → 刪除整個 step key
                        if str(step) in current_all_steps_data["steps"]:
                            del current_all_steps_data["steps"][str(step)]
                            logger.info(f"🗑️ Step {step} 清除完成（刪除 key），案件: {case_number}")
                        else:
                            logger.info(f"🗑️ Step {step} 本來就是空的，無需清除，案件: {case_number}")
                    else:
                        # 有業務資料 → 正常更新
                        current_all_steps_data["steps"][str(step)] = actual_data
                        logger.info(f"Step {step} 更新完成（{len(business_data_keys)} 個業務欄位），案件: {case_number}")
                    
                    # 計算新的雜湊值
                    new_data_hash = calculate_data_hash(current_all_steps_data)
                    
                    # 更新版本資料
                    await GrantVersions.filter(id=current_version.id).update(
                        all_steps_data=current_all_steps_data,
                        all_steps_data_hash=new_data_hash,
                        modified_at=get_taiwan_datetime()
                    )
                    
                    logger.info(f"成功更新 step {step} 資料到版本 {current_version.version}，案件: {case_number}")
                    
                    # 更新案件的當前步驟（如果需要）
                    if grant.current_step < step:
                        await Grants.filter(id=grant.id).update(current_step=step)
                    
                    # 建立歷史紀錄
                    await GrantHistory.create(
                        grant=grant,
                        action_type=tracking_info.get('action_type', GrantActionType.VERSION_UPDATE.value),
                        grant_status=grant.status,
                        step_number=step,
                        changed_fields=tracking_info.get('changed_fields', []),
                        old_value=tracking_info.get('old_value', {}),
                        new_value=actual_data,
                        session_id=tracking_info.get('session_id'),
                        changed_by_id=current_user.id,
                        notes=f"Step {step} 資料更新到版本 {current_version.version} - {tracking_info.get('notes', '')}"
                    )
                    
                    logger.info(f"Step {step} 資料處理完成，案件: {case_number}, 版本: {current_version.version}")
                    
                except Exception as step_error:
                    logger.error(f"Step {step} 資料更新失敗，案件: {case_number}, 錯誤: {str(step_error)}")
                    raise AppError(500, "資料更新失敗", diagnostic=f"Step {step}: {str(step_error)}")
            # Add cases for other steps as needed
            
            # Fetch and return the updated grant data
            return await get_grant_step_data(case_number, step)
            
        except DoesNotExist:
            raise HTTPException(status_code=404, detail=f"補助案件編號 {case_number} 不存在")
        except Exception as e:
            logger.error(f"更新步驟 {step} 資料發生錯誤: {str(e)}")
            raise AppError(500, "資料更新失敗", diagnostic=f"步驟 {step}: {str(e)}")

# async def update_grant(grant_id: int, grant_data: GrantUpdateSchema, current_user: UserOutSchema) -> Dict[str, Any]:
#     """更新補助申請案件基本資料"""
#     async with in_transaction():
#         try:
#             # 檢查補助申請案件是否存在
#             try:
#                 grant = await Grant.get(id=grant_id)
#             except DoesNotExist:
#                 raise HTTPException(status_code=404, detail=f"補助案件ID {grant_id} 不存在")
            
#             # 準備更新資料
#             update_data = {}
            
#             # 更新申請人資訊
#             if grant_data.applicant_name is not None:
#                 update_data["applicant_name"] = grant_data.applicant_name
#             if grant_data.applicant_id is not None:
#                 update_data["applicant_id"] = grant_data.applicant_id
#             if grant_data.applicant_phone is not None:
#                 update_data["applicant_phone"] = grant_data.applicant_phone
            
#             # 更新地址資訊
#             if grant_data.county_id is not None:
#                 try:
#                     county = await County.get(id=grant_data.county_id)
#                     update_data["county"] = county
#                 except DoesNotExist:
#                     raise HTTPException(status_code=400, detail=f"縣市ID {grant_data.county_id} 不存在")
            
#             if grant_data.town_id is not None:
#                 try:
#                     town = await Town.get(id=grant_data.town_id)
#                     update_data["town"] = town
#                 except DoesNotExist:
#                     raise HTTPException(status_code=400, detail=f"鄉鎮市區ID {grant_data.town_id} 不存在")
            
#             if grant_data.village_id is not None:
#                 try:
#                     village = await Village.get(id=grant_data.village_id)
#                     update_data["village"] = village
#                 except DoesNotExist:
#                     raise HTTPException(status_code=400, detail=f"村里ID {grant_data.village_id} 不存在")
            
#             if grant_data.address is not None:
#                 update_data["address"] = grant_data.address
            
#             # 更新管理處與承辦人
#             if grant_data.office_id is not None:
#                 try:
#                     office = await Office.get(id=grant_data.office_id)
#                     update_data["office"] = office
#                 except DoesNotExist:
#                     raise HTTPException(status_code=400, detail=f"管理處ID {grant_data.office_id} 不存在")
            
#             if grant_data.manager is not None:
#                 update_data["manager"] = grant_data.manager
            
#             # 更新案件狀態
#             if grant_data.status is not None:
#                 update_data["status"] = grant_data.status
#             if grant_data.status_detail is not None:
#                 update_data["status_detail"] = grant_data.status_detail
#             if grant_data.current_step is not None:
#                 update_data["current_step"] = grant_data.current_step
            
#             # 更新修改者與修改時間
#             update_data["modified_by_id"] = current_user.id
            
#             # 更新補助申請案件
#             await Grant.filter(id=grant_id).update(**update_data)
            
#             # 記錄審核日誌
#             await AuditLog.create(
#                 grant_id=grant_id,
#                 action="update",
#                 description=f"更新補助申請案件基本資料",
#                 from_status=grant.status,
#                 to_status=grant_data.status or grant.status,
#                 created_by_id=current_user.id
#             )
            
#             # 返回更新後的資料
#             return await get_grant(grant_id)
            
#         except IntegrityError as e:
#             logger.error(f"更新補助申請案件失敗: {str(e)}")
#             raise HTTPException(status_code=400, detail=f"更新補助申請案件失敗: {str(e)}")
#         except Exception as e:
#             logger.error(f"更新補助申請案件發生錯誤: {str(e)}")
#             raise HTTPException(status_code=500, detail=f"更新補助申請案件發生錯誤: {str(e)}")


# async def update_grant_step(
#     grant_id: int, 
#     step: int, 
#     step_data: GrantStepSchema, 
#     current_user: UserOutSchema
# ) -> Dict[str, Any]:
#     """更新補助申請案件特定步驟資料"""
#     async with in_transaction():
#         try:
#             # 檢查補助申請案件是否存在
#             try:
#                 grant = await Grant.get(id=grant_id)
#             except DoesNotExist:
#                 raise HTTPException(status_code=404, detail=f"補助案件ID {grant_id} 不存在")
            
#             # 根據步驟處理不同資料
#             if step == 1:
#                 # 步驟1: 申請人資料
#                 await _handle_step1(grant, step_data.data, current_user)
#             elif step == 2:
#                 # 步驟2: 土地資料
#                 await _handle_step2(grant, step_data.data, current_user)
#             elif step == 3:
#                 # 步驟3: 灌溉調控設施
#                 await _handle_step3(grant, step_data.data, current_user)
#             elif step == 4:
#                 # 步驟4: 田間管路
#                 await _handle_step4(grant, step_data.data, current_user)
#             elif step == 5:
#                 # 步驟5: 現場勘查
#                 await _handle_step5(grant, step_data.data, current_user)
#             elif step == 6:
#                 # 步驟6: 補助申請資料
#                 await _handle_step6(grant, step_data.data, current_user)
#             elif step == 7:
#                 # 步驟7: 變更設計及結案申報
#                 await _handle_step7(grant, step_data.data, current_user)
#             elif step == 8:
#                 # 步驟8: 佐證及相關文件上傳
#                 await _handle_step8(grant, step_data.data, current_user)
#             else:
#                 raise HTTPException(status_code=400, detail=f"步驟 {step} 不存在")
            
#             # 更新補助申請案件步驟
#             if step > grant.current_step:
#                 await Grant.filter(id=grant_id).update(
#                     current_step=step,
#                     modified_by_id=current_user.id
#                 )
            
#             # 返回更新後的資料
#             return await get_grant(grant_id)
            
#         except Exception as e:
#             logger.error(f"更新補助申請案件步驟 {step} 發生錯誤: {str(e)}")
#             raise HTTPException(status_code=500, detail=f"更新補助申請案件步驟 {step} 發生錯誤: {str(e)}")


async def delete_grant(grant_id: int, current_user: UserOutSchema) -> Dict[str, str]:
    """邏輯刪除補助申請案件"""
    from src.database.models import GrantStatus
    async with in_transaction():
        try:
            # 檢查補助申請案件是否存在
            try:
                grant = await Grants.get(id=grant_id)
            except DoesNotExist:
                raise HTTPException(status_code=404, detail=f"補助案件ID {grant_id} 不存在")
            
            # 檢查是否已經被刪除
            if grant.status == GrantStatus.SOFT_DELETE:
                raise HTTPException(status_code=400, detail=f"補助案件ID {grant_id} 已經被刪除")
            
            # 記錄刪除動作
            await GrantHistory.create(
                grant_id=grant_id,
                action_type=GrantActionType.STATUS_CHANGE,
                description=f"邏輯刪除補助申請案件 (案號: {grant.case_number})",
                grant_status=GrantStatus.SOFT_DELETE,
                changed_by_id=current_user.id
            )
            
            # 邏輯刪除：設置狀態為 deleted，而不是物理刪除
            await Grants.filter(id=grant_id).update(
                status=GrantStatus.SOFT_DELETE
            )

            # 同步 grant_locations（去正規化副本）
            from src.crud.grant_locations import sync_single_grant_metadata
            await sync_single_grant_metadata(grant_id, GrantStatus.SOFT_DELETE, grant.year)

            logger.info(f"[delete_grant] Grant {grant.case_number} (ID: {grant_id}) soft deleted by user {current_user.id}")
            
            # 返回結果
            return {"message": f"補助案件 {grant.case_number} (ID: {grant_id}) 已刪除"}
            
        except Exception as e:
            logger.error(f"刪除補助申請案件發生錯誤: {str(e)}")
            raise AppError(500, "刪除補助申請案件發生錯誤", diagnostic=str(e))


# async def get_grant_land_details(grant_id: int) -> Dict[str, Any]:
#     """取得補助申請案件的土地資料"""
#     # 檢查補助申請案件是否存在
#     try:
#         grant = await Grant.get(id=grant_id)
#     except DoesNotExist:
#         raise HTTPException(status_code=404, detail=f"補助案件ID {grant_id} 不存在")
    
#     # 獲取土地資料
#     land = await Land.filter(grant_id=grant_id).first().prefetch_related(
#         'county', 'town', 'village', 'section'
#     )
    
#     if not land:
#         return {
#             "land": None,
#             "crops": [],
#             "owners": []
#         }
    
#     # 格式化土地資料
#     land_data = {
#         "id": land.id,
#         "county": {
#             "id": land.county.id,
#             "name": land.county.name,
#             "code": land.county.code
#         },
#         "town": {
#             "id": land.town.id,
#             "name": land.town.name,
#             "code": land.town.code,
#             "is_indigenous": land.town.is_indigenous,
#             "indigenous_type": land.town.indigenous_type
#         },
#         "village": None,
#         "section": None,
#         "land_number": land.land_number,
#         "is_aboriginal_area": land.is_aboriginal_area,
#         "is_irrigation_area": land.is_irrigation_area,
#         "is_reapplied": land.is_reapplied,
#         "longitude": float(land.longitude),
#         "latitude": float(land.latitude),
#         "land_area": float(land.land_area),
#         "land_area_ha": float(land.land_area_ha),
#         "facility_area": float(land.facility_area),
#         "facility_area_ha": float(land.facility_area_ha)
#     }
    
#     # 加入村里資訊（如果有）
#     if land.village:
#         land_data["village"] = {
#             "id": land.village.id,
#             "name": land.village.name,
#             "code": land.village.code
#         }
    
#     # 加入地段資訊（如果有）
#     if land.section:
#         land_data["section"] = {
#             "id": land.section.id,
#             "name": land.section.name,
#             "code": land.section.code
#         }
    
#     # 獲取作物資料
#     crops = await Crop.filter(land_id=land.id).prefetch_related('category', 'name')
#     crop_data = []
#     for crop in crops:
#         crop_data.append({
#             "id": crop.id,
#             "category": {
#                 "id": crop.category.id,
#                 "name": crop.category.name
#             },
#             "name": {
#                 "id": crop.name.id,
#                 "name": crop.name.name
#             }
#         })
    
#     # 獲取土地所有權人資料
#     owners = await LandOwner.filter(land_id=land.id).prefetch_related(
#         'county', 'town', 'village'
#     )
#     owner_data = []
#     for owner in owners:
#         owner_item = {
#             "id": owner.id,
#             "name": owner.name,
#             "id_number": owner.id_number,
#             "county": {
#                 "id": owner.county.id,
#                 "name": owner.county.name,
#                 "code": owner.county.code
#             },
#             "town": {
#                 "id": owner.town.id,
#                 "name": owner.town.name,
#                 "code": owner.town.code
#             },
#             "village": None,
#             "address": owner.address,
#             "share_numerator": owner.share_numerator,
#             "share_denominator": owner.share_denominator,
#             "share_area": float(owner.share_area)
#         }
        
#         # 加入村里資訊（如果有）
#         if owner.village:
#             owner_item["village"] = {
#                 "id": owner.village.id,
#                 "name": owner.village.name,
#                 "code": owner.village.code
#             }
        
#         owner_data.append(owner_item)
    
#     # 返回結果
#     return {
#         "land": land_data,
#         "crops": crop_data,
#         "owners": owner_data
#     }


# async def create_grant_land(
#     grant_id: int, 
#     land_data: GrantLandInSchema, 
#     current_user: UserOutSchema
# ) -> Dict[str, Any]:
#     """建立/更新補助申請案件的土地資料"""
#     async with in_transaction():
#         try:
#             # 檢查補助申請案件是否存在
#             try:
#                 grant = await Grant.get(id=grant_id)
#             except DoesNotExist:
#                 raise HTTPException(status_code=404, detail=f"補助案件ID {grant_id} 不存在")
            
#             # 檢查地區資料是否存在
#             try:
#                 county = await County.get(id=land_data.county_id)
#                 town = await Town.get(id=land_data.town_id)
                
#                 # 檢查村里是否存在（如果有提供）
#                 village = None
#                 if land_data.village_id:
#                     village = await Village.get(id=land_data.village_id)
                
#                 # 檢查地段是否存在（如果有提供）
#                 section = None
#                 if land_data.section_id:
#                     section = await Section.get(id=land_data.section_id)
#             except DoesNotExist as e:
#                 raise HTTPException(status_code=400, detail=f"參考資料不存在: {str(e)}")
            
#             # 檢查是否已有土地資料
#             land = await Land.filter(grant_id=grant_id).first()
            
#             if land:
#                 # 更新現有土地資料
#                 await Land.filter(id=land.id).update(
#                     county=county,
#                     town=town,
#                     village=village,
#                     section=section,
#                     land_number=land_data.land_number,
#                     is_aboriginal_area=land_data.is_aboriginal_area,
#                     is_irrigation_area=land_data.is_irrigation_area,
#                     is_reapplied=land_data.is_reapplied,
#                     longitude=land_data.longitude,
#                     latitude=land_data.latitude,
#                     land_area=land_data.land_area,
#                     land_area_ha=land_data.land_area_ha,
#                     facility_area=land_data.facility_area,
#                     facility_area_ha=land_data.facility_area_ha,
#                     modified_at=datetime.now()
#                 )
                
#                 # 刪除現有作物資料
#                 await Crop.filter(land_id=land.id).delete()
                
#                 # 刪除現有土地所有權人資料
#                 await LandOwner.filter(land_id=land.id).delete()
#             else:
#                 # 建立新的土地資料
#                 land = await Land.create(
#                     grant=grant,
#                     county=county,
#                     town=town,
#                     village=village,
#                     section=section,
#                     land_number=land_data.land_number,
#                     is_aboriginal_area=land_data.is_aboriginal_area,
#                     is_irrigation_area=land_data.is_irrigation_area,
#                     is_reapplied=land_data.is_reapplied,
#                     longitude=land_data.longitude,
#                     latitude=land_data.latitude,
#                     land_area=land_data.land_area,
#                     land_area_ha=land_data.land_area_ha,
#                     facility_area=land_data.facility_area,
#                     facility_area_ha=land_data.facility_area_ha
#                 )
            
#             # 建立作物資料
#             for crop_item in land_data.crops:
#                 await Crop.create(
#                     land=land,
#                     category_id=crop_item.category_id,
#                     name_id=crop_item.name_id
#                 )
            
#             # 建立土地所有權人資料
#             for owner_item in land_data.owners:
#                 # 檢查地區資料是否存在
#                 try:
#                     owner_county = await County.get(id=owner_item.county_id)
#                     owner_town = await Town.get(id=owner_item.town_id)
                    
#                     # 檢查村里是否存在（如果有提供）
#                     owner_village = None
#                     if owner_item.village_id:
#                         owner_village = await Village.get(id=owner_item.village_id)
#                 except DoesNotExist as e:
#                     raise HTTPException(status_code=400, detail=f"所有權人地區資料不存在: {str(e)}")
                
#                 await LandOwner.create(
#                     land=land,
#                     name=owner_item.name,
#                     id_number=owner_item.id_number,
#                     county=owner_county,
#                     town=owner_town,
#                     village=owner_village,
#                     address=owner_item.address,
#                     share_numerator=owner_item.share_numerator,
#                     share_denominator=owner_item.share_denominator,
#                     share_area=owner_item.share_area
#                 )
            
#             # 更新補助申請案件步驟
#             if grant.current_step < 2:
#                 await Grant.filter(id=grant_id).update(
#                     current_step=2,
#                     modified_by_id=current_user.id
#                 )
            
#             # 記錄審核日誌


async def claim_inactive_grant_ownership(grant_id: int, current_user):
    """
    認領 inactive 案件的所有權

    當用戶進入編輯 inactive 狀態的案件時，自動將 created_by_id 更新為當前用戶
    這樣可以讓歷史案件被新用戶接管處理

    Args:
        grant_id: 案件 ID
        current_user: 當前用戶

    Returns:
        更新後的案件資料

    Raises:
        HTTPException: 如果案件不存在或不是 inactive 狀態
    """
    async with in_transaction():
        try:
            # 檢查案件是否存在
            try:
                grant = await Grants.get(id=grant_id).prefetch_related(
                    'created_by', 'attachments', 'comments__user',
                    'history__changed_by', 'active_version'
                )
            except DoesNotExist:
                raise HTTPException(status_code=404, detail=f"案件 ID {grant_id} 不存在")

            # 檢查案件狀態是否為 inactive
            if grant.status != 'inactive':
                raise HTTPException(
                    status_code=400,
                    detail=f"只能認領 inactive 狀態的案件，當前狀態為: {grant.status}"
                )

            # 保存舊的值
            old_created_by_id = grant.created_by_id
            old_status = grant.status

            # 更新 created_by_id 為當前用戶，同時將 status 設為 approved
            await Grants.filter(id=grant.id).update(
                created_by_id=current_user.id,
                status='approved'
            )

            # 建立歷史紀錄
            await GrantHistory.create(
                grant=grant,
                action_type=GrantActionType.OWNERSHIP_CLAIM,
                grant_status='approved',
                step_number=grant.current_step,
                changed_fields=['created_by_id', 'status'],
                old_value={'created_by_id': old_created_by_id, 'status': old_status},
                new_value={'created_by_id': current_user.id, 'status': 'approved'},
                changed_by_id=current_user.id,
                notes=f"認領 inactive 案件所有權（原承辦人 ID: {old_created_by_id}，狀態 {old_status} → approved）"
            )

            logger.info(
                f"用戶 {current_user.username} (ID: {current_user.id}) "
                f"成功認領案件 {grant.case_number} (ID: {grant_id}) 的所有權"
            )

            # 返回簡化的成功響應
            return {
                "success": True,
                "message": f"成功認領案件 {grant.case_number} 的所有權",
                "grant_id": grant_id,
                "case_number": grant.case_number,
                "created_by_id": current_user.id,
                "created_by_username": current_user.username,
                "status": "approved"
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"認領案件所有權失敗: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"認領案件所有權失敗: {str(e)}"
            )


async def update_grant_status(case_number: str, new_status: str, current_user):
    """更新補助申請案件的狀態"""
    async with in_transaction():
        try:
            # 檢查案件是否存在
            try:
                grant = await Grants.get(case_number=case_number)
            except DoesNotExist:
                raise HTTPException(status_code=404, detail=f"案件編號 {case_number} 不存在")
            
            # 驗證狀態值（使用 GrantStatus 枚舉的有效值）
            valid_statuses = ["draft", "submitted", "under_review", "approved", "rejected", "completed", "withdrawn", "inactive", "cross_year", "deleted"]
            if new_status not in valid_statuses:
                raise HTTPException(
                    status_code=400, 
                    detail=f"無效的狀態值：{new_status}。有效值：{', '.join(valid_statuses)}"
                )
            
            # 保存舊狀態
            old_status = grant.status

            # 驗證補助上限（approved → under_review 時觸發）
            if old_status == GrantStatus.APPROVED and new_status == GrantStatus.UNDER_REVIEW:
                await _check_subsidy_limit_guard(grant)

            # 更新狀態
            await Grants.filter(id=grant.id).update(status=new_status)

            # 同步 grant_locations（去正規化副本）
            from src.crud.grant_locations import sync_single_grant_metadata
            await sync_single_grant_metadata(grant.id, new_status, grant.year)

            # 建立歷史紀錄
            await GrantHistory.create(
                grant=grant,
                action_type=GrantActionType.STATUS_CHANGE,
                grant_status=new_status,
                step_number=grant.current_step,
                changed_fields=['status'],
                old_value={'status': old_status},
                new_value={'status': new_status},
                changed_by_id=current_user.id,
                notes=f"更新案件狀態：{old_status} → {new_status}"
            )
            
            logger.info(f"成功更新案件 {case_number} 的狀態：{old_status} → {new_status}")
            
            return {
                "success": True,
                "case_number": case_number,
                "status": new_status,
                "old_status": old_status,
                "message": f"成功更新案件狀態為 {new_status}"
            }
            
        except HTTPException:
            # 重新拋出 HTTPException
            raise
        except Exception as e:
            logger.error(f"更新案件 {case_number} 狀態時發生錯誤: {str(e)}")
            raise HTTPException(
                status_code=500, 
                detail=f"更新狀態失敗: {str(e)}"
            )


async def update_grant_current_step(case_number: str, current_step: int, current_user):
    """更新補助申請案件的當前步驟"""
    async with in_transaction():
        try:
            # 檢查案件是否存在
            try:
                grant = await Grants.get(case_number=case_number)
            except DoesNotExist:
                raise HTTPException(status_code=404, detail=f"案件編號 {case_number} 不存在")
            
            # 驗證步驟範圍
            if current_step < 1 or current_step > 9:
                raise HTTPException(status_code=400, detail=f"步驟值必須在1-9之間，收到：{current_step}")
            
            # 更新當前步驟
            await Grants.filter(id=grant.id).update(current_step=current_step)
            
            # 建立歷史紀錄
            await GrantHistory.create(
                grant=grant,
                action_type=GrantActionType.CURRENT_STEP_UPDATE,  # 添加必需的 action_type
                grant_status=grant.status,
                step_number=current_step,
                changed_fields=['current_step'],
                old_value={'current_step': grant.current_step},
                new_value={'current_step': current_step},
                changed_by_id=current_user.id,  # 使用 changed_by_id
                notes=f"更新當前步驟為 {current_step}"
            )
            
            logger.info(f"成功更新案件 {case_number} 的當前步驟為 {current_step}")
            
            return {
                "success": True,
                "case_number": case_number,
                "current_step": current_step,
                "message": f"成功更新當前步驟為 {current_step}"
            }
            
        except HTTPException:
            # 重新拋出 HTTPException
            raise
        except Exception as e:
            logger.error(f"更新案件 {case_number} 當前步驟時發生錯誤: {str(e)}")
            raise HTTPException(
                status_code=500, 
                detail=f"更新當前步驟失敗: {str(e)}"
            )


async def batch_cross_year_grants(case_numbers: List[str], current_user) -> List[Dict[str, Any]]:
    """批次跨年度處理 - 複製案件並設定跨年度狀態"""
    results = []
    
    # 批次處理，但每個案件獨立處理以避免單一失敗影響整批
    for case_number in case_numbers:
        try:
            result = await process_single_cross_year_grant(case_number, current_user)
            results.append(result)
            logger.info(f"案件 {case_number} 跨年度處理成功")
            
        except Exception as e:
            logger.error(f"案件 {case_number} 跨年度處理失敗: {str(e)}")
            results.append({
                "original_case_number": case_number,
                "success": False,
                "message": f"跨年度處理失敗: {str(e)}",
                "error": str(e)
            })
    
    return results


async def process_single_cross_year_grant(case_number: str, current_user) -> Dict[str, Any]:
    """處理單一案件的跨年度複製"""
    async with in_transaction():
        try:
            # 1. 取得原始案件
            original_grant = await Grants.get(case_number=case_number).prefetch_related('active_version')
            logger.info(f"處理案件: {case_number}, 申請人: {original_grant.applicant_name}")
            
            # 2. 計算次年度
            next_year = original_grant.year + 1
            current_taiwan_year = datetime.now().year - 1911
            
            # 如果次年度超過當前年度，使用當前年度
            if next_year > current_taiwan_year:
                next_year = current_taiwan_year
                logger.info(f"次年度 {next_year + 1} 超過當前年度，調整為 {next_year}")
            
            # 3. 複製案件資料並建立新案件
            new_grant = Grants(
                year=next_year,
                applicant_name=original_grant.applicant_name,
                applicant_id=original_grant.applicant_id,
                applicant_phone=original_grant.applicant_phone,
                county=original_grant.county,
                town=original_grant.town,
                village=original_grant.village,
                address=original_grant.address,
                office=original_grant.office,
                office_id=original_grant.office_id,
                undertracker=original_grant.undertracker,
                is_disaster_case=original_grant.is_disaster_case,
                disaster_case_description=original_grant.disaster_case_description,
                created_by_id=current_user.id,
                received_date=get_taiwan_date(),
                received_time=get_taiwan_time_naive(),
                status=GrantStatus.DRAFT,  # 新案件從草稿開始
                current_step=1  # 新案件從步驟1開始
            )
            
            # 儲存新案件
            await new_grant.save()
            logger.info(f"📄 成功建立新案件: {new_grant.case_number}")
            
            # 4. 複製原案件的版本資料到新案件
            if original_grant.active_version:
                original_version = await GrantVersions.get(id=original_grant.active_version_id)
                
                # 計算新版本的雜湊值
                new_version_data = original_version.all_steps_data.copy() if original_version.all_steps_data else {"steps": {}}
                data_hash = calculate_data_hash(new_version_data)
                
                # 建立新案件的初始版本，並在 comment 中記錄來源
                new_version = await GrantVersions.create(
                    grant_id=new_grant.id,
                    version=1,
                    all_steps_data=new_version_data,
                    all_steps_data_hash=data_hash,
                    comment=f"跨年度案件 - 來源案件ID: {original_grant.id} (案件編號: {case_number})",
                    created_by_id=current_user.id
                )
                
                # 設定新案件的 active_version
                await Grants.filter(id=new_grant.id).update(active_version_id=new_version.id)
                logger.info(f"📦 成功複製版本資料到新案件")
            else:
                # 如果原案件沒有版本資料，建立空的初始版本
                initial_version_data = {
                    "steps": {str(i): {} for i in range(2, 9)}
                }
                data_hash = calculate_data_hash(initial_version_data)
                
                new_version = await GrantVersions.create(
                    grant_id=new_grant.id,
                    version=1,
                    all_steps_data=initial_version_data,
                    all_steps_data_hash=data_hash,
                    comment=f"跨年度案件 - 來源案件ID: {original_grant.id} (案件編號: {case_number})",
                    created_by_id=current_user.id
                )
                
                await Grants.filter(id=new_grant.id).update(active_version_id=new_version.id)
                logger.info(f"📦 成功建立新案件的初始版本")
            
            # 5. 更新原案件為跨年度狀態
            await Grants.filter(id=original_grant.id).update(
                status=GrantStatus.CROSS_YEAR,  # 設定為跨年度案件狀態
                status_detail=f"預算用罄，移至{next_year}年度撥款"
            )
            
            # 6. 建立原案件的歷史紀錄
            await GrantHistory.create(
                grant=original_grant,
                action_type=GrantActionType.STATUS_CHANGE,
                grant_status=GrantStatus.CROSS_YEAR,
                changed_fields=['status', 'status_detail'],
                old_value={
                    'status': original_grant.status,
                    'status_detail': original_grant.status_detail or ''
                },
                new_value={
                    'status': GrantStatus.CROSS_YEAR,
                    'status_detail': f"預算用罄，移至{next_year}年度撥款"
                },
                changed_by_id=current_user.id,
                notes=f"批次跨年度處理 - 案件複製到 {new_grant.case_number}"
            )
            
            # 7. 建立新案件的歷史紀錄
            await GrantHistory.create(
                grant=new_grant,
                action_type=GrantActionType.CASE_CREATE,
                grant_status=GrantStatus.DRAFT,
                changed_by_id=current_user.id,
                notes=f"跨年度案件建立 - 來源案件: {case_number}"
            )
            
            logger.info(f"案件 {case_number} 跨年度處理完成，新案件編號: {new_grant.case_number}")
            
            return {
                "original_case_number": case_number,
                "new_case_number": new_grant.case_number,
                "new_year": next_year,
                "success": True,
                "message": f"成功複製到 {next_year} 年度，新案件編號: {new_grant.case_number}"
            }
            
        except DoesNotExist:
            raise HTTPException(status_code=404, detail=f"案件編號 {case_number} 不存在")
        except Exception as e:
            logger.error(f"處理案件 {case_number} 跨年度時發生錯誤: {str(e)}")
            raise HTTPException(
                status_code=500, 
                detail=f"跨年度處理失敗: {str(e)}"
            )


async def get_grant_papers_by_case_number(case_number: str, document_type: str = "budget_statement", grants_id: Optional[int] = None) -> Dict[str, Any]:
    """依案件編號取得 grant_papers 文件資料（根據 active_version_id 匹配）
    
    Args:
        case_number: 案件編號
        document_type: 文件類型，預設為 'budget_statement'
        grants_id: 案件ID，用於區分重複案件編號（歷史案件）
    """
    try:
        # 1. 先取得案件和其 active_version_id
        if grants_id:
            # 如果提供了 grants_id，優先使用 ID 查詢
            grant = await Grants.get(id=grants_id, case_number=case_number).select_related('active_version')
        else:
            # 沒有提供 grants_id，使用案件編號查詢（可能有多筆，取最新的）
            grant = await Grants.filter(case_number=case_number).select_related('active_version').order_by('-id').first()
        
        if not grant:
            raise HTTPException(status_code=404, detail=f"案件編號 {case_number} 不存在")
        
        if not grant.active_version_id:
            raise HTTPException(status_code=404, detail=f"案件 {case_number} 沒有有效的版本資料")
        
        # 2. 根據 active_version_id 查詢 grant_papers
        try:
            grant_paper = await GrantPapers.get(
                version_id=grant.active_version_id,
                document_type=document_type
            )
            
            return {
                "case_number": case_number,
                "version_id": grant.active_version_id,
                "document_type": grant_paper.document_type,
                "document_data": grant_paper.document_data,
                "generated_at": grant_paper.generated_at.isoformat() if grant_paper.generated_at else None,
                "is_valid": grant_paper.is_valid,
                "data_hash": grant_paper.data_hash
            }
            
        except DoesNotExist:
            raise HTTPException(
                status_code=404, 
                detail=f"案件 {case_number} 的 {document_type} 文件不存在（版本ID: {grant.active_version_id}）"
            )
        
    except DoesNotExist:
        raise HTTPException(status_code=404, detail=f"案件編號 {case_number} 不存在")
    except Exception as e:
        logger.error(f"取得案件 {case_number} 的文件資料時發生錯誤: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"取得文件資料失敗: {str(e)}"
        )


async def compare_grant_versions(case_number: str) -> Dict[str, Any]:
    """比較案件的第一版本與最新版本設施差異"""
    try:
        # 1. 取得案件
        grant = await Grants.filter(case_number=case_number).order_by('-id').first()
        if not grant:
            raise HTTPException(status_code=404, detail=f"案件編號 {case_number} 不存在")

        # 2. 取得版本資料
        versions = await GrantVersions.filter(grant_id=grant.id).order_by('version')
        if len(versions) < 1:
            raise HTTPException(status_code=404, detail=f"案件 {case_number} 沒有版本資料")

        # 3. 取得第一版和最新版
        first_version = versions[0]
        latest_version = versions[-1] if len(versions) > 1 else versions[0]

        # 4. 比較設施差異
        facilities_comparison = compare_facilities_data(
            first_version.all_steps_data,
            latest_version.all_steps_data
        )

        return {
            "case_number": case_number,
            "first_version": {
                "id": first_version.id,
                "version": first_version.version,
                "created_at": first_version.created_at.isoformat() if first_version.created_at else None,
                "comment": first_version.comment
            },
            "latest_version": {
                "id": latest_version.id,
                "version": latest_version.version,
                "created_at": latest_version.created_at.isoformat() if latest_version.created_at else None,
                "comment": latest_version.comment
            },
            "facilities_comparison": facilities_comparison
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"比較案件 {case_number} 版本時發生錯誤: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"版本比較失敗: {str(e)}"
        )


async def get_grant_version_summary(case_number: str) -> Dict[str, Any]:
    """取得案件版本摘要資訊"""
    try:
        # 取得案件
        grant = await Grants.filter(case_number=case_number).order_by('-id').first()
        if not grant:
            raise HTTPException(status_code=404, detail=f"案件編號 {case_number} 不存在")

        # 取得版本資料
        versions = await GrantVersions.filter(grant_id=grant.id).order_by('version')
        
        if not versions:
            return {
                "case_number": case_number,
                "total_versions": 0,
                "has_versions": False,
                "first_version": None,
                "latest_version": None
            }

        first_version = versions[0]
        latest_version = versions[-1]

        return {
            "case_number": case_number,
            "total_versions": len(versions),
            "has_versions": True,
            "first_version": {
                "id": first_version.id,
                "version": first_version.version,
                "created_at": first_version.created_at.isoformat() if first_version.created_at else None
            },
            "latest_version": {
                "id": latest_version.id,
                "version": latest_version.version,
                "created_at": latest_version.created_at.isoformat() if latest_version.created_at else None
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"取得案件 {case_number} 版本摘要時發生錯誤: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"取得版本摘要失敗: {str(e)}"
        )


def compare_facilities_data(first_version_data: Dict[str, Any], latest_version_data: Dict[str, Any]) -> Dict[str, Any]:
    """比較兩個版本的設施資料差異（v1 vs vN 累積比較）"""

    first_steps = first_version_data.get("steps", {})
    latest_steps = latest_version_data.get("steps", {})

    # 灌溉調控設施：UI step 4 → steps["4"]（Bug 1 修正：原為 steps["3"]）
    first_step4_data = first_steps.get("4", {})
    latest_step4_data = latest_steps.get("4", {})

    # 田間管路設施：UI step 5 → steps["5"]（Bug 2a 修正：原為 steps["4"]）
    first_step5_data = first_steps.get("5", {})
    latest_step5_data = latest_steps.get("5", {})

    # 比較灌溉調控設施
    irrigation_comparison = compare_facility_list(
        first_step4_data.get("facilities", []),
        latest_step4_data.get("facilities", []),
        "irrigation"
    )

    # 比較田間管路材料清單（Bug 2b/2c 修正：原為 mainPipes / irrigationSystem）
    # 比較鍵為 matname + specification 複合鍵
    pipeline_comparison = compare_pipeline_list(
        first_step5_data.get("pipes", []),
        latest_step5_data.get("pipes", [])
    )

    # 田間管路配置層比較（irrigationTypeId 等 5 個欄位）
    config_fields = ["irrigationTypeId", "mainPipeDiameterId", "mainPipeMaterialId", "dripperSubtypeId", "sprinklerSubtypeId"]
    pipeline_config_changes = [
        {
            "field": field,
            "before": first_step5_data.get(field),
            "after": latest_step5_data.get(field),
            "changed": first_step5_data.get(field) != latest_step5_data.get(field)
        }
        for field in config_fields
    ]

    # 金額匯總
    irrigation_before = sum(float(item.get("totalPrice", 0) or 0) for item in first_step4_data.get("facilities", []))
    irrigation_after = sum(float(item.get("totalPrice", 0) or 0) for item in latest_step4_data.get("facilities", []))
    pipeline_before = sum(float(item.get("totalPrice", 0) or 0) for item in first_step5_data.get("pipes", []))
    pipeline_after = sum(float(item.get("totalPrice", 0) or 0) for item in latest_step5_data.get("pipes", []))

    return {
        "irrigation_control_facilities": irrigation_comparison,
        "pipeline_facilities": pipeline_comparison,
        "pipeline_config_changes": pipeline_config_changes,
        "summary": {
            "total_changes": len([item for item in irrigation_comparison + pipeline_comparison if item["change_type"] != "unchanged"]),
            "has_irrigation_changes": any(item["change_type"] != "unchanged" for item in irrigation_comparison),
            "has_pipeline_changes": any(item["change_type"] != "unchanged" for item in pipeline_comparison),
            "irrigation_amount_before": irrigation_before,
            "irrigation_amount_after": irrigation_after,
            "pipeline_amount_before": pipeline_before,
            "pipeline_amount_after": pipeline_after,
            "total_amount_change": (irrigation_after + pipeline_after) - (irrigation_before + pipeline_before)
        }
    }


def compare_pipeline_list(before_list: List[Dict], after_list: List[Dict]) -> List[Dict[str, Any]]:
    """比較田間管路材料清單，以 matname + specification 複合鍵識別項目"""
    results = []
    processed_keys: set = set()

    def composite_key(item: Dict) -> str:
        return f"{item.get('matname', '')} {item.get('specification', '')}"

    for after_item in after_list:
        key = composite_key(after_item)
        processed_keys.add(key)
        before_item = next((i for i in before_list if composite_key(i) == key), None)

        if not before_item:
            results.append({
                "name": key,
                "before_quantity": 0,
                "after_quantity": float(after_item.get("matamount", 0) or 0),
                "quantity_change": float(after_item.get("matamount", 0) or 0),
                "before_price": "0",
                "after_price": str(after_item.get("matprice", 0) or 0),
                "before_total": 0,
                "after_total": float(after_item.get("totalPrice", 0) or 0),
                "unit": after_item.get("itemunit", ""),
                "change_type": "added"
            })
        else:
            before_qty = float(before_item.get("matamount", 0) or 0)
            after_qty = float(after_item.get("matamount", 0) or 0)
            qty_change = after_qty - before_qty
            results.append({
                "name": key,
                "before_quantity": before_qty,
                "after_quantity": after_qty,
                "quantity_change": qty_change,
                "before_price": str(before_item.get("matprice", 0) or 0),
                "after_price": str(after_item.get("matprice", 0) or 0),
                "before_total": float(before_item.get("totalPrice", 0) or 0),
                "after_total": float(after_item.get("totalPrice", 0) or 0),
                "unit": after_item.get("itemunit", "") or before_item.get("itemunit", ""),
                "change_type": "unchanged" if qty_change == 0 and before_item.get("matprice") == after_item.get("matprice") else "modified"
            })

    for before_item in before_list:
        key = composite_key(before_item)
        if key not in processed_keys:
            results.append({
                "name": key,
                "before_quantity": float(before_item.get("matamount", 0) or 0),
                "after_quantity": 0,
                "quantity_change": -float(before_item.get("matamount", 0) or 0),
                "before_price": str(before_item.get("matprice", 0) or 0),
                "after_price": "0",
                "before_total": float(before_item.get("totalPrice", 0) or 0),
                "after_total": 0,
                "unit": before_item.get("itemunit", ""),
                "change_type": "removed"
            })

    return sorted(results, key=lambda x: x["name"])


def compare_facility_list(before_list: List[Dict], after_list: List[Dict], facility_type: str) -> List[Dict[str, Any]]:
    """比較設施列表的差異"""
    results = []
    processed_names = set()

    # 處理 after 設施
    for after_item in after_list:
        name = after_item.get("name") or after_item.get("typeLabel") or f"未命名{facility_type}設施"
        processed_names.add(name)
        
        before_item = next((item for item in before_list if (item.get("name") or item.get("typeLabel")) == name), None)
        
        if not before_item:
            # 新增的設施
            results.append({
                "name": name,
                "specification": after_item.get("specification", ""),
                "before_quantity": 0,
                "after_quantity": float(after_item.get("quantity", 0)),
                "quantity_change": float(after_item.get("quantity", 0)),
                "before_price": "0",
                "after_price": str(after_item.get("unitPrice") or after_item.get("totalPrice") or 0),
                "unit": after_item.get("unit", "台"),
                "change_type": "added"
            })
        else:
            # 比較修改的設施
            before_qty = float(before_item.get("quantity", 0))
            after_qty = float(after_item.get("quantity", 0))
            quantity_change = after_qty - before_qty
            
            results.append({
                "name": name,
                "specification": after_item.get("specification") or before_item.get("specification", ""),
                "before_quantity": before_qty,
                "after_quantity": after_qty,
                "quantity_change": quantity_change,
                "before_price": str(before_item.get("unitPrice") or before_item.get("totalPrice") or 0),
                "after_price": str(after_item.get("unitPrice") or after_item.get("totalPrice") or 0),
                "unit": after_item.get("unit") or before_item.get("unit", "台"),
                "change_type": "unchanged" if quantity_change == 0 else "modified"
            })

    # 處理已移除的設施
    for before_item in before_list:
        name = before_item.get("name") or before_item.get("typeLabel") or f"未命名{facility_type}設施"
        
        if name not in processed_names:
            results.append({
                "name": name,
                "specification": before_item.get("specification", ""),
                "before_quantity": float(before_item.get("quantity", 0)),
                "after_quantity": 0,
                "quantity_change": -float(before_item.get("quantity", 0)),
                "before_price": str(before_item.get("unitPrice") or before_item.get("totalPrice") or 0),
                "after_price": "0",
                "unit": before_item.get("unit", "台"),
                "change_type": "removed"
            })

    return sorted(results, key=lambda x: x["name"])


# ============================================================================
# 年度補助額度限制功能
# ============================================================================

ANNUAL_SUBSIDY_LIMIT = 500000  # 個人年度政府補助款上限 50 萬（元），法規要求


def _extract_grant_subsidy_amount(grant: Grants) -> int:
    """
    從單筆案件的 active_version 計算政府補助金額，回傳整數。
    lenient 模式：資料缺失或格式錯誤時回傳 0，不拋出例外。
    供 guard 的 other_grants 計算與 calculate_applicant_yearly_subsidy 共用（SSOT）。
    """
    if not grant.active_version or not grant.active_version.all_steps_data:
        return 0
    if grant.is_legacy:
        pd = grant.active_version.all_steps_data.get("pay_detail", {})
        return int(float(pd.get("amount", 0) or 0)) - int(float(pd.get("self_raised", 0) or 0))
    steps = grant.active_version.all_steps_data.get("steps", {})
    step4_subsidy = sum(
        int(float(f.get("subsidyAmount", 0) or 0))
        for f in steps.get("4", {}).get("facilities", [])
        if isinstance(f, dict)
    )
    step5_subsidy = int(float(steps.get("5", {}).get("subsidyAmount", 0) or 0))
    return step4_subsidy + step5_subsidy


async def _check_subsidy_limit_guard(grant: Grants) -> None:
    """
    approved → under_review 補助上限驗證 guard。
    超限時拋出 HTTP 409，附帶建議調整金額。
    必須在已開啟的 DB transaction 內呼叫（使用 select_for_update）。
    """
    COUNTED_STATUSES = [
        GrantStatus.SUBMITTED, GrantStatus.UNDER_REVIEW,
        GrantStatus.APPROVED, GrantStatus.COMPLETED,
    ]

    # 1. 確認 active_version 存在
    await grant.fetch_related('active_version')
    if not grant.active_version or not grant.active_version.all_steps_data:
        raise HTTPException(status_code=500, detail="案件版本資料遺失，無法執行補助上限驗證")

    steps_data = grant.active_version.all_steps_data.get("steps", {})

    # 2. 讀取本案補助金額（整數驗證，guard 是安全邊界）
    step4_data = steps_data.get("4", {})
    facilities = step4_data.get("facilities", [])
    if not isinstance(facilities, list):
        raise HTTPException(status_code=500, detail="案件步驟 4 設施資料格式錯誤")

    step4_subsidy = 0
    for f in facilities:
        if not isinstance(f, dict):
            continue
        raw = f.get("subsidyAmount", 0) or 0
        if raw != int(raw):
            raise AppError(500, "補助金額格式錯誤", diagnostic=f"設施補助金額包含非整數值：{raw}")
        step4_subsidy += int(raw)

    step5_data = steps_data.get("5", {})
    step5_raw = step5_data.get("subsidyAmount", 0) or 0
    if step5_raw != int(step5_raw):
        raise AppError(500, "補助金額格式錯誤", diagnostic=f"田間管路補助金額包含非整數值：{step5_raw}")
    step5_subsidy = int(step5_raw)

    this_case_subsidy = step4_subsidy + step5_subsidy

    # 3. 本案補助為 0，直接通過
    if this_case_subsidy == 0:
        return

    # 4. SELECT FOR UPDATE 鎖定其他計入案件，防止並發
    other_grants = await (
        Grants.filter(
            applicant_id=grant.applicant_id,
            year=grant.year,
            status__in=COUNTED_STATUSES,
        )
        .exclude(id=grant.id)
        .select_for_update()
        .prefetch_related('active_version')
    )

    # 5. 計算其他案件已用補助（呼叫共用 helper，SSOT）
    other_subsidy = sum(_extract_grant_subsidy_amount(g) for g in other_grants)

    # 6. 計算可用額度與超限量
    allowed = max(0, ANNUAL_SUBSIDY_LIMIT - other_subsidy)
    excess = this_case_subsidy - allowed

    if excess <= 0:
        return  # 通過

    # 7a. 先壓縮 step5（田間管路）
    suggested_step5 = max(0, step5_subsidy - excess)
    remaining_excess = excess - (step5_subsidy - suggested_step5)
    step5_total_cost = int(step5_data.get("totalCost", 0) or step5_data.get("totalAmount", 0) or 0)

    # 7b. 再壓縮 step4 facilities（由大到小）
    facilities_indexed = [
        (i, f) for i, f in enumerate(facilities) if isinstance(f, dict)
    ]
    facilities_sorted = sorted(
        facilities_indexed,
        key=lambda x: int(x[1].get("subsidyAmount", 0) or 0),
        reverse=True,
    )

    adjustments: dict = {}
    for orig_idx, f in facilities_sorted:
        orig_subsidy = int(f.get("subsidyAmount", 0) or 0)
        total_price = int(f.get("totalPrice", 0) or 0)
        if remaining_excess > 0:
            new_subsidy = max(0, orig_subsidy - remaining_excess)
            remaining_excess -= (orig_subsidy - new_subsidy)
        else:
            new_subsidy = orig_subsidy
        adjustments[orig_idx] = {
            "suggested_subsidy": new_subsidy,
            "suggested_self_paid": total_price - new_subsidy,
        }

    # 8. 建構 422 payload
    step4_facilities_payload = []
    for i, f in enumerate(facilities):
        if not isinstance(f, dict):
            continue
        adj = adjustments.get(i, {})
        step4_facilities_payload.append({
            "index": i,
            "type": f.get("type", ""),
            "name": f.get("name", ""),
            "original_subsidy": int(f.get("subsidyAmount", 0) or 0),
            "suggested_subsidy": adj.get("suggested_subsidy", int(f.get("subsidyAmount", 0) or 0)),
            "original_self_paid": int(f.get("selfPaidAmount", 0) or 0),
            "suggested_self_paid": adj.get("suggested_self_paid", int(f.get("selfPaidAmount", 0) or 0)),
        })

    raise HTTPException(
        status_code=409,
        detail={
            "code": "SUBSIDY_LIMIT_EXCEEDED",
            "applicant_id": grant.applicant_id,
            "year": grant.year,
            "subsidy_limit": ANNUAL_SUBSIDY_LIMIT,
            "other_cases_sum": other_subsidy,
            "allowed_for_this_case": allowed,
            "original_total": this_case_subsidy,
            "suggested_total": allowed,
            "step5": {
                "original": step5_subsidy,
                "suggested": suggested_step5,
                "total_cost": step5_total_cost,
            },
            "step4_facilities": step4_facilities_payload,
            "message": "補助金額超過個人年度上限，請確認建議金額後重新送出申報",
        },
    )


async def calculate_applicant_yearly_subsidy(
    applicant_id: str,
    year: int,
    current_grant_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    計算申請人在指定年度的補助總額

    Args:
        applicant_id: 申請人身分證字號
        year: 申請年度 (民國年)
        current_grant_id: 目前正在編輯的案件ID (用於排除自己)

    補助金額計算邏輯：
        - 新系統案件 (is_legacy=False):
            補助金額 = sum(step4.facilities[].subsidyAmount)  # 調控/調蓄/動力設施
                     + step5.subsidyAmount                    # 田間管路
        - 歷史案件 (is_legacy=True):
            補助金額 = pay_detail.amount - pay_detail.self_raised

    Returns:
        Dict包含：
        - applicant_id: 申請人身分證字號
        - applicant_name: 申請人姓名
        - year: 申請年度
        - total_subsidy_amount: 已用補助額度
        - remaining_amount: 剩餘可用額度
        - subsidy_limit: 年度補助上限 (500000)
        - grant_count: 案件數量
        - grants: 案件列表
    """
    try:
        # 需要計入額度的申請狀態
        COUNTED_STATUSES = [
            GrantStatus.SUBMITTED,
            GrantStatus.UNDER_REVIEW,
            GrantStatus.APPROVED,
            GrantStatus.COMPLETED
        ]

        logger.info(f"開始計算申請人 {applicant_id} 在 {year} 年度的補助總額")

        # 查詢符合條件的案件
        query = Grants.filter(
            applicant_id=applicant_id,
            year=year,
            status__in=COUNTED_STATUSES
        ).prefetch_related('active_version')

        # 排除當前正在編輯的案件 (避免重複計算)
        if current_grant_id:
            query = query.exclude(id=current_grant_id)

        grants = await query.order_by('-created_at')

        # 計算每個案件的補助金額
        grant_subsidies = []
        total_subsidy = 0
        applicant_name = ""

        for grant in grants:
            subsidy_amount = _extract_grant_subsidy_amount(grant)

            # 記錄申請人姓名 (取第一筆即可)
            if not applicant_name:
                applicant_name = grant.applicant_name

            # 加入案件列表
            grant_subsidies.append({
                "case_number": grant.case_number,
                "status": grant.status,
                "subsidy_amount": subsidy_amount,
                "created_at": grant.created_at
            })

            total_subsidy += subsidy_amount

        # 計算剩餘額度
        remaining_amount = max(0, ANNUAL_SUBSIDY_LIMIT - total_subsidy)

        result = {
            "applicant_id": applicant_id,
            "applicant_name": applicant_name,
            "year": year,
            "total_subsidy_amount": total_subsidy,
            "remaining_amount": remaining_amount,
            "subsidy_limit": ANNUAL_SUBSIDY_LIMIT,
            "grant_count": len(grant_subsidies),
            "grants": grant_subsidies
        }

        logger.info(
            f"申請人 {applicant_id} ({applicant_name}) 在 {year} 年度: "
            f"已用額度 {total_subsidy:,.0f} 元, "
            f"剩餘額度 {remaining_amount:,.0f} 元, "
            f"共 {len(grant_subsidies)} 筆案件"
        )

        return result

    except Exception as e:
        logger.error(f"計算申請人 {applicant_id} 年度補助總額失敗: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"計算年度補助總額失敗: {str(e)}"
        )