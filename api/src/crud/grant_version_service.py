# 新版本管理服務 - grant_version_service.py
# 實作新的版本控制策略：僅「變更設計」觸發新版本建立

from typing import Dict, Any, Optional, List
from datetime import datetime
import hashlib
import json
import logging

from tortoise.transactions import in_transaction
from tortoise.exceptions import DoesNotExist
from fastapi import HTTPException

from src.database.models import (
    Grants, GrantVersions, GrantHistory, 
    GrantActionType, GrantStatus
)

logger = logging.getLogger(__name__)

class GrantVersionService:
    """補助案件版本管理服務 - 新策略實作"""
    
    # 定義不需要版本控制的步驟（基本資料）
    BASIC_DATA_STEPS = [0, 1]
    
    # 定義需要版本控制的步驟（業務流程資料）
    BUSINESS_PROCESS_STEPS = [2, 3, 4, 5, 6, 7, 8, 9]
    
    @classmethod
    async def update_current_version_data(
        cls,
        grant_id: int,
        step: int,
        step_data: Dict[str, Any],
        user_id: int,
        action_type: str = 'data_update',
        notes: str = None,
        session_id: str = None,
        ip_address: str = None
    ) -> Dict[str, Any]:
        """
        更新當前版本的資料（適用於日常資料異動）
        這是主要的資料更新方法，不會建立新版本
        """
        async with in_transaction():
            try:
                # 取得案件
                grant = await Grants.get(id=grant_id)
                
                # 取得當前版本
                current_version = await cls._get_or_create_current_version(grant, user_id)
                
                # 記錄舊資料（用於歷史追蹤）
                old_step_data = current_version.all_steps_data.get('steps', {}).get(str(step), {})
                
                # 更新版本資料
                if 'steps' not in current_version.all_steps_data:
                    current_version.all_steps_data['steps'] = {}
                
                # 根據步驟類型決定更新策略
                if step in cls.BASIC_DATA_STEPS:
                    # 基本資料同時更新 Grants model 和版本資料
                    await cls._update_basic_data_in_grants(grant, step_data, step)
                    # 同步更新版本中的基本資料
                    current_version.all_steps_data['steps'][str(step)] = cls._build_basic_data_for_version(grant)
                else:
                    # 業務流程資料僅更新版本資料
                    current_version.all_steps_data['steps'][str(step)] = step_data
                
                # 更新元資料
                current_version.all_steps_data['metadata'] = {
                    **current_version.all_steps_data.get('metadata', {}),
                    'last_updated': datetime.now().isoformat(),
                    # 'current_step': max(grant.current_step, step),
                    # 'status': grant.status
                }
                
                # 重新計算雜湊值
                current_version.all_steps_data_hash = cls._calculate_hash(current_version.all_steps_data)
                
                # 儲存版本變更
                await current_version.save()
                
                # 建立詳細的歷史記錄
                await cls._create_history_record(
                    grant=grant,
                    action_type=action_type,
                    step_number=step,
                    old_value=old_step_data,
                    new_value=step_data,
                    user_id=user_id,
                    notes=notes or f"更新步驟 {step} 資料",
                    session_id=session_id,
                    ip_address=ip_address
                )
                
                logger.info(f"成功更新案件 {grant.case_number} 步驟 {step} 資料")
                
                return {
                    'grant_id': grant_id,
                    'version_id': current_version.id,
                    'version': current_version.version,
                    'step': step,
                    'updated_data': step_data,
                    'action': 'data_updated'
                }
                
            except Exception as e:
                logger.error(f"更新版本資料失敗: {str(e)}")
                raise HTTPException(status_code=500, detail=f"更新資料失敗: {str(e)}")
    
    @classmethod
    async def create_design_change_version(
        cls,
        grant_id: int,
        user_id: int,
        comment: str = None,
        session_id: str = None,
        ip_address: str = None
    ) -> Dict[str, Any]:
        """
        建立新的設計變更版本
        只有此方法會建立新版本
        """
        async with in_transaction():
            try:
                # 取得案件
                grant = await Grants.get(id=grant_id)
                
                # 取得當前版本
                current_version = await cls._get_current_version(grant_id)
                if not current_version:
                    raise HTTPException(status_code=400, detail="找不到當前版本，無法建立設計變更版本")
                
                # 複製當前版本資料作為新版本的基礎
                new_version_data = json.loads(json.dumps(current_version.all_steps_data))
                
                # 更新新版本的元資料
                new_version_data['metadata'] = {
                    **new_version_data.get('metadata', {}),
                    'design_change_created': datetime.now().isoformat(),
                    'design_change_from_version': current_version.version,
                    'design_change_reason': comment or "設計變更"
                }
                
                # 建立新版本
                new_version = await GrantVersions.create(
                    grant_id=grant_id,
                    version=current_version.version + 1,
                    all_steps_data=new_version_data,
                    all_steps_data_hash=cls._calculate_hash(new_version_data),
                    comment=comment or f"設計變更 - 版本 {current_version.version + 1}",
                    created_by_id=user_id
                )
                
                # 更新 active_version_id 並將案件狀態退回 draft（FR-005），同一 transaction 確保原子性
                await Grants.filter(id=grant_id).update(
                    active_version_id=new_version.id,
                    status=GrantStatus.DRAFT
                )

                # 建立歷史記錄
                await cls._create_history_record(
                    grant=grant,
                    action_type=GrantActionType.STEP_CHANGE,  # 使用 STEP_CHANGE 表示設計變更
                    old_value={'version': current_version.version},
                    new_value={'version': new_version.version},
                    user_id=user_id,
                    notes=f"建立設計變更版本 {new_version.version}：{comment or '設計變更'}",
                    session_id=session_id,
                    ip_address=ip_address
                )
                
                logger.info(f"成功為案件 {grant.case_number} 建立設計變更版本 {new_version.version}")
                
                return {
                    'grant_id': grant_id,
                    'new_version_id': new_version.id,
                    'new_version': new_version.version,
                    'previous_version': current_version.version,
                    'comment': comment,
                    'action': 'design_change_version_created'
                }
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"建立設計變更版本失敗: {str(e)}")
                raise HTTPException(status_code=500, detail=f"建立設計變更版本失敗: {str(e)}")
    
    @classmethod
    async def get_complete_case_data(
        cls, 
        grant_id: int, 
        version_id: int = None
    ) -> Dict[str, Any]:
        """
        取得完整案件資料（基本資料 + 業務流程資料）
        """
        try:
            # 從 Grants 取得基本資料
            grant = await Grants.get(id=grant_id)
            
            # 從 GrantVersions 取得業務流程資料
            if version_id:
                version = await GrantVersions.get(id=version_id, grant_id=grant_id)
            else:
                version = await cls._get_current_version(grant_id)
            
            if not version:
                # 如果沒有版本，建立一個基本版本
                version = await cls._create_initial_version(grant, grant.created_by_id)
            
            # 合併基本資料與版本資料
            complete_data = {
                'grant': {
                    'id': grant.id,
                    'case_number': grant.case_number,
                    'year': grant.year,
                    'status': grant.status,
                    'current_step': grant.current_step,
                    'created_at': grant.created_at.isoformat() if grant.created_at else None,
                    'modified_at': grant.modified_at.isoformat() if grant.modified_at else None
                },
                'version': {
                    'id': version.id,
                    'version': version.version,
                    'comment': version.comment,
                    'created_at': version.created_at.isoformat() if version.created_at else None
                },
                'all_steps_data': version.all_steps_data
            }
            
            return complete_data
            
        except DoesNotExist:
            raise HTTPException(status_code=404, detail=f"找不到案件 ID {grant_id}")
        except Exception as e:
            logger.error(f"取得完整案件資料失敗: {str(e)}")
            raise HTTPException(status_code=500, detail=f"取得案件資料失敗: {str(e)}")
    
    @classmethod
    async def get_version_history(cls, grant_id: int) -> List[Dict[str, Any]]:
        """取得案件的版本歷史"""
        try:
            versions = await GrantVersions.filter(grant_id=grant_id).order_by('-version').prefetch_related('created_by')
            
            history = []
            for version in versions:
                history.append({
                    'id': version.id,
                    'version': version.version,
                    'comment': version.comment,
                    'created_at': version.created_at.isoformat() if version.created_at else None,
                    'created_by': {
                        'id': version.created_by.id,
                        'username': version.created_by.username,
                        'full_name': version.created_by.full_name
                    } if version.created_by else None,
                    'data_hash': version.all_steps_data_hash
                })
            
            return history
            
        except Exception as e:
            logger.error(f"取得版本歷史失敗: {str(e)}")
            raise HTTPException(status_code=500, detail=f"取得版本歷史失敗: {str(e)}")
    
    @classmethod
    async def get_change_history(cls, grant_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """取得案件的變更歷史"""
        try:
            history = await GrantHistory.filter(grant_id=grant_id).order_by('-changed_at').limit(limit).prefetch_related('changed_by')
            
            changes = []
            for record in history:
                changes.append({
                    'id': record.id,
                    'action_type': record.action_type,
                    'grant_status': record.grant_status,
                    'step_number': record.step_number,
                    'changed_fields': record.changed_fields,
                    'old_value': record.old_value,
                    'new_value': record.new_value,
                    'notes': record.notes,
                    'changed_at': record.changed_at.isoformat() if record.changed_at else None,
                    'changed_by': {
                        'id': record.changed_by.id,
                        'username': record.changed_by.username,
                        'full_name': record.changed_by.full_name
                    } if record.changed_by else None,
                    'session_id': record.session_id,
                    'ip_address': record.ip_address
                })
            
            return changes
            
        except Exception as e:
            logger.error(f"取得變更歷史失敗: {str(e)}")
            raise HTTPException(status_code=500, detail=f"取得變更歷史失敗: {str(e)}")
    
    # 私有方法
    @classmethod
    async def _get_current_version(cls, grant_id: int) -> Optional[GrantVersions]:
        """取得案件的當前版本"""
        return await GrantVersions.filter(grant_id=grant_id).order_by('-version').first()
    
    @classmethod
    async def _get_or_create_current_version(cls, grant: Grants, user_id: int) -> GrantVersions:
        """取得或建立當前版本"""
        current_version = await cls._get_current_version(grant.id)
        
        if not current_version:
            current_version = await cls._create_initial_version(grant, user_id)
        
        return current_version
    
    @classmethod
    async def _create_initial_version(cls, grant: Grants, user_id: int) -> GrantVersions:
        """建立初始版本"""
        initial_data = {
            'steps': {
                '0': cls._build_basic_data_for_version(grant),
                '1': cls._build_basic_data_for_version(grant)
            },
            'metadata': {
                'created_at': grant.created_at.isoformat() if grant.created_at else None,
                'case_number': grant.case_number,
                # 'current_step': grant.current_step,
                # 'status': grant.status,
                'initial_version': True
            }
        }
        
        return await GrantVersions.create(
            grant_id=grant.id,
            version=1,
            all_steps_data=initial_data,
            all_steps_data_hash=cls._calculate_hash(initial_data),
            comment="初始版本",
            created_by_id=user_id
        )
    
    @classmethod
    def _build_basic_data_for_version(cls, grant: Grants) -> Dict[str, Any]:
        """從 Grant model 建立版本用的基本資料"""
        return {
            'applicant_name': grant.applicant_name,
            'applicant_id': grant.applicant_id,
            'applicant_phone': grant.applicant_phone,
            'county': grant.county,
            'town': grant.town,
            'village': grant.village,
            'address': grant.address,
            'office': grant.office,
            'office_id': grant.office_id,
            'undertracker': grant.undertracker,
            'is_disaster_case': grant.is_disaster_case,
            'disaster_case_description': grant.disaster_case_description,
            'received_date': grant.received_date.isoformat() if grant.received_date else None,
            'received_time': grant.received_time.strftime("%H:%M") if grant.received_time else None,
            'case_number': grant.case_number
        }
    
    @classmethod
    async def _update_basic_data_in_grants(cls, grant: Grants, step_data: Dict[str, Any], step: int):
        """更新 Grants model 中的基本資料"""
        update_data = {}
        
        # 定義欄位映射
        field_mapping = {
            'name': 'applicant_name',
            'applicant_name': 'applicant_name',
            'id': 'applicant_id',
            'applicant_id': 'applicant_id',
            'phone': 'applicant_phone',
            'applicant_phone': 'applicant_phone',
            'county': 'county',
            'town': 'town',
            'village': 'village',
            'address': 'address',
            'office': 'office',
            'office_id': 'office_id',
            'undertracker': 'undertracker',
            'isDisasterCase': 'is_disaster_case',
            'is_disaster_case': 'is_disaster_case',
            'disasterCaseDescription': 'disaster_case_description',
            'disaster_case_description': 'disaster_case_description'
        }
        
        # 應用欄位映射
        for step_field, grant_field in field_mapping.items():
            if step_field in step_data:
                update_data[grant_field] = step_data[step_field]
        
        # 更新資料庫
        if update_data:
            await Grants.filter(id=grant.id).update(**update_data)
            
            # 重新載入 grant 物件以反映變更
            await grant.refresh_from_db()
    
    @classmethod
    async def _create_history_record(
        cls,
        grant: Grants,
        action_type: str,
        user_id: int,
        step_number: int = None,
        old_value: Dict[str, Any] = None,
        new_value: Dict[str, Any] = None,
        notes: str = None,
        session_id: str = None,
        ip_address: str = None
    ):
        """建立詳細的歷史記錄"""
        
        # 計算變更的欄位
        changed_fields = []
        if old_value and new_value:
            changed_fields = [
                key for key in new_value.keys()
                if key not in old_value or old_value[key] != new_value[key]
            ]
        
        await GrantHistory.create(
            grant=grant,
            action_type=action_type,
            grant_status=grant.status,
            step_number=step_number,
            changed_fields=changed_fields,
            old_value=old_value,
            new_value=new_value,
            session_id=session_id,
            ip_address=ip_address,
            changed_by_id=user_id,
            notes=notes
        )
    
    @staticmethod
    def _calculate_hash(data: Dict[str, Any]) -> str:
        """計算資料的 hash 值"""
        json_str = json.dumps(data, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(json_str.encode('utf-8')).hexdigest()


# 便利的介面函數供現有代碼使用
async def update_grant_version_data(
    grant_id: int,
    step: int,
    step_data: Dict[str, Any],
    user_id: int,
    action_type: str = 'data_update',
    notes: str = None,
    session_id: str = None,
    ip_address: str = None
) -> Dict[str, Any]:
    """更新案件版本資料（不建立新版本）"""
    return await GrantVersionService.update_current_version_data(
        grant_id=grant_id,
        step=step,
        step_data=step_data,
        user_id=user_id,
        action_type=action_type,
        notes=notes,
        session_id=session_id,
        ip_address=ip_address
    )

async def create_grant_design_change(
    grant_id: int,
    user_id: int,
    comment: str = None,
    session_id: str = None,
    ip_address: str = None
) -> Dict[str, Any]:
    """建立設計變更版本"""
    return await GrantVersionService.create_design_change_version(
        grant_id=grant_id,
        user_id=user_id,
        comment=comment,
        session_id=session_id,
        ip_address=ip_address
    )

async def get_grant_complete_data(grant_id: int, version_id: int = None) -> Dict[str, Any]:
    """取得完整案件資料"""
    return await GrantVersionService.get_complete_case_data(grant_id, version_id)

async def get_grant_version_history(grant_id: int) -> List[Dict[str, Any]]:
    """取得案件版本歷史"""
    return await GrantVersionService.get_version_history(grant_id)

async def get_grant_change_history(grant_id: int, limit: int = 50) -> List[Dict[str, Any]]:
    """取得案件變更歷史"""
    return await GrantVersionService.get_change_history(grant_id, limit)
