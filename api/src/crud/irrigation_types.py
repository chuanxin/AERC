from typing import List, Optional
from tortoise.exceptions import DoesNotExist

from src.database.models import IrrigationTypes
from src.schemas.irrigation_types import IrrigationType as IrrigationTypeSchema, IrrigationTypeOptions # Use the Pydantic schema

async def get_irrigation_types(skip: int = 0, limit: int = 100) -> List[IrrigationTypeSchema]:
    """
    Retrieve a list of irrigation types with pagination.
    Tortoise ORM models are Pydantic-compatible, so they can be returned directly
    if the response_model in the router is configured to use the Pydantic schema with orm_mode=True.
    """
    return await IrrigationTypes.all().offset(skip).limit(limit)

async def get_irrigation_type(irrigation_type_id: int) -> Optional[IrrigationTypeSchema]:
    """
    Retrieve a single irrigation type by its ID.
    Returns the object if found, or None if not found.
    """
    try:
        # Tortoise's .get() method raises DoesNotExist if not found.
        # We can also use .get_or_none() if we prefer None to be returned directly by Tortoise.
        irrigation_type = await IrrigationTypes.get_or_none(id=irrigation_type_id)
        return irrigation_type 
    except DoesNotExist: # This catch might be redundant if using .get_or_none()
        return None

async def get_irrigation_type_options() -> List[IrrigationTypeOptions]:
    """
    Retrieve all active irrigation types and organize them into a hierarchical tree structure.
    Includes self-referencing nodes once inside their own option list.
    """
    all_items = await IrrigationTypes.filter(is_active=True).values()
    id_map = {item["id"]: {**item, "option": []} for item in all_items}
    roots = []

    for item in id_map.values():
        parent_id = item["parent_id"]

        # Self-referencing node (e.g., id=2, parent_id=2)
        if parent_id == item["id"]:
            # Add to roots
            roots.append(item)

            # Clone self and add to own option list (prevent pointer issues)
            item["option"].append({**item, "option": []})

        elif parent_id is None:
            roots.append(item)

        else:
            parent = id_map.get(parent_id)
            if parent:
                parent["option"].append(item)

    return [IrrigationTypeOptions(**root) for root in roots]
# Since it's read-only, we are not implementing create, update, delete for now.
# If full CRUD were needed, they would look like this:
#
# from src.schemas.irrigation_types import IrrigationTypeCreate, IrrigationTypeUpdate
#
# async def create_irrigation_type(irrigation_type: IrrigationTypeCreate) -> IrrigationTypeSchema:
#     db_irrigation_type = await IrrigationTypes.create(**irrigation_type.model_dump())
#     return db_irrigation_type
#
# async def update_irrigation_type(irrigation_type_id: int, irrigation_type_update: IrrigationTypeUpdate) -> Optional[IrrigationTypeSchema]:
#     db_irrigation_type = await IrrigationTypes.get_or_none(id=irrigation_type_id)
#     if db_irrigation_type:
#         # Update fields from irrigation_type_update, excluding unset values
#         update_data = irrigation_type_update.model_dump(exclude_unset=True)
#         db_irrigation_type.update_from_dict(update_data) # Tortoise ORM method
#         await db_irrigation_type.save()
#         return db_irrigation_type
#     return None
#
# async def delete_irrigation_type(irrigation_type_id: int) -> bool:
#     deleted_count = await IrrigationTypes.filter(id=irrigation_type_id).delete()
#     return deleted_count > 0
