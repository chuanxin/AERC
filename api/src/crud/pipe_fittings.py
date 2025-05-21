from typing import List, Optional, Type
from tortoise.exceptions import DoesNotExist, IntegrityError
from fastapi import HTTPException

from src.database.models import PipeFittings, PFAnnualPrices, PFMaterials, PFModules, PFDiameters, Offices, Users
from src.schemas.pipe_fittings import PipeFittingCreate, PipeFittingUpdate

async def get_pipe_fitting(pomno: int) -> Optional[PipeFittings]:
    try:
        return await PipeFittings.get(pomno=pomno).prefetch_related(
            "material", "module", "diameter1", "diameter2", "diameter3", "office", "created_by", "modified_by"
        )
        
        # 獲取價格歷史記錄
        if pipe_fitting.office_id:
            pipe_fitting.price_history = await PFAnnualPrices.filter(
                pipe_fitting_id=pomno,
                office_id=pipe_fitting.office_id
            ).order_by("-year").limit(20)
            
            # 如果存在價格歷史，設置當前價格（最新年份的價格）
            if pipe_fitting.price_history:
                pipe_fitting.current_price = pipe_fitting.price_history[0].price
        else:
            pipe_fitting.price_history = []
            pipe_fitting.current_price = None
            
        return pipe_fitting
    except DoesNotExist:
        return None

async def get_pipe_fittings(skip: int = 0, limit: int = 100) -> List[PipeFittings]:
    return await PipeFittings.all().offset(skip).limit(limit).prefetch_related(
        "material", "module", "diameter1", "diameter2", "diameter3", "office", "created_by", "modified_by"
    )

    # 獲取所有管件 ID
    pipe_fitting_ids = [pf.pomno for pf in pipe_fittings]
    
    # 獲取價格歷史和當前價格
    await _add_price_info_to_pipe_fittings(pipe_fittings)
    
    return pipe_fittings

async def get_pipe_fittings_count() -> int:
    return await PipeFittings.all().count()

async def get_pipe_fittings_by_office(office_id: int, skip: int = 0, limit: int = 100) -> List[PipeFittings]:
    """
    Retrieve pipe fittings filtered by office_id with pagination.
    """
    pipe_fittings = await PipeFittings.filter(office_id=office_id).offset(skip).limit(limit).prefetch_related(
        "material", "module", "diameter1", "diameter2", "diameter3", "office", "created_by", "modified_by"
    )

    # 獲取價格歷史和當前價格
    await _add_price_info_to_pipe_fittings(pipe_fittings, office_id)
    
    return pipe_fittings

async def get_pipe_fittings_by_office_count(office_id: int) -> int:
    """
    Count pipe fittings filtered by office_id.
    """
    return await PipeFittings.filter(office_id=office_id).count()

async def create_pipe_fitting(pipe_fitting_in: PipeFittingCreate) -> PipeFittings:
    # Ensure related objects exist (basic check by ID)
    # More robust checks might involve trying to fetch them first
    if not await PFMaterials.exists(id=pipe_fitting_in.material_id):
        raise HTTPException(status_code=404, detail=f"PFMaterial with id {pipe_fitting_in.material_id} not found")
    if not await PFModules.exists(id=pipe_fitting_in.module_id):
        raise HTTPException(status_code=404, detail=f"PFModule with id {pipe_fitting_in.module_id} not found")
    if pipe_fitting_in.diameter1_id and not await PFDiameters.exists(id=pipe_fitting_in.diameter1_id):
        raise HTTPException(status_code=404, detail=f"PFDiameter (1) with id {pipe_fitting_in.diameter1_id} not found")
    if pipe_fitting_in.diameter2_id and not await PFDiameters.exists(id=pipe_fitting_in.diameter2_id):
        raise HTTPException(status_code=404, detail=f"PFDiameter (2) with id {pipe_fitting_in.diameter2_id} not found")
    if pipe_fitting_in.diameter3_id and not await PFDiameters.exists(id=pipe_fitting_in.diameter3_id):
        raise HTTPException(status_code=404, detail=f"PFDiameter (3) with id {pipe_fitting_in.diameter3_id} not found")
    if pipe_fitting_in.office_id and not await Offices.exists(id=pipe_fitting_in.office_id):
        raise HTTPException(status_code=404, detail=f"Office with id {pipe_fitting_in.office_id} not found")
    if pipe_fitting_in.created_by_id and not await Users.exists(id=pipe_fitting_in.created_by_id):
        raise HTTPException(status_code=404, detail=f"User (created_by) with id {pipe_fitting_in.created_by_id} not found")

    pipe_fitting_data = pipe_fitting_in.dict(exclude_unset=True)
    
    # Handle FKs correctly by assigning the ID to the _id field
    # Tortoise ORM expects related_field_id = value for FK assignment from ID
    for fk_field in ["material", "module", "diameter1", "diameter2", "diameter3", "office", "created_by"]:
        if f"{fk_field}_id" in pipe_fitting_data:
            pipe_fitting_data[f"{fk_field}_id"] = pipe_fitting_data.pop(f"{fk_field}_id")

    try:
        pipe_fitting_obj = await PipeFittings.create(**pipe_fitting_data)
        # To return the object with prefetched relations as in `get_pipe_fitting`
        return await get_pipe_fitting(pipe_fitting_obj.pomno)
    except IntegrityError as e:
        # This can happen due to the unique_together constraint
        raise HTTPException(status_code=409, detail=f"Pipe fitting with these attributes already exists or other integrity error: {e}")


async def update_pipe_fitting(pomno: int, pipe_fitting_in: PipeFittingUpdate) -> Optional[PipeFittings]:
    pipe_fitting_obj = await get_pipe_fitting(pomno)
    if not pipe_fitting_obj:
        return None

    update_data = pipe_fitting_in.dict(exclude_unset=True)

    # Validate FKs if they are being updated
    if "material_id" in update_data and not await PFMaterials.exists(id=update_data["material_id"]):
        raise HTTPException(status_code=404, detail=f"PFMaterial with id {update_data['material_id']} not found")
    if "module_id" in update_data and not await PFModules.exists(id=update_data["module_id"]):
        raise HTTPException(status_code=404, detail=f"PFModule with id {update_data['module_id']} not found")
    # ... add similar checks for other updatable FKs (diameter1_id, diameter2_id, diameter3_id, office_id, modified_by_id)

    # Handle FKs correctly
    for fk_field in ["material", "module", "diameter1", "diameter2", "diameter3", "office", "modified_by"]:
        if f"{fk_field}_id" in update_data:
            setattr(pipe_fitting_obj, f"{fk_field}_id", update_data.pop(f"{fk_field}_id"))
            
    for key, value in update_data.items():
        setattr(pipe_fitting_obj, key, value)
    
    try:
        await pipe_fitting_obj.save()
        # Return the updated object with prefetched relations
        return await get_pipe_fitting(pipe_fitting_obj.pomno)
    except IntegrityError as e:
        raise HTTPException(status_code=409, detail=f"Update failed due to integrity constraint: {e}")


async def delete_pipe_fitting(pomno: int) -> bool:
    pipe_fitting_obj = await get_pipe_fitting(pomno)
    if not pipe_fitting_obj:
        return False
    await pipe_fitting_obj.delete()
    return True

async def _add_price_info_to_pipe_fittings(pipe_fittings: List[PipeFittings], office_id: Optional[int] = None) -> None:
    """
    為管件列表添加價格信息
    """
    if not pipe_fittings:
        return
    
    # 獲取所有管件 ID
    pipe_fitting_ids = [pf.pomno for pf in pipe_fittings]
    
    # 獲取價格歷史記錄
    price_query = PFAnnualPrices.filter(pipe_fitting_id__in=pipe_fitting_ids)
    if office_id is not None:
        price_query = price_query.filter(office_id=office_id)
    
    all_prices = await price_query.all()
    
    # 按管件 ID 分組
    prices_by_pipe_fitting = {}
    for price in all_prices:
        if price.pipe_fitting_id not in prices_by_pipe_fitting:
            prices_by_pipe_fitting[price.pipe_fitting_id] = []
        prices_by_pipe_fitting[price.pipe_fitting_id].append(price)
    
    # 為每個管件添加價格信息
    for pipe_fitting in pipe_fittings:
        pipe_fitting_prices = prices_by_pipe_fitting.get(pipe_fitting.pomno, [])
        
        # 按年份降序排序
        pipe_fitting_prices.sort(key=lambda p: p.year, reverse=True)
        
        # 設置價格歷史和當前價格
        pipe_fitting.price_history = pipe_fitting_prices
        pipe_fitting.current_price = pipe_fitting_prices[0].price if pipe_fitting_prices else None