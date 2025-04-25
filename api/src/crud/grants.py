from typing import List, Optional, Dict, Any, Union
import logging
from datetime import datetime, date

from fastapi import HTTPException
from tortoise.exceptions import DoesNotExist, IntegrityError
from tortoise.transactions import in_transaction
from tortoise.expressions import Q

from src.database.models import (Offices, Counties, Towns, Villages, Grants, GrantHistory, GrantStatus)
from src.schemas.users import UserOutSchema
from src.schemas.grants import (
    GrantInSchema, GrantUpdateSchema, GrantStepSchema, 
    GrantSearchSchema, GrantLandInSchema
)
from src.schemas.token import Status


logger = logging.getLogger(__name__)


# async def get_grants(
#     year: Optional[int] = None,
#     office_id: Optional[int] = None,
#     search: Optional[str] = None,
#     skip: int = 0,
#     limit: int = 100
# ) -> List[Dict[str, Any]]:
#     """取得補助申請案件列表，可依條件過濾"""
#     # 建立基本查詢
#     query = Grant.all()
    
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
#         pipes = await Pipe.filter(grant_id=grant.id, type="end").first()
#         if pipes:
#             facility_type = pipes.installation_type
        
#         results.append({
#             "id": grant.id,
#             "case_number": grant.case_number,
#             "year": grant.year,
#             "applicant_name": grant.applicant_name,
#             "status": grant.status,
#             "status_detail": grant.status_detail,
#             "current_step": grant.current_step,
#             "county_name": grant.county.name,
#             "town_name": grant.town.name,
#             "office_name": grant.office.name,
#             "facility_type": facility_type,
#             "facility_area": facility_area,
#             "created_at": grant.created_at
#         })
    
#     return results


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

async def create_grant(data: GrantInSchema, current_user: UserOutSchema) -> Dict[str, Any]:
    """建立新的補助申請案件"""
    async with in_transaction():
        try:
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
                village=data.village if data.village else None,
                address=data.address,
                office=data.office,
                office_id=data.office_id,
                undertracker=data.undertracker,
                created_by_id=current_user.id,
                received_date=datetime.now().date(),
                received_time=datetime.now().time(),
                status=GrantStatus.DRAFT,
                current_step=1
            )

            # 儲存 Grant (save 方法會自動處理 sn 和 case_number)
            await grant.save()

            # 建立歷史紀錄
            await GrantHistory.create(
                grant=grant,
                status=GrantStatus.DRAFT,
                changed_by_id=current_user.id,
                notes="初始案件建立"
            )

            # 返回案件資訊
            return {
                "id": grant.id,
                "case_number": grant.case_number,
                "year": grant.year,
                "applicant_name": grant.applicant_name,
                "status": grant.status,
                "received_date": grant.received_date,
                "received_time": grant.received_time.strftime("%H:%M")
            }
        
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
            'created_by', 'attachments', 'comments__user', 'history__changed_by'
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
            "received_date": grant.received_date,
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
                    "status": history.status,
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
        
        # Add step-specific data
        if step == 1:  # Basic applicant information step
            result.update({
                "name": grant.applicant_name,
                "id": grant.applicant_id,
                "phone": grant.applicant_phone,
                "county": grant.county,
                "town": grant.town, 
                "village": grant.village,
                "address": grant.address,
                "manager": grant.undertracker,
                "department": grant.office,
                "departmentId": grant.office_id,
                "caseNumber": grant.case_number,
                "receivedDate": grant.received_date.isoformat() if grant.received_date else None,
                "receivedTime": grant.received_time.strftime("%H:%M") if grant.received_time else None
            })
        elif step == 2:  # Land information step
            # Fetch land-related data for step 2
            # This would include fetching from related tables if you have them
            result.update({
                "land_data": {}  # Placeholder - replace with actual land data structure
            })
        # Add cases for other steps as needed
        
        return result
    except DoesNotExist:
        raise HTTPException(status_code=404, detail=f"補助案件編號 {case_number} 不存在")


async def update_grant_step_data(case_number: str, step: int, data: Dict[str, Any], current_user: UserOutSchema) -> Dict[str, Any]:
    """更新補助申請案件特定步驟資料"""
    async with in_transaction():
        try:
            # Get the grant by case number
            grant = await Grants.get(case_number=case_number)
            
            # Update step-specific data
            if step == 1:  # Basic applicant information step
                # Update the applicant information
                update_data = {}
                
                if "name" in data:
                    update_data["applicant_name"] = data["name"]
                if "id" in data:
                    update_data["applicant_id"] = data["id"]
                if "phone" in data:
                    update_data["applicant_phone"] = data["phone"]
                if "county" in data:
                    update_data["county"] = data["county"]
                if "town" in data:
                    update_data["town"] = data["town"]
                if "village" in data:
                    update_data["village"] = data["village"]
                if "address" in data:
                    update_data["address"] = data["address"]
                if "undertracker" in data:
                    update_data["undertracker"] = data["undertracker"]
                
                # Apply updates
                await Grants.filter(id=grant.id).update(**update_data)
                
                # Update the current step if needed
                if grant.current_step < step:
                    await Grants.filter(id=grant.id).update(current_step=step)
                
                # Create history record
                if update_data:
                    await GrantHistory.create(
                        grant=grant,
                        status=grant.status,
                        changed_by_id=current_user.id,
                        notes=f"更新步驟 {step} 資料"
                    )
                
            elif step == 2:  # Land information step
                # Implement updates for land-related data
                pass
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