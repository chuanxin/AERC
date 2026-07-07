import logging
from typing import Dict, Any
from fastapi import HTTPException
from tortoise.exceptions import DoesNotExist, IntegrityError
from src.schemas.offices import OfficeOutSchema

from src.database.models import Offices

logger = logging.getLogger(__name__)


async def paginate_queryset(queryset, page: int = 1, size: int = 10):
    """通用分頁函數"""
    total = await queryset.count()
    
    if size <= 0:
        size = total or 1
    
    pages = (total + size - 1) // size  # 計算總頁數
    
    if page < 1:
        page = 1
    elif page > pages and pages > 0:
        page = pages
    
    skip = (page - 1) * size
    
    items = await queryset.offset(skip).limit(size)
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "size": size,
        "pages": pages
    }


# ==================== Offices CRUD ====================

async def get_all_offices():
    # TODO: Consider replacing from_queryset with manual schema construction
    # if OfficeOutSchema includes complex relations in the future
    # Currently safe as OfficeOutSchema only includes basic fields
    """獲取所有管理處/單位並以 id 排序，可以擴充分頁和搜索方法"""
    return await OfficeOutSchema.from_queryset(Offices.all().order_by("id"))


async def get_office_by_id(office_id: int):
    """獲取單一管理處/單位"""
    try:
        return await Offices.get(id=office_id)
    except DoesNotExist:
        raise HTTPException(status_code=404, detail=f"Office with ID {office_id} not found")


async def create_office(data: Dict[str, Any]):
    """創建新的管理處/單位"""
    try:
        return await Offices.create(**data)
    except IntegrityError as e:
        # name/short_name/code 三個候選欄位皆可能觸發，訊息刻意不指控單一欄位；
        # 保留診斷以便排查非這三者造成的衝突（如 PK 序列問題）
        logger.warning("[create_office] IntegrityError（data=%s）：%s", data, str(e))
        raise HTTPException(status_code=409, detail="單位名稱、縮寫或代碼已存在")


async def update_office(office_id: int, data: Dict[str, Any]):
    """更新管理處/單位"""
    try:
        office = await get_office_by_id(office_id)

        # 更新欄位
        for key, value in data.items():
            setattr(office, key, value)

        await office.save()
        return office
    except IntegrityError as e:
        logger.warning("[update_office] IntegrityError（office_id=%s）：%s", office_id, str(e))
        raise HTTPException(status_code=409, detail="單位名稱、縮寫或代碼已存在")


async def delete_office(office_id: int):
    """刪除管理處/單位"""
    office = await get_office_by_id(office_id)
    
    # 檢查是否有關聯的數據
    # 如果有可能想要防止刪除有關聯數據的記錄
    
    await office.delete()
    return {"message": f"Office with ID {office_id} has been deleted"}