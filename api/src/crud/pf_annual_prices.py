from typing import List, Optional
from tortoise.exceptions import DoesNotExist, IntegrityError
from fastapi import HTTPException

from src.database.models import PFAnnualPrices, PipeFittings, Offices, Users
from src.schemas.pf_annual_prices import PFAnnualPriceCreate, PFAnnualPriceUpdate

# async def get_pf_annual_price(price_id: int) -> Optional[models.PfAnnualPrices]:
#     """
#     Retrieve a single annual price by its ID.
#     """
#     return await models.PfAnnualPrices.get_or_none(id=price_id)

# async def get_pf_annual_prices_by_fitting_id(
#     fitting_id: int, skip: int = 0, limit: int = 100
# ) -> List[models.PfAnnualPrices]:
#     """
#     Retrieve all annual prices for a specific pipe fitting, ordered by year descending.
#     """
#     return (
#         await models.PfAnnualPrices.filter(pipe_fitting_id=fitting_id)
#         .order_by("-year")
#         .offset(skip)
#         .limit(limit)
#     )

# async def get_latest_pf_annual_price_for_fitting(
#     fitting_id: int
# ) -> Optional[models.PfAnnualPrices]:
#     """
#     Retrieve the most recent annual price for a specific pipe fitting based on the year.
#     """
#     return (
#         await models.PfAnnualPrices.filter(pipe_fitting_id=fitting_id)
#         .order_by("-year")
#         .first()
#     )

# async def get_pf_annual_price_for_fitting_and_year(
#     fitting_id: int, year: int
# ) -> Optional[models.PfAnnualPrices]:
#     """
#     Retrieve a specific annual price for a fitting and year.
#     """
#     return await models.PfAnnualPrices.get_or_none(
#         pipe_fitting_id=fitting_id, year=year
#     )

# async def create_or_update_fitting_annual_price(
#     fitting_id: int, year: int, unit_price: float
# ) -> models.PfAnnualPrices:
#     """
#     Creates a new annual price for a pipe fitting or updates it if it already exists for that year.
#     """
#     # Check if the related PipeFitting exists to ensure data integrity
#     pipe_fitting = await models.PipeFittings.get_or_none(id=fitting_id)
#     if not pipe_fitting:
#         # Consider raising an exception here that can be caught by the route
#         # For example: raise ValueError(f"PipeFitting with id {fitting_id} not found")
#         # which would then be handled in the route to return an HTTPException
#         # For now, this function assumes fitting_id is valid or route handles it.
#         pass # Or raise an error

#     # Tortoise's update_or_create is ideal here.
#     # It requires specifying which fields to match for the 'get' part,
#     # and which fields to update or use for creation.
#     defaults = {"unit_price": unit_price, "updated_at": datetime.datetime.utcnow()}
    
#     # We need the pipe_fitting object (or its id) for creation.
#     # If pipe_fitting_id is a direct field in PfAnnualPrices, it's simpler.
#     # If it's through a relation `pipe_fitting`, we'd pass `pipe_fitting=pipe_fitting_obj`.
#     # Assuming `pipe_fitting_id` is the foreign key field name in `PfAnnualPrices` model.
    
#     annual_price, created = await models.PfAnnualPrices.update_or_create(
#         defaults=defaults,
#         pipe_fitting_id=fitting_id, # Match existing record by fitting_id and year
#         year=year
#     )
    
#     # If it was just created, the 'created_at' might not be set by update_or_create's defaults
#     # if it uses default=datetime.utcnow in the model.
#     # If 'created_at' is auto_now_add=True in the model, it's handled.
#     # If not, and it was created, we might need to set it explicitly if not handled by model defaults.
#     # However, update_or_create typically handles this well if model fields are defined with defaults.
#     # The `updated_at` is in `defaults`, so it will be set.

#     return annual_price


# async def delete_pf_annual_price(price_id: int) -> int:
#     """
#     Deletes an annual price by its ID.
#     Returns the number of rows deleted (0 or 1).
#     """
#     deleted_count = await models.PfAnnualPrices.filter(id=price_id).delete()
#     return deleted_count

async def get_annual_price(price_id: int) -> Optional[PFAnnualPrices]:
    try:
        return await PFAnnualPrices.get(id=price_id).prefetch_related(
            "pipe_fitting", "office", "created_by", "modified_by"
        )
    except DoesNotExist:
        return None

async def get_annual_prices(skip: int = 0, limit: int = 100) -> List[PFAnnualPrices]:
    return await PFAnnualPrices.all().offset(skip).limit(limit).prefetch_related(
        "pipe_fitting", "office", "created_by", "modified_by"
    )

async def get_annual_prices_count() -> int:
    return await PFAnnualPrices.all().count()

async def get_annual_prices_by_pipe_fitting(
    pipe_fitting_id: int, 
    office_id: Optional[int] = None,
    skip: int = 0, 
    limit: int = 100
) -> List[PFAnnualPrices]:
    """
    獲取指定管件的年度價格列表
    """
    query = PFAnnualPrices.filter(pipe_fitting_id=pipe_fitting_id)
    if office_id:
        query = query.filter(office_id=office_id)
    
    return await query.order_by("-year").offset(skip).limit(limit).prefetch_related(
        "pipe_fitting", "office", "created_by", "modified_by"
    )

async def get_annual_prices_by_pipe_fitting_count(
    pipe_fitting_id: int, 
    office_id: Optional[int] = None
) -> int:
    """
    獲取指定管件的年度價格數量
    """
    query = PFAnnualPrices.filter(pipe_fitting_id=pipe_fitting_id)
    if office_id:
        query = query.filter(office_id=office_id)
    
    return await query.count()

async def get_current_price_by_pipe_fitting(
    pipe_fitting_id: int,
    office_id: Optional[int] = None
) -> Optional[PFAnnualPrices]:
    """
    獲取指定管件的當前價格(最新年度的價格)
    """
    query = PFAnnualPrices.filter(pipe_fitting_id=pipe_fitting_id, is_active=True)
    if office_id:
        query = query.filter(office_id=office_id)
    
    return await query.order_by("-year").first().prefetch_related(
        "pipe_fitting", "office", "created_by", "modified_by"
    )

async def create_annual_price(price_in: PFAnnualPriceCreate) -> PFAnnualPrices:
    # 確認關聯實體存在
    if not await PipeFittings.exists(pomno=price_in.pipe_fitting_id):
        raise HTTPException(status_code=404, detail=f"PipeFitting with id {price_in.pipe_fitting_id} not found")
    
    if price_in.office_id and not await Offices.exists(id=price_in.office_id):
        raise HTTPException(status_code=404, detail=f"Office with id {price_in.office_id} not found")
    
    if price_in.created_by_id and not await Users.exists(id=price_in.created_by_id):
        raise HTTPException(status_code=404, detail=f"User with id {price_in.created_by_id} not found")

    # 檢查是否已存在相同管件和年度的價格記錄
    existing_price = await PFAnnualPrices.filter(
        pipe_fitting_id=price_in.pipe_fitting_id,
        year=price_in.year,
        office_id=price_in.office_id
    ).first()
    
    if existing_price:
        raise HTTPException(
            status_code=409, 
            detail=f"Price record for pipe_fitting_id={price_in.pipe_fitting_id}, year={price_in.year}, office_id={price_in.office_id} already exists"
        )

    try:
        price_obj = await PFAnnualPrices.create(**price_in.dict(exclude_unset=True))
        return await get_annual_price(price_obj.id)
    except IntegrityError as e:
        raise HTTPException(status_code=409, detail=f"Failed to create price record: {e}")

async def update_annual_price(price_id: int, price_in: PFAnnualPriceUpdate) -> Optional[PFAnnualPrices]:
    price_obj = await get_annual_price(price_id)
    if not price_obj:
        return None

    update_data = price_in.dict(exclude_unset=True)
    
    # 驗證外鍵
    if "pipe_fitting_id" in update_data and not await PipeFittings.exists(pomno=update_data["pipe_fitting_id"]):
        raise HTTPException(status_code=404, detail=f"PipeFitting with id {update_data['pipe_fitting_id']} not found")
    
    if "office_id" in update_data and update_data["office_id"] and not await Offices.exists(id=update_data["office_id"]):
        raise HTTPException(status_code=404, detail=f"Office with id {update_data['office_id']} not found")
    
    if "modified_by_id" in update_data and update_data["modified_by_id"] and not await Users.exists(id=update_data["modified_by_id"]):
        raise HTTPException(status_code=404, detail=f"User with id {update_data['modified_by_id']} not found")

    # 檢查更新後是否會違反唯一約束
    if ("pipe_fitting_id" in update_data or "year" in update_data or "office_id" in update_data):
        pipe_fitting_id = update_data.get("pipe_fitting_id", price_obj.pipe_fitting_id)
        year = update_data.get("year", price_obj.year)
        office_id = update_data.get("office_id", price_obj.office_id)
        
        existing_price = await PFAnnualPrices.filter(
            pipe_fitting_id=pipe_fitting_id,
            year=year,
            office_id=office_id
        ).exclude(id=price_id).first()
        
        if existing_price:
            raise HTTPException(
                status_code=409, 
                detail=f"Price record for pipe_fitting_id={pipe_fitting_id}, year={year}, office_id={office_id} already exists"
            )

    # 更新對象
    for key, value in update_data.items():
        setattr(price_obj, key, value)
    
    try:
        await price_obj.save()
        return await get_annual_price(price_obj.id)
    except IntegrityError as e:
        raise HTTPException(status_code=409, detail=f"Failed to update price record: {e}")

async def delete_annual_price(price_id: int) -> bool:
    price_obj = await get_annual_price(price_id)
    if not price_obj:
        return False
    
    await price_obj.delete()
    return True

