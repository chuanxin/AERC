# 前後端字段映射配置
# 用於確保前後端字段名稱一致性，避免數據同步問題

from typing import Dict, Any, List
from enum import Enum

class FieldMappingConfig:
    """前後端字段映射配置類"""
    
    # 定義各個步驟的標準字段映射
    STEP_FIELD_MAPPINGS = {
        1: {  # Step 1: 申請人基本資料
            # 標準字段名 -> 數據庫字段名
            "name": "applicant_name",
            "id": "applicant_id", 
            "phone": "applicant_phone",
            "phone2": "applicant_phone2",
            "county": "county",
            "countyId": "county_id",
            "town": "town",
            "townId": "town_id", 
            "village": "village",
            "villageId": "village_id",
            "address": "address",
            "undertracker": "undertracker",  # 統一使用新字段名
            "office": "office",              # 統一使用新字段名
            "officeId": "office_id",
            "caseNumber": "case_number",
            "receivedDate": "received_date",
            "receivedTime": "received_time",
            "valid": "valid",
            "isDisasterCase": "is_disaster_case",
            "disasterCaseDescription": "disaster_case_description"
        },
        2: {  # Step 2: 土地資訊
            "landCounty": "land_county",
            "landTown": "land_town", 
            "landSec": "land_section",
            "landNumber": "land_number",
            "landArea": "land_area",
            "facilityArea": "facility_area",
            # ... 其他 step2 字段
        },
        # ... 其他步驟
    }
    
    # 已棄用的字段名映射（向後兼容）
    DEPRECATED_FIELD_MAPPINGS = {
        1: {
            # "manager": "undertracker",      # 舊字段名 -> 新字段名
            # "department": "office",         # 舊字段名 -> 新字段名
            # "departmentId": "officeId",     # 舊字段名 -> 新字段名
        }
    }
    
    @classmethod
    def get_api_response_fields(cls, step: int) -> Dict[str, str]:
        """獲取 API 響應應該使用的字段名（前端字段名 -> 數據庫字段名）"""
        return cls.STEP_FIELD_MAPPINGS.get(step, {})
    
    @classmethod
    def get_db_to_api_mapping(cls, step: int) -> Dict[str, str]:
        """獲取數據庫字段到 API 字段的映射（數據庫字段名 -> 前端字段名）"""
        field_mapping = cls.STEP_FIELD_MAPPINGS.get(step, {})
        return {db_field: api_field for api_field, db_field in field_mapping.items()}
    
    @classmethod
    def validate_request_fields(cls, step: int, data: Dict[str, Any]) -> Dict[str, List[str]]:
        """驗證請求數據的字段名是否正確"""
        expected_fields = set(cls.STEP_FIELD_MAPPINGS.get(step, {}).keys())
        received_fields = set(data.keys())
        deprecated_fields = set(cls.DEPRECATED_FIELD_MAPPINGS.get(step, {}).keys())
        
        return {
            "missing_fields": list(expected_fields - received_fields),
            "unexpected_fields": list(received_fields - expected_fields - deprecated_fields),
            "deprecated_fields": list(received_fields & deprecated_fields)
        }
    
    @classmethod
    def normalize_request_data(cls, step: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """標準化請求數據，將舊字段名轉換為新字段名"""
        normalized_data = data.copy()
        deprecated_mappings = cls.DEPRECATED_FIELD_MAPPINGS.get(step, {})
        
        for old_field, new_field in deprecated_mappings.items():
            if old_field in normalized_data and new_field not in normalized_data:
                normalized_data[new_field] = normalized_data.pop(old_field)
                
        return normalized_data


# 字段驗證裝飾器
def validate_step_fields(step: int):
    """裝飾器：驗證 API 端點的字段名稱"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            import inspect
            import logging
            
            logger = logging.getLogger(__name__)
            
            # 檢查函數是否返回字典（API 響應）
            result = func(*args, **kwargs)
            
            # 如果是異步函數，需要等待結果
            if inspect.iscoroutine(result):
                async def async_wrapper():
                    actual_result = await result
                    if isinstance(actual_result, dict):
                        # 驗證響應字段
                        validation = FieldMappingConfig.validate_request_fields(step, actual_result)
                        
                        if validation["unexpected_fields"]:
                            logger.warning(f"Step {step} API 響應包含未預期字段: {validation['unexpected_fields']}")
                        
                        if validation["deprecated_fields"]:
                            logger.warning(f"Step {step} API 響應包含棄用字段: {validation['deprecated_fields']}")
                            
                    return actual_result
                return async_wrapper()
            else:
                if isinstance(result, dict):
                    # 驗證響應字段
                    validation = FieldMappingConfig.validate_request_fields(step, result)
                    
                    if validation["unexpected_fields"]:
                        logger.warning(f"Step {step} API 響應包含未預期字段: {validation['unexpected_fields']}")
                    
                    if validation["deprecated_fields"]:
                        logger.warning(f"Step {step} API 響應包含棄用字段: {validation['deprecated_fields']}")
                        
                return result
        return wrapper
    return decorator


# 類型定義（與前端 TypeScript 類型對應）
class Step1Fields:
    """Step 1 字段定義，與前端 Step1Data 類型對應"""
    name: str
    id: str
    phone: str
    county: str
    countyId: int = None
    town: str
    townId: int = None
    village: str
    villageId: int = None
    address: str
    undertracker: str
    office: str
    officeId: int = None
    caseNumber: str
    receivedDate: str
    receivedTime: str
    valid: bool = None
    isDisasterCase: bool = False
    disasterCaseDescription: str = ""
