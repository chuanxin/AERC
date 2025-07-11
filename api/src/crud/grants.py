from typing import List, Optional, Dict, Any, Union
from datetime import datetime, date

from fastapi import HTTPException
from tortoise.exceptions import DoesNotExist, IntegrityError
from tortoise.transactions import in_transaction
from tortoise.expressions import Q

from src.database.models import (Offices, Counties, Towns, Villages, Grants, GrantHistory, GrantStatus, GrantActionType, GrantVersions)
from src.config.field_mappings import FieldMappingConfig, validate_step_fields
from src.schemas.users import UserOutSchema
from src.schemas.grants import (
    GrantInSchema, GrantUpdateSchema, GrantStepSchema, 
    GrantSearchSchema, GrantLandInSchema, GrantCreateRequestSchema, GrantCreateResponseSchema
)
from src.crud.grant_versions import calculate_data_hash
from src.schemas.token import Status

from datetime import datetime, date

import logging
import pytz

TAIWAN_TZ = pytz.timezone('Asia/Taipei')

def get_taiwan_now():
    """獲取台灣時區的當前時間"""
    return datetime.now(TAIWAN_TZ)

def get_taiwan_time_naive():
    """獲取台灣時區的當前時間（無時區資訊，適用於 TimeField）"""
    # 先獲取台灣時間，然後完全移除任何時區資訊
    taiwan_datetime = datetime.now(TAIWAN_TZ)
    # 創建一個全新的 time 對象，確保沒有任何時區資訊
    return taiwan_datetime.replace(tzinfo=None).time()

def get_taiwan_date():
    """獲取台灣時區的當前日期"""
    return datetime.now(TAIWAN_TZ).date()

def get_taiwan_datetime():
    """獲取台灣時區的當前日期時間（用於 DatetimeField）"""
    return datetime.now(TAIWAN_TZ)


logger = logging.getLogger(__name__)


async def get_grants(
    year: Optional[int] = None,
    office_id: Optional[int] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    current_user = None  # 添加使用者權限控制
) -> List[Dict[str, Any]]:
    """取得補助申請案件列表，可依條件過濾
    
    Args:
        year: 申請年度過濾
        office_id: 管理處過濾
        search: 搜尋關鍵字（案件編號、申請人姓名、身分證字號）
        skip: 分頁跳過筆數
        limit: 分頁每頁筆數
        current_user: 當前使用者（用於權限控制）
    
    Returns:
        案件列表
    """
    try:
        # 建立基本查詢
        query = Grants.all()
        
        # 權限控制：如果使用者不是管理員，只能看到自己管理處的案件
        if current_user and hasattr(current_user, 'office_id') and current_user.office_id:
            if not hasattr(current_user, 'role') or current_user.role != 'admin':
                query = query.filter(office_id=current_user.office_id)
        
        # 應用過濾條件
        if year:
            query = query.filter(year=year)
        if office_id:
            query = query.filter(office_id=office_id)
        if search:
            # 使用 Q 物件進行多欄位搜尋
            query = query.filter(
                Q(case_number__icontains=search) | 
                Q(applicant_name__icontains=search) |
                Q(applicant_id__icontains=search)
            )
        
        # 執行查詢並預載入相關資料
        grants = await query.prefetch_related(
            'created_by',  # 建立者資訊
            'active_version'  # 啟用版本資訊
        ).offset(skip).limit(limit).order_by('-created_at')
        
        # 格式化結果
        results = []
        for grant in grants:
            # 基本案件資訊
            grant_data = {
                "id": grant.id,
                "case_number": grant.case_number,
                "year": grant.year,
                "applicant_name": grant.applicant_name,
                "applicant_id": grant.applicant_id,
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
            }
            
            # 添加建立者資訊
            if hasattr(grant, 'created_by') and grant.created_by:
                grant_data["created_by"] = {
                    "id": grant.created_by.id,
                    "username": grant.created_by.username,
                    "full_name": grant.created_by.full_name
                }
            
            # 從 active_version 取得額外資訊
            facility_area = None
            facility_type = None
            
            if hasattr(grant, 'active_version') and grant.active_version:
                try:
                    version_data = grant.active_version.all_steps_data
                    if version_data and isinstance(version_data, dict):
                        steps = version_data.get("steps", {})
                        
                        # 從 step 2 取得土地/設施面積
                        step2_data = steps.get("2", {}) or steps.get(2, {})
                        if step2_data:
                            # 優先使用設施面積，其次土地面積
                            facility_area = (
                                step2_data.get("facilityAreaHa") or 
                                step2_data.get("landAreaHa") or 
                                step2_data.get("facility_area_ha") or 
                                step2_data.get("land_area_ha")
                            )
                            
                        # 從 step 4 取得設施類型/灌溉類型
                        step4_data = steps.get("4", {}) or steps.get(4, {})
                        if step4_data:
                            facility_type = (
                                step4_data.get("irrigationType") or 
                                step4_data.get("facilityType") or 
                                step4_data.get("irrigation_type") or 
                                step4_data.get("facility_type")
                            )
                            
                except Exception as e:
                    logger.warning(f"解析版本資料失敗，案件: {grant.case_number}, 錯誤: {str(e)}")
            
            # 將計算出的資料添加到結果
            grant_data.update({
                "facility_area": facility_area,
                "facility_type": facility_type,
                # 轉換面積單位（公頃轉平方公尺）用於前端顯示
                "facility_area_m2": int(float(facility_area) * 10000) if facility_area else None
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
                applicant_name=data.applicant_name,
                applicant_id=data.applicant_id,
                applicant_phone=data.applicant_phone if hasattr(data, 'applicant_phone') else '',
                county=data.county,
                town=data.town,
                village=data.village if hasattr(data, 'village') and data.village else None,
                address=data.address,
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

            # 儲存 Grant (save 方法會自動處理 sn 和 case_number)
            await grant.save()

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
                "applicant_name": grant.applicant_name,
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
            raise HTTPException(status_code=400, detail=f"資料格式錯誤: {str(e)}")
        except IntegrityError as e:
            logger.error(f"建立補助申請案件失敗: {str(e)}")
            raise HTTPException(status_code=400, detail=f"建立補助申請案件失敗: {str(e)}")
        except Exception as e:
            logger.error(f"建立補助申請案件發生錯誤: {str(e)}")
            raise HTTPException(status_code=500, detail=f"建立補助申請案件發生錯誤: {str(e)}")


async def get_grant_by_case_number(case_number: str) -> Dict[str, Any]:
    """依案件編號取得單一補助申請案件詳細資料"""
    try:
        grant = await Grants.get(case_number=case_number).prefetch_related(
            'created_by', 'attachments', 'comments__user', 'history__changed_by', 'active_version'
        )
        
        # Format the grant data
        result = {
            "id": grant.id,
            "case_number": grant.case_number,
            "year": grant.year,
            "applicant_name": grant.applicant_name,
            "applicant_id": grant.applicant_id,
            "applicant_phone": grant.applicant_phone,
            "county": grant.county,
            "town": grant.town,
            "village": grant.village,
            "address": grant.address,
            "office": grant.office,
            "office_id": grant.office_id,
            "undertracker": grant.undertracker,
            "received_date": format_tw_date(grant.received_date) if grant.received_date else None,
            "received_time": grant.received_time.strftime("%H:%M") if grant.received_time else None,
            "status": grant.status,
            "current_step": grant.current_step,
            "created_at": grant.created_at,
            "modified_at": grant.modified_at,
            "created_by": {
                "id": grant.created_by.id,
                "username": grant.created_by.username,
                "full_name": grant.created_by.full_name
            } if hasattr(grant, "created_by") and grant.created_by else None,
            
            # Add active version information
            "active_version": {
                "id": grant.active_version.id,
                "version": grant.active_version.version,
                "comment": grant.active_version.comment,
                "created_at": grant.active_version.created_at
            } if hasattr(grant, "active_version") and grant.active_version else None,
            
            "comments": [
                {
                    "id": comment.id,
                    "text": comment.text,
                    "created_at": comment.created_at,
                    "user": {
                        "id": comment.user.id,
                        "username": comment.user.username,
                        "full_name": comment.user.full_name
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
                        "full_name": history.changed_by.full_name
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
                    "file_name": attachment.file_name,
                    "file_path": attachment.file_path,
                    "file_type": attachment.file_type,
                    "file_size": attachment.file_size,
                    "upload_time": attachment.upload_time.isoformat() if hasattr(attachment, "upload_time") else None,
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
        raise HTTPException(status_code=500, detail=f"案件不存在: {str(e)}")


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
                # 🆕 從 grant_versions 表讀取步驟資料 - 優先使用 active_version
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
    """根據字段映射配置構建步驟響應數據"""
    db_to_api_mapping = FieldMappingConfig.get_db_to_api_mapping(step)
    step_data = {}
    
    for db_field, api_field in db_to_api_mapping.items():
        try:
            # 獲取數據庫字段值
            db_value = getattr(grant, db_field, None)
            
            # 特殊處理某些字段格式
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
                # Update the applicant information
                update_data = {}
                
                if "name" in actual_data:
                    update_data["applicant_name"] = actual_data["name"]
                if "id" in actual_data:
                    update_data["applicant_id"] = actual_data["id"]
                if "phone" in actual_data:
                    update_data["applicant_phone"] = actual_data["phone"]
                if "county" in actual_data:
                    update_data["county"] = actual_data["county"]
                if "town" in actual_data:
                    update_data["town"] = actual_data["town"]
                if "village" in actual_data:
                    update_data["village"] = actual_data["village"]
                if "address" in actual_data:
                    update_data["address"] = actual_data["address"]
                if "undertracker" in actual_data:
                    update_data["undertracker"] = actual_data["undertracker"]
                if "isDisasterCase" in actual_data:
                    update_data["is_disaster_case"] = actual_data["isDisasterCase"]
                if "disasterCaseDescription" in actual_data:
                    update_data["disaster_case_description"] = actual_data["disasterCaseDescription"]
                
                # Apply updates
                await Grants.filter(id=grant.id).update(**update_data)
                
                # Update the current step if needed
                if grant.current_step < step:
                    await Grants.filter(id=grant.id).update(current_step=step)
                
                # Create enhanced history record
                if update_data or tracking_info.get('changed_fields'):
                    await GrantHistory.create(
                        grant=grant,
                        action_type=tracking_info.get('action_type', GrantActionType.DATA_UPDATE.value),
                        grant_status=grant.status,
                        step_number=step,
                        changed_fields=tracking_info.get('changed_fields'),
                        old_value=tracking_info.get('old_value'),
                        new_value=actual_data,
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
                    
                    # 更新 step 2 的資料
                    current_all_steps_data["steps"]["2"] = actual_data
                    
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
                    await sync_grant_locations(grant.id, actual_data)

                    logger.info(f"Step 2 資料處理完成，案件: {case_number}, 版本: {current_version.version}")
                    
                except Exception as step2_error:
                    logger.error(f"Step 2 資料更新失敗，案件: {case_number}, 錯誤: {str(step2_error)}")
                    raise HTTPException(status_code=500, detail=f"Step 2 資料更新失敗: {str(step2_error)}")
                    
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
                    
                    # 更新對應步驟的資料
                    current_all_steps_data["steps"][str(step)] = actual_data
                    
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
                    raise HTTPException(status_code=500, detail=f"Step {step} 資料更新失敗: {str(step_error)}")
            # Add cases for other steps as needed
            
            # Fetch and return the updated grant data
            return await get_grant_step_data(case_number, step)
            
        except DoesNotExist:
            raise HTTPException(status_code=404, detail=f"補助案件編號 {case_number} 不存在")
        except Exception as e:
            logger.error(f"更新步驟 {step} 資料發生錯誤: {str(e)}")
            raise HTTPException(status_code=500, detail=f"更新步驟 {step} 資料發生錯誤: {str(e)}")

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


# async def delete_grant(grant_id: int, current_user: UserOutSchema) -> Dict[str, str]:
#     """刪除補助申請案件"""
#     async with in_transaction():
#         try:
#             # 檢查補助申請案件是否存在
#             try:
#                 grant = await Grant.get(id=grant_id)
#             except DoesNotExist:
#                 raise HTTPException(status_code=404, detail=f"補助案件ID {grant_id} 不存在")
            
#             # 記錄刪除動作
#             await AuditLog.create(
#                 grant_id=grant_id,
#                 action="delete",
#                 description=f"刪除補助申請案件",
#                 from_status=grant.status,
#                 to_status="deleted",
#                 created_by_id=current_user.id
#             )
            
#             # 刪除補助申請案件
#             await Grant.filter(id=grant_id).delete()
            
#             # 返回結果
#             return {"message": f"補助案件ID {grant_id} 已刪除"}
            
#         except Exception as e:
#             logger.error(f"刪除補助申請案件發生錯誤: {str(e)}")
#             raise HTTPException(status_code=500, detail=f"刪除補助申請案件發生錯誤: {str(e)}")


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