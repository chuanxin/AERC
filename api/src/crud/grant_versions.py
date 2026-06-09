from typing import List, Optional, Dict, Any, Tuple
import logging
import hashlib
import json
from datetime import datetime

from fastapi import HTTPException
from tortoise.exceptions import DoesNotExist, IntegrityError
from tortoise.transactions import in_transaction
from tortoise.expressions import Q

from src.database.models import Grants, GrantVersions, Users
from src.schemas.users import UserOutSchema
from src.schemas.grant_versions import (
    GrantVersionCreateSchema, GrantVersionUpdateSchema, 
    GrantVersionCompareSchema, GrantVersionDetailSchema
)

logger = logging.getLogger(__name__)


def calculate_data_hash(data: Dict[str, Any]) -> str:
    """計算資料的雜湊值"""
    try:
        # 將字典轉換為 JSON 字串並排序鍵值，確保相同資料產生相同雜湊值
        json_str = json.dumps(data, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(json_str.encode('utf-8')).hexdigest()
    except Exception as e:
        logger.error(f"計算資料雜湊值失敗: {str(e)}")
        return ""


async def create_grant_version(
    data: GrantVersionCreateSchema, 
    current_user: UserOutSchema
) -> Dict[str, Any]:
    """建立新的補助申請案件版本"""
    async with in_transaction():
        try:
            # 檢查補助申請案件是否存在
            try:
                grant = await Grants.get(id=data.grant_id)
            except DoesNotExist:
                raise HTTPException(
                    status_code=404, 
                    detail=f"補助申請案件ID {data.grant_id} 不存在"
                )
            
            # 計算資料雜湊值
            data_hash = calculate_data_hash(data.all_steps_data)
            
            # 檢查是否已存在相同資料的版本
            existing_version = await GrantVersions.filter(
                grant_id=data.grant_id,
                all_steps_data_hash=data_hash
            ).first()
            
            if existing_version:
                return {
                    "id": existing_version.id,
                    "grant_id": existing_version.grant_id,
                    "version": existing_version.version,
                    "comment": existing_version.comment,
                    "created_at": existing_version.created_at,
                    "case_number": grant.case_number,
                    "is_duplicate": True,
                    "message": "資料內容與現有版本相同，未建立新版本"
                }
            
            # 取得下一個版本號
            last_version = await GrantVersions.filter(
                grant_id=data.grant_id
            ).order_by("-version").first()
            
            next_version = (last_version.version + 1) if last_version else 1
            
            # 建立新版本
            version = await GrantVersions.create(
                grant_id=data.grant_id,
                version=next_version,
                all_steps_data=data.all_steps_data,
                all_steps_data_hash=data_hash,
                comment=data.comment,
                created_by_id=current_user.id
            )
            
            # 更新 Grant 的 active_version_id
            await Grants.filter(id=data.grant_id).update(
                active_version_id=version.id
            )
            
            logger.info(f"建立版本成功: Grant ID {data.grant_id}, Version {next_version}")
            
            return {
                "id": version.id,
                "grant_id": version.grant_id,
                "version": version.version,
                "comment": version.comment,
                "created_at": version.created_at,
                "case_number": grant.case_number,
                "is_duplicate": False,
                "message": "版本建立成功"
            }
            
        except IntegrityError:
            raise HTTPException(
                status_code=409,
                detail="版本號已存在，請重新操作",
            )
        except Exception as e:
            logger.error(f"建立版本發生錯誤: {str(e)}")
            raise HTTPException(
                status_code=500, 
                detail=f"建立版本發生錯誤: {str(e)}"
            )


async def get_grant_versions(
    grant_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """取得補助申請案件的所有版本列表"""
    try:
        # 檢查補助申請案件是否存在
        try:
            grant = await Grants.get(id=grant_id)
        except DoesNotExist:
            raise HTTPException(
                status_code=404, 
                detail=f"補助申請案件ID {grant_id} 不存在"
            )
        
        # 取得版本列表
        versions = await GrantVersions.filter(
            grant_id=grant_id
        ).prefetch_related("created_by").order_by("-version").offset(skip).limit(limit)
        
        results = []
        for version in versions:
            result = {
                "id": version.id,
                "grant_id": version.grant_id,
                "version": version.version,
                "comment": version.comment,
                "created_at": version.created_at,
                "created_by_name": None
            }
            
            if version.created_by:
                result["created_by_name"] = version.created_by.full_name or version.created_by.username
            
            results.append(result)
        
        return results
        
    except Exception as e:
        logger.error(f"取得版本列表發生錯誤: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"取得版本列表發生錯誤: {str(e)}"
        )


async def get_grant_version(version_id: int) -> Dict[str, Any]:
    """取得單一版本的詳細資料"""
    try:
        version = await GrantVersions.get(id=version_id).prefetch_related(
            "grant", "created_by"
        )
        
        result = {
            "id": version.id,
            "grant_id": version.grant_id,
            "version": version.version,
            "all_steps_data": version.all_steps_data,
            "all_steps_data_hash": version.all_steps_data_hash,
            "data_schema_version": version.data_schema_version,
            "comment": version.comment,
            "created_at": version.created_at,
            "modified_at": version.modified_at,
            "created_by": None
        }
        
        if version.created_by:
            result["created_by"] = {
                "id": version.created_by.id,
                "username": version.created_by.username,
                "full_name": version.created_by.full_name
            }
        
        return result
        
    except DoesNotExist:
        raise HTTPException(
            status_code=404, 
            detail=f"版本ID {version_id} 不存在"
        )
    except Exception as e:
        logger.error(f"取得版本詳細資料發生錯誤: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"取得版本詳細資料發生錯誤: {str(e)}"
        )


async def update_grant_version(
    version_id: int,
    data: GrantVersionUpdateSchema,
    current_user: UserOutSchema
) -> Dict[str, Any]:
    """更新版本資料（僅允許更新註解）"""
    async with in_transaction():
        try:
            # 檢查版本是否存在
            try:
                version = await GrantVersions.get(id=version_id)
            except DoesNotExist:
                raise HTTPException(
                    status_code=404, 
                    detail=f"版本ID {version_id} 不存在"
                )
            
            # 準備更新資料
            update_data = {}
            
            # 只允許更新註解，不允許修改實際資料
            if data.comment is not None:
                update_data["comment"] = data.comment
            
            # 如果有提供新的步驟資料，則建立新版本而不是更新現有版本
            if data.all_steps_data is not None:
                raise HTTPException(
                    status_code=400,
                    detail="不允許直接修改版本資料，請建立新版本"
                )
            
            if update_data:
                await GrantVersions.filter(id=version_id).update(**update_data)
                logger.info(f"更新版本註解成功: Version ID {version_id}")
            
            # 返回更新後的資料
            return await get_grant_version(version_id)
            
        except Exception as e:
            logger.error(f"更新版本發生錯誤: {str(e)}")
            raise HTTPException(
                status_code=500, 
                detail=f"更新版本發生錯誤: {str(e)}"
            )


async def delete_grant_version(
    version_id: int,
    current_user: UserOutSchema
) -> Dict[str, str]:
    """刪除版本（僅允許刪除非現行版本）"""
    async with in_transaction():
        try:
            # 檢查版本是否存在
            try:
                version = await GrantVersions.get(id=version_id).prefetch_related("grant")
            except DoesNotExist:
                raise HTTPException(
                    status_code=404, 
                    detail=f"版本ID {version_id} 不存在"
                )
            
            # 檢查是否為現行版本
            if version.grant.active_version_id == version_id:
                raise HTTPException(
                    status_code=400,
                    detail="不能刪除目前現行的版本"
                )
            
            # 刪除版本
            await GrantVersions.filter(id=version_id).delete()
            
            logger.info(f"刪除版本成功: Version ID {version_id}")
            
            return {"message": f"版本ID {version_id} 已刪除"}
            
        except Exception as e:
            logger.error(f"刪除版本發生錯誤: {str(e)}")
            raise HTTPException(
                status_code=500, 
                detail=f"刪除版本發生錯誤: {str(e)}"
            )


async def compare_grant_versions(
    version_a_id: int, 
    version_b_id: int
) -> Dict[str, Any]:
    """比較兩個版本的差異"""
    try:
        # 取得兩個版本的資料
        version_a = await get_grant_version(version_a_id)
        version_b = await get_grant_version(version_b_id)
        
        # 檢查是否屬於同一個補助申請案件
        if version_a["grant_id"] != version_b["grant_id"]:
            raise HTTPException(
                status_code=400,
                detail="只能比較同一個補助申請案件的不同版本"
            )
        
        # 比較資料差異
        differences = _compare_data(
            version_a["all_steps_data"], 
            version_b["all_steps_data"]
        )
        
        return {
            "version_a": version_a,
            "version_b": version_b,
            "differences": differences
        }
        
    except Exception as e:
        logger.error(f"比較版本發生錯誤: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"比較版本發生錯誤: {str(e)}"
        )


def _compare_data(data_a: Dict[str, Any], data_b: Dict[str, Any]) -> Dict[str, Any]:
    """比較兩個資料字典的差異"""
    differences = {
        "added": {},
        "removed": {},
        "modified": {},
        "unchanged": {}
    }
    
    all_keys = set(data_a.keys()) | set(data_b.keys())
    
    for key in all_keys:
        if key in data_a and key in data_b:
            if data_a[key] != data_b[key]:
                differences["modified"][key] = {
                    "old_value": data_a[key],
                    "new_value": data_b[key]
                }
            else:
                differences["unchanged"][key] = data_a[key]
        elif key in data_a:
            differences["removed"][key] = data_a[key]
        else:
            differences["added"][key] = data_b[key]
    
    return differences


async def set_active_version(
    grant_id: int,
    version_id: int,
    current_user: UserOutSchema
) -> Dict[str, Any]:
    """設定現行版本"""
    async with in_transaction():
        try:
            # 檢查補助申請案件是否存在
            try:
                grant = await Grants.get(id=grant_id)
            except DoesNotExist:
                raise HTTPException(
                    status_code=404, 
                    detail=f"補助申請案件ID {grant_id} 不存在"
                )
            
            # 檢查版本是否存在且屬於該補助申請案件
            try:
                version = await GrantVersions.get(id=version_id, grant_id=grant_id)
            except DoesNotExist:
                raise HTTPException(
                    status_code=404, 
                    detail=f"版本ID {version_id} 不存在或不屬於該補助申請案件"
                )
            
            # 更新現行版本
            await Grants.filter(id=grant_id).update(active_version_id=version_id)
            
            logger.info(f"設定現行版本成功: Grant ID {grant_id}, Version ID {version_id}")
            
            return {
                "grant_id": grant_id,
                "active_version_id": version_id,
                "version": version.version,
                "message": "現行版本設定成功"
            }
            
        except Exception as e:
            logger.error(f"設定現行版本發生錯誤: {str(e)}")
            raise HTTPException(
                status_code=500, 
                detail=f"設定現行版本發生錯誤: {str(e)}"
            )


async def get_active_version(grant_id: int) -> Optional[Dict[str, Any]]:
    """取得補助申請案件的現行版本"""
    try:
        # 檢查補助申請案件是否存在
        try:
            grant = await Grants.get(id=grant_id).prefetch_related("active_version")
        except DoesNotExist:
            raise HTTPException(
                status_code=404, 
                detail=f"補助申請案件ID {grant_id} 不存在"
            )
        
        if not grant.active_version_id:
            return None
        
        return await get_grant_version(grant.active_version_id)
        
    except Exception as e:
        logger.error(f"取得現行版本發生錯誤: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"取得現行版本發生錯誤: {str(e)}"
        )


async def update_schema_version(
    version_id: int,
    schema_version: str,
    current_user: UserOutSchema
) -> Dict[str, Any]:
    """更新版本的資料結構版本標記"""
    try:
        # 檢查版本是否存在
        try:
            version = await GrantVersions.get(id=version_id)
        except DoesNotExist:
            raise HTTPException(
                status_code=404,
                detail=f"版本ID {version_id} 不存在"
            )
        
        # 驗證 schema_version 值（符合資料庫 DataSchemaVersions enum）
        valid_versions = ['1.0', '1.1', '1.2', '1.3', '1.4', '2.0', 'legacy']
        if schema_version not in valid_versions:
            raise HTTPException(
                status_code=400,
                detail=f"無效的資料結構版本: {schema_version}，有效值為: {', '.join(valid_versions)}"
            )
        
        # 更新 data_schema_version
        await GrantVersions.filter(id=version_id).update(
            data_schema_version=schema_version
        )
        
        logger.info(f"更新版本 {version_id} 的 data_schema_version 為 {schema_version}，操作者: {current_user.username}")
        
        return {
            "version_id": version_id,
            "data_schema_version": schema_version,
            "updated_by": current_user.username,
            "message": "資料結構版本更新成功"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新資料結構版本發生錯誤: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"更新資料結構版本發生錯誤: {str(e)}"
        )
