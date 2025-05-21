from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.crud import pf_annual_prices as crud_pf_annual_prices
from src.schemas.pf_annual_prices import PFAnnualPriceCreate, PFAnnualPriceUpdate, PFAnnualPricesResponse, PFAnnualPricesListResponse

router = APIRouter(
    prefix="/pf_annual_prices",
    tags=["PFAnnualPrices"],
)

@router.post("/", response_model=PFAnnualPricesResponse, status_code=status.HTTP_201_CREATED)
async def create_annual_price(
    price_in: PFAnnualPriceCreate,
):
    """
    創建一個新的管件年度價格
    """
    return await crud_pf_annual_prices.create_annual_price(price_in=price_in)

@router.get("/", response_model=PFAnnualPricesListResponse)
async def read_annual_prices(
    skip: int = Query(0, ge=0, description="分頁起始位置"),
    limit: int = Query(100, ge=1, le=500, description="每頁數量"),
):
    """
    獲取所有管件年度價格
    """
    items = await crud_pf_annual_prices.get_annual_prices(skip=skip, limit=limit)
    total = await crud_pf_annual_prices.get_annual_prices_count()
    return {"items": items, "total": total}

@router.get("/{price_id}", response_model=PFAnnualPricesResponse)
async def read_annual_price(
    price_id: int,
):
    """
    根據ID獲取管件年度價格
    """
    price = await crud_pf_annual_prices.get_annual_price(price_id)
    if not price:
        raise HTTPException(status_code=404, detail="Annual price not found")
    return price

@router.get("/pipe_fitting/{pipe_fitting_id}", response_model=PFAnnualPricesListResponse)
async def read_annual_prices_by_pipe_fitting(
    pipe_fitting_id: int,
    office_id: Optional[int] = Query(None, description="所屬單位/管理處ID"),
    skip: int = Query(0, ge=0, description="分頁起始位置"),
    limit: int = Query(100, ge=1, le=500, description="每頁數量"),
):
    """
    獲取指定管件的所有年度價格
    """
    items = await crud_pf_annual_prices.get_annual_prices_by_pipe_fitting(
        pipe_fitting_id=pipe_fitting_id,
        office_id=office_id,
        skip=skip,
        limit=limit,
    )
    total = await crud_pf_annual_prices.get_annual_prices_by_pipe_fitting_count(
        pipe_fitting_id=pipe_fitting_id,
        office_id=office_id,
    )
    return {"items": items, "total": total}

@router.get("/pipe_fitting/{pipe_fitting_id}/current", response_model=PFAnnualPricesResponse)
async def read_current_price_by_pipe_fitting(
    pipe_fitting_id: int,
    office_id: Optional[int] = Query(None, description="所屬單位/管理處ID"),
):
    """
    獲取指定管件的當前價格(最新年度價格)
    """
    price = await crud_pf_annual_prices.get_current_price_by_pipe_fitting(
        pipe_fitting_id=pipe_fitting_id,
        office_id=office_id,
    )
    if not price:
        raise HTTPException(status_code=404, detail="No active price found for this pipe fitting")
    return price

@router.put("/{price_id}", response_model=PFAnnualPricesResponse)
async def update_annual_price(
    price_id: int,
    price_in: PFAnnualPriceUpdate,
):
    """
    更新指定的管件年度價格
    """
    updated_price = await crud_pf_annual_prices.update_annual_price(price_id=price_id, price_in=price_in)
    if not updated_price:
        raise HTTPException(status_code=404, detail="Annual price not found")
    return updated_price

@router.delete("/{price_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_annual_price(
    price_id: int,
):
    """
    刪除指定的管件年度價格
    """
    success = await crud_pf_annual_prices.delete_annual_price(price_id=price_id)
    if not success:
        raise HTTPException(status_code=404, detail="Annual price not found")
    return None