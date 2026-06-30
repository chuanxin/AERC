from typing import List
from fastapi import APIRouter, HTTPException, Depends, Query

from src.schemas.pipe_fittings import PipeFittingCreate, PipeFittingUpdate, PipeFittingResponse, PipeFittingListResponse
from src.database.models import Offices
import src.crud.pipe_fittings as crud_pipe_fittings
from src.auth.guard import require_full_auth
from src.services.permission_service import permission_service
from src.schemas.permissions import ModuleName, PermissionAction
from src.exceptions import AppError

router = APIRouter()

@router.post("/", response_model=PipeFittingResponse, status_code=201, summary="Create Pipe Fitting")
async def create_pipe_fitting_endpoint(
    pipe_fitting_in: PipeFittingCreate,
    current_user=Depends(require_full_auth),
):
    """Create a new pipe fitting."""
    allowed, _ = permission_service.check_permission(
        current_user.role, current_user.permissions, ModuleName.MATERIALS, PermissionAction.CREATE
    )
    if not allowed:
        raise AppError(403, "無此操作權限")
    return await crud_pipe_fittings.create_pipe_fitting(pipe_fitting_in=pipe_fitting_in)

@router.get("/{pomno}", response_model=PipeFittingResponse, summary="Read Pipe Fitting")
async def read_pipe_fitting_endpoint(pomno: int):
    """Get a specific pipe fitting by its POMNO."""
    db_pipe_fitting = await crud_pipe_fittings.get_pipe_fitting(pomno=pomno)
    if db_pipe_fitting is None:
        raise HTTPException(status_code=404, detail="PipeFitting not found")
    return db_pipe_fitting

@router.get("/", response_model=PipeFittingListResponse, summary="Read Pipe Fittings")
async def read_pipe_fittings_endpoint(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
):
    """Retrieve a list of pipe fittings with pagination."""
    items = await crud_pipe_fittings.get_pipe_fittings(skip=skip, limit=limit)
    total = await crud_pipe_fittings.get_pipe_fittings_count()
    return {"items": items, "total": total}

@router.get("/office/{office_id}", response_model=PipeFittingListResponse, summary="Read Pipe Fittings by Office ID")
async def read_pipe_fittings_by_office_endpoint(
    office_id: int,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    include_inactive: bool = Query(False, description="Include inactive pipe fittings (for management UI)"),
):
    """Retrieve a list of pipe fittings filtered by office_id with pagination."""
    if not await Offices.exists(id=office_id):
        raise HTTPException(status_code=404, detail=f"Office with id {office_id} not found")
    items = await crud_pipe_fittings.get_pipe_fittings_by_office(
        office_id=office_id, skip=skip, limit=limit, include_inactive=include_inactive
    )
    total = await crud_pipe_fittings.get_pipe_fittings_by_office_count(
        office_id=office_id, include_inactive=include_inactive
    )
    return {"items": items, "total": total}

@router.put("/{pomno}", response_model=PipeFittingResponse, summary="Update Pipe Fitting")
async def update_pipe_fitting_endpoint(
    pomno: int,
    pipe_fitting_in: PipeFittingUpdate,
    current_user=Depends(require_full_auth),
):
    """Update an existing pipe fitting."""
    allowed, _ = permission_service.check_permission(
        current_user.role, current_user.permissions, ModuleName.MATERIALS, PermissionAction.EDIT
    )
    if not allowed:
        raise AppError(403, "無此操作權限")
    updated_pipe_fitting = await crud_pipe_fittings.update_pipe_fitting(pomno=pomno, pipe_fitting_in=pipe_fitting_in)
    if updated_pipe_fitting is None:
        raise HTTPException(status_code=404, detail="PipeFitting not found")
    return updated_pipe_fitting

@router.delete("/{pomno}", status_code=204, summary="Delete Pipe Fitting")
async def delete_pipe_fitting_endpoint(
    pomno: int,
    current_user=Depends(require_full_auth),
):
    """Delete a pipe fitting."""
    allowed, _ = permission_service.check_permission(
        current_user.role, current_user.permissions, ModuleName.MATERIALS, PermissionAction.DELETE
    )
    if not allowed:
        raise AppError(403, "無此操作權限")
    deleted = await crud_pipe_fittings.delete_pipe_fitting(pomno=pomno)
    if not deleted:
        raise HTTPException(status_code=404, detail="PipeFitting not found")
    return
