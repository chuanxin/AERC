# from typing import List, Optional
# from pydantic import BaseModel, Field
from tortoise.contrib.pydantic import pydantic_model_creator

from src.database.models import Offices


# Office model
OfficeInSchema = pydantic_model_creator(
    Offices, name="OfficeIn", exclude_readonly=True
)
OfficeOutSchema = pydantic_model_creator(
    Offices, name="OfficeOut", exclude=("grant", "user")
)

# # 通用的分頁響應模型
# class PaginatedResponse(BaseModel):
#     """通用分頁響應格式"""
#     items: List
#     total: int
#     page: int
#     size: int
#     pages: int


# # Office 分頁響應
# class PaginatedOfficeResponse(PaginatedResponse):
#     items: List[OfficeOutSchema]